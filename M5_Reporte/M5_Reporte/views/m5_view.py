# m5_view.py
import tkinter as tk
from tkinter import ttk, messagebox, font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from controllers.m5_controller import SpeedReportController
import re

# Paleta y tipografías
C_HEADER    = "#3F5F91"
C_ACCENT    = "#2C3E50"
C_BODY_BG   = "#EBF0F5"
C_CARD_BG   = "#FFFFFF"
TEXT_COLOR  = "#1f2937"

DEFAULT_FONT = ('Segoe UI', 10)
TITLE_FONT = ('Segoe UI', 14, 'bold')
SMALL_FONT = ('Segoe UI', 9)


class SpeedReportView(tk.Tk):
    """
    Vista principal del módulo 5 (Reporte de Velocidad) con DOS gráficas:
      - izquierda: Tareas por semana
      - derecha: Tareas por iteración (sprint)
    Los controles (proyecto + checkbox) se aplican a ambas; hay botón 'Actualizar ambas'.
    """

    def __init__(self, controller: SpeedReportController):
        super().__init__()
        self.controller = controller
        self.title('Reporte de Velocidad')
        self.configure(bg=C_BODY_BG)
        self.geometry('1100x700')
        self.minsize(900, 600)

        # estilos
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TCombobox', padding=4, relief='flat', font=DEFAULT_FONT)
        style.configure('TButton', font=DEFAULT_FONT)
        default = font.nametofont("TkDefaultFont")
        default.configure(family=DEFAULT_FONT[0], size=DEFAULT_FONT[1])

        # header
        header = tk.Frame(self, bg=C_HEADER, height=64)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        tk.Label(header, text='Reporte de Velocidad', bg=C_HEADER, fg='white', font=TITLE_FONT).pack(side='left', padx=20, pady=12)
        tk.Label(header, text=f'{datetime.utcnow().strftime("%Y-%m-%d")}', bg=C_HEADER, fg='white', font=SMALL_FONT).pack(side='right', padx=16)

        # body
        body = tk.Frame(self, bg=C_BODY_BG)
        body.pack(fill='both', expand=True, padx=16, pady=12)

        # controles
        controls = tk.Frame(body, bg=C_BODY_BG)
        controls.pack(fill='x', pady=(0,8))

        left_controls = tk.Frame(controls, bg=C_BODY_BG)
        left_controls.pack(side='left', anchor='w')

        tk.Label(left_controls, text='Proyecto:', bg=C_BODY_BG, fg=TEXT_COLOR, font=DEFAULT_FONT).grid(row=0, column=0, sticky='w', padx=(0,8), pady=2)
        self.combo_values = []
        self.project_map = {}
        self.combo = ttk.Combobox(left_controls, values=self.combo_values, state='readonly', width=36)
        self.combo.grid(row=0, column=1, sticky='w', pady=2)

        self.solo_iter_var = tk.BooleanVar(value=False)
        self.chk_solo_iter = tk.Checkbutton(left_controls, text='Solo iteración actual (si aplica)', variable=self.solo_iter_var,
                                            bg=C_BODY_BG, fg=TEXT_COLOR, font=SMALL_FONT, activebackground=C_BODY_BG)
        self.chk_solo_iter.grid(row=1, column=1, sticky='w', pady=(4,0))

        # botones (derecha)
        right_controls = tk.Frame(controls, bg=C_BODY_BG)
        right_controls.pack(side='right', anchor='e')

        btn_refresh = tk.Button(right_controls, text='Refrescar proyectos', command=self.cargar_proyectos,
                                bg=C_CARD_BG, fg=TEXT_COLOR, relief='groove', padx=8, pady=4)
        btn_refresh.pack(side='right', padx=(8,0))

        btns = tk.Frame(right_controls, bg=C_BODY_BG)
        btns.pack(side='right', padx=(0,8))
        btn_week = tk.Button(btns, text='Mostrar semana', command=self.mostrar_semana,
                             bg=C_HEADER, fg='white', relief='raised', padx=12, pady=6)
        btn_week.pack(side='left', padx=(0,8))
        btn_iter = tk.Button(btns, text='Mostrar iteración', command=self.mostrar_iteracion,
                             bg=C_HEADER, fg='white', relief='raised', padx=12, pady=6)
        btn_iter.pack(side='left', padx=(0,8))

        # Botón que actualiza AMBAS gráficas con los filtros actuales
        btn_both = tk.Button(btns, text='Actualizar ambas', command=self.actualizar_ambas,
                             bg=C_ACCENT, fg='white', relief='raised', padx=12, pady=6)
        btn_both.pack(side='left')

        # Panel de tarjetas con dos columnas (izquierda: semana, derecha: iteración)
        cards_frame = tk.Frame(body, bg=C_BODY_BG)
        cards_frame.pack(fill='both', expand=True)

        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(0, weight=1, uniform='col')
        cards_frame.grid_columnconfigure(1, weight=1, uniform='col')

        # tarjeta izquierda: por semana
        left_card = tk.Frame(cards_frame, bg=C_CARD_BG, padx=12, pady=10, width=1, height=540)
        left_card.configure(highlightthickness=1, highlightbackground='#D0D5DD')
        left_card.grid(row=0, column=0, sticky='nsew', padx=(0,8), pady=4)
        left_card.grid_propagate(False)   # fija el tamaño vertical

        tk.Label(left_card, text='Tareas completadas por semana', bg=C_CARD_BG, fg=C_ACCENT, font=('Segoe UI',10,'bold')).pack(anchor='w', pady=(0,6))

        self.fig_week = Figure(figsize=(8,6))
        self.ax_week = self.fig_week.add_subplot(111)
        self.canvas_week = FigureCanvasTkAgg(self.fig_week, master=left_card)
        self.canvas_week.get_tk_widget().pack(fill='both', expand=True)

        # tarjeta derecha: por iteración
        right_card = tk.Frame(cards_frame, bg=C_CARD_BG, padx=12, pady=10, width=1, height=540)
        right_card.configure(highlightthickness=1, highlightbackground='#D0D5DD')
        right_card.grid(row=0, column=1, sticky='nsew', padx=(8,0), pady=4)
        right_card.grid_propagate(False)  # fija el tamaño vertical

        tk.Label(right_card, text='Tareas completadas por iteración', bg=C_CARD_BG, fg=C_ACCENT, font=('Segoe UI',10,'bold')).pack(anchor='w', pady=(0,6))

        self.fig_iter = Figure(figsize=(8,6))
        self.ax_iter = self.fig_iter.add_subplot(111)
        self.canvas_iter = FigureCanvasTkAgg(self.fig_iter, master=right_card)
        self.canvas_iter.get_tk_widget().pack(fill='both', expand=True)

        # status inferior
        status_frame = tk.Frame(self, bg=C_BODY_BG)
        status_frame.pack(fill='x', side='bottom')
        self.status = tk.Label(status_frame, text='Estado: listo', anchor='w', bg=C_BODY_BG, fg=TEXT_COLOR, font=SMALL_FONT)
        self.status.pack(fill='x', padx=12, pady=8)

        # cargar proyectos
        self.cargar_proyectos()

        # inicializar ambas gráficas vacías
        self._plot_on_axis(self.ax_week, [], [], title='(Sin datos)')   # semana
        self._plot_on_axis(self.ax_iter, [], [], title='(Sin datos)')   # iteración

    # ---------------------------
    # helpers / plotting
    # ---------------------------
    def _strip_week_token(self, label: str) -> str:
        """
        Quita tokens tipo '(W29)' o '(W5)' y espacios sobrantes de una etiqueta de semana.
        Ej: "01-Dic-25 - 07-Dic-25 (W29)" -> "01-Dic-25 - 07-Dic-25"
        """
        if not label:
            return label
        # quitar cualquier "(W123)" (W seguido de dígitos) y también variantes con espacios
        cleaned = re.sub(r'\s*\(W\d+\)', '', str(label))
        return cleaned.strip()

    def _shorten_week_labels(self, labels):
        """
        Devuelve una lista de etiquetas "acortadas" para las semanas,
        pero **sin** el sufijo de semana (Wxx). Si la etiqueta tiene un rango
        'inicio - fin' lo convertimos a 'inicio a fin' para mostrarse limpio.
        """
        short = []
        for lbl in labels:
            if not lbl:
                short.append('')
                continue

            # Primero limpiar token W#
            cleaned = self._strip_week_token(lbl)

            # Si contiene el separador de rango ' - ' lo transformamos a ' a '
            if ' - ' in cleaned:
                parts = cleaned.split(' - ')
                # normalizar a "inicio a fin" (si hay más guiones, solo tomamos los dos primeros)
                inicio = parts[0].strip()
                fin = parts[1].strip() if len(parts) > 1 else ''
                short_label = f"{inicio} a {fin}" if fin else inicio
                # si se desea, mantener en dos líneas con el 'a' en la misma línea
                short.append(short_label)
            else:
                # si no es un rango, devolver una versión truncada si es muy larga
                display = cleaned[:12] + ('...' if len(cleaned) > 12 else '')
                short.append(display)
        return short

    def _plot_on_axis(self, ax, labels, values, title='Velocidad'):
        """Dibuja en el eje dado; ajusta automáticamente el espacio inferior para las etiquetas."""
        ax.clear()
        ax.set_title(title, fontsize=12, color=C_ACCENT)
        ax.set_xlabel('Periodo', fontsize=8)
        ax.set_ylabel('Tareas completadas', fontsize=10)

        if not labels:
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#777')
            for spine in ax.spines.values():
                spine.set_color('#D0D5DD')
            ax.set_xticks([])
            ax.set_yticks([])
            # asegurar que la figura refresque su layout si estaba modificada
            try:
                ax.figure.subplots_adjust(bottom=0.12)
            except Exception:
                pass
            return

        # ---- limpiar etiquetas para eliminar "(Wxx)" en todos los casos ----
        labels_clean = [self._strip_week_token(lbl) for lbl in labels]

        # acortar etiquetas si son muchas
        max_labels_before_shorten = 12
        use_short = len(labels_clean) > max_labels_before_shorten
        plot_labels = self._shorten_week_labels(labels_clean) if use_short else labels_clean
        # --------------------------------------------------------------------


        # adaptar fontsize
        if len(plot_labels) > 30:
            fontsize = 6
        elif len(plot_labels) > 18:
            fontsize = 7
        elif len(plot_labels) > 12:
            fontsize = 8
        else:
            fontsize = 9

        bars = ax.bar(range(len(values)), values, color=C_HEADER)
        ax.set_xticks(range(len(plot_labels)))
        ax.set_xticklabels(plot_labels, rotation=45, fontsize=fontsize, color=TEXT_COLOR)

        for spine in ax.spines.values():
            spine.set_color('#D0D5DD')
        ax.tick_params(axis='x', colors=TEXT_COLOR)
        ax.tick_params(axis='y', colors=TEXT_COLOR)

        # --- ajuste dinámico del espacio inferior para evitar que las etiquetas se corten ---
        try:
            # Basado en: longitud máxima de etiqueta y número de etiquetas
            max_label_len = max((len(str(x)) for x in plot_labels), default=0)
            n_labels = len(plot_labels)

            # fórmula heurística (ajusta si quieres más/menos separación)
            bottom = 0.12 + 0.005 * max_label_len + 0.003 * n_labels

            # límites razonables
            if bottom < 0.12:
                bottom = 0.12
            if bottom > 0.5:
                bottom = 0.5

            ax.figure.subplots_adjust(bottom=bottom)
        except Exception:
            # en caso de error, aplicar un valor conservador
            try:
                ax.figure.subplots_adjust(bottom=0.18)
            except Exception:
                pass

    # ---------------------------
    # data loading / handlers
    # ---------------------------
    def cargar_proyectos(self):
        try:
            proyectos = self.controller.get_projects()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo obtener proyectos: {e}')
            return
        values = ['-- Todos --']
        self.project_map = {'-- Todos --': None}
        for p in proyectos:
            nombre = p.get('nombre') or str(p.get('_id'))
            pid = p.get('_id')
            values.append(nombre)
            self.project_map[nombre] = pid
        self.combo['values'] = values
        self.combo.current(0)
        self.status.config(text=f'Proyectos cargados: {len(proyectos)}')

    def obtener_project_id_seleccionado(self):
        nombre = self.combo.get()
        return self.project_map.get(nombre)

    def mostrar_semana(self):
        """actualiza sólo la gráfica de semana usando los filtros actuales"""
        pid = self.obtener_project_id_seleccionado()
        solo = self.solo_iter_var.get()
        try:
            data = self.controller.get_data_by_week(pid, None, None, solo_sprint_actual=solo)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo obtener datos por semana: {e}')
            return
        if not data:
            self._plot_on_axis(self.ax_week, [], [], title='Tareas completadas por semana')
            self.canvas_week.draw()
            self.status.config(text='Sin datos para semana con los filtros actuales.')
            return
        labels = [d[0] for d in data]
        values = [d[1] for d in data]
        self._plot_on_axis(self.ax_week, labels, values, title='Tareas completadas por semana')
        self.canvas_week.draw()
        self.status.config(text=f'Mostrando {len(labels)} periodos (semana)')

    def mostrar_iteracion(self):
        """actualiza sólo la gráfica de iteración usando los filtros actuales"""
        pid = self.obtener_project_id_seleccionado()
        solo = self.solo_iter_var.get()
        try:
            data = self.controller.get_data_by_sprint(pid, solo_sprint_actual=solo)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo obtener datos por iteración: {e}')
            return
        if not data:
            self._plot_on_axis(self.ax_iter, [], [], title='Tareas completadas por iteración')
            self.canvas_iter.draw()
            self.status.config(text='Sin datos para iteración con los filtros actuales.')
            return
        labels = [d[0] for d in data]
        values = [d[1] for d in data]
        self._plot_on_axis(self.ax_iter, labels, values, title='Tareas completadas por iteración')
        self.canvas_iter.draw()
        self.status.config(text=f'Mostrando {len(labels)} iteraciones')

    def actualizar_ambas(self):
        """Actualiza ambas gráficas con los filtros actuales (proyecto + checkbox)."""
        # actualizar semana
        try:
            pid = self.obtener_project_id_seleccionado()
            solo = self.solo_iter_var.get()

            data_week = self.controller.get_data_by_week(pid, None, None, solo_sprint_actual=solo)
            if data_week:
                labels_w = [d[0] for d in data_week]
                values_w = [d[1] for d in data_week]
            else:
                labels_w, values_w = [], []

            data_iter = self.controller.get_data_by_sprint(pid, solo_sprint_actual=solo)
            if data_iter:
                labels_i = [d[0] for d in data_iter]
                values_i = [d[1] for d in data_iter]
            else:
                labels_i, values_i = [], []

            # dibujar ambos
            self._plot_on_axis(self.ax_week, labels_w, values_w, title='Tareas completadas por semana')
            self.canvas_week.draw()

            self._plot_on_axis(self.ax_iter, labels_i, values_i, title='Tareas completadas por iteración')
            self.canvas_iter.draw()

            # estado informativo
            txt = f'Semana: {len(labels_w)} periodos · Iteración: {len(labels_i)} items'
            if solo and pid:
                txt += '  (filtrado por iteración actual)'
            self.status.config(text=txt)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo actualizar: {e}')

