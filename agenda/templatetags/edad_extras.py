# agenda/templatetags/edad_extras.py

from django import template
from datetime import date

register = template.Library()


@register.filter
def calcular_edad(fecha_nacimiento):
    if not fecha_nacimiento:
        return ""
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
