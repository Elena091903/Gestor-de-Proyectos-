from models.m3_model import TareaModel
from views.m3_view import TareaView
from tkinter import messagebox

class TareaController:
    def __init__(self, root):
        self.model = TareaModel()
        self.proyectos_list, self.usuarios_list = self.model.obtener_catalogos()
        
        self.mapa_proyectos = {p['nombre']: p for p in self.proyectos_list}
        self.mapa_usuarios = {u['usuario']: u for u in self.usuarios_list}
        self.mapa_tareas_actuales = {}
        self.id_tarea_actual = None
        self.current_project_sprint = 1

        nombres_p = list(self.mapa_proyectos.keys())
        self.view = TareaView(root, self, nombres_p)

    def preparar_nueva(self):
        self.id_tarea_actual = None
        self.view.limpiar_form()
        self.view.cb_filtro_tarea.set('')
        self.view.btn_save.config(text="GUARDAR NUEVA TAREA")
        
        # Restaurar info del proyecto seleccionado
        nombre = self.view.cb_filtro_proy.get()
        proyecto = self.mapa_proyectos.get(nombre)
        if proyecto:
            self.view.lbl_proy_nombre.config(text=proyecto['nombre'])
            self.view.lbl_proy_desc.config(text=proyecto.get('descripcion', 'Sin descripción'))
            self.view.entry_sprint_tarea.set(self.current_project_sprint)

    def evento_filtrar_proyecto(self, event):
        nombre = self.view.cb_filtro_proy.get()
        proyecto = self.mapa_proyectos.get(nombre)
        
        if proyecto:
            # Actualizar Tarjeta Contexto
            self.view.lbl_proy_nombre.config(text=proyecto['nombre'])
            self.view.lbl_proy_desc.config(text=proyecto.get('descripcion', 'Sin descripción'))
            
            # Configurar Sprint
            self.current_project_sprint = proyecto.get('sprint_actual', 1)
            self.view.configurar_limite_sprint(self.current_project_sprint)
            
            id_sm = proyecto.get('id_scrum_master')
            sm_nombre = next((u['usuario'] for u in self.usuarios_list if u['_id'] == id_sm), "Sin asignar")
            
            self.view.lbl_sm.config(text=f"Scrum Master: {sm_nombre.title()}")
            self.view.lbl_sprint.config(text=f"Sprint Actual Proyecto: {self.current_project_sprint}")

            ids_miembros = proyecto.get('miembros', [])
            nombres_miembros = [u['usuario'].title() for u in self.usuarios_list if u['_id'] in ids_miembros]
            
            self.view.cb_asignado['values'] = nombres_miembros
            if nombres_miembros:
                self.view.cb_asignado.current(0)
            
            tareas = self.model.buscar_tareas_por_proyecto(proyecto['_id'])
            self.mapa_tareas_actuales = {t['titulo']: t['_id'] for t in tareas}
            self.view.cb_filtro_tarea['values'] = list(self.mapa_tareas_actuales.keys())
            self.view.cb_filtro_tarea.set('')
            
            self.id_tarea_actual = None
            self.view.limpiar_form()
            self.view.lbl_proy_nombre.config(text=proyecto['nombre'])
            self.view.lbl_proy_desc.config(text=proyecto.get('descripcion', 'Sin descripción'))
            self.view.entry_sprint_tarea.set(self.current_project_sprint)
            self.view.btn_save.config(text="GUARDAR NUEVA TAREA")

    def evento_seleccionar_tarea(self, event):
        nombre_t = self.view.cb_filtro_tarea.get()
        id_t = self.mapa_tareas_actuales.get(nombre_t)
        
        if id_t:
            data = self.model.obtener_tarea_detalle(id_t)
            if data:
                self.id_tarea_actual = id_t
                self.view.llenar_form(data)
                
                nombre = self.view.cb_filtro_proy.get()
                proyecto = self.mapa_proyectos.get(nombre)
                if proyecto:
                    self.view.lbl_proy_nombre.config(text=proyecto['nombre'])
                    self.view.lbl_proy_desc.config(text=proyecto.get('descripcion', ''))

                id_asig = data.get('asignado_a')
                user_obj = next((u for u in self.usuarios_list if u['_id'] == id_asig), None)
                if user_obj:
                    self.view.cb_asignado.set(user_obj['usuario'].title())
                
                self.view.btn_save.config(text="ACTUALIZAR TAREA")

    def guardar_datos(self):
        errores = []
        proy_nom = self.view.cb_filtro_proy.get()
        if not proy_nom: errores.append("Error: Selecciona un PROYECTO.")
        
        titulo = self.view.entry_titulo.get().strip()
        if not titulo: errores.append("Error: Falta el Título.")
        
        user_nom_bonito = self.view.cb_asignado.get()
        
        if not user_nom_bonito: errores.append("Error: Debes asignar un miembro.")
        
        try:
            sprint_elegido = int(self.view.entry_sprint_tarea.get())
        except:
            errores.append(" Error: El Sprint debe ser un número.")
            sprint_elegido = 1

        if errores:
            messagebox.showwarning("Datos Incompletos", "\n".join(errores))
            return 

        proyecto = self.mapa_proyectos[proy_nom]
        usuario_encontrado = next((u for u in self.usuarios_list if u['usuario'].lower() == user_nom_bonito.lower()), None)

        if not usuario_encontrado:
             messagebox.showerror("Error", "Usuario no encontrado.")
             return

        datos = {
            "id_proyecto": proyecto['_id'],
            "titulo": titulo,
            "descripcion": self.view.txt_desc.get("1.0", "end").strip(),
            "prioridad": self.view.cb_prioridad.get(),
            "sprint": sprint_elegido,
            "fecha_limite": self.view.cal_limite.get(),
            "id_usuario": usuario_encontrado['_id'],
            "subtareas": self.view.obtener_subtareas(), 
            "comentarios": self.view.obtener_comentarios()
        }
        
        ok, msg = self.model.guardar_transaccion(datos, self.id_tarea_actual)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.evento_filtrar_proyecto(None)
        else:
            messagebox.showerror("Error", msg)