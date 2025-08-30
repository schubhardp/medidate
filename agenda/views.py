from __future__ import annotations
from datetime import date, time, datetime, timedelta
from typing import List

from django import forms
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CitaForm, UserUpdateForm, PacienteForm, RegistroForm
from .models import Cita, Paciente, Medico, Especialidad


# -------------------------------------------------------------------
# Guards / helpers de rol
# -------------------------------------------------------------------

def _es_paciente(user):
    return user.is_authenticated and Paciente.objects.filter(user=user).exists()


def patient_required(view_func):
    """Permite acceso solo a usuarios que son pacientes."""
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _es_paciente(request.user):
            messages.info(
                request, "Solo los pacientes pueden acceder a esta sección.")
            if request.user.has_perm("agenda.access_consultorio"):
                return redirect("agenda:consultorio_citas")
            return redirect("agenda:inicio")
        return view_func(request, *args, **kwargs)
    return _wrapped


def _get_or_create_paciente_for_user(request: HttpRequest) -> Paciente:
    paciente, _ = Paciente.objects.get_or_create(user=request.user)
    return paciente


# -------------------------------------------------------------------
# Páginas
# -------------------------------------------------------------------

def inicio(request):
    ctx = {}
    hoy = timezone.localdate()
    ahora = timezone.localtime().time()

    if request.user.is_authenticated:
        # Si tiene permiso de consultorio -> panel staff
        if request.user.has_perm("agenda.access_consultorio"):
            semana_fin = hoy + timedelta(days=7)
            ctx["kpis_staff"] = {
                "hoy": Cita.objects.filter(fecha=hoy).count(),
                "semana": Cita.objects.filter(fecha__range=(hoy, semana_fin)).count(),
                "canceladas_hoy": Cita.objects.filter(fecha=hoy, estado="cancelada").count(),
            }
            ctx["citas_hoy"] = (
                Cita.objects
                .select_related("paciente__user", "medico", "medico__especialidad")
                .filter(fecha=hoy)
                .order_by("hora")[:5]
            )
        else:
            # Panel paciente: SOLO próximas (hoy desde ahora o futuras)
            paciente = Paciente.objects.filter(user=request.user).first()
            if paciente:
                proximas_qs = (
                    Cita.objects.filter(
                        paciente=paciente,
                        estado__in=["pendiente", "agendada"],
                    )
                    .filter(Q(fecha__gt=hoy) | (Q(fecha=hoy) & Q(hora__gte=ahora)))
                )

                ctx["proximas_count"] = proximas_qs.count()
                ctx["proxima_cita"] = (
                    proximas_qs
                    .select_related("medico", "medico__especialidad")
                    .order_by("fecha", "hora")
                    .first()
                )

    return render(request, "inicio.html", ctx)


@patient_required
def perfil(request: HttpRequest) -> HttpResponse:
    paciente = _get_or_create_paciente_for_user(request)

    now = timezone.localtime()         # fecha y hora local
    hoy = now.date()
    hora_actual = now.time()

    # Próximas: hoy con hora >= actual, o cualquier fecha futura.
    # Excluimos canceladas y atendidas.
    proximas = (
        Cita.objects.filter(paciente=paciente)
        .exclude(estado__in=["cancelada", "atendida"])
        .filter(
            Q(fecha__gt=hoy) |
            Q(fecha=hoy, hora__gte=hora_actual)
        )
        .select_related("medico", "medico__especialidad")
        .order_by("fecha", "hora")
    )

    # Historial: fechas pasadas, o de hoy con hora < actual,
    # además de cualquier cita cancelada o atendida (sin importar fecha).
    historial = (
        Cita.objects.filter(paciente=paciente)
        .filter(
            Q(fecha__lt=hoy) |
            Q(fecha=hoy, hora__lt=hora_actual) |
            Q(estado__in=["cancelada", "atendida"])
        )
        .select_related("medico", "medico__especialidad")
        .order_by("-fecha", "-hora")
    )

    ctx = {"paciente": paciente, "proximas": proximas, "historial": historial}
    return render(request, "agenda/perfil.html", ctx)


@patient_required
def perfil_editar(request: HttpRequest) -> HttpResponse:
    paciente = _get_or_create_paciente_for_user(request)

    if request.method == "POST":
        f_user = UserUpdateForm(request.POST, instance=request.user)
        f_pac = PacienteForm(request.POST, instance=paciente)
        if f_user.is_valid() and f_pac.is_valid():
            f_user.save()
            f_pac.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("agenda:perfil")
    else:
        f_user = UserUpdateForm(instance=request.user)
        f_pac = PacienteForm(instance=paciente)

    return render(request, "agenda/perfil_editar.html", {"form_user": f_user, "form_paciente": f_pac})


@patient_required
def agendar(request: HttpRequest) -> HttpResponse:
    paciente = _get_or_create_paciente_for_user(request)

    if request.method == "POST":
        form = CitaForm(request.POST, paciente=paciente)
        medicos_qs = Medico.objects.none()
        esp_id = request.POST.get("especialidad")
        if esp_id and esp_id.isdigit():
            medicos_qs = Medico.objects.filter(
                especialidad_id=esp_id).order_by("nombre")
    else:
        form = CitaForm(paciente=paciente)
        medicos_qs = Medico.objects.none()

    especialidades_qs = Especialidad.objects.all().order_by("nombre")

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "¡Cita agendada con éxito!")
        return redirect("agenda:perfil")

    ctx = {"form": form, "especialidades": especialidades_qs, "medicos": medicos_qs}
    return render(request, "agenda/agendar_cita.html", ctx)


# -------------------------------------------------------------------
# Consultorio (login + permiso específico)
# -------------------------------------------------------------------

