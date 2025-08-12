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
    print(f"[bulk_delete] model_name recibido: {model_name}")
    print(f"[bulk_delete] redirect_url recibido: {redirect_url}")
    print(f"[bulk_delete] IDs recibidos: {ids}")
    # Mapeo de modelos a sus respectivas apps
    model_map = {
        'ingredientes': ('comedor', 'Ingredientes'),
        'saucers': ('comedor', 'Platillo'),
        'ads': ('comedor', 'Noticias'),
        'users': ('core', 'Usuarios'),
        'tutors': ('core', 'Tutor'),
        'students': ('core', 'Alumnos'),
        'employees': ('core', 'Empleados'),
        'education_levels': ('core', 'NivelEducativo'),
    }
    app_label, model_class_name = model_map.get(model_name.lower(), ('core', model_name.capitalize()))
    print(f"[bulk_delete] app_label: {app_label}, model_class_name: {model_class_name}")
    try:
        Model = apps.get_model(app_label, model_class_name)
        print(f"[bulk_delete] Modelo encontrado: {Model}")
    except LookupError:
        print(f"[bulk_delete] Modelo no encontrado para {app_label}.{model_class_name}")
        return redirect(redirect_url)
    # Filtrar valores vacíos
    valid_ids = [i for i in ids if i.strip()]
    print(f"[bulk_delete] IDs válidos: {valid_ids}")
    if valid_ids:
        if model_name.lower() == 'users':
            usuarios = Model.objects.filter(id__in=valid_ids)
            print(f"[bulk_delete] Usuarios a eliminar: {[u.id for u in usuarios]}")
            for usuario in usuarios:
                print(f"[bulk_delete] Eliminando usuario Usuarios.id={usuario.id}, User.id={usuario.user.id if usuario.user else None}")
                user_obj = usuario.user
                if user_obj and User.objects.filter(id=user_obj.id).exists():
                    print(f"[bulk_delete] Eliminando primero User.id={user_obj.id}")
                    user_obj.delete()
                usuario.delete()
        else:
            print(f"[bulk_delete] Eliminando objetos de {Model} con IDs: {valid_ids}")
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
        # Si el usuario es staff, mostrar solo el formulario de registro (sin login)
        if request.user.is_staff:
            # Si es POST, procesar registro
            print(f"[DEBUG] Método recibido: {request.method}")
            if request.method == "GET" and request.GET.get("username"):
                print("[DEBUG] Intento de registro por GET, ignorando por seguridad.")
                messages.error(request, 'El registro debe realizarse mediante POST.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
            if request.method == "POST":
                print("[DEBUG] POST recibido para registro staff")
                username = request.POST.get("username")
                userlastname = request.POST.get("userlastname")
                userlastname2 = request.POST.get("userlastname2")
                useremail = request.POST.get("useremail")
                registerPassword = request.POST.get("password")
                confirmPassword = request.POST.get("confirmPassword")
                userType = request.POST.get("userType")
                userphone = request.POST.get("userphone")
                print(f"[DEBUG] username={username}, userlastname={userlastname}, userlastname2={userlastname2}, useremail={useremail}, userType={userType}, userphone={userphone}")

                # Validación de campos obligatorios
                if not all([username, userlastname, useremail, registerPassword, confirmPassword]):
                    print("[DEBUG] Faltan campos obligatorios")
                    messages.error(request, 'Por favor, completa todos los campos obligatorios.')
                    return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
                if registerPassword != confirmPassword:
                    print("[DEBUG] Contraseñas no coinciden")
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
                if User.objects.filter(username=useremail).exists():
                    print("[DEBUG] Usuario ya existe")
                    messages.error(request, 'Ya existe un usuario con ese correo.')
                    return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

                try:
                    group = Group.objects.get(name=userType) if userType else Group.objects.get(pk=2)
                    print(f"[DEBUG] Grupo asignado: {group}")
                except Group.DoesNotExist:
                    print("[DEBUG] Tipo de usuario inválido")
                    messages.error(request, 'Tipo de usuario inválido.')
                    return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

                try:
                    user = User.objects.create_user(
                        username=useremail,
                        email=useremail,
                        password=registerPassword,
                        first_name=username,
                        last_name=f"{userlastname} {userlastname2}"
                    )
                    print(f"[DEBUG] User creado: {user}")
                    user.groups.add(group)
                    user.save()
                except Exception as e:
                    print(f"[DEBUG] Error creando User: {e}")
                    messages.error(request, f'Error creando usuario: {e}')
                    return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

                try:
                    usuario = Usuarios.objects.create(
                        user=user,
                        groupId=group,
                        email=useremail,
                        nombre=username,
                        paterno=userlastname,
                        materno=userlastname2,
                        telefono=userphone or ''
                    )
                    print(f"[DEBUG] Usuarios creado: {usuario}")
                except Exception as e:
                    print(f"[DEBUG] Error creando Usuarios: {e}")
                    messages.error(request, f'Error creando perfil de usuario: {e}')
                    return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

                print(f"[DEBUG] Usuario creado: {useremail}, {registerPassword}")
                messages.success(request, f'El usuario {useremail} ha sido creado exitosamente.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
            # GET: mostrar solo el registro
            return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
        else:
            # Si está autenticado pero no es staff, redirigir a dashboard
            return redirect(reverse('core:dashboard'))
    else:
        # No autenticado: login y registro normal
        if request.method == "POST":
            username = request.POST.get("username")
            userlastname = request.POST.get("userlastname")
            userlastname2 = request.POST.get("userlastname2")
            useremail = request.POST.get("useremail")
            registerPassword = request.POST.get("password")
            confirmPassword = request.POST.get("confirmPassword")
            userType = request.POST.get("userType")

            # Si no se especifica userType, asignar 'Tutor' por defecto
            if not userType:
                try:
                    group = Group.objects.get(name="Tutor")
                except Group.DoesNotExist:
                    messages.error(request, 'No existe el grupo Tutor. Contacta al administrador.')
                    return render(request, 'Login/siginup.html')
            else:
                try:
                    group = Group.objects.get(name=userType)
                except Group.DoesNotExist:
                    messages.error(request, 'Tipo de usuario inválido.')
                    return render(request, 'Login/siginup.html')

            user = User.objects.create_user(
                username=useremail,
                email=useremail,
                password=registerPassword,
                first_name=username,
                last_name=f"{userlastname} {userlastname2}"
            )

            user.set_password(registerPassword)
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
    alumno_id = request.GET.get('id') or request.POST.get('id')
    alumno = None
    if alumno_id:
        try:
            alumno = Alumnos.objects.get(id=alumno_id)
        except Alumnos.DoesNotExist:
            alumno = None

    context = {'alumno': alumno}
    if request.user.is_staff:
        context['tutores'] = Tutor.objects.all()
        context['is_staff'] = True

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        paterno = request.POST.get("apellidoPaterno")
        materno = request.POST.get("apellidoMaterno")
        grado = request.POST.get("grado")
        grupo = request.POST.get("grupo")
        nivelEducativo = request.POST.get("nivelEducativo")
        tutor_id = request.POST.get("tutor") if request.user.is_staff else None

        try:
            nivelEducativoAlumno = NivelEducativo.objects.get(
                nivel=int(nivelEducativo),
                grado=int(grado),
                grupo=int(grupo)
            )
        except NivelEducativo.DoesNotExist:
            nivelEducativoAlumno = None

        if not nivelEducativoAlumno:
            messages.error(request, 'Nivel educativo no válido.')
            return render(request, 'students/students_form_view.html', context)

        try:
            if request.user.is_staff:
                tutor = Tutor.objects.get(id=tutor_id) if tutor_id else None
            else:
                tutor = Tutor.objects.get(usuario=Usuarios.objects.get(user=request.user))
            if alumno:
                alumno.nombre = nombre
                alumno.paterno = paterno
                alumno.materno = materno
                alumno.nivelEducativo = nivelEducativoAlumno
                alumno.tutorId = tutor
                alumno.save()
                messages.success(request, 'Estudiante actualizado exitosamente.')
            else:
                Alumno = Alumnos.objects.create(
                    nombre=nombre,
                    paterno=paterno,
                    materno=materno,
                    tutorId=tutor,
                    nivelEducativo=nivelEducativoAlumno
                )
                messages.success(request, 'Estudiante creado exitosamente.')
            return redirect('core:students')
        except Tutor.DoesNotExist:
            messages.error(request, 'Tutor no encontrado.')
            return render(request, 'students/students_form_view.html', context)
    else:
        return render(request, 'students/students_form_view.html', context)

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
        users = Usuarios.objects.filter(groupId__name__in=["Tutor", "Employee"])
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
    if not request.user.is_authenticated:
        return redirect('core:signInUp')

    user = request.user
    try:
        usuario = Usuarios.objects.get(user=user)
    except Usuarios.DoesNotExist:
        messages.error(request, 'No existe un perfil de usuario asociado. Contacta al administrador.')
        return redirect('core:dashboard')

    if request.method == "POST":
        nombre = request.POST.get("nombre", usuario.nombre)
        paterno = request.POST.get("apellidoPaterno", usuario.paterno)
        materno = request.POST.get("apellidoMaterno", usuario.materno)
        correo = request.POST.get("correo", usuario.email)
        telefono = request.POST.get("telefono", usuario.telefono)
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        # Actualizar datos en Usuarios
        usuario.nombre = nombre
        usuario.paterno = paterno
        usuario.materno = materno
        usuario.telefono = telefono

        # Si cambia el correo, actualizar en ambos modelos
        if correo and correo != usuario.email:
            usuario.email = correo
            user.email = correo
            user.username = correo


        # Cambiar contraseña si ambas coinciden y no están vacías
        if password:
            if password == confirm_password:
                user.set_password(password)
                user.save()
                usuario.save()
                # Reautenticar y hacer login con la nueva contraseña
                user_auth = authenticate(request, username=user.username, password=password)
                if user_auth is not None:
                    login(request, user_auth)
                messages.success(request, 'Ajustes de cuenta actualizados exitosamente.')
                return redirect('core:account_settings')
            else:
                messages.error(request, 'Las contraseñas no coinciden o están vacías.')
                return render(request, 'account_settings/account_settings_form_view.html', {'usuario': usuario})

        user.save()
        usuario.save()
        messages.success(request, 'Ajustes de cuenta actualizados exitosamente.')
        return redirect('core:account_settings')

    # GET: mostrar datos actuales
    return render(request, 'account_settings/account_settings_form_view.html', {'usuario': usuario})
            
