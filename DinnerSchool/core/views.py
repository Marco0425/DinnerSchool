# Imports de Django
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from comedor.models import Ingredientes, Noticias, Pedido, Credito
from core.models import Empleados
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.http import require_POST
from django.apps import apps
from django.core.paginator import Paginator
from .choices import *
from .herramientas import *
from django.conf import settings

# Imports para reset de contraseña
import json
import string
import random

# Imports del core
from .models import *

from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def reset_password(request):
    """Vista para resetear contraseña (sin envío de correo)"""
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            email = data.get('email')
        else:
            email = request.POST.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'El correo electrónico es requerido.'
            })
        
        # Verificar si el usuario existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'No existe una cuenta con ese correo electrónico.'
            })
        
        # Por seguridad, generar una contraseña temporal
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Cambiar la contraseña
        print(f"[reset_password] Cambiando contraseña para {email} a {temp_password}")
        print(f"[reset_password] User antes del cambio: {user}")
        user.set_password(temp_password)
        user.save()
        
        logger.info(f"Password reset for user: {email}")
        
        return JsonResponse({
            'success': True,
            'message': f'Tu nueva contraseña temporal es: {temp_password}. Te recomendamos cambiarla en tus ajustes de cuenta.',
            'temp_password': temp_password
        })
        
    except Exception as e:
        logger.error(f"Error in reset_password view: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor. Inténtalo más tarde.'
        })

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

def crearUsuarioYPerfil(username, userlastname, userlastname2, useremail, registerPassword, userType, userphone):
    # Capitalizar nombres y apellidos
    username = username.title().strip()
    userlastname = userlastname.title().strip()
    userlastname2 = userlastname2.title().strip() if userlastname2 else ''
    
    # 1. Crear usuario base
    user = User.objects.create_user(
        username=useremail,
        email=useremail,
        password=registerPassword,
        first_name=username,
        last_name=f"{userlastname} {userlastname2}".strip()
    )

    group = Group.objects.get(pk=3 if userType in [3, 4] else userType)
    user.groups.add(group)
    user.save()

    # 2. Crear usuario extendido
    usuario = Usuarios.objects.create(
        user=user,
        groupId=group,
        email=useremail,
        nombre=username,
        paterno=userlastname,
        materno=userlastname2,
        telefono=userphone or ''
    )

    # 3. Crear perfil según tipo
    if userType == 1:
        tutor = Tutor.objects.create(usuario=usuario)
        Credito.objects.create(tutorId=tutor, monto=0, fecha=datetime.today())
    elif userType in [3, 4]:
        puesto = 'Cocinero' if userType == 3 else 'Profesor'
        empleado = Empleados.objects.create(usuario=usuario, puesto=puesto)
        if '@liceoemperadores.edu.mx' in useremail:
            Credito.objects.create(profesorId=empleado, monto=0, fecha=datetime.today())

    return user, usuario

