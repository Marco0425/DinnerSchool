from django.db import models

from django.contrib.auth.models import Group
from .choices import *

# Create your models here.
class Usuarios(models.Model):
    nombre = models.CharField(max_length=100)
    paterno = models.CharField(max_length=100)
    materno = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    groupId = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class NivelEducativo(models.Model):
    nivel = models.PositiveIntegerField(choices=NIVELEDUCATIVO)
    grado = models.PositiveIntegerField(choices=GRADO)

    def __str__(self):
        return str(self.nivel)