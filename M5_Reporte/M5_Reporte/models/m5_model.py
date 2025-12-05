# m5_model.py
from datetime import datetime, date, timedelta
from collections import defaultdict
from bson import ObjectId
from mongo_con import MongoConnection

class SpeedReportModel:
    """
    Modelo que obtiene y agrupa datos de la colección 'tareas' para generar
    el reporte de velocidad (tareas completadas por semana o por iteración).
    """

    def __init__(self, mongo_conn: MongoConnection):
        # Colecciones usadas: tareas y proyectos
        self.tareas = mongo_conn.get_collection('tareas')
        self.proyectos = mongo_conn.get_collection('proyectos')

    def get_proyectos(self):
        """Devuelve una lista simple de proyectos con nombre y sprint_actual."""
        cursor = self.proyectos.find({}, projection={'nombre': 1, 'sprint_actual': 1}).sort('nombre', 1)
        return list(cursor)

    def _week_label(self, year:int, week:int):
        """
        Genera una etiqueta legible para una semana ISO.
        Ej: '01 Sep - 07 Sep 2025 (W36)'
        """
        try:
            monday = date.fromisocalendar(year, week, 1)
        except Exception:
            return f'W{week} {year}'
        sunday = monday + timedelta(days=6)
        return f"{monday.strftime('%d %b')} - {sunday.strftime('%d %b %Y')} (W{week})"

    def tareas_completadas_por_semana(self, id_proyecto=None, fecha_desde=None, fecha_hasta=None, solo_sprint_actual=False):
        """
        Agrupa tareas terminadas por semana.
        - id_proyecto: filtra por proyecto si se pasa.
        - solo_sprint_actual: si es True y se pasa id_proyecto, filtra por la iteración actual del proyecto.
        Devuelve lista de (etiqueta, conteo) ordenada cronológicamente.
        """
        query = { 'estado': 'Terminada' }

        if id_proyecto:
            if isinstance(id_proyecto, str):
                try:
                    id_proyecto = ObjectId(id_proyecto)
                except Exception:
                    pass
            query['id_proyecto'] = id_proyecto

            if solo_sprint_actual:
                # Si se pide, obtenemos el sprint_actual (iteración actual) del proyecto
                proj = self.proyectos.find_one({'_id': id_proyecto}, projection={'sprint_actual': 1})
                if proj and 'sprint_actual' in proj:
                    query['sprint'] = proj['sprint_actual']

        # Filtro por rango de fechas si se proporcionan
        if fecha_desde or fecha_hasta:
            qrange = {}
            if fecha_desde:
                qrange['$gte'] = fecha_desde
            if fecha_hasta:
                qrange['$lte'] = fecha_hasta
            query['fecha_completado'] = qrange

        cursor = self.tareas.find(query)

        # Agrupamos por (año, semana ISO)
        groups = defaultdict(int)
        for doc in cursor:
            fecha = doc.get('fecha_completado')
            if not fecha:
                continue
            iso = fecha.isocalendar()  # (year, week, weekday)
            key = (iso[0], iso[1])
            groups[key] += 1

        keys_sorted = sorted(groups.keys(), key=lambda k: (int(k[0]), int(k[1])))
        return [(self._week_label(k[0], k[1]), groups[k]) for k in keys_sorted]

    def tareas_completadas_por_sprint(self, id_proyecto=None, solo_sprint_actual=False):
        """
        Agrupa tareas terminadas por iteración (campo 'sprint' en tareas).
        - Si id_proyecto y solo_sprint_actual=True, filtra por la iteración actual del proyecto.
        """
        query = { 'estado': 'Terminada' }

        if id_proyecto:
            if isinstance(id_proyecto, str):
                try:
                    id_proyecto = ObjectId(id_proyecto)
                except Exception:
                    pass
            query['id_proyecto'] = id_proyecto

            if solo_sprint_actual:
                proj = self.proyectos.find_one({'_id': id_proyecto}, projection={'sprint_actual': 1})
                if proj and 'sprint_actual' in proj:
                    query['sprint'] = proj['sprint_actual']

        cursor = self.tareas.find(query, projection={'sprint': 1})
        groups = defaultdict(int)
        for doc in cursor:
            sprint = doc.get('sprint')
            sprint_key = f"Iteración {sprint}" if sprint is not None else 'Sin Iteración'
            groups[sprint_key] += 1

        # Ordenar por número de iteración cuando sea posible
        def keyfunc(k):
            try:
                return int(k.split(' ')[1])
            except Exception:
                return 9999

        keys_sorted = sorted(groups.keys(), key=keyfunc)
        return [(k, groups[k]) for k in keys_sorted]
