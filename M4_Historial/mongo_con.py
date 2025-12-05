# connection.py
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoConnection:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)

            uri = "mongodb+srv://admin:EwUMEAJtTFAvpe4Y@cluster.zpxcapr.mongodb.net/?appName=Cluster"

            try:
                cls._instance.client = MongoClient(uri, server_api=ServerApi('1'))
                cls._instance.client.admin.command("ping")
                print("Conexión exitosa a MongoDB Atlas.")
            except Exception as e:
                print("Error de conexión:", e)


            cls._instance.db = cls._instance.client["kanban_agile_db"]

        return cls._instance

    def get_collection(self, name: str):
        """Regresa una colección lista para usarse."""
        return self.db[name]