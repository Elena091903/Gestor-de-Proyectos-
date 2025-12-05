# M4_Historial/models/m4_history_model.py
from bson import ObjectId
from datetime import datetime
from mongo_con import MongoConnection

class HistoryModel:
    def __init__(self):
        conn = MongoConnection()
        self.collection = conn.get_collection("historial")
        # aseguramos índices
        self._ensure_indexes()

    def _ensure_indexes(self):
        try:
            self.collection.create_index([("id_proyecto", 1), ("fecha", -1)])
            self.collection.create_index("id_usuario")
            self.collection.create_index("tipo_de_accion")
            self.collection.create_index("fecha")
        except Exception:
            pass

    def _to_objectid_if_hex(self, v):
        if v is None:
            return None
        try:
            if isinstance(v, ObjectId):
                return v
            if isinstance(v, str) and len(v) == 24:
                return ObjectId(v)
        except Exception:
            pass
        return v

    def insert(self, entry: dict):
        e = dict(entry)
        # fecha -> datetime UTC
        if "fecha" not in e or not isinstance(e.get("fecha"), datetime):
            e["fecha"] = datetime.utcnow()
        # normalizar ids
        if e.get("id_proyecto") is not None:
            e["id_proyecto"] = self._to_objectid_if_hex(e["id_proyecto"])
        if e.get("id_usuario") is not None:
            e["id_usuario"] = self._to_objectid_if_hex(e["id_usuario"])
        # insertar
        res = self.collection.insert_one(e)
        return str(res.inserted_id)

    def find_by_filters(self, project_id=None, user_id=None, tipo=None, start_date=None, end_date=None,
                        text_search=None, page=1, per_page=50, sort=None):
        q = {}
        if project_id:
            q["id_proyecto"] = self._to_objectid_if_hex(project_id)
        if user_id:
            q["id_usuario"] = self._to_objectid_if_hex(user_id)
        if tipo:
            q["tipo_de_accion"] = tipo
        if start_date or end_date:
            q["fecha"] = {}
            if start_date:
                q["fecha"]["$gte"] = start_date
            if end_date:
                q["fecha"]["$lte"] = end_date
        if text_search:
            # pequeño texto libre sobre usuario_nombre, campo, valor_anterior, nuevo_valor
            q["$or"] = [
                {"usuario_nombre": {"$regex": text_search, "$options": "i"}},
                {"campo": {"$regex": text_search, "$options": "i"}},
                {"valor_anterior": {"$regex": text_search, "$options": "i"}},
                {"nuevo_valor": {"$regex": text_search, "$options": "i"}},
            ]
        skip = max(0, (page-1) * per_page)
        s = sort or [("fecha", -1)]
        cursor = self.collection.find(q).sort(s).skip(skip).limit(per_page)
        return list(cursor)

    def count_by_filters(self, **kwargs):
        q = {}
        # reuse similar logic as find_by_filters (can refactor), but simple version:
        if kwargs.get("project_id"):
            q["id_proyecto"] = self._to_objectid_if_hex(kwargs["project_id"])
        if kwargs.get("user_id"):
            q["id_usuario"] = self._to_objectid_if_hex(kwargs["user_id"])
        if kwargs.get("tipo"):
            q["tipo_de_accion"] = kwargs["tipo"]
        if kwargs.get("start_date") or kwargs.get("end_date"):
            q["fecha"] = {}
            if kwargs.get("start_date"): q["fecha"]["$gte"] = kwargs["start_date"]
            if kwargs.get("end_date"): q["fecha"]["$lte"] = kwargs["end_date"]
        if kwargs.get("text_search"):
            q["$or"] = [
                {"usuario_nombre": {"$regex": kwargs["text_search"], "$options": "i"}},
                {"campo": {"$regex": kwargs["text_search"], "$options": "i"}},
                {"valor_anterior": {"$regex": kwargs["text_search"], "$options": "i"}},
                {"nuevo_valor": {"$regex": kwargs["text_search"], "$options": "i"}},
            ]
        return self.collection.count_documents(q)
