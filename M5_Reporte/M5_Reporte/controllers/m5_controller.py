# m5_controller.py
from bson import ObjectId
from models.m5_model import SpeedReportModel

class SpeedReportController:
    """
    Controlador simple que conecta la vista (GUI) con el modelo.
    Pasa parámetros recibidos desde la vista al modelo y devuelve los datos listos.
    """

    def __init__(self, model: SpeedReportModel):
        self.model = model

    def get_projects(self):
        """Devuelve la lista de proyectos para poblar el combobox."""
        return self.model.get_proyectos()

    def get_data_by_week(self, id_proyecto=None, fecha_desde=None, fecha_hasta=None, solo_sprint_actual: bool = False):
        """Obtiene datos agrupados por semana. Pasa la bandera de iteración actual al modelo."""
        return self.model.tareas_completadas_por_semana(id_proyecto, fecha_desde, fecha_hasta, solo_sprint_actual=solo_sprint_actual)

    def get_data_by_sprint(self, id_proyecto=None, solo_sprint_actual: bool = False):
        """Obtiene datos agrupados por iteración (sprint)."""
        return self.model.tareas_completadas_por_sprint(id_proyecto, solo_sprint_actual=solo_sprint_actual)
