from django.db import models
from cloudinary.models import CloudinaryField

from .choices import *
from core.models import Tutor, Alumnos, NivelEducativo, Usuarios, Empleados
from .choices import STATUSPEDIDO, TURNO, TIPOANUNCIO

# Create your models here.
class Credito(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    tutorId = models.OneToOneField(Tutor, on_delete=models.CASCADE, unique=True, verbose_name='Tutor', null=True, blank=True)
    profesorId = models.OneToOneField(Empleados, on_delete=models.CASCADE, unique=True, verbose_name='Profesor', null=True, blank=True)
    fecha = models.DateField(verbose_name='Fecha')
    
    class Meta:
        verbose_name = 'Crédito'
        verbose_name_plural = 'Créditos'

    def __str__(self):
        return f"{self.monto}"
    
class Ingredientes(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')

    class Meta:
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'

    def __str__(self):
        return self.nombre
    
class Platillo(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    ingredientes = models.CharField(max_length=200, verbose_name='Ingredientes')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    disponible = models.BooleanField(default=True, verbose_name='Disponible')
    class Meta:
        verbose_name = 'Platillo'
        verbose_name_plural = 'Platillos'

    def __str__(self):
        return self.nombre
    
class Pedido(models.Model):
    platillo = models.ForeignKey(Platillo, on_delete=models.PROTECT, verbose_name='Platillo')
    ingredientePlatillo = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Ingredientes del Platillo')
    nota = models.TextField(max_length=300, blank=True, null=True, verbose_name='Nota')
    alumnoId = models.ForeignKey(Alumnos, on_delete=models.CASCADE, verbose_name='Alumno', null=True, blank=True)
    profesorId = models.ForeignKey(Empleados, on_delete=models.CASCADE, verbose_name='Profesor', null=True, blank=True, related_name='profesor_pedidos')
    nivelEducativo = models.ForeignKey(NivelEducativo, on_delete=models.CASCADE, verbose_name='Nivel Educativo', null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total')
    fecha = models.DateField(verbose_name='Fecha')  # Removido auto_now=True
    status = models.PositiveIntegerField(choices=STATUSPEDIDO, default=0, verbose_name='Estado del Pedido')
    turno = models.PositiveIntegerField(choices=TURNO, default=0, verbose_name='Turno')
    encargadoId = models.ForeignKey(Empleados, on_delete=models.CASCADE, verbose_name='Encargado', null=True, blank=True, related_name='encargado_pedidos')
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    creado = models.DateTimeField(auto_now=True, verbose_name='Fecha de Creación')

    def get_status_label(self):
        """Devuelve la etiqueta legible del estado del pedido."""
        return dict(STATUSPEDIDO).get(self.status)

    def get_turno_label(self):
        """Devuelve la etiqueta legible del turno."""
        return dict(TURNO).get(self.turno)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"{self.fecha} - {self.total}"
    
class CreditoDiario(models.Model):
    fecha = models.DateField(verbose_name='Fecha')
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    tutorId = models.ForeignKey(Tutor, on_delete=models.CASCADE, verbose_name='Tutor', null=True, blank=True)
    profesorId = models.ForeignKey(Empleados, on_delete=models.CASCADE, verbose_name='Profesor', null=True, blank=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, default=None, null=True, blank=True, verbose_name='Pedido')

    class Meta:
        verbose_name = 'Crédito Diario'
        verbose_name_plural = 'Créditos Diarios'

    def __str__(self):
        return f"{self.fecha} - {self.monto}"
    
class Noticias(models.Model):
    titulo = models.CharField(max_length=100, verbose_name='Título')
    contenido = models.TextField(verbose_name='Contenido')
    tipoAnuncio = models.PositiveSmallIntegerField(choices=TIPOANUNCIO, default=1, verbose_name='Tipo de Anuncio')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    rutaImagen = CloudinaryField(
        'imagen',
        folder='noticias/',  # Organiza en carpetas
        null=True,
        blank=True,
        transformation={
            'quality': 'auto',  # Optimización automática
            'fetch_format': 'auto',  # Formato automático (WebP cuando sea posible)
            'width': 800,  # Ancho máximo
            'height': 600,  # Alto máximo
            'crop': 'limit'  # No cortar, solo redimensionar
        }
    )
    autor = models.ForeignKey(Usuarios, on_delete=models.CASCADE, verbose_name='Autor')
    fecha = models.DateField(auto_now=True, verbose_name='Fecha')
    
    def get_imagen_url(self):
        """Retorna la URL de la imagen o None si no existe"""
        if self.rutaImagen:
            return self.rutaImagen.url
        return None
    
    def get_imagen_thumbnail(self, width=200, height=150):
        """Retorna una URL de thumbnail de la imagen"""
        if self.rutaImagen:
            from cloudinary import CloudinaryImage
            return CloudinaryImage(str(self.rutaImagen)).build_url(
                width=width,
                height=height,
                crop='fill',
                quality='auto',
                fetch_format='auto'
            )
        return None

    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'

    def __str__(self):
        return self.titulo