from django.contrib import admin
from django.utils.html import format_html
from .models import *

import ast

@admin.register(Credito)
class CreditoAdmin(admin.ModelAdmin):
    list_display = ('id','monto', 'nombre_tutor', 'nombre_profesor', 'fecha')
    
    def nombre_tutor(self, obj):
        return f"{obj.tutorId.usuario.nombre} {obj.tutorId.usuario.paterno} {obj.tutorId.usuario.materno}" if obj.tutorId and obj.tutorId.usuario else "-"
    
    def nombre_profesor(self, obj):
        return f"{obj.profesorId.usuario.nombre} {obj.profesorId.usuario.paterno} {obj.profesorId.usuario.materno}" if obj.profesorId and obj.profesorId.usuario else "-"
    
    search_fields = ('tutorId__usuario__nombre', 'tutorId__usuario__paterno', 'tutorId__usuario__materno')
    list_filter = ('fecha',)
    
    nombre_tutor.short_description = 'Tutor'
    nombre_profesor.short_description = 'Profesor'

@admin.register(CreditoDiario)
class CreditoDiarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'monto', 'alumno', 'nombre_tutor', 'nombre_profesor', 'pedido')
    search_fields = ('tutorId__usuario__nombre', 'tutorId__usuario__paterno', 'tutorId__usuario__materno', 'pedido__platillo__nombre')

    def nombre_tutor(self, obj):
        return f"{obj.tutorId.usuario.nombre} {obj.tutorId.usuario.paterno} {obj.tutorId.usuario.materno}" if obj.tutorId and obj.tutorId.usuario else "-"

    def nombre_profesor(self, obj):
        return f"{obj.profesorId.usuario.nombre} {obj.profesorId.usuario.paterno} {obj.profesorId.usuario.materno}" if obj.profesorId and obj.profesorId.usuario else "-"
    
    def alumno(self, obj):
        if obj.pedido and obj.pedido.alumnoId:
            return f"{obj.pedido.alumnoId.nombre} {obj.pedido.alumnoId.paterno} {obj.pedido.alumnoId.materno}"
        return "-"

    nombre_tutor.short_description = 'Tutor'
    nombre_profesor.short_description = 'Profesor'
    alumno.short_description = 'Alumno'

@admin.register(Ingredientes)
class IngredientesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre',)
    search_fields = ('nombre',)

@admin.register(Platillo)
class PlatilloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ingredientes_list', 'precio')
    search_fields = ('nombre',)
    
    def ingredientes_list(self, obj):
        if not obj.ingredientes:  # Si está vacío o None
            return "-"
        try:
            ingredientes_ids = ast.literal_eval(obj.ingredientes)
            # Convertir a nombres
            nombres = [
                Ingredientes.objects.get(id=int(ing)).nombre
                for ing in ingredientes_ids
            ]
            return ", ".join(nombres)
        except (ValueError, SyntaxError):
            return format_html('<span style="color:red;">Formato inválido</span>')

    ingredientes_list.short_description = 'Ingredientes'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'alumnoId', 'nombreTutor', 'profesorId', 'platillo', 'total', 'fecha', 'status', 'turno')
    search_fields = ('alumnoId__nombre', 'alumnoId__paterno', 'alumnoId__materno',
                     'platillo__nombre', 'profesorId__usuario__nombre', 'profesorId__usuario__paterno', 
                     'profesorId__usuario__materno','alumnoId__tutorId__usuario__nombre',
                     'alumnoId__tutorId__usuario__paterno','alumnoId__tutorId__usuario__materno',)
    list_filter = ('status', 'turno', 'fecha')

    def nombreTutor(self, obj):
        if obj.alumnoId and obj.alumnoId.tutorId:
            return f"{obj.alumnoId.tutorId.usuario.nombre} {obj.alumnoId.tutorId.usuario.paterno} {obj.alumnoId.tutorId.usuario.materno}" if obj.alumnoId.tutorId and obj.alumnoId.tutorId.usuario else "-"
        return "-"

    nombreTutor.short_description = 'Tutor'

@admin.register(Noticias)
class NoticiasAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'activo', 'fecha')
    search_fields = ('titulo', 'contenido', 'autor__nombre', 'autor__paterno', 'autor__materno')