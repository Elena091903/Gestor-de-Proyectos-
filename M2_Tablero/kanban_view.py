import tkinter as tk
from tkinter import ttk
from datetime import datetime

PALETA = {
    "primary": "#3F5F91", "dark_blue": "#314168", "light_blue": "#D1D9EA",
    "bg_app": "#F4F6F7", "white": "#FFFFFF",
    "prio_high": "#D63A1B", "prio_med": "#F17646", "prio_low": "#2ECC71",
    "text_gray": "#666666", "text_meta": "#888888"
}

class KanbanView(tk.Frame):
    def __init__(self, parent, controller, lista_nombres_proyectos):
        super().__init__(parent, bg=PALETA["bg_app"])
        self.controller = controller
        self.lista_proyectos = lista_nombres_proyectos 
        
        self.crear_header()
        self.area_tablero = tk.Frame(self, bg=PALETA["bg_app"], padx=10, pady=10)
        self.area_tablero.pack(fill="both", expand=True)

    def crear_header(self):
        header = tk.Frame(self, bg=PALETA["primary"], height=60, padx=20, pady=10)
        header.pack(fill="x")
        
        
        tk.Label(header, text="Proyecto:", font=("Helvetica", 12, "bold"), 
                 bg=PALETA["primary"], fg=PALETA["light_blue"]).pack(side="left", padx=(0, 5))
        
        self.cb_proyectos = ttk.Combobox(header, values=self.lista_proyectos, state="readonly", width=30)
        self.cb_proyectos.pack(side="left", ipady=3)
        self.cb_proyectos.bind("<<ComboboxSelected>>", self.controller.evento_cambiar_proyecto)

      
        tk.Button(header, text="↻ Recargar", command=self.controller.refresh_data,
                  bg=PALETA["dark_blue"], fg=PALETA["white"], relief="flat", cursor="hand2").pack(side="right")

    def set_project_selection(self, nombre_proyecto):
        """Pone el nombre del proyecto actual en el menú"""
        if nombre_proyecto in self.cb_proyectos['values']:
            self.cb_proyectos.set(nombre_proyecto)

    def update_header_info(self, sprint):
        
        pass

    def render_board(self, tasks, user_map):
        for w in self.area_tablero.winfo_children(): w.destroy()
        columnas = ["Pendiente", "En Progreso", "Bloqueada", "Terminada"]
        for idx, col in enumerate(columnas):
            self._dibujar_columna(idx, col, tasks, columnas, user_map)

    def _dibujar_columna(self, col_idx, nombre_col, todas_tareas, lista_cols, user_map):
        frame = tk.Frame(self.area_tablero, bg=PALETA["light_blue"], width=260)
        frame.pack(side="left", fill="both", expand=True, padx=5)
        frame.pack_propagate(False)

        tk.Label(frame, text=nombre_col.upper(), bg=PALETA["light_blue"], fg=PALETA["dark_blue"], font=("Arial", 10, "bold"), pady=8).pack(fill="x")
        
        
        canvas = tk.Canvas(frame, bg=PALETA["light_blue"], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        container = tk.Frame(canvas, bg=PALETA["light_blue"])

        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=container, anchor="nw", width=240)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=2)
        scrollbar.pack(side="right", fill="y")

        
        tareas_col = [t for t in todas_tareas if t.get("estado") == nombre_col]
        for t in tareas_col:
            self._dibujar_tarjeta(container, t, col_idx, lista_cols, user_map)

    def _dibujar_tarjeta(self, parent, task, col_idx, lista_cols, user_map):
        
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", pady=5, padx=2, ipady=2)
        
        
        prio = task.get("prioridad", "Baja")
        color_prio = PALETA["prio_high"] if prio == "Alta" else PALETA["prio_med"] if prio == "Media" else PALETA["prio_low"]
        tk.Frame(card, bg=color_prio, width=6).pack(side="left", fill="y")

        
        content = tk.Frame(card, bg="white", padx=8, pady=5)
        content.pack(side="left", fill="both", expand=True)

        
        tk.Label(content, text=task.get("titulo", "Sin Título"), font=("Arial", 10, "bold"), 
                 bg="white", fg="#333", wraplength=170, justify="left").pack(anchor="w")

        
        uid = task.get("asignado_a")
        uname = user_map.get(uid, "Desconocido")
        if isinstance(uname, str) and len(uname) > 15: uname = uname.split(" ")[0]
        
        row_info = tk.Frame(content, bg="white")
        row_info.pack(fill="x", pady=2)
        tk.Label(row_info, text=f"👤 {uname}", font=("Arial", 8), fg=PALETA["text_gray"], bg="white").pack(side="left")
        
        icono = "🔥" if prio == "Alta" else "⚡" if prio == "Media" else "🌱"
        tk.Label(row_info, text=f" {icono} {prio}", font=("Arial", 8, "bold"), fg=color_prio, bg="white").pack(side="right")

        
        row_meta = tk.Frame(content, bg="white")
        row_meta.pack(fill="x", pady=2)
        
        f_lim = task.get("fecha_limite")
        str_f = ""
        if f_lim:
            try: 
                if isinstance(f_lim, str): f_obj = datetime.strptime(f_lim.split(" ")[0], "%Y-%m-%d")
                else: f_obj = f_lim
                str_f = f_obj.strftime("%d/%b")
            except: pass
        
        if str_f: tk.Label(row_meta, text=f"📅 {str_f}", font=("Arial", 7), fg=PALETA["text_meta"], bg="white").pack(side="left", padx=(0,5))

        n_s = len(task.get("subtareas", [])) if task.get("subtareas") else 0
        n_c = len(task.get("comentarios", [])) if task.get("comentarios") else 0
        if n_s: tk.Label(row_meta, text=f"☑ {n_s}", font=("Arial", 7), fg=PALETA["text_meta"], bg="white").pack(side="left", padx=2)
        if n_c: tk.Label(row_meta, text=f"💬 {n_c}", font=("Arial", 7), fg=PALETA["text_meta"], bg="white").pack(side="left", padx=2)

        
        btns = tk.Frame(content, bg="white")
        btns.pack(fill="x", pady=(5,0))
        if col_idx > 0:
            tk.Button(btns, text="◄", bg="#F0F0F0", bd=0, cursor="hand2", width=2, font=("Arial", 8),
                      command=lambda: self.controller.move_task(task, lista_cols[col_idx-1])).pack(side="left")
        if col_idx < len(lista_cols)-1:
            tk.Button(btns, text="►", bg="#F0F0F0", bd=0, cursor="hand2", width=2, font=("Arial", 8),
                      command=lambda: self.controller.move_task(task, lista_cols[col_idx+1])).pack(side="right")