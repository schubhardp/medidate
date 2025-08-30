from .models import Paciente


def rol_flags(request):
    es_paciente = False
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        es_paciente = Paciente.objects.filter(user=user).exists()
    return {"es_paciente": es_paciente}
