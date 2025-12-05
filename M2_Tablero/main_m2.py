import tkinter as tk
import pymongo
from kanban_controller import KanbanController


URI_ATLAS = "mongodb+srv://admin:EwUMEAJtTFAvpe4Y@cluster.zpxcapr.mongodb.net/?appName=Cluster"

if __name__ == "__main__":
    try:
        print("Conectando a Mongo Atlas (Nube)...")
        
        client = pymongo.MongoClient(URI_ATLAS)
    
        db = client["kanban_agile_db"]
        
        tarea_ejemplo = db["tareas"].find_one()
        
        if tarea_ejemplo:
            id_proy = tarea_ejemplo["id_proyecto"]
            
            
            proyecto = db["proyectos"].find_one({"_id": id_proy})
            usuario = db["usuarios"].find_one()
            
            nombre_proy = proyecto['nombre'] if proyecto else "Sin Nombre"
            
            print(f"DATOS ENCONTRADOS EN LA NUBE.")
            print(f"Abriendo Tablero para: {nombre_proy}")
            
            root = tk.Tk()
            root.geometry("1100x600")
            root.title(f"Tablero Kanban ")
            
            app = KanbanController(root, id_proy, usuario)
            root.mainloop()
            
        else:
            print("Conexión exitosa a Atlas, pero la colección 'tareas' está VACÍA.")
            print("Ejecuta el script de llenado de datos en la consola de Compass.")

    except Exception as e:
        print(f"Error de Conexión: {e}")