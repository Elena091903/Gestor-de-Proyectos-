# M4_Historial/controllers/m4_history_controller.py
from models.m4_history_model import HistoryModel
from bson import ObjectId
from datetime import datetime

class HistoryController:
    def __init__(self):
        self.model = HistoryModel()

    def insert_entry(self, user_doc, project_id, tipo_de_accion, campo=None, valor_anterior=None, nuevo_valor=None):
        # columnas de la colección historial 
        entry = {
            "fecha": datetime.utcnow(),
            "id_usuario": user_doc.get("_id") if user_doc else None,
            "usuario_nombre": user_doc.get("usuario") if user_doc else None,
            "rol": user_doc.get("rol") if user_doc else None,
            "id_proyecto": project_id,
            "tipo_de_accion": tipo_de_accion,
            "campo": campo,
            "valor_anterior": valor_anterior,
            "nuevo_valor": nuevo_valor,
        }
        return self.model.insert(entry)

    def list(self, **filters):
        # pasa filtros al modelo (project_name, tipo, start_date, end_date)
        return self.model.find_by_filters(**filters)

    def count(self, **filters):
        return self.model.count_by_filters(**filters)
