
from bson import ObjectId
from M5_Reporte.models.m5_model import SpeedReportModel

class SpeedReportController:


    def __init__(self, model: SpeedReportModel):
        self.model = model

    def get_projects(self):
        
        return self.model.get_proyectos()

    def get_data_by_week(self, id_proyecto=None, fecha_desde=None, fecha_hasta=None, solo_sprint_actual: bool = False):
       
        return self.model.tareas_completadas_por_semana(id_proyecto, fecha_desde, fecha_hasta, solo_sprint_actual=solo_sprint_actual)

    def get_data_by_sprint(self, id_proyecto=None, solo_sprint_actual: bool = False):
        
        return self.model.tareas_completadas_por_sprint(id_proyecto, solo_sprint_actual=solo_sprint_actual)
