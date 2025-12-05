# views/m1_project_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
from bson import ObjectId

from controllers.m1_project_controller import ProjectController

# COLORES / ESTILOS
C_HEADER    = "#3F5F91"
C_ACCENT    = "#2C3E50"
C_BODY_BG   = "#EBF0F5"
C_CARD_BG   = "#FFFFFF"
C_SUCCESS   = "#27AE60"
C_DANGER    = "#D64545"
TEXT_COLOR  = "#1f2937"

FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI", 14, "bold")

class ProjectManagerUI(tk.Tk):
    def __init__(self, current_user=None):
        super().__init__()
        # current_user viene desde main_m1.py (o None si se instancia localmente)
        self.current_user = current_user or {}   # {'_id':..., 'usuario':..., 'rol':...}
        self.controller = ProjectController()
        self.title("Gestión de Proyectos y Equipos")
        self.configure(bg=C_BODY_BG)
        self.geometry("1300x820")
        self.minsize(1000, 640)

        self._editing_project_id = None
        self._all_projects = []   # cache para filtrar
        # bandera: si estamos creando (True) o editando (False)
        self._creating_project = False

        self._configure_style()
        self._build_ui()
        self._apply_permissions()
        self.load_projects()
        self.load_scrum_masters()
        self.load_members_list()

    def _apply_permissions(self):
        # Deshabilitar botones si el rol no es Admin/Scrum Master
        rol = (self.current_user.get("rol") or "").lower()
        allowed = rol in ("administrador", "scrum master", "scrum_master", "admin")
        try:
            self.b_new.configure(state="normal" if allowed else "disabled")
            self.b_edit.configure(state="normal" if allowed else "disabled")
            self.b_delete.configure(state="normal" if allowed else "disabled")
        except Exception:
            pass

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Card.TFrame", background=C_CARD_BG, relief="flat")
        style.configure("Header.TLabel", background=C_HEADER, foreground="white", font=("Segoe UI", 16, "bold"))
        style.configure("CardTitle.TLabel", background=C_CARD_BG, foreground=C_HEADER, font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        # HEADER
        header = tk.Frame(self, bg=C_HEADER, height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="Gestión Proyectos / Equipos", bg=C_HEADER, fg="white", font=TITLE_FONT).pack(side="left", padx=18)

        # TOOLBAR (blanco, filtros + nuevo)
        toolbar = tk.Frame(self, bg="white", height=64, padx=14)
        toolbar.pack(fill="x", side="top")
        toolbar.pack_propagate(False)

        # izquierda: filtro global de proyectos
        left_tools = tk.Frame(toolbar, bg="white")
        left_tools.pack(side="left", anchor="w")

        tk.Label(left_tools, text="Buscar proyecto:", bg="white", fg=C_ACCENT, font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0,8))
        self.entry_search = ttk.Entry(left_tools, width=30)
        self.entry_search.pack(side="left", padx=(0,8))
        self.entry_search.bind("<KeyRelease>", lambda e: self._filter_projects())
        tk.Button(left_tools, text="Limpiar", bg="#F3F4F6", fg=TEXT_COLOR, relief="flat",
                  command=lambda: (self.entry_search.delete(0,'end'), self._filter_projects())).pack(side="left", padx=(4,0))

        # derecha: botón nuevo
        tk.Button(toolbar, text="+ NUEVO PROYECTO", bg=C_HEADER, fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=18, pady=8, cursor="hand2", command=self.on_new_project).pack(side="right")

        # MAIN: panel dividido (izq = lista, der = contenido)
        main_pane = ttk.Panedwindow(self, orient="horizontal")
        main_pane.pack(fill="both", expand=True, padx=12, pady=12)

        # LEFT: lista de proyectos (card-like)
        left_frame = tk.Frame(main_pane, bg=C_BODY_BG)
        left_frame.configure(width=360)
        main_pane.add(left_frame, weight=1)

        card_left = tk.Frame(left_frame, bg=C_CARD_BG, padx=10, pady=10)
        card_left.pack(fill="both", expand=True)

        ttk.Label(card_left, text="Proyectos", style="CardTitle.TLabel").pack(anchor="w", pady=(0,8))

        tree_container = tk.Frame(card_left, bg=C_CARD_BG)
        tree_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_container, columns=("nombre","sprint","estado","miembros"), show="headings", height=18)
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("sprint", text="Sprint")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("miembros", text="Miembros")
        self.tree.column("nombre", width=220, anchor="w")
        self.tree.column("sprint", width=50, anchor="center")
        self.tree.column("estado", width=100, anchor="center")
        self.tree.column("miembros", width=50, anchor="center")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_project_select())

        # botones CRUD compactos (2x2)
        left_btns = tk.Frame(card_left, bg=C_CARD_BG)
        left_btns.pack(fill="x", pady=(10,0))
        # botones con colores sólidos
        self.b_new = tk.Button(left_btns, text="Nuevo", bg=C_HEADER, fg="white", command=self.on_new_project, padx=8, pady=6)
        self.b_edit = tk.Button(left_btns, text="Editar", bg=C_HEADER, fg="white", command=lambda: self.on_project_select(), padx=8, pady=6)
        self.b_delete = tk.Button(left_btns, text="Eliminar", bg=C_DANGER, fg="white", command=self.on_delete_project, padx=8, pady=6)
        self.b_refresh = tk.Button(left_btns, text="Refrescar", bg="#6B7280", fg="white", command=self.load_projects, padx=8, pady=6)

        self.b_new.grid(row=0, column=0, padx=6, pady=4, sticky="ew")
        self.b_edit.grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        self.b_delete.grid(row=1, column=0, padx=6, pady=4, sticky="ew")
        self.b_refresh.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        left_btns.columnconfigure(0, weight=1)
        left_btns.columnconfigure(1, weight=1)

        # RIGHT: formulario + tareas en tarjetas
        right_frame = tk.Frame(main_pane, bg=C_BODY_BG)
        main_pane.add(right_frame, weight=3)

        # Form card
        form_card = tk.Frame(right_frame, bg=C_CARD_BG, padx=14, pady=12)
        form_card.pack(fill="x", pady=(0,8))
        self._card_title(form_card, "Crear / Editar Proyecto")

        form = tk.Frame(form_card, bg=C_CARD_BG)
        form.pack(fill="x", pady=6)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=0)

        # Nombre
        tk.Label(form, text="Nombre:", bg=C_CARD_BG).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.entry_nombre = ttk.Entry(form)
        self.entry_nombre.grid(row=0, column=1, sticky="ew", padx=6, pady=6)

        # Scrum Master
        tk.Label(form, text="Scrum Master:", bg=C_CARD_BG).grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.scrum_cb = ttk.Combobox(form, state="readonly")
        self.scrum_cb.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        # Sprint & Estado (compactos en la misma fila) -> usando subframe para controlar mejor layout
        tk.Label(form, text="Sprint actual:", bg=C_CARD_BG).grid(row=2, column=0, sticky="w", padx=6, pady=6)
        f_row2 = tk.Frame(form, bg=C_CARD_BG)
        f_row2.grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        # spinbox
        self.spin_sprint = tk.Spinbox(f_row2, from_=1, to=100, width=6, validate='focusout')
        self.spin_sprint.pack(side="left")
        # bind para controlar cambios (flechas + entrada manual)
        try:
            # comando para clicks de flecha
            self.spin_sprint.configure(command=self._on_spin_changed)
        except Exception:
            pass
        self.spin_sprint.bind("<FocusOut>", lambda e: self._on_spin_changed())
        self.spin_sprint.bind("<KeyRelease>", lambda e: self._on_spin_changed())

        # etiqueta "Estado:" al lado del combobox
        lbl_estado_inline = tk.Label(f_row2, text="Estado:", bg=C_CARD_BG)
        lbl_estado_inline.pack(side="left", padx=(12,6))
        self.estado_cb = ttk.Combobox(f_row2, state="readonly", values=["En progreso", "Terminado", "Pausado"], width=18)
        self.estado_cb.pack(side="left")

        # Fecha inicio
        tk.Label(form, text="Fecha inicio:", bg=C_CARD_BG).grid(row=3, column=0, sticky="w", padx=6, pady=6)
        self.date_inicio = DateEntry(form, date_pattern="yyyy-mm-dd", mindate=date.today(), width=14)
        self.date_inicio.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        # Descripción
        tk.Label(form, text="Descripción:", bg=C_CARD_BG).grid(row=4, column=0, sticky="nw", padx=6, pady=6)
        self.text_desc = tk.Text(form, width=40, height=5, bg="#FAFAFA", relief="solid", bd=1)
        self.text_desc.grid(row=4, column=1, sticky="ew", padx=6, pady=6)

        # Miembros list (columna derecha)
        tk.Label(form, text="Miembros (varios):", bg=C_CARD_BG).grid(row=0, column=2, sticky="w", padx=12, pady=6)
        members_frame = tk.Frame(form, bg=C_CARD_BG)
        members_frame.grid(row=1, column=2, rowspan=4, sticky="n", padx=12, pady=6)

        self.lb_available = tk.Listbox(members_frame, selectmode="extended", width=32, height=8)
        self.lb_available.pack(side="left", fill="y")
        members_scroll = ttk.Scrollbar(members_frame, orient="vertical", command=self.lb_available.yview)
        members_scroll.pack(side="left", fill="y")
        self.lb_available.configure(yscrollcommand=members_scroll.set)

        mtools = tk.Frame(form, bg=C_CARD_BG)
        mtools.grid(row=5, column=2, sticky="w", padx=12, pady=(4,0))
        ttk.Button(mtools, text="Nuevo miembro", command=self.open_new_member_popup, width=14).pack(side="left", padx=4)
        ttk.Button(mtools, text="Limpiar selección", command=lambda: self.lb_available.selection_clear(0, "end"), width=14).pack(side="left", padx=4)

        # actions
        actions = tk.Frame(form_card, bg=C_CARD_BG)
        actions.pack(fill="x", pady=(8,0))
        tk.Button(actions, text="Guardar proyecto", command=self.on_save_project, bg=C_SUCCESS, fg="white", padx=12, pady=6).pack(side="left", padx=6)
        tk.Button(actions, text="Cancelar edición", command=self.on_cancel_edit, bg="#6B7280", fg="white", padx=12, pady=6).pack(side="left", padx=6)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=8)

        # TAREAS CARD (inferior derecho)
        tasks_card = tk.Frame(right_frame, bg=C_CARD_BG, padx=12, pady=12)
        tasks_card.pack(fill="both", expand=True)
        self._card_title(tasks_card, "Tareas del proyecto seleccionado")

        tasks_container = tk.Frame(tasks_card, bg=C_CARD_BG)
        tasks_container.pack(fill="both", expand=True)

        self.tasks_tree = ttk.Treeview(tasks_container, columns=("titulo","estado","sprint","asignado","fecha"), show="headings")
        self.tasks_tree.heading("titulo", text="Título")
        self.tasks_tree.heading("estado", text="Estado")
        self.tasks_tree.heading("sprint", text="Sprint")
        self.tasks_tree.heading("asignado", text="Asignado a")
        self.tasks_tree.heading("fecha", text="Fecha Límite")
        self.tasks_tree.column("titulo", width=320, anchor="w")
        self.tasks_tree.column("estado", width=120, anchor="center")
        self.tasks_tree.column("sprint", width=80, anchor="center")
        self.tasks_tree.column("asignado", width=160, anchor="w")
        self.tasks_tree.column("fecha", width=120, anchor="center")

        tasks_v = ttk.Scrollbar(tasks_container, orient="vertical", command=self.tasks_tree.yview)
        tasks_h = ttk.Scrollbar(tasks_container, orient="horizontal", command=self.tasks_tree.xview)
        self.tasks_tree.configure(yscrollcommand=tasks_v.set, xscrollcommand=tasks_h.set)
        tasks_v.pack(side="right", fill="y")
        tasks_h.pack(side="bottom", fill="x")
        self.tasks_tree.pack(fill="both", expand=True, side="left")

        # task buttons compact
        t_buttons = tk.Frame(tasks_card, bg=C_CARD_BG)
        t_buttons.pack(pady=8, anchor="w")
        ttk.Button(t_buttons, text="Nueva tarea", command=self.on_new_task, width=16).pack(side="left", padx=6)
        ttk.Button(t_buttons, text="Refrescar tareas", command=self.on_refresh_tasks, width=16).pack(side="left", padx=6)
        ttk.Button(t_buttons, text="Ver / Editar tarea", command=self.on_edit_task, width=16).pack(side="left", padx=6)

        # status bar
        self.status = tk.Label(self, text="Estado: listo", bg=C_BODY_BG, anchor="w")
        self.status.pack(fill="x", side="bottom")

    # pequeño helper para títulos de tarjeta
    def _card_title(self, parent, text):
        header = tk.Frame(parent, bg=C_CARD_BG)
        header.pack(fill="x", side="top", pady=(0,6))
        tk.Frame(header, bg=C_HEADER, width=4, height=20).pack(side="left", padx=(0,8))
        ttk.Label(header, text=text, style="CardTitle.TLabel").pack(side="left")

    # -------------------------- Validation / helpers for spinbox --------------------------
    def _get_spin_value(self):
        try:
            return int(str(self.spin_sprint.get()).strip())
        except Exception:
            return 1

    def _set_spin_value(self, val: int):
        try:
            self.spin_sprint.delete(0, "end")
            self.spin_sprint.insert(0, str(val))
        except Exception:
            try:
                self.spin_sprint.delete(0, "end")
                self.spin_sprint.insert(0, "1")
            except Exception:
                pass

    def _on_spin_changed(self):
        # Esta función se llama al cambiar el spinbox (flechas, focusout, keyrelease).
        val = self._get_spin_value()
        if self._creating_project:
            if val > 1:
                messagebox.showwarning("Restricción", "Al crear un proyecto el sprint inicial debe ser 1. Se restablecerá a 1.")
                self._set_spin_value(1)

    # -------------------------- Helpers: filtro local para proyectos --------------------------
    def _filter_projects(self):
        q = self.entry_search.get().strip().lower()
        if not q:
            self._show_projects(self._all_projects)
            return
        filtered = [p for p in self._all_projects if q in (p.get("nombre","").lower())]
        self._show_projects(filtered)

    def _show_projects(self, proyectos):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for p in proyectos:
            self.tree.insert("", "end", iid=p["_id"], values=(p["nombre"], p.get("sprint_actual", p.get("sprint","-")), p.get("estado","-"), p.get("miembros",0)))
        self.status.config(text=f"Proyectos mostrados: {len(proyectos)}")

    # -------------------------- Cargas y helpers --------------------------
    def load_projects(self):
        proyectos = self.controller.get_projects_for_view()
        self._all_projects = proyectos or []
        self._show_projects(self._all_projects)

    def load_scrum_masters(self):
        masters = []
        try:
            masters = self.controller.get_scrum_masters() or []
        except Exception:
            masters = []
        vals = []
        self._scrum_map = {}
        for u in masters:
            try:
                name = u.get("usuario") or u.get("nombre") or str(u.get("_id"))
                display = f"{name} ({str(u.get('_id'))[:6]})"
                vals.append(display)
                self._scrum_map[display] = str(u.get("_id"))
            except Exception:
                continue
        if not vals:
            vals = ["-- Ninguno --"]
            self._scrum_map = {"-- Ninguno --": None}
        self.scrum_cb['values'] = vals
        if vals:
            self.scrum_cb.current(0)

    def load_members_list(self):
        self.lb_available.delete(0, "end")
        members = self.controller.get_members()
        self._members_map = {}
        for m in members:
            display = f"{m.get('nombre')} — {m.get('cargo')}"
            self._members_map[display] = str(m.get("_id"))
            self.lb_available.insert("end", display)

    def get_selected_project_id(self):
        sel = self.tree.focus()
        return sel if sel else None

    # -------------------------- Lectura de proyecto seleccionado --------------------------
    def on_project_select(self):
        pid = self.get_selected_project_id()
        if not pid:
            return
        proj = self.controller.get_project(pid)
        if not proj:
            return
        # cambiamos a modo edición
        self._creating_project = False
        self._editing_project_id = pid

        self.entry_nombre.delete(0, "end"); self.entry_nombre.insert(0, proj.get("nombre", ""))
        self.text_desc.delete("1.0", "end"); self.text_desc.insert("1.0", proj.get("descripcion", ""))
        id_scrum = proj.get("id_scrum_master")
        if id_scrum:
            id_s = str(id_scrum)
            for k, v in self._scrum_map.items():
                if v == id_s:
                    try:
                        idx = self.scrum_cb['values'].index(k)
                        self.scrum_cb.current(idx)
                    except Exception:
                        pass
                    break
        miembros = [str(x) for x in proj.get("miembros", [])]
        self.lb_available.selection_clear(0, "end")
        for i, display in enumerate(self.lb_available.get(0, "end")):
            mid = self._members_map.get(display)
            if mid and mid in miembros:
                self.lb_available.selection_set(i)
        self.spin_sprint.delete(0, "end"); self.spin_sprint.insert(0, str(proj.get("sprint_actual", 1)))
        self.estado_cb.set(proj.get("estado", "En progreso"))
        fi = proj.get("fecha_inicio")
        if isinstance(fi, str):
            try: self.date_inicio.set_date(fi)
            except Exception: pass
        elif fi:
            try: self.date_inicio.set_date(fi)
            except Exception: pass
        self.load_tasks_for_project(pid)

    def load_tasks_for_project(self, project_id):
        for r in self.tasks_tree.get_children():
            self.tasks_tree.delete(r)
        tareas = self.controller.get_tasks_by_project(project_id)
        for t in tareas:
            fecha = t.get("fecha_limite")
            fecha_str = fecha.strftime("%Y-%m-%d") if fecha and hasattr(fecha, "strftime") else (str(fecha) if fecha else "-")
            asignado = self.controller.get_user_name(t.get("asignado_a"))
            self.tasks_tree.insert("", "end", iid=str(t["_id"]),
                                   values=(t.get("titulo", ""), t.get("estado", ""), t.get("sprint", ""), asignado, fecha_str))
        self.status.config(text=f"Tareas cargadas: {len(tareas)}")

    # -------------------------- Acciones --------------------------
    def on_new_project(self):
        # modo creación
        self._editing_project_id = None
        self._creating_project = True

        self.entry_nombre.delete(0, "end")
        self.text_desc.delete("1.0", "end")
        if self.scrum_cb['values']:
            try: self.scrum_cb.current(0)
            except Exception: pass
        self.lb_available.selection_clear(0, "end")
        # sprint inicial forzado a 1 en creación
        self._set_spin_value(1)
        self.estado_cb.set("En progreso")
        self.date_inicio.set_date(date.today())

    def on_cancel_edit(self):
        self.on_new_project()

    def on_save_project(self):
        nombre = self.entry_nombre.get().strip()
        descripcion = self.text_desc.get("1.0", "end").strip()
        if not nombre:
            messagebox.showerror("Error", "Nombre obligatorio.")
            return
        scrum_disp = self.scrum_cb.get()
        id_scrum = self._scrum_map.get(scrum_disp)
        sel = [self.lb_available.get(i) for i in self.lb_available.curselection()]
        miembros_ids = [self._members_map[d] for d in sel]
        try:
            sprint = int(self.spin_sprint.get())
        except Exception:
            sprint = 1

        # Si estamos creando: forzamos sprint = 1 y avisamos si intento cambiar
        if self._creating_project and sprint > 1:
            messagebox.showwarning("Restricción", "El sprint inicial no puede ser mayor a 1. Se establecerá en 1.")
            sprint = 1
            self._set_spin_value(1)

        estado = self.estado_cb.get() or "En progreso"
        fecha_inicio = self.date_inicio.get_date()
        if isinstance(fecha_inicio, date) and not isinstance(fecha_inicio, datetime):
            fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())

        data = {
            "nombre": nombre,
            "descripcion": descripcion,
            "id_scrum_master": ObjectId(id_scrum) if id_scrum else None,
            "miembros": [ObjectId(m) for m in miembros_ids],
            "sprint_actual": sprint,
            "estado": estado,
            "fecha_inicio": fecha_inicio
        }

        if self._editing_project_id and estado == "Terminado":
            ok = self.controller.can_mark_project_finished(self._editing_project_id)
            if not ok:
                messagebox.showwarning("No permitido", "No puede marcar el proyecto como 'Terminado' porque hay tareas no terminadas.")
                return

        if self._editing_project_id:
            # update (modo edición)
            self.controller.update_project(self._editing_project_id, data, user_doc=self.current_user)
            messagebox.showinfo("Éxito", "Proyecto actualizado.")
            # después de update, ya no estamos en creación
            self._creating_project = False
        else:
            # create
            new_id = self.controller.create_project(data, user_doc=self.current_user)
            if new_id:
                messagebox.showinfo("Éxito", "Proyecto creado.")
                self._editing_project_id = new_id
                # ya no estamos en creación
                self._creating_project = False
            else:
                return

        self.load_projects()
        if self._editing_project_id:
            try:
                self.tree.selection_set(self._editing_project_id)
                self.tree.focus(self._editing_project_id)
            except Exception:
                pass

    def on_delete_project(self):
        pid = self.get_selected_project_id()
        if not pid:
            messagebox.showwarning("Atención", "Seleccione un proyecto.")
            return
        if not messagebox.askyesno("Confirmar", "Eliminar proyecto y todas sus tareas asociadas?"):
            return
        self.controller.delete_project(pid, user_doc=self.current_user)
        self.load_projects()
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        messagebox.showinfo("Eliminado", "Proyecto y tareas asociadas eliminadas.")

    # tareas delegated
    def on_new_task(self):
        pid = self.get_selected_project_id()
        if not pid:
            messagebox.showwarning("Atención", "Seleccione un proyecto para crear la tarea.")
            return
        from views.m1_project_task_form import ProjectTaskForm
        ProjectTaskForm(self, mode="create", project_id=pid, controller=self.controller, refresh=lambda: self.load_tasks_for_project(pid))

    def on_edit_task(self):
        sel = self.tasks_tree.focus()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una tarea.")
            return
        from views.m1_project_task_form import ProjectTaskForm
        ProjectTaskForm(self, mode="edit", project_id=self.get_selected_project_id(), controller=self.controller, task_id=sel, refresh=lambda: self.load_tasks_for_project(self.get_selected_project_id()))

    def on_refresh_tasks(self):
        pid = self.get_selected_project_id()
        if pid:
            self.load_tasks_for_project(pid)

    # members popup (mejor diseño)
    def open_new_member_popup(self):
        p = tk.Toplevel(self)
        p.transient(self)
        p.title("Crear miembro")
        p.configure(bg=C_BODY_BG)
        p.geometry("440x280")
        p.resizable(False, False)

        # Card
        card = tk.Frame(p, bg=C_CARD_BG, padx=12, pady=12)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.configure(highlightthickness=1, highlightbackground="#D0D5DD")

        # Header
        header = tk.Frame(card, bg=C_HEADER, height=48)
        header.pack(fill="x", side="top", pady=(0,10))
        header.pack_propagate(False)
        tk.Label(header, text="Crear Nuevo Miembro", bg=C_HEADER, fg="white", font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)

        # form area
        form = tk.Frame(card, bg=C_CARD_BG)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Nombre completo", bg=C_CARD_BG, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", padx=6, pady=(6,4))
        e_name = ttk.Entry(form, width=42)
        e_name.grid(row=1, column=0, padx=6, pady=(0,10))

        tk.Label(form, text="Cargo / Rol (opcional)", bg=C_CARD_BG, fg=TEXT_COLOR).grid(row=2, column=0, sticky="w", padx=6, pady=(6,4))
        e_cargo = ttk.Entry(form, width=42)
        e_cargo.grid(row=3, column=0, padx=6, pady=(0,10))

        # Activo checkbox
        activo_var = tk.BooleanVar(value=True)
        chk = ttk.Checkbutton(form, text="Activo", variable=activo_var)
        chk.grid(row=4, column=0, sticky="w", padx=6, pady=(4,8))

        # buttons
        btns = tk.Frame(card, bg=C_CARD_BG)
        btns.pack(fill="x", pady=(8,0))
        def save():
            nombre = e_name.get().strip()
            cargo = e_cargo.get().strip()
            activo = bool(activo_var.get())
            if not nombre:
                messagebox.showerror("Error", "Nombre obligatorio.")
                return
            data = {"nombre": nombre, "cargo": cargo or "Desarrollador", "activo": activo}
            res = self.controller.create_member(data)
            if res:
                p.destroy()
                self.load_members_list()
                messagebox.showinfo("Éxito", "Miembro creado.")
            else:
                # el controller puede mostrar error
                pass

        btn_create = tk.Button(btns, text="Crear miembro", bg=C_SUCCESS, fg="white", command=save, padx=14, pady=8, relief="flat")
        btn_create.pack(side="right", padx=8)
        btn_cancel = tk.Button(btns, text="Cancelar", bg="#E5E7EB", fg=TEXT_COLOR, command=p.destroy, padx=12, pady=8, relief="flat")
        btn_cancel.pack(side="right")

    # fin de clase

if __name__ == "__main__":
    app = ProjectManagerUI()  # sin current_user, usará {}
    app.mainloop()
