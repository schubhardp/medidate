# agenda/urls.py
from django.urls import path
from django.views.generic.base import RedirectView
from . import views

app_name = "agenda"

urlpatterns = [
    # Inicio
    path("", views.inicio, name="inicio"),

    # Perfil
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/editar/", views.perfil_editar, name="perfil_editar"),

    # Agendar (dos nombres por compatibilidad con plantillas antiguas)
    path("agendar/", views.agendar, name="agendar_cita"),
    path("agendar/", views.agendar, name="agendar"),

    # 👉 Panel de staff (consultorio)
    path("consultorio/", views.consultorio_citas, name="consultorio_citas"),
    path('consultorio/citas/<int:cita_id>/cancelar/', views.consultorio_cita_cancelar,
         name='consultorio_cita_cancelar'),

    # AJAX
    path("ajax/medicos/", views.ajax_medicos, name="ajax_medicos"),
    path("ajax/horas/", views.ajax_horas, name="ajax_horas"),

    # Acciones de cita
    path("cita/<int:cita_id>/cancelar/",
         views.cita_cancelar, name="cita_cancelar"),

    # Info
    path("politica-cookies/", views.politica_cookies, name="politica_cookies"),

    # Registro
    path("registro/", views.registro, name="registro"),

    # Compatibilidad: 'agenda:login' → redirige al login real ('login')
    path("login/", RedirectView.as_view(pattern_name="login"), name="login"),

    # Sobre
    path("sobre/", views.sobre, name="sobre"),
]
