from django.apps import AppConfig


class AgendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agenda'

    def ready(self):
        # importa signals para que se registren
        from . import signals  # noqa: F401
