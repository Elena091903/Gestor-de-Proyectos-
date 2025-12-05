import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from bson import ObjectId

AZUL = "#3F5F91"
BLANCO = "#FFFFFF"
NEGRO = "#000000"
GRIS = "#F4F4F4"


class ProjectTaskForm(tk.Toplevel):

    def __init__(self, master=None, mode="create", project_id=None,
                 controller=None, task_id=None, refresh=None):

        super().__init__(master)

        self.title("Formulario de Tarea")
        self.geometry("1150x750")
        self.resizable(False, False)
        self.configure(bg=BLANCO)

        self.mode = mode               
        self.project_id = project_id
        self.controller = controller
        self.task_id = task_id
        self.refresh = refresh

        self.users = self.controller.get_all_users()
        self.comments_list = []

        self.apply_styles()
        self.create_widgets()

        if self.mode == "edit" and self.task_id:
            self.load_task_data()

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabel",
                        background=BLANCO,
                        foreground=NEGRO,
                        font=("Segoe UI", 11))

        style.configure("Accent.TButton",
                        background=AZUL,
                        foreground=BLANCO,
                        padding=8,
                        font=("Segoe UI Semibold", 11))

    def create_widgets(self):

        tk.Label(self, text="Datos de la Tarea",
                 font=("Segoe UI Semibold", 22),
                 fg=AZUL, bg=BLANCO).pack(pady=15)

        main = tk.Frame(self, bg=BLANCO)
        main.pack(padx=30, pady=10, fill="both")

        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        pady_input = 10

        left = tk.Frame(main, bg=BLANCO)
        left.grid(row=0, column=0, sticky="nsew", padx=10)

        ttk.Label(left, text="Título:").pack(anchor="w")
        self.entry_titulo = ttk.Entry(left, width=45)
        self.entry_titulo.pack(pady=pady_input)

        ttk.Label(left, text="Descripción:").pack(anchor="w")
        self.text_desc = tk.Text(left, width=45, height=6, bg=GRIS)
        self.text_desc.pack(pady=pady_input)

        ttk.Label(left, text="Estado:").pack(anchor="w")
        self.combo_estado = ttk.Combobox(left, width=42,
                                         values=["Pendiente", "En Progreso", "Terminada"],
                                         state="readonly")
        self.combo_estado.pack(pady=pady_input)

        ttk.Label(left, text="Prioridad:").pack(anchor="w")
        self.combo_prioridad = ttk.Combobox(left, width=42,
                                            values=["Alta", "Media", "Baja"],
                                            state="readonly")
        self.combo_prioridad.pack(pady=pady_input)

        ttk.Label(left, text="Sprint:").pack(anchor="w")
        self.spin_sprint = tk.Spinbox(left, from_=1, to=50, width=10)
        self.spin_sprint.pack(pady=pady_input)

        ttk.Label(left, text="Fecha límite (YYYY-MM-DD):").pack(anchor="w")
        self.entry_fecha = ttk.Entry(left, width=20)
        self.entry_fecha.pack(pady=pady_input)

        ttk.Label(left, text="Asignado a:").pack(anchor="w")
        self.combo_user = ttk.Combobox(left,
                                       values=[u["usuario"] for u in self.users],
                                       width=42, state="readonly")
        self.combo_user.pack(pady=pady_input)

        ttk.Label(left, text="Fecha Completado (si Terminada):").pack(anchor="w")
        self.entry_completado = ttk.Entry(left, width=20)
        self.entry_completado.pack(pady=pady_input)

        right = tk.Frame(main, bg=BLANCO)
        right.grid(row=0, column=1, sticky="nsew", padx=10)

        ttk.Label(right, text="Subtareas:").pack(anchor="w")
        self.subtasks_frame = tk.Frame(right, bg=BLANCO)
        self.subtasks_frame.pack(fill="both", pady=5)

        self.subtasks_entries = []
        self.add_subtask_row()

        ttk.Button(right, text="Agregar subtarea",
                   style="Accent.TButton",
                   command=self.add_subtask_row).pack(pady=7)

        ttk.Label(right, text="Comentarios:").pack(anchor="w")
        self.text_comentario = tk.Text(right, width=45, height=4, bg=GRIS)
        self.text_comentario.pack(pady=5)

        ttk.Button(right, text="Agregar Comentario",
                   style="Accent.TButton",
                   command=self.add_comment_to_list).pack(pady=4)


        btn_text = "Actualizar Tarea" if self.mode == "edit" else "Guardar Tarea"

        self.btn_guardar = ttk.Button(right, text=btn_text,
                                      style="Accent.TButton",
                                      command=self.save_task)
        self.btn_guardar.pack(pady=15)

    def add_subtask_row(self, nombre="", done=False):
        frame = tk.Frame(self.subtasks_frame, bg=BLANCO)
        frame.pack(anchor="w", pady=3)

        var_done = tk.BooleanVar(value=done)

        chk = tk.Checkbutton(frame, variable=var_done, bg=BLANCO)
        chk.pack(side="left")

        entry = ttk.Entry(frame, width=40)
        entry.insert(0, nombre)
        entry.pack(side="left", padx=5)

        self.subtasks_entries.append((entry, var_done))

    def add_comment_to_list(self):
        texto = self.text_comentario.get("1.0", "end").strip()
        if texto:
            self.comments_list.append({
                "usuario": "admin",           
                "texto": texto,
                "fecha_comentario": datetime.now()
            })
            self.text_comentario.delete("1.0", "end")
            messagebox.showinfo("Comentario", "Comentario agregado.")

    def load_task_data(self):
        t = self.controller.get_task_by_id(self.task_id)

        self.entry_titulo.insert(0, t["titulo"])
        self.text_desc.insert("1.0", t["descripcion"])

        self.combo_estado.set(t["estado"])
        self.combo_prioridad.set(t["prioridad"])

        self.spin_sprint.delete(0, "end")
        self.spin_sprint.insert(0, t["sprint"])

        if t.get("fecha_limite"):
            self.entry_fecha.insert(0, t["fecha_limite"].strftime("%Y-%m-%d"))

        if t.get("asignado_a"):
            for idx, u in enumerate(self.users):
                if u["_id"] == t["asignado_a"]:
                    self.combo_user.current(idx)

        if t.get("fecha_completado"):
            self.entry_completado.insert(0, t["fecha_completado"].strftime("%Y-%m-%d"))

        for widget in self.subtasks_frame.winfo_children():
            widget.destroy()
        self.subtasks_entries = []
        for s in t["subtareas"]:
            self.add_subtask_row(s["nombre"], s["done"])

        self.comments_list = t.get("comentarios", [])

    def save_task(self):

        try:
            fecha_limite = datetime.strptime(self.entry_fecha.get(), "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Formato de fecha límite incorrecto.")
            return

        fecha_completado = None
        if self.entry_completado.get().strip():
            fecha_completado = datetime.strptime(self.entry_completado.get(), "%Y-%m-%d")

        # Usuario asignado
        user_index = self.combo_user.current()
        asignado = self.users[user_index]["_id"] if user_index != -1 else None

        # Subtareas
        subtareas = []
        for entry, done_var in self.subtasks_entries:
            nombre = entry.get().strip()
            if nombre:
                subtareas.append({"nombre": nombre, "done": done_var.get()})

        tarea = {
            "id_proyecto": ObjectId(self.project_id),
            "titulo": self.entry_titulo.get().strip(),
            "descripcion": self.text_desc.get("1.0", "end").strip(),
            "estado": self.combo_estado.get(),
            "prioridad": self.combo_prioridad.get(),
            "sprint": int(self.spin_sprint.get()),
            "fecha_limite": fecha_limite,
            "asignado_a": asignado,
            "subtareas": subtareas,
            "comentarios": self.comments_list,
            "fecha_completado": fecha_completado
        }

        if self.mode == "create":
            tarea["fecha_creacion"] = datetime.now()
            self.controller.create_task(tarea)
            messagebox.showinfo("Éxito", "Tarea creada correctamente.")

        else:
            self.controller.update_task(self.task_id, tarea)
            messagebox.showinfo("Éxito", "Tarea actualizada correctamente.")

        if self.refresh:
            self.refresh()

        self.destroy()
