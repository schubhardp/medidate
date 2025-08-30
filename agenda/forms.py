from datetime import time
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from .models import Cita, Paciente, Medico, Especialidad, User

# =========================
#  Autenticación / Registro
# =========================
GENERO_CHOICES = [("", "---------"), ("M", "Masculino"),
                  ("F", "Femenino"), ("O", "Otro")]


class RegistroForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombre", max_length=150, required=False)
    last_name = forms.CharField(
        label="Apellidos", max_length=150, required=False)
    email = forms.EmailField(label="Email", required=True)
    genero = forms.ChoiceField(
        label="Género", choices=GENERO_CHOICES, required=False)
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False)
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = User  # tu modelo custom
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # clases Bootstrap para tu estética
        for name, f in self.fields.items():
            if isinstance(f.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                f.widget.attrs.update({"class": "form-control"})
            elif isinstance(f.widget, forms.Select):
                f.widget.attrs.update({"class": "form-select"})
        self.fields["first_name"].widget.attrs["placeholder"] = "Nombre"
        self.fields["last_name"].widget.attrs["placeholder"] = "Apellidos"
        self.fields["email"].widget.attrs["placeholder"] = "correo@ejemplo.com"

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise forms.ValidationError("Este campo no puede estar vacío.")
        UserModel = get_user_model()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        if p1:
            validate_password(p1)
        return cleaned

    def save(self, commit=True):
        email = self.cleaned_data["email"].strip().lower()
        user = User(
            email=email,
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
        )
        # si tu modelo aún tiene username, úsalo igual que el email
        if hasattr(user, "username"):
            user.username = email
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            # Crear/actualizar Paciente con género y teléfono
            try:
                Paciente.objects.update_or_create(
                    user=user,
                    defaults={
                        "telefono": self.cleaned_data.get("telefono") or "",
                        "genero": self.cleaned_data.get("genero") or "",
                    },
                )
            except Exception:
                # si tu modelo Paciente no tiene esos campos, ignora
                pass
        return user


# =========================
#  Perfil de Usuario
# =========================
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control"})


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ("telefono",)
        widgets = {
            "telefono": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "+56 9 1234 5678"}
            ),
        }


# =========================
#  Citas
# =========================
class CitaForm(forms.ModelForm):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all().order_by("nombre"),
        required=True,
        label="Especialidad",
        widget=forms.Select(
            attrs={"class": "form-select", "id": "id_especialidad"}),
    )
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.none(),
        required=True,
        label="Médico",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_medico"}),
    )
    fecha = forms.DateField(
        required=True,
        label="Fecha",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control", "id": "id_fecha"}),
    )
    hora = forms.TimeField(
        required=True,
        label="Hora",
        widget=forms.TimeInput(
            attrs={"type": "time", "class": "form-control", "id": "id_hora"}),
    )
    motivo = forms.CharField(
        required=False,
        label="Motivo",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3,
                   "placeholder": "Describe brevemente tu motivo"}
        ),
    )

    class Meta:
        model = Cita
        fields = ["especialidad", "medico", "fecha", "hora", "motivo"]

    def __init__(self, *args, **kwargs):
        self.paciente = kwargs.pop("paciente", None)
        super().__init__(*args, **kwargs)

        esp_id = None
        if self.is_bound:
            esp_id = (self.data.get(self.add_prefix("especialidad"))
                      or self.data.get("especialidad"))
        if not esp_id and isinstance(self.initial, dict):
            esp_id = self.initial.get("especialidad")
        if not esp_id and getattr(self.instance, "pk", None) and getattr(self.instance, "medico_id", None):
            esp_id = self.instance.medico.especialidad_id

        try:
            if esp_id:
                self.fields["medico"].queryset = Medico.objects.filter(
                    especialidad_id=int(esp_id)).order_by("nombre")
            else:
                self.fields["medico"].queryset = Medico.objects.select_related(
                    "especialidad").order_by("nombre")
        except (TypeError, ValueError):
            self.fields["medico"].queryset = Medico.objects.none()

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if not fecha:
            return fecha
        hoy = timezone.localdate()
        if fecha < hoy:
            raise forms.ValidationError("La fecha no puede ser pasada.")
        if fecha.weekday() >= 5:
            raise forms.ValidationError("No se atiende sábados ni domingos.")
        return fecha

    def clean_hora(self):
        hora = self.cleaned_data.get("hora")
        if not hora:
            return hora
        inicio, fin = time(9, 0), time(18, 0)
        if not (inicio <= hora <= fin):
            raise forms.ValidationError(
                "La hora debe estar entre 09:00 y 18:00.")
        return hora

    def clean(self):
        cleaned = super().clean()
        medico = cleaned.get("medico")
        fecha = cleaned.get("fecha")
        hora = cleaned.get("hora")
        if not (medico and fecha and hora):
            return cleaned

        now = timezone.localtime()
        if fecha == now.date() and hora <= now.time():
            self.add_error("hora", "La hora seleccionada ya pasó.")

        qs = Cita.objects.filter(medico=medico, fecha=fecha, hora=hora)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            self.add_error(
                "hora", "Esta hora ya está reservada para el médico seleccionado.")
        return cleaned

    def save(self, commit=True):
        cita = super().save(commit=False)
        if self.paciente and not cita.paciente_id:
            cita.paciente = self.paciente
        if commit:
            cita.save()
        return cita
