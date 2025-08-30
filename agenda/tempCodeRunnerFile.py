# agenda/models.py

from django.db import models
from django.contrib.auth.models import User


class Paciente(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="paciente",
        verbose_name="Usuario"
    )
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name="medicos"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} — {self.especialidad.nombre}"


class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico,    on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    motivo = models.TextField()

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        fecha_str = self.fecha.strftime("%d/%m/%Y %H:%M")
        return f"{self.paciente} ↔ {self.medico} · {fecha_str}"
