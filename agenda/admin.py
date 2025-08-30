from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Paciente, Especialidad, Medico, Cita


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': (
            'email', 'password1', 'password2')}),
    )
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('last_login', 'date_joined',)
    exclude = ('username',)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'fecha_nacimiento', 'genero')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad')
    list_filter = ('especialidad',)
    search_fields = ('nombre',)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'paciente', 'medico', 'estado')
    list_filter = ('estado', 'medico__especialidad', 'medico', 'fecha')
    search_fields = (
        'paciente__user__email',
        'paciente__user__first_name',
        'paciente__user__last_name',
        'medico__nombre',
    )
    ordering = ('-fecha', '-hora')
    date_hierarchy = 'fecha'
