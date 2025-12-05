# models/m1_task_model.py
from bson import ObjectId
from mongo_con import MongoConnection
from datetime import datetime

class TaskModel:
    def __init__(self):
        conn = MongoConnection()
        self.collection = conn.get_collection("tareas")
        self.users = conn.get_collection("usuarios")

    def get_tasks_by_project(self, project_id):
        return list(self.collection.find({"id_proyecto": ObjectId(project_id)}).sort("fecha_creacion", -1))

    def get_task(self, task_id):
        try:
            return self.collection.find_one({"_id": ObjectId(task_id)})
        except Exception:
            return None

    def create_task(self, data):
        data["fecha_creacion"] = datetime.now()
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def update_task(self, task_id, data):
        self.collection.update_one({"_id": ObjectId(task_id)}, {"$set": data})

    def delete_task(self, task_id):
        self.collection.delete_one({"_id": ObjectId(task_id)})

    def update_subtasks(self, task_id, subtask_list):
        self.collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"subtareas": subtask_list}})

    def get_user_name(self, user_id):
        if not user_id:
            return "-"
        u = self.users.find_one({"_id": ObjectId(user_id)})
        return u["usuario"] if u else "-"

    # models/m1_task_model.py  (añadir método)
    # def delete_tasks_by_project(self, project_id):
    #     self.collection.delete_many({"id_proyecto": ObjectId(project_id)})

    def delete_tasks_by_project(self, project_id):
        try:
            self.collection.delete_many({"id_proyecto": ObjectId(project_id)})
            return True
        except Exception:
            return False
