from tkinter import messagebox
import tkinter as tk
import sys
import os


ruta_tablero = os.path.dirname(os.path.abspath(__file__))
ruta_proyecto = os.path.dirname(ruta_tablero)

from kanban_model import KanbanModel
from kanban_view import KanbanView

class KanbanController:
    def __init__(self, root, project_id, current_user):
        self.root = root
        self.current_user = current_user
        
        self.model = KanbanModel()
        
       
        self.lista_proyectos = self.model.get_all_projects()
        
        self.mapa_proyectos = {p['nombre']: p for p in self.lista_proyectos}
        nombres_proyectos = list(self.mapa_proyectos.keys())

        
        self.project_id = project_id
        
        
        if (not self.project_id) and self.lista_proyectos:
            self.project_id = self.lista_proyectos[0]["_id"]

        
        self.view = KanbanView(root, self, nombres_proyectos)
        self.view.pack(fill="both", expand=True)
        
        
        if self.project_id:
            info = self.model.get_project_info(self.project_id)
            if info:
                self.view.set_project_selection(info["nombre"])

        self.refresh_data()

    def evento_cambiar_proyecto(self, event):
        """Se ejecuta automáticamente cuando cambias el Combobox"""
        nombre_seleccionado = self.view.cb_proyectos.get()
        
        if nombre_seleccionado in self.mapa_proyectos:
            
            proyecto_data = self.mapa_proyectos[nombre_seleccionado]
            self.project_id = proyecto_data["_id"]
            
            print(f"Cambiando tablero a: {nombre_seleccionado}")
            self.refresh_data()

    def refresh_data(self):
        try:
            if not self.project_id: return

            
            proyecto = self.model.get_project_info(self.project_id)
            tareas = self.model.get_tasks_by_project(self.project_id)
            user_map = self.model.get_users_map()
            
            sprint = proyecto.get("sprint_actual", "-") if proyecto else "-"
            
            
            self.view.update_header_info(sprint)
            self.view.render_board(tareas, user_map)
        except Exception as e:
            print(f"Error al refrescar: {e}")

    def move_task(self, task, new_status):
        old_status = task.get("estado")
        if old_status == new_status: return
        try:
            self.model.update_task_status(task["_id"], new_status)
            if self.current_user:
                self.model.log_history(
                    self.current_user["_id"], 
                    self.project_id, 
                    task.get("titulo"), 
                    old_status, new_status
                )
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))