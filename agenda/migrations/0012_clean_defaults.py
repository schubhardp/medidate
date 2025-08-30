from django.db import migrations
from datetime import time


def clean_defaults(apps, schema_editor):
    Paciente = apps.get_model("agenda", "Paciente")
    Cita = apps.get_model("agenda", "Cita")

    # 1) Limpia teléfonos que quedaron con el texto del fix
    Paciente.objects.filter(telefono="sin-telefono").update(telefono=None)

    # 2) Opcional: marca las citas en 09:00:00 (si ese valor se usó como fix)
    #    No podemos poner hora a NULL porque el campo es obligatorio.
    #    Si no quieres tocar nada acá, borra la línea de update.
    Cita.objects.filter(hora=time(9, 0, 0), motivo="").update(
        motivo="(revisar hora asignada de forma automática)")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("agenda", "0011_alter_paciente_telefono"),
    ]

    operations = [
        migrations.RunPython(clean_defaults, noop),
    ]
