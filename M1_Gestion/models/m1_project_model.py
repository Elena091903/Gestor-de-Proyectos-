# models/m1_project_model.py
from bson import ObjectId
from mongo_con import MongoConnection
from datetime import datetime, date as date_cls  # <-- añadir

class ProjectModel:
    def __init__(self):
        conn = MongoConnection()
        self.collection = conn.get_collection("proyectos")
        # referencia a tareas para borrado en cascada
        self.tasks = conn.get_collection("tareas")

    def get_all_projects(self):
        return list(self.collection.find().sort("nombre", 1))

    def get_project(self, project_id):
        try:
            return self.collection.find_one({"_id": ObjectId(project_id)})
        except Exception:
            return None

    def _normalize_dates_and_strip_id(self, data: dict) -> dict:
        # Trabajar sobre copia para no mutar el original pasado por la vista
        d = dict(data)
        # Si el dict trae _id (por accidente), eliminarlo para insert
        if "_id" in d:
            try:
                d.pop("_id")
            except Exception:
                d.pop("_id", None)

        # Normalizar fecha_inicio: si es datetime.date convertir a datetime
        fi = d.get("fecha_inicio")
        if fi is not None:
            # Si viene como date (pero no datetime) convertir
            if isinstance(fi, date_cls) and not isinstance(fi, datetime):
                d["fecha_inicio"] = datetime.combine(fi, datetime.min.time())
            # Si viene como str intentar parsear? (opcional) - dejamos str tal cual
        return d

    def create_project(self, data):
        data = self._normalize_dates_and_strip_id(data)
        data.setdefault("miembros", [])
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def update_project(self, project_id, data):
        # en update también normalizamos los campos que se van a setear
        data_to_set = self._normalize_dates_and_strip_id(data)
        self.collection.update_one({"_id": ObjectId(project_id)}, {"$set": data_to_set})

    def delete_project(self, project_id):
        # eliminar proyecto
        self.collection.delete_one({"_id": ObjectId(project_id)})
        # eliminar tareas asociadas (borrado en cascada)
        self.tasks.delete_many({"id_proyecto": ObjectId(project_id)})

    def update_members(self, project_id, members):
        self.collection.update_one({"_id": ObjectId(project_id)}, {"$set": {"miembros": members}})
