# Imports de Django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from comedor.models import Ingredientes, Noticias
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_POST
from django.apps import apps
from .choices import *
from .herramientas import getChoiceLabel

# Imports del core
from .models import *

# Vista genérica para eliminar
@require_POST
def bulk_delete(request, model_name, redirect_url):
    if not request.user.is_authenticated:
        return redirect('core:signInUp')
    ids = request.POST.getlist('selected_ids')
    # Mapeo de modelos a sus respectivas apps
    # Mapeo de nombres de modelo a (app_label, model_class_name)
    model_map = {
        'ingredientes': ('comedor', 'Ingredientes'),
        'saucers': ('comedor', 'Platillo'),
        'ads': ('comedor', 'Noticias'),
        'users': ('core', 'Usuarios'),
        'tutors': ('core', 'Tutor'),
        'students': ('core', 'students'),
        'employees': ('core', 'Empleados'),
        'education_levels': ('core', 'NivelEducativo'),
    }
    app_label, model_class_name = model_map.get(model_name.lower(), ('core', model_name.capitalize()))
    try:
        Model = apps.get_model(app_label, model_class_name)
    except LookupError:
        return redirect(redirect_url)
    # Filtrar valores vacíos
    valid_ids = [i for i in ids if i.strip()]
    if valid_ids:
        Model.objects.filter(id__in=valid_ids).delete()
    return redirect(redirect_url)

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
            'is_admin': request.user.is_staff,
            'noticias': Noticias.objects.filter(activo=True),
        }
        return render(request, 'HOME/home_dashboard_view.html', context)
    else:
        return redirect('core:signInUp')  # Redirigir a la página de inicio de sesión/registro si no está autenticado

def students(request):
    """
    Vista para manejar los estudiantes.
    Esta vista se encarga de mostrar y gestionar los estudiantes registrados.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la lista de estudiantes.
    """
    if not request.user.is_authenticated:
        return redirect('core:signInUp')

    if request.user.is_staff:
        students = Alumnos.objects.all()
        return render(request, 'students/students_list_view.html', {'students': students})

    try:
        usuario = Usuarios.objects.get(user=request.user)
        tutor = Tutor.objects.get(usuario=usuario)
        students = Alumnos.objects.filter(tutorId=tutor)
    except (Usuarios.DoesNotExist, Tutor.DoesNotExist):
        messages.warning(request, 'No se encontró un tutor asociado a este usuario.')
        return render(request, 'students/students_form_view.html')

    studentsTutor = []
    for student in students:
        studentsTutor.append({
            'id': student.id,
            'nombre': student.nombre,
            'paterno': student.paterno,
            'materno': student.materno,
            'nivel': getChoiceLabel(NIVELEDUCATIVO, student.nivelEducativo.nivel),
            'grupo': getChoiceLabel(GRUPO, student.nivelEducativo.grupo),
            'grado': getChoiceLabel(GRADO, student.nivelEducativo.grado)
        })

    if studentsTutor:
        return render(request, 'students/students_list_view.html', {'students': studentsTutor})
    else:
        messages.warning(request, 'No se encontraron estudiantes.')
        return render(request, 'students/students_form_view.html')

def createStudents(request):
    """
    Vista para crear un nuevo estudiante.
    Esta vista se encarga de manejar la creación de un nuevo estudiante.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige a la lista de estudiantes.
    """
    if request.method == "POST":
        print("Datos recibidos del formulario:", request.POST)
        nombre = request.POST.get("nombre")
        paterno = request.POST.get("apellidoPaterno")
        materno = request.POST.get("apellidoMaterno")
        tutorId = request.user
        grado = request.POST.get("grado")
        grupo = request.POST.get("grupo")
        nivelEducativo = request.POST.get("nivelEducativo")

        nivelEducativoAlumno = NivelEducativo.objects.get(
            nivel=int(nivelEducativo),
            grado=int(grado),
            grupo=int(grupo)
        )

        if not nivelEducativoAlumno:
            messages.error(request, 'Nivel educativo no válido.')
            return render(request, 'students/students_form_view.html')

        try:
            tutor = Tutor.objects.get(usuario=Usuarios.objects.get(user=tutorId))
            Alumno = Alumnos.objects.create(
                nombre=nombre,
                paterno=paterno,
                materno=materno,
                tutorId=tutor,
                nivelEducativo=nivelEducativoAlumno
            )
            print(f"Alumno creado: {Alumno.nombre}, Tutor: {tutor.usuario.nombre}")
            messages.success(request, 'Estudiante creado exitosamente.')
            return redirect('core:students')
        except Tutor.DoesNotExist:
            messages.error(request, 'Tutor no encontrado.')
            return render(request, 'students/students_form_view.html')
    else:
        return render(request, 'students/students_form_view.html')

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

def user_list_view(request):
    """
    Vista para manejar la lista de usuarios.
    Esta vista se encarga de mostrar y gestionar los usuarios registrados en el sistema.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:    
        HttpResponse: Respuesta HTTP que renderiza la lista de usuarios.
    """
    if request.user.is_authenticated:
        users = User.objects.filter(groups__name__in = ['Employee','Tutor'])
        return render(request, 'Users/users_list_view.html', {'users': users})
    else:
        return redirect('core:signInUp')
    
def account_settings_form_view(request):
    """
    Vista para manejar los ajustes de cuenta del usuario.
    Esta vista se encarga de mostrar y gestionar los ajustes de cuenta del usuario autenticado.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza el formulario de ajustes de cuenta.
    """
    if request.user.is_authenticated:
        user = request.user
        if request.method == "POST":
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.email = request.POST.get("email", user.email)
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password and new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Ajustes de cuenta actualizados exitosamente.')
                return redirect('core:account_settings')
            else:
                messages.error(request, 'Las contraseñas no coinciden o están vacías.')
        return render(request, 'account_settings/account_settings_form_view.html', {'user': user})
    else:
        return redirect('core:signInUp')
            