def signInUp(request):
    if request.user.is_authenticated and request.user.is_staff:
        # Staff: solo registro
        if request.method == "POST":
            username = request.POST.get("username", "").title().strip()
            userlastname = request.POST.get("userlastname", "").title().strip()
            userlastname2 = request.POST.get("userlastname2", "").title().strip()
            useremail = request.POST.get("useremail").lower()
            registerPassword = request.POST.get("password")
            confirmPassword = request.POST.get("confirmPassword")
            userType = request.POST.get("userType")
            userphone = request.POST.get("userphone")
            
            # Validaciones consolidadas
            if User.objects.filter(email=useremail).exists():
                messages.error(request, 'El correo electrónico ya está en uso.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
            
            if not all([username, userlastname, useremail, registerPassword, confirmPassword]):
                messages.error(request, 'Por favor, completa todos los campos obligatorios.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
            
            if registerPassword != confirmPassword:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

            if User.objects.filter(username=useremail).exists():
                messages.error(request, 'Ya existe un usuario con ese correo.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

            try:
                userType = int(userType)
                user, usuario = crearUsuarioYPerfil(
                    username, userlastname, userlastname2, useremail, registerPassword, userType, userphone
                )
                messages.success(request, f'El usuario {useremail} ha sido creado exitosamente.')
                return redirect('core:signInUp')
            except Group.DoesNotExist:
                messages.error(request, 'Tipo de usuario inválido.')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})
            except Exception as e:
                messages.error(request, f'Error creando usuario: {e}')
                return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

        # GET: mostrar solo el registro
        return render(request, 'Login/siginup.html', {'is_staff': True, 'only_register': True})

    else:
        # No autenticado: login y registro normal
        if request.method == "POST":
            # Detectar si es login o registro
            if 'useremail' in request.POST:
                # Es registro
                username = request.POST.get("username", "").title().strip()
                userlastname = request.POST.get("userlastname", "").title().strip()
                userlastname2 = request.POST.get("userlastname2", "").title().strip()
                useremail = request.POST.get("useremail").lower()
                registerPassword = request.POST.get("password")
                confirmPassword = request.POST.get("confirmPassword")
                userType = int(request.POST.get("userType")) if request.POST.get("userType") else 1
                userphone = request.POST.get("userphone")
                
                if '@liceoemperadores.edu.mx' in useremail:
                    userType = 4  # Profesor

                # Validaciones
                if User.objects.filter(email=useremail).exists():
                    messages.error(request, 'El correo electrónico ya está en uso.')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})
                
                if not all([username, userlastname, useremail, registerPassword, confirmPassword]):
                    messages.error(request, 'Por favor, completa todos los campos obligatorios.')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})
                
                if registerPassword != confirmPassword:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})

                try:
                    if not all([username, userlastname, useremail, registerPassword, confirmPassword]):
                        raise ValueError("Faltan campos obligatorios.")
                    user, usuario = crearUsuarioYPerfil(
                        username, userlastname, userlastname2, useremail, registerPassword, userType, userphone
                    )
                    # Login automático tras registro
                    userAuth = authenticate(request, username=useremail, password=registerPassword)
                    if userAuth is not None:
                        login(request, userAuth)
                        messages.success(request, 'Registro exitoso. ¡Bienvenido!')
                        return redirect('core:dashboard')
                    else:
                        messages.error(request, 'Error en la autenticación después del registro.')
                        return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})
                except Group.DoesNotExist:
                    messages.error(request, 'Tipo de usuario inválido.')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})
                except Exception as e:
                    messages.error(request, f'Error creando usuario: {e}')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})
            
            else:
                # Es login - no necesita capitalización
                correo = request.POST.get("username")
                contrasena = request.POST.get("password")
                
                print(f"[LOGIN] Intentando login con: {correo}")
                
                if not correo or not contrasena:
                    messages.error(request, 'Por favor, ingresa tu correo y contraseña.')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})
                
                user = authenticate(request, username=correo, password=contrasena)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Inicio de sesión exitoso.')
                    return redirect('core:dashboard')
                else:
                    print(f"[LOGIN] Autenticación fallida para: {correo}")
                    # Verificar si el usuario existe
                    if User.objects.filter(email=correo).exists():
                        messages.error(request, 'Contraseña incorrecta.')
                    else:
                        messages.error(request, 'No existe una cuenta con ese correo electrónico.')
                    return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})

        return render(request, 'Login/siginup.html', {'recaptcha_site_key': settings.SITE_KEY})

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
        is_profesor = Empleados.objects.filter(usuario__email=request.user.username, puesto='Profesor').exists()

        listaPedidos = Pedido.objects.filter(alumnoId__tutorId__usuario__email=request.user.username) if not is_profesor else Pedido.objects.filter(profesorId__usuario__email=request.user.username)

        if is_profesor:
            credito = Credito.objects.filter(profesorId__usuario__email=request.user.username).first()
        else:
            credito = Credito.objects.filter(tutorId__usuario__email=request.user.username).first()

        context = {
            'user': request.user,
            'TipoUsuario': 'Profesor' if is_profesor else 'Tutor' if request.user.groups.filter(name='Tutor').exists() else 'Empleado' if request.user.groups.filter(name='Empleado').exists() else 'Administrador' if request.user.is_staff else 'Invitado',
            'is_tutor': request.user.groups.filter(name='Tutor').exists(),
            'is_employee': request.user.groups.filter(name='Empleado').exists() if not is_profesor else False,
            'is_profesor': is_profesor,
            'is_admin': request.user.is_staff,
            'noticias': Noticias.objects.filter(activo=True),
            'statusPedidos': listaPedidos.filter(fecha__gte=timezone.localtime().date()),
            'credito'   : credito,
            'MEDIA_URL': settings.MEDIA_URL,
            'pedidos_bloqueados': timezone.localtime().hour >= 14 and not request.user.is_staff,
        }
        
        return render(request, 'Home/home_dashboard_view.html', context)
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

    # Filtros avanzados
    nombre = request.GET.get('nombre', '').strip()
    nivel = request.GET.get('nivel', '').strip()
    grado = request.GET.get('grado', '').strip()
    grupo = request.GET.get('grupo', '').strip()

    # Obtener el queryset de estudiantes basado en el tipo de usuario
    if request.user.is_staff:
        students_queryset = Alumnos.objects.all()
    else:
        try:
            usuario = Usuarios.objects.get(user=request.user)
            tutor = Tutor.objects.get(usuario=usuario)
            students_queryset = Alumnos.objects.filter(tutorId=tutor)
        except (Usuarios.DoesNotExist, Tutor.DoesNotExist):
            messages.warning(request, 'No se encontró un tutor asociado a este usuario.')
            return redirect('core:createStudents')

    # Aplicar filtros
    if nombre:
        students_queryset = students_queryset.filter(nombre__icontains=nombre)
    if nivel:
        students_queryset = students_queryset.filter(nivelEducativo__nivel=nivel)
    if grado:
        students_queryset = students_queryset.filter(nivelEducativo__grado=grado)
    if grupo:
        students_queryset = students_queryset.filter(nivelEducativo__grupo=grupo)

    # Aplicar la paginación al queryset
    paginator = Paginator(students_queryset, 10)
    page_number = request.GET.get('page')
    students_page_obj = paginator.get_page(page_number)

    # Procesar solo los alumnos de la página actual
    students_list = []
    for student in students_page_obj:
        students_list.append({
            'id': student.id,
            'nombre': student.nombre,
            'paterno': student.paterno,
            'materno': student.materno,
            'nivel': getChoiceLabel(NIVELEDUCATIVO, student.nivelEducativo.nivel),
            'grupo': getChoiceLabel(GRUPO, student.nivelEducativo.grupo),
            'grado': getChoiceLabel(GRADO, student.nivelEducativo.grado)
        })

    if students_list:
        context = {
            'students_list': students_list,
            'students_page_obj': students_page_obj,
            'NIVELEDUCATIVO': NIVELEDUCATIVO,
            'GRADO': GRADO,
            'GRUPO': GRUPO,
            'request': request,
        }
        return render(request, 'Students/students_list_view.html', context)
    else:
        messages.info(request, 'No tienes estudiantes registrados. Crea uno nuevo.')
        return redirect('core:createStudents')

