from django.core.management.base import BaseCommand
from agenda.models import Especialidad, Medico


class Command(BaseCommand):
    help = "Crea datos iniciales de ejemplo (especialidades y médicos)."

    def handle(self, *args, **kwargs):
        esp1, _ = Especialidad.objects.get_or_create(nombre="Medicina General")
        esp2, _ = Especialidad.objects.get_or_create(nombre="Dermatología")

        Medico.objects.get_or_create(
            nombre="Dra. Ana Pérez", especialidad=esp1)
        Medico.objects.get_or_create(
            nombre="Dr. Luis Gómez", especialidad=esp1)
        Medico.objects.get_or_create(
            nombre="Dra. Carla Soto", especialidad=esp2)

        self.stdout.write(self.style.SUCCESS("Datos iniciales creados."))
