# models/m1_member_model.py
from bson import ObjectId
from mongo_con import MongoConnection

class MemberModel:
    def __init__(self):
        conn = MongoConnection()
        # colección para miembros del equipo (creada por este módulo)
        self.collection = conn.get_collection("miembros")
        # colección que puede contener usuarios (scrum masters)
        self.users_collection = conn.get_collection("usuarios")

    def get_all_members(self, include_inactive=False):
        q = {} if include_inactive else {"activo": True}
        return list(self.collection.find(q).sort("nombre", 1))

    def get_member_by_id(self, member_id):
        try:
            return self.collection.find_one({"_id": ObjectId(member_id)})
        except Exception:
            return None

    def create_member(self, data):
        data.setdefault("activo", True)
        res = self.collection.insert_one(data)
        return str(res.inserted_id)

    def delete_member(self, member_id):
        try:
            self.collection.delete_one({"_id": ObjectId(member_id)})
            return True
        except Exception:
            return False

    def get_scrum_masters(self):
        # Si los scrum masters están en la colección 'usuarios'
        return list(self.users_collection.find({"rol": "Scrum Master", "activo": True}))
