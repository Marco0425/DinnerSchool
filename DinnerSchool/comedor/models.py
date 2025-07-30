from django.db import models

from .choices import *
from core.models import Tutor, Alumnos, NivelEducativo    

# Create your models here.
class Credito(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tutorId = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.monto}"
    
class Ingredientes(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Platillo(models.Model):
    nombre = models.CharField(max_length=100)
    ingredientes = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
    
class Pedido(models.Model):
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE)
    nota = models.TextField(max_length=50, blank=True, null=True)
    alumnoId = models.ForeignKey(Alumnos, on_delete=models.CASCADE)
    nivelEducativo = models.ForeignKey(NivelEducativo, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now=True)
    status = models.PositiveIntegerField(choices=STATUSPEDIDO, default=0)
    turno = models.PositiveIntegerField(choices=TURNO, default=0)

    def __str__(self):
        return f"{self.fecha} - {self.monto}"
    
class CreditoDiario(models.Model):
    fecha = models.DateField(auto_now=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tutorId = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.fecha} - {self.monto}"