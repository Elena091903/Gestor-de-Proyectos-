import sys
import os
from datetime import datetime
from bson import ObjectId

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mongo_con import MongoConnection 

class TareaModel:
    def __init__(self):
        self.conexion = MongoConnection()
        self.col_tareas = self.conexion.get_collection('tareas')
        self.col_proyectos = self.conexion.get_collection('proyectos')
        self.col_usuarios = self.conexion.get_collection('usuarios')

    def obtener_catalogos(self):
        try:
            p = list(self.col_proyectos.find({}, {
                "_id": 1, 
                "nombre": 1, 
                "descripcion": 1, 
                "id_scrum_master": 1, 
                "sprint_actual": 1, 
                "miembros": 1
            }))
            u = list(self.col_usuarios.find({}, {"_id": 1, "usuario": 1}))
            return p, u
        except:
            return [], []

    def buscar_tareas_por_proyecto(self, id_proyecto):
        try:
            query = {
                "id_proyecto": ObjectId(id_proyecto),
                "estado": {"$ne": "Terminada"}
            }
            return list(self.col_tareas.find(query, {"_id": 1, "titulo": 1}))
        except:
            return []

    def obtener_tarea_detalle(self, id_tarea):
        return self.col_tareas.find_one({"_id": ObjectId(id_tarea)})

    def guardar_transaccion(self, datos, id_tarea=None):
        try:
            doc = {
                "id_proyecto": ObjectId(datos['id_proyecto']),
                "titulo": datos['titulo'],
                "descripcion": datos['descripcion'],
                "prioridad": datos['prioridad'],
                "sprint": int(datos['sprint']),
                "fecha_limite": datetime.strptime(datos['fecha_limite'], "%Y-%m-%d"),
                "asignado_a": ObjectId(datos['id_usuario']),
                "subtareas": datos['subtareas'],      
                "comentarios": datos['comentarios']
            }

            if id_tarea:
                self.col_tareas.update_one({"_id": ObjectId(id_tarea)}, {"$set": doc})
                return True, "Tarea actualizada con éxito."
            else:
                doc["estado"] = "Pendiente"
                doc["fecha_creacion"] = datetime.now()
                doc["fecha_completado"] = None 
                self.col_tareas.insert_one(doc)
                return True, "Nueva tarea creada con éxito."
        except Exception as e:
            return False, f"Error BD: {str(e)}"