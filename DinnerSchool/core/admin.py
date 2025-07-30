from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Usuarios)
admin.site.register(NivelEducativo)
admin.site.register(Alumnos)
admin.site.register(Tutor)
admin.site.register(Empleados)