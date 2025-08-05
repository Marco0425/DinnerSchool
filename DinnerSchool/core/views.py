# Imports de Django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from comedor.models import Ingredientes

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
    if request.user.is_authenticated:
        # Si el usuario ya está autenticado, redirigir a la página de dashboard
        # Aquí podrías redirigir a una página de dashboard o inicio
        return redirect(reverse('core:dashboard'))
    else:
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

        return render(request, 'Login/siginup.html')

def dashboard(request):
    """
    Vista para el dashboard del usuario autenticado.
    Esta vista muestra información relevante al usuario que ha iniciado sesión.
    
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza el dashboard del usuario.
    """
    if request.user.is_authenticated:
        # Aquí podrías obtener información del usuario y pasarla al template
        return render(request, 'HOME/home_dashboard_view.html', {'user': request.user})
    else:
        return redirect('core:signInUp')  # Redirigir a la página de inicio de sesión/registro si no está autenticado
    
def ingredients(request):
    """
    Vista para manejar los ingredientes.
    Esta vista se encarga de mostrar y gestionar los ingredientes disponibles.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de ingredientes.
    """
    if request.user.is_authenticated:
        # Aquí podrías obtener los ingredientes y pasarlos al template
        ingredients = Ingredientes.objects.all()
        return render(request, 'ingredients/ingredients_list_view.html', {'ingredientes': ingredients})
    else:
        return redirect('core:signInUp')

def students(request):
    """
    Vista para manejar los estudiantes.
    Esta vista se encarga de mostrar y gestionar los estudiantes registrados.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de estudiantes.
    """
    if request.user.is_authenticated:
        students = Usuarios.objects.all()
        return render(request, 'students/students_list_view.html', {'students': students})
    else:
        return redirect('core:signInUp')

def saucers(request):
    """
    Vista para manejar los platillos (sauces).
    Esta vista se encarga de mostrar y gestionar los platillos disponibles.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de platillos.
    """
    if request.user.is_authenticated:
        saucers = []
        return render(request, 'saucers/saucers_list_view.html', {'saucers': saucers})
    else:
        return redirect('core:signInUp')


def logout_view(request):
    """
    Vista para manejar el cierre de sesión del usuario.
    Esta vista se encarga de cerrar la sesión del usuario autenticado.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige al usuario a la página de inicio de sesión/registro.
    """
    if request.user.is_authenticated:
        # Cerrar la sesión del usuario
        django_logout(request)
        return redirect('core:signInUp')
    else:
        return redirect('core:signInUp')  # Redirigir a la página de inicio de sesión/registro si no está autenticado