def createStudents(request):
    """
    Vista para crear un nuevo estudiante.
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
        # Capitalizar nombres de estudiantes
        nombre = request.POST.get("nombre", "").title().strip()
        paterno = request.POST.get("apellidoPaterno", "").title().strip()
        materno = request.POST.get("apellidoMaterno", "").title().strip()
        grado = request.POST.get("grado")
        grupo = request.POST.get("grupo")
        nivelEducativo = request.POST.get("nivelEducativo")
        tutor_id = request.POST.get("tutor") if request.user.is_staff else None
        
        if not all([nombre, paterno, grado, grupo, nivelEducativo]):
            campos = ''
            if not nombre:
                campos += 'nombre, '
            if not paterno:
                campos += 'apellido paterno, '
            if not materno:
                campos += 'apellido materno, '
            if not grado:
                campos += 'grado, '
            if not grupo:
                campos += 'grupo, '
            if not nivelEducativo:
                campos += 'nivel educativo, '
            messages.error(request, f"Por favor, completa todos los campos {campos[:-2]}.")
            return render(request, 'Students/students_form_view.html', context)

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
            return render(request, 'Students/students_form_view.html', context)

        try:
            if request.user.is_staff:
                tutor = Tutor.objects.get(id=tutor_id) if tutor_id else None
            else:
                tutor = Tutor.objects.get(usuario=Usuarios.objects.get(user=request.user))
            
            alumno_exists = Alumnos.objects.filter(
                nombre=nombre,
                paterno=paterno,
                materno=materno,
                nivelEducativo=nivelEducativoAlumno
            )

            if alumno_exists.exists() and not alumno:
                tutor_exist = alumno_exists.first().tutorId
                messages.error(request, f'El estudiante {nombre} {paterno} {materno} ya está registrado. Con el tutor {tutor_exist.usuario.nombre} {tutor_exist.usuario.paterno}.')
                return render(request, 'Students/students_form_view.html', context)
            
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
            return render(request, 'Students/students_form_view.html', context)
    else:
        return render(request, 'Students/students_form_view.html', context)

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
        return render(request, 'Employees/employees_list_view.html')
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
        # Obtener filtros de GET
        nombre = request.GET.get('nombre', '').strip()
        correo = request.GET.get('correo', '').strip()
        tipo = request.GET.get('tipo', '').strip()

        users = Usuarios.objects.filter(groupId__name__in=["Tutor", "Empleado"])
        # Aplicar filtros
        if nombre:
            users = users.filter(nombre__icontains=nombre)
        if correo:
            users = users.filter(email__icontains=correo)
        if tipo:
            # tipo puede ser Tutor, Cocinero, Profesor
            if tipo == 'Tutor':
                users = users.filter(groupId__name='Tutor')
            elif tipo in ['Cocinero', 'Profesor']:
                empleados_ids = Empleados.objects.filter(puesto=tipo).values_list('usuario_id', flat=True)
                users = users.filter(id__in=empleados_ids)

        usersData = []
        for user in users:
            if user.groupId.name == 'Tutor':
                grupo = user.groupId.name
            elif user.groupId.name == 'Empleado':
                empleado = Empleados.objects.get(usuario=user)
                grupo = user.groupId.name if empleado.puesto == 'Cocinero' else empleado.puesto
            usersData.append({
                'id': user.id,
                'nombre': user.nombre,
                'paterno': user.paterno,
                'materno': user.materno,
                'email': user.email,
                'tipo': grupo,
                'alumnos': Alumnos.objects.filter(tutorId__usuario=user).all() if user.groupId.name == 'Tutor' else '',
            })

        paginator = Paginator(usersData, 10) # Muestra 10 usuarios por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'users': page_obj,
            'request': request,
        }
        return render(request, 'Users/users_list_view.html', context)
    else:
        return redirect('core:signInUp')
    
def account_settings_form_view(request):
    """
    Vista para manejar los ajustes de cuenta del usuario.
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
        # Capitalizar nombres en configuración de cuenta
        nombre = request.POST.get("nombre", usuario.nombre).title().strip()
        paterno = request.POST.get("apellidoPaterno", usuario.paterno).title().strip()
        materno = request.POST.get("apellidoMaterno", usuario.materno).title().strip()
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

        # Actualizar nombre completo en User model
        user.first_name = nombre
        user.last_name = f"{paterno} {materno}".strip()

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
            
def custom_404(request, exception):
    """Vista personalizada para error 404"""
    logger.warning(f"Error 404: {request.path} - IP: {request.META.get('REMOTE_ADDR')}")
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    """Vista personalizada para error 500"""
    logger.error(f"Error 500 en: {request.path} - IP: {request.META.get('REMOTE_ADDR')}")
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    """Vista personalizada para error 403"""
    logger.warning(f"Error 403: {request.path} - IP: {request.META.get('REMOTE_ADDR')}")
    return render(request, 'errors/403.html', status=403)

def custom_400(request, exception):
    """Vista personalizada para error 400"""
    logger.warning(f"Error 400: {request.path} - IP: {request.META.get('REMOTE_ADDR')}")
    return render(request, 'errors/400.html', status=400)