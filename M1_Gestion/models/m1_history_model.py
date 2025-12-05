# models/m1_history_model.py
from datetime import datetime
from bson import ObjectId
from mongo_con import MongoConnection

class HistoryModel:
    def __init__(self):
        conn = MongoConnection()
        self.collection = conn.get_collection("historial")

    def insert(self, entry: dict):
        # entry debe ser un dict ya válido
        e = dict(entry)
        e.setdefault("fecha", datetime.utcnow())
        # convertir strings a ObjectId si se pasan como str para id_usuario / id_proyecto
        if e.get("id_usuario") and isinstance(e.get("id_usuario"), str):
            try:
                e["id_usuario"] = ObjectId(e["id_usuario"])
            except Exception:
                pass
        if e.get("id_proyecto") and isinstance(e.get("id_proyecto"), str):
            try:
                e["id_proyecto"] = ObjectId(e["id_proyecto"])
            except Exception:
                pass
        res = self.collection.insert_one(e)
        return str(res.inserted_id)

    def find_by_project(self, project_id, limit=200):
        from bson import ObjectId
        try:
            q = {"id_proyecto": ObjectId(project_id)}
        except Exception:
            q = {"id_proyecto": project_id}
        return list(self.collection.find(q).sort("fecha", -1).limit(limit))
