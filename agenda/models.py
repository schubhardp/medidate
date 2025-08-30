from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name() or self.email


class Paciente(models.Model):
    GENERO = [('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='paciente')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Especialidad(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField(max_length=150)
    especialidad = models.ForeignKey(
        Especialidad, on_delete=models.PROTECT, related_name='medicos')

    def __str__(self):
        return f"{self.nombre} ({self.especialidad})"


class Cita(models.Model):
    ESTADO = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    paciente = models.ForeignKey(
        'Paciente', on_delete=models.CASCADE, related_name='citas')
    medico = models.ForeignKey(
        'Medico',    on_delete=models.PROTECT, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=250, blank=True)
    estado = models.CharField(
        max_length=12, choices=ESTADO, default='pendiente')
    creada = models.DateTimeField(auto_now_add=True)

    # Nuevo: auditoría de cancelación
    cancelada_por = models.ForeignKey(
        'User', null=True, blank=True, on_delete=models.SET_NULL, related_name='citas_canceladas_por'
    )
    cancelada_en = models.DateTimeField(null=True, blank=True)
    cancel_motivo = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('medico', 'fecha', 'hora')
        ordering = ['fecha', 'hora']
        permissions = (
            ("access_consultorio", "Puede acceder al panel de consultorio"),
        )
        # Índices para acelerar listados/filtrados
        indexes = [
            models.Index(fields=['fecha', 'hora']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.fecha} {self.hora} - {self.paciente} / {self.medico}"

    # ---- Lógica de estado UI (no cambia tu semántica) ----
    @property
    def estado_ui(self) -> str:
        if self.estado == "cancelada":
            return "cancelada"
        hoy = timezone.localdate()
        ahora = timezone.localtime().time()
        if self.fecha < hoy or (self.fecha == hoy and self.hora <= ahora):
            return "atendida"     # pasada
        return "agendada"

    @property
    def estado_badge_class(self) -> str:
        s = self.estado_ui
        if s == "agendada":
            return "badge-brand"  # color de marca (teal)
        if s == "atendida":
            return "bg-success"   # verde
        return "bg-secondary"     # cancelada (gris)

    # ---- Helpers para cancelar desde staff ----
    def es_pasada(self) -> bool:
        """True si ya ocurrió (no debería poder cancelarse)."""
        hoy = timezone.localdate()
        ahora = timezone.localtime().time()
        return self.fecha < hoy or (self.fecha == hoy and self.hora <= ahora)

    def cancelar(self, user, motivo: str = "") -> bool:
        """Marca la cita como cancelada (si procede). Devuelve True si cambió."""
        if self.estado == 'cancelada' or self.es_pasada():
            return False
        self.estado = 'cancelada'
        self.cancelada_por = user
        self.cancelada_en = timezone.now()
        if motivo:
            self.cancel_motivo = motivo[:200]
        self.save(update_fields=[
                  'estado', 'cancelada_por', 'cancelada_en', 'cancel_motivo'])
        return True