@login_required(login_url="login")
@permission_required("agenda.access_consultorio", raise_exception=True)
def consultorio_citas(request: HttpRequest) -> HttpResponse:
    """
    Si no estás logueado: /accounts/login/?next=/consultorio/
    Si estás logueado sin permiso: 403
    """
    qs = (
        Cita.objects
        .select_related("paciente__user", "medico", "medico__especialidad")
        .all()
        .order_by("fecha", "hora")
    )

    # Filtros
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(paciente__user__first_name__icontains=q) |
            Q(paciente__user__last_name__icontains=q) |
            Q(paciente__user__email__icontains=q)
        )

    estado = (request.GET.get("estado") or "").strip()
    if estado:
        qs = qs.filter(estado=estado)

    esp_id = (request.GET.get("especialidad") or "").strip()
    if esp_id.isdigit():
        qs = qs.filter(medico__especialidad_id=int(esp_id))

    medico_id = (request.GET.get("medico") or "").strip()
    if medico_id.isdigit():
        qs = qs.filter(medico_id=int(medico_id))

    f_desde = parse_date(request.GET.get("desde") or "")
    f_hasta = parse_date(request.GET.get("hasta") or "")
    if f_desde:
        qs = qs.filter(fecha__gte=f_desde)
    if f_hasta:
        qs = qs.filter(fecha__lte=f_hasta)

    page_obj = Paginator(qs, 20).get_page(request.GET.get("page"))

    especialidades = Especialidad.objects.all().order_by("nombre")
    medicos = (
        Medico.objects.filter(especialidad_id=int(esp_id)).order_by("nombre")
        if esp_id.isdigit() else Medico.objects.all().order_by("nombre")
    )
    ESTADOS = [("", "Todos")] + list(Cita.ESTADO)

    ctx = {
        "page_obj": page_obj,
        "especialidades": especialidades,
        "medicos": medicos,
        "ESTADOS": ESTADOS,
        "f": {
            "q": q,
            "estado": estado,
            "especialidad": esp_id,
            "medico": medico_id,
            "desde": request.GET.get("desde") or "",
            "hasta": request.GET.get("hasta") or "",
        },
    }
    return render(request, "agenda/consultorio_citas.html", ctx)


# -------------------------------------------------------------------
# AJAX
# -------------------------------------------------------------------

@login_required
def ajax_medicos(request: HttpRequest) -> JsonResponse:
    esp_id = request.GET.get("especialidad")
    items: List[dict] = []
    if esp_id and esp_id.isdigit():
        items = list(
            Medico.objects.filter(especialidad_id=esp_id)
            .order_by("nombre")
            .values("id", "nombre")
        )
    return JsonResponse({"items": items})


@login_required
def ajax_horas(request: HttpRequest) -> JsonResponse:
    med_id = request.GET.get("medico")
    fecha_str = request.GET.get("fecha")

    if not (med_id and fecha_str):
        return JsonResponse({"items": []})

    try:
        med_id_int = int(med_id)
    except ValueError:
        return JsonResponse({"items": []})

    try:
        y, m, d = [int(x) for x in fecha_str.split("-")]
        f = date(y, m, d)
    except Exception:
        return JsonResponse({"items": []})

    base_slots = [time(h, mm) for h in range(9, 17) for mm in (0, 30)]
    ocupadas_qs = Cita.objects.filter(
        medico_id=med_id_int, fecha=f).values_list("hora", flat=True)
    ocupadas = {t.strftime("%H:%M") for t in ocupadas_qs}
    libres = [t.strftime("%H:%M")
              for t in base_slots if t.strftime("%H:%M") not in ocupadas]
    return JsonResponse({"items": libres})


# -------------------------------------------------------------------
# Acciones sobre Citas (paciente)
# -------------------------------------------------------------------

@login_required
def cita_cancelar(request: HttpRequest, cita_id: int) -> HttpResponse:
    cita = get_object_or_404(
        Cita.objects.select_related("paciente"),
        pk=cita_id,
        paciente__user=request.user,
    )
    if request.method != "POST":
        raise Http404()
    cita.estado = "cancelada"
    cita.save(update_fields=["estado"])
    messages.success(request, "Cita cancelada.")
    return redirect("agenda:perfil")


# -------------------------------------------------------------------
# Info / Errores
# -------------------------------------------------------------------

def politica_cookies(request: HttpRequest) -> HttpResponse:
    return render(request, "politica_cookies.html")


def error_404(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def error_500(request: HttpRequest) -> HttpResponse:
    return render(request, "500.html", status=500)


def error_403(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, "403.html", status=403)


# -------------------------------------------------------------------
# Registro
# -------------------------------------------------------------------

def registro(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Tu cuenta fue creada correctamente. Ahora puedes iniciar sesión.")
            return redirect("login")
    else:
        form = RegistroForm()
    return render(request, "registration/registro.html", {"form": form})


# -------------------------------------------------------------------
# Acciones de consultorio (staff)
# -------------------------------------------------------------------

@permission_required('agenda.access_consultorio')
@require_POST
def consultorio_cita_cancelar(request: HttpRequest, cita_id: int) -> HttpResponse:
    cita = get_object_or_404(Cita, id=cita_id)
    if not cita.cancelar(request.user, motivo=request.POST.get('motivo', '')):
        if cita.estado == 'cancelada':
            messages.info(request, "La cita ya estaba cancelada.")
        else:
            messages.warning(
                request, "No es posible cancelar una cita pasada.")
    else:
        messages.success(
            request,
            f"Cita cancelada: {cita.paciente.user.get_full_name() or cita.paciente.user.email} · "
            f"{cita.fecha} {cita.hora.strftime('%H:%M')}"
        )
    return redirect(request.POST.get('next') or 'agenda:consultorio_citas')


def sobre(request):
    return render(request, "sobre.html")
