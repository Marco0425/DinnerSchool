# Imports de Django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from comedor.models import Ingredientes

# Imports del core
from .models import *


def index(request):
    return HttpResponse("Hello, world. You're at the core index.")

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
        if request.user.is_staff:
            return render(request, 'Login/siginup.html', {'is_staff': request.user.is_staff})
        else:
            return redirect(reverse('core:dashboard'))
    else:
        # Funcion para manejar el registro de usuarios
        if request.method == "POST":
            username = request.POST.get("username")
            userlastname = request.POST.get("userlastname")
            userlastname2 = request.POST.get("userlastname2")
            useremail = request.POST.get("useremail")
            registerPassword = request.POST.get("password")
            confirmPassword = request.POST.get("confirmPassword")
            userType = request.POST.get("userType")

            user = User.objects.create_user(
                username=useremail,
                email=useremail,
                password=registerPassword,
                first_name=username,
                last_name=f"{userlastname} {userlastname2}"
            )

            user.set_password(registerPassword)  # Asegurarse de que la contraseña esté encriptada

            group = Group.objects.get(name=userType) if userType else Group.objects.get(pk=2)
            user.groups.add(group)
            user.save()
            
            usuario = Usuarios.objects.create(
                user=user,
                groupId=group,
                email=useremail,
                nombre=username,
                paterno=userlastname,
                materno=userlastname2,
            )
            print(f"Usuario creado: {useremail}, {registerPassword}")
            userAuth = authenticate(request, username=useremail, password=registerPassword)
            print(f"Usuario autenticado: {userAuth}")
            if userAuth is not None:
                login(request, userAuth)
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Credenciales inválidas')
                return render(request, 'Login/siginup.html')

        elif request.method == "GET":
            correo = request.GET.get("username")
            contrasena = request.GET.get("password")

            user = authenticate(request, username=correo, password=contrasena)
            if user is not None:
                login(request, user)
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Credenciales inválidas')
                return render(request, 'Login/siginup.html')

        return render(request, 'Login/signup.html')

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
        context = {
            'user': request.user,
            'is_tutor': request.user.groups.filter(name='Tutor').exists(),
            'is_employee': request.user.groups.filter(name='Employee').exists(),
        }
        return render(request, 'HOME/home_dashboard_view.html', context)
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
        return render(request, 'Ingredients/ingredients_list_view.html', {'ingredientes': ingredients})
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
        return render(request, 'Saucer/saucer_list_view.html', {'saucers': saucers})
    else:
        return redirect('core:signInUp')
    
def order(request):
    """
    Vista para manejar los pedidos.
    Esta vista se encarga de mostrar y gestionar los pedidos realizados por los estudiantes.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de pedidos.
    """
    if request.user.is_authenticated:
        return render(request, 'orders/orders_kanban_view.html')
    else:
        return redirect('core:signInUp')

def employee(request):
    """
    Vista para manejar los empleados.
    Esta vista se encarga de mostrar y gestionar los empleados registrados.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de empleados.
    """
    if request.user.is_authenticated:
        return render(request, 'employees/employees_list_view.html')
    else:
        return redirect('core:signInUp')

def education_level(request):
    """
    Vista para manejar los niveles educativos.
    Esta vista se encarga de mostrar y gestionar los niveles educativos disponibles.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de niveles educativos.
    """
    if request.user.is_authenticated:
        return render(request, 'educational_levels/level_list_view.html')
    else:
        return redirect('core:signInUp')
    
def credit(request):
    """
    Vista para manejar los créditos.
    Esta vista se encarga de mostrar y gestionar los créditos disponibles.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de créditos.
    """
    if request.user.is_authenticated:
        return render(request, 'credit/credit_list_view.html')
    else:
        return redirect('core:signInUp')

def ads(request):
    """
    Vista para manejar los anuncios.
    Esta vista se encarga de mostrar y gestionar los anuncios disponibles.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de anuncios.
    """
    if request.user.is_authenticated:
        return render(request, 'ads/ads_list_view.html')
    else:
        return redirect('core:signInUp')
