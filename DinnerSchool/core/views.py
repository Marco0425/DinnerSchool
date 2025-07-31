# Imports de Django
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User

# Imports del core
from .models import *


def index(request):
    return HttpResponse("Hello, world. You're at the core index.")

def signInUp(request):
    """
    Vista para manejar el registro de usuarios.
    Esta vista se encarga de recibir los datos del formulario de registro,
    crear un nuevo usuario en el sistema y asignarlo al grupo correspondiente.
    
    Args:
        request: Objeto HttpRequest que contiene los datos del formulario.
    Returns:
        HttpResponse: Respuesta HTTP que indica el resultado del registro.
    """
    # Funcion para manejar el registro de usuarios
    if request.method == "POST":
        # Variables para obtener los datos del formulario
        Nombre = request.POST.get("Nombre")
        ApellidoPaterno = request.POST.get("ApellidoPaterno")
        ApellidoMaterno = request.POST.get("ApellidoMaterno")
        numeroTelefonico = request.POST.get("numeroTelefonico")
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        
        # Crear la instancia de usuario
        user = User.objects.create_user(
            username = f"{Nombre} {ApellidoPaterno} {ApellidoMaterno}",
            email = correo,
            password = contrasena
        )
        
        # Asignar el grupo correspondiente
        group = Group.objects.get(name='Tutor')
        
        # Crear el usuario personalizado
        Usuarios.objects.create(
            user = user,
            groupId = group,
            email = correo,
            telefono = numeroTelefonico,
            nombre = Nombre,
            paterno = ApellidoPaterno,
            materno = ApellidoMaterno,
        )
        
        # Aquí podrías redirigir a una página de éxito o mostrar un mensaje
        # return redirect('vista_exito')  # Usa el nombre de tu URL 'vista_exito'
        return HttpResponse("Usuario registrado exitosamente.")

    return render(request, 'siginup.html')