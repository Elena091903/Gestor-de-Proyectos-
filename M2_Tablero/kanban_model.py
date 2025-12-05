import pymongo
from bson import ObjectId
from datetime import datetime
import sys
import os


URI_ATLAS = "mongodb+srv://admin:EwUMEAJtTFAvpe4Y@cluster.zpxcapr.mongodb.net/?appName=Cluster"

class KanbanModel:
    def __init__(self):
        self.db = None
        print("MODELO: Conectando a ATLAS...")
        try:
            client = pymongo.MongoClient(URI_ATLAS)
            self.db = client["kanban_agile_db"]
            self.db.command('ping')
            print("MODELO: Conexión exitosa.")
        except Exception as e:
            print(f"Error DB: {e}")

    def get_collection(self, name):
        return self.db[name]

    def get_users_map(self):
        mapa = {}
        try:
            for u in self.get_collection("usuarios").find():
                mapa[u["_id"]] = u["usuario"]
        except: pass
        return mapa

    
    def get_all_projects(self):
        """Devuelve una lista de todos los proyectos (ID y Nombre)"""
        try:
           
            return list(self.get_collection("proyectos").find({}, {"_id": 1, "nombre": 1, "sprint_actual": 1}))
        except Exception as e:
            print(f"Error obteniendo proyectos: {e}")
            return []

    def get_project_info(self, project_id):
        if not project_id: return None
        return self.get_collection("proyectos").find_one({"_id": project_id})

    def get_tasks_by_project(self, project_id):
        if not project_id: return []
        
        return list(self.get_collection("tareas").find({"id_proyecto": project_id}))

    def update_task_status(self, task_id, new_status):
        
        updates = {"estado": new_status}
        
        if new_status == "Terminada":
            updates["fecha_completado"] = datetime.now()
            print(f"Tarea finalizada. Fecha registrada.")
        else:
            updates["fecha_completado"] = None
            
        self.get_collection("tareas").update_one({"_id": task_id}, {"$set": updates})

    def log_history(self, user_id, project_id, task_title, old_status, new_status):
        try:
            log = {
                "fecha": datetime.now(),
                "id_usuario": user_id,
                "id_proyecto": project_id,
                "tipo_de_accion": "CAMBIO_ESTADO",
                "valor_anterior": old_status,
                "nuevo_valor": new_status,
                "detalles": f"Tarea '{task_title}' movida a {new_status}"
            }
            self.get_collection("historial").insert_one(log)
        except Exception as e:
            print(f"Error log: {e}")