# controllers/m1_project_controller.py
from bson import ObjectId
from datetime import datetime
from tkinter import messagebox
from models.m1_project_model import ProjectModel
from models.m1_task_model import TaskModel
from models.m1_member_model import MemberModel
from models.m1_history_model import HistoryModel

class ProjectController:
    def __init__(self):
        self.project_model = ProjectModel()
        self.task_model = TaskModel()
        self.member_model = MemberModel()
        self.history_model = HistoryModel()

    # -------------------------
    # Helpers internos
    # -------------------------
    def _to_str(self, v):
        if v is None:
            return None
        try:
            from bson import ObjectId
            if isinstance(v, ObjectId):
                return str(v)
        except Exception:
            pass
        try:
            return str(v)
        except Exception:
            return v

    def record_history(self, user_doc, project_id, tipo_de_accion, campo=None, valor_anterior=None, nuevo_valor=None, detalles=None):
        """
        user_doc: dict como {'_id': '...', 'usuario':'...', 'rol':'...'} o None
        project_id: str u ObjectId
        """
        entry = {
            "fecha": datetime.utcnow(),
            "id_usuario": None,
            "usuario_nombre": None,
            "rol": None,
            "id_proyecto": project_id,
            "tipo_de_accion": tipo_de_accion,
            "campo": campo,
            "valor_anterior": valor_anterior,
            "nuevo_valor": nuevo_valor,
            "detalles": detalles or {}
        }
        if user_doc:
            # aceptar dict con _id string o ObjectId
            uid = user_doc.get("_id") or user_doc.get("id") or user_doc.get("id_usuario")
            entry["id_usuario"] = uid
            entry["usuario_nombre"] = user_doc.get("usuario") or user_doc.get("usuario_nombre")
            entry["rol"] = user_doc.get("rol")
        # insertar
        try:
            return self.history_model.insert(entry)
        except Exception as e:
            # no interrumpir el flujo por fallo en historial, pero avisar en consola/log
            print("Error insertando historial:", e)
            return None

    # -------------------------
    # Proyectos
    # -------------------------
    def get_projects_for_view(self):
        proyectos = self.project_model.get_all_projects()
        lista = []
        for p in proyectos:
            lista.append({
                "_id": str(p.get("_id")),
                "nombre": p.get("nombre", "-"),
                "descripcion": p.get("descripcion", "")[:400],
                "sprint": p.get("sprint_actual", "-"),
                "miembros": len(p.get("miembros", [])),
                "estado": p.get("estado", "-"),
            })
        return lista

    def get_project(self, project_id):
        return self.project_model.get_project(project_id)

    def create_project(self, data, user_doc=None):
        if not data.get("nombre"):
            messagebox.showerror("Error", "El nombre del proyecto es obligatorio.")
            return None
        new_id = self.project_model.create_project(data)
        if new_id:
            # registrar historial: creación completa
            try:
                snapshot = {
                    "nombre": data.get("nombre"),
                    "estado": data.get("estado"),
                    "sprint_actual": data.get("sprint_actual"),
                }
                self.record_history(user_doc, new_id, "CREATE_PROJECT", campo=None, valor_anterior=None, nuevo_valor=snapshot, detalles={"nota":"Proyecto creado"})
            except Exception as e:
                print("Warning: historial create_project:", e)
        return new_id

    def update_project(self, project_id, data, user_doc=None):
        if not data.get("nombre"):
            messagebox.showerror("Error", "El nombre del proyecto es obligatorio.")
            return False
        # leer snapshot actual
        old = self.get_project(project_id) or {}
        # aplicar update
        self.project_model.update_project(project_id, data)
        # después del update, generar entradas de historial por cada campo cambiado (fields of interest)
        fields = ["nombre", "descripcion", "id_scrum_master", "miembros", "sprint_actual", "estado", "fecha_inicio"]
        for f in fields:
            old_v = old.get(f)
            new_v = data.get(f, old_v)
            # convertir a strings comparables (especialmente ObjectId y listas)
            def norm(x):
                if x is None: return None
                # ObjectId a str
                try:
                    from bson import ObjectId
                    if isinstance(x, ObjectId):
                        return str(x)
                except Exception:
                    pass
                # listas de ObjectId -> lista de str
                if isinstance(x, list):
                    return [str(i) for i in x]
                return x
            if norm(old_v) != norm(new_v):
                tipo = "UPDATE_PROJECT"
                campo = f
                if f == "estado":
                    tipo = "CAMBIO_ESTADO"
                # para miembros identificar añadidos / removidos
                detalles = {}
                if f == "miembros":
                    old_set = set([str(i) for i in (old_v or [])])
                    new_set = set([str(i) for i in (new_v or [])])
                    añadidos = list(new_set - old_set)
                    removidos = list(old_set - new_set)
                    detalles = {"añadidos": añadidos, "removidos": removidos}
                    valor_anterior = list(old_set)
                    nuevo_valor = list(new_set)
                else:
                    valor_anterior = norm(old_v)
                    nuevo_valor = norm(new_v)
                try:
                    self.record_history(user_doc, project_id, tipo, campo=campo, valor_anterior=valor_anterior, nuevo_valor=nuevo_valor, detalles=detalles)
                except Exception as e:
                    print("Warning: record_history on update:", e)
        return True

    def delete_project(self, project_id, user_doc=None):
        # snapshot anterior para guardar en historial
        snapshot = self.get_project(project_id)
        try:
            if snapshot:
                self.record_history(user_doc, project_id, "DELETE_PROJECT", campo=None, valor_anterior=snapshot, nuevo_valor=None, detalles={"nota":"Proyecto eliminado"})
        except Exception as e:
            print("Warning: historial delete:", e)
        # borrar proyecto y tareas asociadas
        self.project_model.delete_project(project_id)
        try:
            self.task_model.delete_tasks_by_project(project_id)
        except Exception:
            pass

    # -------------------------
    # Miembros / usuarios
    # -------------------------
    def get_members(self, include_inactive=False):
        return self.member_model.get_all_members(include_inactive=include_inactive)

    def create_member(self, data):
        if not data.get("nombre"):
            messagebox.showerror("Error", "El nombre del miembro es obligatorio.")
            return None
        return self.member_model.create_member(data)

    def delete_member(self, member_id):
        return self.member_model.delete_member(member_id)

    def get_scrum_masters(self):
        try:
            return self.member_model.get_scrum_masters()
        except AttributeError:
            return []

    def get_all_users(self, include_inactive=False):
        return self.member_model.get_all_members(include_inactive=include_inactive)

    def get_user_name(self, user_id):
        if not user_id:
            return "-"
        try:
            u = self.member_model.get_member_by_id(user_id)
            if u:
                return u.get("nombre") or u.get("usuario") or "-"
        except Exception:
            pass
        return "-"

    # ----- Tareas (delegadas) -----
    def get_tasks_by_project(self, project_id):
        return self.task_model.get_tasks_by_project(project_id)

    def get_task_by_id(self, task_id):
        return self.task_model.get_task(task_id)

    def create_task(self, data):
        return self.task_model.create_task(data)

    def update_task(self, task_id, data):
        return self.task_model.update_task(task_id, data)

    def delete_task(self, task_id):
        return self.task_model.delete_task(task_id)

    def update_subtasks(self, task_id, subtasks):
        return self.task_model.update_subtasks(task_id, subtasks)

    # ----- Reglas de negocio -----
    def can_mark_project_finished(self, project_id):
        tareas = self.task_model.get_tasks_by_project(project_id)
        if not tareas:
            return True
        for t in tareas:
            estado = (t.get("estado") or "").strip().lower()
            if estado != "terminada":
                return False
        return True
