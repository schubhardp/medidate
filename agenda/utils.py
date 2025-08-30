from datetime import datetime, time, timedelta
from django.utils import timezone
from .models import Cita, Medico


def _rango_horas(inicio: time, fin: time, paso_min=30):
    """
    Genera times cada 'paso_min' minutos desde 'inicio' (incluida) hasta 'fin' (excluida).
    """
    # Usamos la fecha local de hoy solo como soporte para sumar minutos
    base = timezone.localdate()
    dt = datetime.combine(base, inicio)
    dt_fin = datetime.combine(base, fin)
    while dt < dt_fin:
        yield dt.time()
        dt += timedelta(minutes=paso_min)


def _ventanas_estandar():
    """
    Horario estándar de atención: 09:00–13:00 y 15:00–19:00, cada 30 minutos.
    Ajusta aquí si tu clínica usa otros rangos.
    """
    maniana = list(_rango_horas(time(9, 0), time(13, 0), 30))
    tarde = list(_rango_horas(time(15, 0), time(19, 0), 30))
    return maniana + tarde


def horas_disponibles_para(medico: Medico, fecha):
    """
    Devuelve una lista de objetos time con los horarios disponibles para un médico
    en la fecha dada, excluyendo:
      - horas ya reservadas en la BD
      - horas pasadas si la fecha es hoy
    """
    # Si la fecha cae sábado o domingo, devolvemos vacío (la vista ya valida esto también)
    if fecha.weekday() >= 5:
        return []

    # Todas las horas del día hábil
    candidatos = _ventanas_estandar()

    # Horas ya ocupadas
    ocupadas = set(
        Cita.objects.filter(medico=medico, fecha=fecha).values_list(
            "hora", flat=True)
    )

    # Si es hoy, removemos horas pasadas
    hoy = timezone.localdate()
    ahora = timezone.localtime().time()
    if fecha == hoy:
        candidatos = [h for h in candidatos if h > ahora]

    # Disponibles = candidatos - ocupadas
    libres = [h for h in candidatos if h not in ocupadas]
    return libres
