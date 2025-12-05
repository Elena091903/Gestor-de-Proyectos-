import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime

C_HEADER  = "#3F5F91"  
C_FILTER_BG = "#FFFFFF"  
C_BODY_BG = "#EBF0F5"     
C_SUCCESS = "#27AE60"      
C_BTN_ADD = "#34495E"      
C_ACCENT = "#2C3E50"      
C_ERROR  = "#C0392B"      

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        self.default_bg = kw.get('bg', C_HEADER)
        self.hover_bg = kw.pop('hover_bg', "#2C3E50")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e): self['background'] = self.hover_bg
    def on_leave(self, e): self['background'] = self.default_bg

class TareaView(tk.Frame):
    def __init__(self, parent, controller, lista_proyectos):
        super().__init__(parent, bg=C_BODY_BG)
        self.controller = controller
        self.lista_proyectos = lista_proyectos
        self.pack(fill="both", expand=True)

        self.configurar_estilos()
        self.crear_layout_profesional()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", foreground="#555", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=C_HEADER, foreground="white", font=("Segoe UI", 16, "bold"))
        style.configure("CardTitle.TLabel", background="white", foreground=C_HEADER, font=("Segoe UI", 11, "bold"))
        style.configure("TEntry", padding=5)
        style.configure("FilterBar.TFrame", background=C_FILTER_BG)
        style.configure("FilterLabel.TLabel", background=C_FILTER_BG, foreground=C_ACCENT, font=("Segoe UI", 9, "bold"))

    def crear_layout_profesional(self):
        header = tk.Frame(self, bg=C_HEADER, height=70, padx=30)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="Creación y detalle de tareas", bg=C_HEADER, fg="white", font=("Segoe UI", 18, "bold")).pack(side="left", fill="y")

        # TOOLBAR
        f_toolbar = tk.Frame(self, bg="white", pady=10, padx=30)
        f_toolbar.pack(fill="x", side="top")
        f_controls = tk.Frame(f_toolbar, bg="#F8F9FA", padx=15, pady=10) 
        f_controls.configure(highlightbackground="#E0E0E0", highlightthickness=1) 
        f_controls.pack(fill="x")

        tk.Label(f_controls, text="1. SELECCIONAR PROYECTO:", bg="#F8F9FA", fg=C_ACCENT, font=("Segoe UI", 8, "bold")).pack(side="left")
        self.cb_filtro_proy = ttk.Combobox(f_controls, values=self.lista_proyectos, state="readonly", width=30)
        self.cb_filtro_proy.pack(side="left", padx=(10, 30))
        self.cb_filtro_proy.bind("<<ComboboxSelected>>", self.controller.evento_filtrar_proyecto)

        tk.Label(f_controls, text="2. EDITAR TAREA:", bg="#F8F9FA", fg=C_ACCENT, font=("Segoe UI", 8, "bold")).pack(side="left")
        self.cb_filtro_tarea = ttk.Combobox(f_controls, state="normal", width=35)
        self.cb_filtro_tarea.pack(side="left", padx=10)
        self.cb_filtro_tarea.bind("<<ComboboxSelected>>", self.controller.evento_seleccionar_tarea)

        HoverButton(f_controls, text="+ NUEVA TAREA", bg=C_SUCCESS, hover_bg="#1E8449", fg="white", 
                    font=("Segoe UI", 9, "bold"), relief="flat", padx=20, cursor="hand2", 
                    command=self.controller.preparar_nueva).pack(side="right")

        tk.Frame(self, bg="#DDD", height=1).pack(fill="x")

        self.canvas = tk.Canvas(self, bg=C_BODY_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=C_BODY_BG, padx=40, pady=20)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.construir_tarjetas()

    def construir_tarjetas(self):
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)

        # INFO GENERAL 
        card_info = self._crear_tarjeta(self.scrollable_frame, "INFORMACIÓN GENERAL", 0, 0, colspan=2)
        card_info.columnconfigure(1, weight=1)
        card_info.columnconfigure(3, weight=1)

        ttk.Label(card_info, text="Título de la Tarea:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_titulo = ttk.Entry(card_info, font=("Segoe UI", 11))
        self.entry_titulo.grid(row=0, column=1, columnspan=5, sticky="ew", pady=5)

        ttk.Label(card_info, text="Descripción:").grid(row=1, column=0, sticky="nw", pady=5)
        self.txt_desc = tk.Text(card_info, height=3, font=("Segoe UI", 10), bg="#FAFAFA", relief="solid", bd=1)
        self.txt_desc.grid(row=1, column=1, columnspan=5, sticky="ew", pady=5)

        ttk.Label(card_info, text="Prioridad:").grid(row=2, column=0, sticky="w", pady=10)
        self.cb_prioridad = ttk.Combobox(card_info, values=["Alta", "Media", "Baja"], state="readonly", width=15)
        self.cb_prioridad.current(1)
        self.cb_prioridad.grid(row=2, column=1, sticky="w")

        ttk.Label(card_info, text="Asignar Miembro:").grid(row=2, column=4, sticky="e", padx=10)
        self.cb_asignado = ttk.Combobox(card_info, state="readonly", width=25)
        self.cb_asignado.grid(row=2, column=5, sticky="ew")

        ttk.Label(card_info, text="Asignar Sprint:").grid(row=3, column=0, sticky="w", pady=10)
        self.entry_sprint_tarea = ttk.Spinbox(card_info, from_=1, to=10, width=5, state="readonly")
        self.entry_sprint_tarea.set(1)
        self.entry_sprint_tarea.grid(row=3, column=1, sticky="w")

        ttk.Label(card_info, text="Fecha Límite:").grid(row=3, column=4, sticky="e", padx=10)
        self.cal_limite = DateEntry(card_info, width=22, background=C_HEADER, foreground='white', borderwidth=2, 
                                    mindate=datetime.now(), date_pattern='yyyy-mm-dd')
        self.cal_limite.grid(row=3, column=5, sticky="ew")


        # CONTEXTO 
        card_ctx = self._crear_tarjeta(self.scrollable_frame, "CONTEXTO DEL PROYECTO", 1, 0, colspan=2)
        
        self.lbl_proy_nombre = tk.Label(card_ctx, text="---", bg="white", fg=C_ACCENT, font=("Segoe UI", 14, "bold"))
        self.lbl_proy_nombre.pack(anchor="w", padx=15, pady=(5,0))

        self.lbl_proy_desc = tk.Label(card_ctx, text="---", bg="white", fg="#777", font=("Segoe UI", 10, "italic"), wraplength=700, justify="left")
        self.lbl_proy_desc.pack(anchor="w", padx=15, pady=(0, 10))

        f_info_box = tk.Frame(card_ctx, bg="#E8F6F3", padx=15, pady=15)
        f_info_box.pack(fill="x", padx=15, pady=5)
        
        self.lbl_sprint = tk.Label(f_info_box, text="Sprint Actual: --", bg="#E8F6F3", fg=C_ACCENT, font=("Segoe UI", 10, "bold"))
        self.lbl_sprint.pack(side="left", padx=20)
        tk.Label(f_info_box, text="|", bg="#E8F6F3", fg="#CCC").pack(side="left")
        self.lbl_sm = tk.Label(f_info_box, text="Scrum Master: --", bg="#E8F6F3", fg=C_ACCENT, font=("Segoe UI", 10, "bold"))
        self.lbl_sm.pack(side="left", padx=20)


        # SUBTAREAS 
        card_sub = self._crear_tarjeta(self.scrollable_frame, "LISTA DE SUBTAREAS", 2, 0)
        self.container_subs = tk.Frame(card_sub, bg="white")
        self.container_subs.pack(fill="both", expand=True)
        HoverButton(card_sub, text="+ Agregar Subtarea", bg=C_BTN_ADD, hover_bg="#2C3E50", fg="white", 
                    font=("Segoe UI", 8, "bold"), relief="flat", padx=10, 
                    command=lambda: self.crear_fila_subtarea("", False)).pack(anchor="w", pady=10)

        #  COMENTARIOS 
        card_com = self._crear_tarjeta(self.scrollable_frame, "NOTAS Y COMENTARIOS", 2, 1)
        self.container_coms = tk.Frame(card_com, bg="white")
        self.container_coms.pack(fill="both", expand=True)
        HoverButton(card_com, text="+ Agregar Nota", bg=C_BTN_ADD, hover_bg="#2C3E50", fg="white", 
                    font=("Segoe UI", 8, "bold"), relief="flat", padx=10, 
                    command=lambda: self.crear_fila_comentario("")).pack(anchor="w", pady=10)

        # GUARDAR 
        self.btn_save = HoverButton(self.scrollable_frame, text="GUARDAR TODO", bg=C_SUCCESS, hover_bg="#1E8449", fg="white", 
                                    font=("Segoe UI", 12, "bold"), padx=50, pady=12, relief="flat", cursor="hand2",
                                    command=self.controller.guardar_datos)
        self.btn_save.grid(row=3, column=0, columnspan=2, pady=40)

        self.rows_subtareas = []
        self.rows_comentarios = []

    def _crear_tarjeta(self, parent, titulo, r, c, colspan=1):
        card = tk.Frame(parent, bg="white", padx=20, pady=15)
        card.configure(highlightbackground="#D0D0D0", highlightthickness=1)
        card.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=10, pady=10)
        header = tk.Frame(card, bg="white")
        header.pack(fill="x", side="top", pady=(0, 15))
        tk.Frame(header, bg=C_HEADER, width=4, height=20).pack(side="left", padx=(0, 10))
        ttk.Label(header, text=titulo, style="CardTitle.TLabel").pack(side="left")
        content = tk.Frame(card, bg="white")
        content.pack(fill="both", expand=True, side="top")
        return content

    def configurar_limite_sprint(self, max_sprint):
        self.entry_sprint_tarea.config(state="readonly", from_=1, to=max_sprint)
        self.entry_sprint_tarea.set(max_sprint)

    def crear_fila_subtarea(self, texto, hecho):
        row = tk.Frame(self.container_subs, bg="white", pady=2)
        row.pack(fill="x")
        var = tk.BooleanVar(value=hecho)
        tk.Checkbutton(row, variable=var, bg="white", activebackground="white").pack(side="left")
        entry = ttk.Entry(row)
        entry.insert(0, texto)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        btn = tk.Label(row, text="×", fg=C_ERROR, bg="white", font=("Arial", 14, "bold"), cursor="hand2")
        btn.pack(side="right", padx=5)
        data = {"frame": row, "var": var, "entry": entry}
        self.rows_subtareas.append(data)
        btn.bind("<Button-1>", lambda e: self.eliminar_fila(data, self.rows_subtareas))

    def crear_fila_comentario(self, texto):
        row = tk.Frame(self.container_coms, bg="white", pady=4)
        row.pack(fill="x")
        entry = tk.Entry(row, bg="#FFF9C4", relief="flat", font=("Segoe UI", 9))
        if texto: entry.insert(0, texto)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=4)
        btn = tk.Label(row, text="×", fg=C_ERROR, bg="white", font=("Arial", 14, "bold"), cursor="hand2")
        btn.pack(side="right")
        data = {"frame": row, "entry": entry}
        self.rows_comentarios.append(data)
        btn.bind("<Button-1>", lambda e: self.eliminar_fila(data, self.rows_comentarios))

    def eliminar_fila(self, data, lista):
        data["frame"].destroy()
        if data in lista: lista.remove(data)

    def obtener_subtareas(self):
        return [{"texto": r["entry"].get(), "hecho": r["var"].get()} for r in self.rows_subtareas if r["entry"].get().strip()]
    def obtener_comentarios(self):
        return [r["entry"].get() for r in self.rows_comentarios if r["entry"].get().strip()]
    
    def limpiar_form(self):
        self.entry_titulo.delete(0, 'end'); self.txt_desc.delete("1.0", 'end')
        self.cal_limite.set_date(datetime.now())
        self.cb_asignado.set('')
        self.entry_sprint_tarea.set(1)
        self.lbl_proy_nombre.config(text="---")
        self.lbl_proy_desc.config(text="---")
        for r in self.rows_subtareas: r["frame"].destroy()
        self.rows_subtareas = []
        for r in self.rows_comentarios: r["frame"].destroy()
        self.rows_comentarios = []

    def llenar_form(self, data):
        self.limpiar_form()
        self.entry_titulo.insert(0, data.get('titulo', ''))
        self.txt_desc.insert("1.0", data.get('descripcion', ''))
        self.cb_prioridad.set(data.get('prioridad', 'Media'))
        self.entry_sprint_tarea.set(data.get('sprint', 1))

        try: self.cal_limite.set_date(data.get('fecha_limite', datetime.now()))
        except: self.cal_limite.set_date(datetime.now())
        
        for sub in data.get('subtareas', []):
            if isinstance(sub, dict): self.crear_fila_subtarea(sub['texto'], sub['hecho'])
            else: self.crear_fila_subtarea(str(sub), False)
        for com in data.get('comentarios', []): self.crear_fila_comentario(str(com))