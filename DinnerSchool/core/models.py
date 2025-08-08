from django.db import models

from django.contrib.auth.models import Group, User
from .choices import *

# Create your models here.
class Usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    nombre = models.CharField(max_length=100)
    paterno = models.CharField(max_length=100)
    materno = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    groupId = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Empleados(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    puesto = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.nombre
    
class Tutor(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    parentesco = models.CharField(max_length=50)

    def __str__(self):
        return self.usuario.nombre

class NivelEducativo(models.Model):
    nivel = models.PositiveIntegerField(choices=NIVELEDUCATIVO, default=1)
    grado = models.PositiveIntegerField(choices=GRADO, default=1)
    grupo = models.PositiveIntegerField(choices=GRUPO, default=1)

    def __str__(self):
        return str(self.nivel)

class Alumnos(models.Model):
    nombre = models.CharField(max_length=100)
    paterno = models.CharField(max_length=100)
    materno = models.CharField(max_length=100)
    tutorId = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    nivelEducativo = models.ForeignKey(NivelEducativo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} {self.paterno} {self.materno}"
