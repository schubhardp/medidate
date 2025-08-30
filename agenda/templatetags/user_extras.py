from django import template
from agenda.models import Medico, Paciente

register = template.Library()


@register.simple_tag
def has_medico(user):
    """
    Retorna True si el usuario tiene perfil de médico.
    """
    if not user.is_authenticated:
        return False
    try:
        # Intenta acceder al perfil del médico asociado al usuario
        return Medico.objects.filter(user=user).exists()
    except Exception:
        return False


@register.simple_tag
def has_paciente(user):
    """
    Retorna True si el usuario tiene perfil de paciente.
    """
    if not user.is_authenticated:
        return False
    try:
        return Paciente.objects.filter(user=user).exists()
    except Exception:
        return False
