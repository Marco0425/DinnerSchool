from django.contrib import admin
from .models import *

@admin.register(NivelEducativo)
class NivelEducativoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nivel', 'grado', 'grupo')
    search_fields = ('nivel',)
    list_filter = ('nivel',)

@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'paterno', 'email')
    search_fields = ('nombre', 'paterno', 'email')

@admin.register(Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'puesto')
    search_fields = ('usuario__username', 'usuario__last_name', 'usuario__email')
    
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario')
    search_fields = ('usuario__username', 'usuario__paterno', 'usuario__email')
    
@admin.register(Alumnos)
class AlumnosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombreCompleto', 'nivelEducativo', 'nombreTutor')
    search_fields = ('nombre', 'paterno', 'materno', 'tutorId__usuario__nombre', 'tutorId__usuario__paterno', 'tutorId__usuario__materno')

    def nombreCompleto(self, obj):
        return f"{obj.nombre} {obj.paterno} {obj.materno}"
    def nombreTutor(self, obj):
        return f"{obj.tutorId.usuario.nombre} {obj.tutorId.usuario.paterno} {obj.tutorId.usuario.materno}"
    
    nombreCompleto.short_description = 'Nombre Completo'
    nombreTutor.short_description = 'Tutor'
