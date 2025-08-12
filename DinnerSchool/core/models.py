from django.db import models

from django.contrib.auth.models import Group, User
from .choices import *

# Create your models here.
class Usuarios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    paterno = models.CharField(max_length=100, verbose_name='Apellido Paterno')
    materno = models.CharField(max_length=100, verbose_name='Apellido Materno')
    email = models.EmailField(verbose_name='Email')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    groupId = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name_plural = 'Usuarios'
        verbose_name = 'Usuario'

    def __str__(self):
        return self.nombre
    
class Empleados(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, verbose_name='Usuario')
    puesto = models.CharField(max_length=100, verbose_name='Puesto')

    class Meta:
        verbose_name_plural = 'Empleados'
        verbose_name = 'Empleado'

    def __str__(self):
        return self.usuario.nombre
    
class Tutor(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, verbose_name='Usuario')
    parentesco = models.CharField(max_length=50, verbose_name='Parentesco')

    class Meta:
        verbose_name_plural = 'Tutores'
        verbose_name = 'Tutor'

    def __str__(self):
        return self.usuario.nombre

class NivelEducativo(models.Model):
    nivel = models.PositiveIntegerField(choices=NIVELEDUCATIVO, default=1, verbose_name='Nivel')
    grado = models.PositiveIntegerField(choices=GRADO, default=1, verbose_name='Grado')
    grupo = models.PositiveIntegerField(choices=GRUPO, default=1, verbose_name='Grupo')

    class Meta:
        verbose_name_plural = 'Niveles Educativos'
        verbose_name = 'Nivel Educativo'

    def __str__(self):
        return str(self.nivel)

class Alumnos(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    paterno = models.CharField(max_length=100, verbose_name='Apellido Paterno')
    materno = models.CharField(max_length=100, verbose_name='Apellido Materno')
    tutorId = models.ForeignKey(Tutor, on_delete=models.CASCADE, verbose_name='Tutor')
    nivelEducativo = models.ForeignKey(NivelEducativo, on_delete=models.CASCADE, verbose_name='Nivel educativo')

    class Meta:
        verbose_name_plural = 'Alumnos'
        verbose_name = 'Alumno'

    def __str__(self):
        return f"{self.nombre} {self.paterno} {self.materno}"
