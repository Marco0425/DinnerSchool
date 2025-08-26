from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_POST
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal

from comedor.models import Ingredientes, Platillo, Pedido, Credito, CreditoDiario, Noticias
from core.models import Alumnos, Usuarios, Tutor, Empleados
from core.choices import *
from .choices import *
from core.herramientas import *
from .reports import generar_reporte_gastos_diarios, generar_reporte_rango_fechas

from datetime import datetime, date, timedelta
import json
import traceback
import os

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
        paginator = Paginator(ingredients, 10) # Muestra 10 ingredientes por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'ingredientes': page_obj # Aquí es donde pasas el objeto paginado a la plantilla
        }
        return render(request, 'Ingredients/ingredients_list_view.html', context)
    else:
        return redirect('core:signInUp')

def createIngredient(request):
    """
    Vista para crear un nuevo ingrediente.
    Esta vista se encarga de manejar la creación de un nuevo ingrediente.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige a la lista de ingredientes.
    """
    ingrediente_id = request.GET.get('id') or request.POST.get('id')
    ingrediente = None
    if ingrediente_id:
        try:
            ingrediente = Ingredientes.objects.get(id=ingrediente_id)
        except Ingredientes.DoesNotExist:
            ingrediente = None

    if request.method == "POST":
        nombre = request.POST.get("ingrediente")
        if nombre:
            if ingrediente:
                ingrediente.nombre = nombre
                ingrediente.save()
                messages.success(request, "Ingrediente actualizado exitosamente.")
            else:
                nuevoIngrediente = Ingredientes(nombre=nombre)
                nuevoIngrediente.save()
                messages.success(request, "Ingrediente creado exitosamente.")
            return redirect('comedor:ingredients')  # SIEMPRE redirect después del mensaje
        else:
            messages.error(request, "Por favor, ingresa un nombre para el ingrediente.")
            return render(request, 'Ingredients/ingredients_form_view.html', {'ingrediente': ingrediente})
    
    return render(request, 'Ingredients/ingredients_form_view.html', {'ingrediente': ingrediente})

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
        creditos = Credito.objects.all()
        return render(request, 'Credit/credit_list_view.html', {'creditos': creditos})
    else:
        return redirect('core:signInUp')
    
def createCredit(request):
    """
    Vista para crear un nuevo crédito.
    Esta vista se encarga de manejar la creación de un nuevo crédito.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige a la lista de créditos.
    """
    if request.method == "POST":
        tutor_id = request.POST.get("tutor")
        credito = request.POST.get("credito")
        print(tutor_id, credito)
        if "tutor_" in tutor_id and credito:
            try:
                tutor = Tutor.objects.get(id=int(tutor_id.split('_')[1]))
                nuevoCredito = Credito(tutorId=tutor, monto=credito)
                nuevoCredito.save()
                messages.success(request, "Crédito creado exitosamente.")
                return redirect('comedor:credit')
            except Tutor.DoesNotExist:
                messages.error(request, "Tutor no encontrado.")
        elif "profesor_" in tutor_id and credito:
            print(tutor_id, credito)
            print(Empleados.objects.get(id=int(tutor_id.split('_')[1])))
            try:
                profesor = Empleados.objects.get(id=int(tutor_id.split('_')[1]))
                nuevoCredito = Credito(profesorId=profesor, monto=credito)
                nuevoCredito.save()
                messages.success(request, "Crédito creado exitosamente.")
                return redirect('comedor:credit')
            except Empleados.DoesNotExist:
                messages.error(request, "Profesor no encontrado.")
                return redirect('comedor:createCredit')
        else:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect('comedor:createCredit')
        
        # Unir ambos querysets
        tutors = Tutor.objects.all()
        profesores = Empleados.objects.filter(puesto='Profesor')
    
        # Crear lista combinada con estructura uniforme
        all_users = []
        
        # Agregar tutores
        for tutor in tutors:
            all_users.append({
                'id': f'tutor_{tutor.id}',
                'nombre': f"{tutor.usuario.nombre} {tutor.usuario.paterno} - Tutor",
                'tipo': 'Tutor'
            })
        
        # Agregar profesores
        for profesor in profesores:
            all_users.append({
                'id': f'profesor_{profesor.id}',
                'nombre': f"{profesor.usuario.nombre} {profesor.usuario.paterno} - Profesor",
                'tipo': 'Profesor'
            })
        
        return render(request, 'Credit/credit_form_view.html', {'users': all_users})
    
    # GET request - mismo proceso
    tutors = Tutor.objects.all()
    profesores = Empleados.objects.filter(puesto='Profesor')
    
    all_users = []
    # Agregar tutores
    for tutor in tutors:
        all_users.append({
            'id': f'tutor_{tutor.id}',
            'nombre': f"{tutor.usuario.nombre} {tutor.usuario.paterno} - Tutor",
            'tipo': 'Tutor'
        })
    
    # Agregar profesores
    for profesor in profesores:
        all_users.append({
            'id': f'profesor_{profesor.id}',
            'nombre': f"{profesor.usuario.nombre} {profesor.usuario.paterno} - Profesor",
            'tipo': 'Profesor'
        })
    
    return render(request, 'Credit/credit_form_view.html', {'users': all_users})
    
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
        noticiaList = Noticias.objects.all()
        return render(request, 'Ads/ads_list_view.html', {'noticias': noticiaList})
    else:
        return redirect('core:signInUp')

def createAds(request):
    """
    Vista para crear un nuevo anuncio.
    Esta vista se encarga de manejar la creación de un nuevo anuncio.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige a la lista de anuncios.
    """
    noticia_id = request.GET.get('id') or request.POST.get('id')
    noticia = None
    if noticia_id:
        try:
            noticia = Noticias.objects.get(id=noticia_id)
        except Noticias.DoesNotExist:
            noticia = None

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        contenido = request.POST.get("contenido")
        if titulo and contenido:
            if noticia:
                noticia.titulo = titulo
                noticia.contenido = contenido
                noticia.activo = True if request.POST.get("estado") == "1" else False
                noticia.tipoAnuncio = request.POST.get("tipoAnuncio")
                noticia.save()
                messages.success(request, "Anuncio actualizado exitosamente.")
                return redirect('comedor:ads')
            else:
                try:
                    usuario = Usuarios.objects.get(user=request.user)
                    nueva_noticia = Noticias(
                        titulo=titulo,
                        contenido=contenido,
                        activo=True,
                        autor=usuario,
                    )
                    nueva_noticia.save()
                    messages.success(request, "Anuncio creado exitosamente.")
                    return redirect('comedor:ads')
                except Usuarios.DoesNotExist:
                    messages.error(request, "No existe un perfil de usuario asociado a este usuario. Contacta al administrador.")
        else:
            messages.error(request, "Por favor, completa todos los campos.")
        
        # Si hay error, mostrar el form con el contexto
        context = {'noticia': noticia}
        return render(request, 'Ads/ads_form_view.html', context)
    
    context = {'noticia': noticia}
    return render(request, 'Ads/ads_form_view.html', context)

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
        orders = []
        
        today = date.today()
        
        status_map = {
            0: "pendiente",
            1: "en preparacion",
            2: "finalizado",
            3: "entregado",
            4: "cancelado",
        }
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()
                
        try:
            for pedido in Pedido.objects.filter(fecha=today):
                is_profesor = pedido.profesorId is not None
                order = {
                    "id": f"order-{pedido.id}",
                    "platillo": pedido.platillo.nombre,
                    "ingredientes": pedido.ingredientePlatillo,
                    "nota": pedido.nota,
                    "is_profesor": is_profesor,
                    "is_employee": is_employee,
                    "alumno": f"{pedido.alumnoId.nombre} {pedido.alumnoId.paterno}" if not is_profesor else f"{pedido.profesorId.usuario} {pedido.profesorId.usuario.paterno}",
                    "nivel": getChoiceLabel(NIVELEDUCATIVO, pedido.nivelEducativo.nivel) if not is_profesor else "Profesor",
                    "turno": pedido.get_turno_label(),
                    "status": status_map.get(pedido.status, "pendiente"),
                    "encargado": f"{pedido.encargadoId.usuario.nombre} {pedido.encargadoId.usuario.paterno}" if pedido.encargadoId else "No asignado"
                }
                orders.append(order)
            return render(request, 'Orders/orders_kanban_view.html', {'orders': orders})
        except Exception as e:
            print("Error en la vista order:")
            traceback.print_exc()
    else:
        return redirect('core:signInUp')
    
def createOrder(request):
    """
    Vista para crear un nuevo pedido.
    Esta vista se encarga de manejar la creación de un nuevo pedido.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige a la lista de pedidos.
    """
    if request.method == "POST":
        is_profesor = Empleados.objects.filter(usuario__email=request.user.username, puesto='Profesor').exists()
        orden = request.POST.get("platillo")
        ordenIngredientes = request.POST.getlist("ingredientes")
        ordenNotas = request.POST.get("notas")
        ordenAlumno = request.POST.get("alumno")
        ordenTurno = request.POST.get("turno")
        precio = request.POST.get("precio")
        tutorProfesor = request.POST.get("tutor")

        profesorRequest = Empleados.objects.get(usuario__email=request.user.username) if is_profesor else None
        tutor, profesor = None, None
        if request.user.is_staff:
            if tutorProfesor.startswith("Tutor_"):
                tutor = Tutor.objects.get(id=tutorProfesor.split("_")[1])
            elif tutorProfesor.startswith("Profesor_"):
                profesor = Empleados.objects.get(id=tutorProfesor.split("_")[1])
                
        is_admin = True if request.user.is_staff else False

        try:
            platillo = Platillo.objects.get(id=orden)
            
            # Convertir precio a Decimal
            precio_decimal = Decimal(str(precio))
            
            if not is_admin:
                nuevaOrden = Pedido(
                    platillo=platillo,
                    ingredientePlatillo=", ".join(ordenIngredientes),
                    nota=ordenNotas,
                    alumnoId=Alumnos.objects.get(id=ordenAlumno) if not is_profesor else None,
                    nivelEducativo=Alumnos.objects.get(id=ordenAlumno).nivelEducativo if not is_profesor else None,
                    profesorId=Empleados.objects.get(usuario__email=request.user.username) if is_profesor else None,
                    turno=ordenTurno,
                    total=precio_decimal  # Usar Decimal aquí también
                )
                nuevaOrden.save()
            else:
                nuevaOrden = Pedido(
                    platillo=platillo,
                    ingredientePlatillo=", ".join(ordenIngredientes),
                    nota=ordenNotas,
                    alumnoId=Alumnos.objects.get(id=ordenAlumno) if tutor else None,
                    nivelEducativo=Alumnos.objects.get(id=ordenAlumno).nivelEducativo if tutor else None,
                    profesorId=profesor if profesor else None,
                    turno=ordenTurno,
                    total=precio_decimal  # Usar Decimal aquí también
                )
                nuevaOrden.save()
            
            if nuevaOrden and not is_admin:
                if is_profesor:
                    profesor = Empleados.objects.get(usuario__email=request.user.username)
                    tutor = None
                else:
                    tutor = Tutor.objects.get(usuario__email=request.user.username)
                    profesor = None

                # Crear crédito diario
                
            creditoDiario = CreditoDiario.objects.create(
                pedido=nuevaOrden,
                tutorId=tutor,
                profesorId=profesor,
                monto=precio_decimal,  # Usar Decimal
                fecha=date.today()
            )

            # Actualizar crédito total
            try:
                if not is_admin:
                    creditoTotal = Credito.objects.get(profesorId=profesorRequest) if is_profesor else Credito.objects.get(tutorId=tutor)
                else:
                    creditoTotal = Credito.objects.get(profesorId=profesor) if profesor else Credito.objects.get(tutorId=tutor)

                creditoTotal.monto -= precio_decimal  # Ahora ambos son Decimal
                creditoTotal.save()

            except Credito.DoesNotExist:
                messages.error(request, "No se encontró crédito disponible para este usuario.")
                return redirect('comedor:createOrder')
            if creditoTotal.monto <= 0:
                    messages.warning(request, "Tu crédito ha llegado a 0 o es negativo. Es necesario recargar para futuros pedidos.")
            elif 0 < creditoTotal.monto <= 100:
                messages.info(request, f"Tu crédito actual es ${creditoTotal.monto}. Te recomendamos recargar pronto.")
            messages.success(request, "Pedido creado exitosamente.")
            return redirect('core:dashboard')
            
        except (Platillo.DoesNotExist) as e:
            messages.error(request, f"Error al crear el pedido: {str(e)}")
            return redirect('comedor:createOrder')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('comedor:createOrder')
    
    # Verificar crédito
    creditoTutor = Credito.objects.filter(tutorId__usuario__email=request.user.username).first()
    if creditoTutor and creditoTutor.monto < -200:
        messages.error(request, "No tienes crédito suficiente para realizar un pedido.")
        return redirect('core:dashboard')

    creditoProfesor = Credito.objects.filter(profesorId__usuario__email=request.user.username).first()
    if creditoProfesor and creditoProfesor.monto < -200:
        messages.error(request, "No tienes crédito suficiente para realizar un pedido.")
        return redirect('core:dashboard')
    
    # Determinar el tipo de usuario
    is_tutor = request.user.groups.filter(name='Tutor').exists()
    is_profesor = Empleados.objects.filter(usuario__email=request.user.username, puesto='Profesor').exists()
    is_admin = request.user.is_staff
    
    platillos = Platillo.objects.all()
    
    if is_tutor:
        # Para tutores: solo mostrar sus alumnos, no el campo de selección de usuario
        tutor = Tutor.objects.get(usuario__email=request.user.username)
        students = Alumnos.objects.filter(tutorId=tutor)
        
        context = {
            "Platillos": [
                {
                    "id": platillo.id,
                    "nombre": platillo.nombre,
                    "ingredientes": json.dumps([Ingredientes.objects.get(id=int(ing)).nombre for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') if ing]),
                    "precio": float(platillo.precio)
                } for platillo in platillos
            ],
            'user_type': 'tutor',  # Enviar el tipo de usuario
            'is_tutor': True,
            'is_employee': False,
            'is_admin': False,
            "Alumnos": [
                {
                    "id": alumno.id,
                    "nombre": f"{alumno.nombre} {alumno.paterno} - {getChoiceLabel(NIVELEDUCATIVO,alumno.nivelEducativo.nivel)} - {getChoiceLabel(GRADO,alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO,alumno.nivelEducativo.grupo)}",
                    "tutor_id": alumno.tutorId.id
                } for alumno in students
            ],
        }
        
    elif is_profesor:
        # Para profesores: no mostrar campos de usuario ni alumnos
        context = {
            "Platillos": [
                {
                    "id": platillo.id,
                    "nombre": platillo.nombre,
                    "ingredientes": json.dumps([Ingredientes.objects.get(id=int(ing)).nombre for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') if ing]),
                    "precio": float(platillo.precio)
                } for platillo in platillos
            ],
            'user_type': 'profesor',  # Enviar el tipo de usuario
            'is_tutor': False,
            'is_employee': True,
            'is_admin': False,
        }
        
    else:
        # Para admins: mostrar todos los campos con opciones completas
        tutors = Tutor.objects.all()
        students = Alumnos.objects.all()
        profesores = Empleados.objects.filter(puesto='Profesor')
        
        # Crear lista combinada de tutores y profesores
        combined_users = []
        
        for tutor in tutors:
            combined_users.append({
                "id": f"Tutor_{tutor.id}",  # ✅ Cambiar formato para coincidir con el POST
                "type": "Tutor",
                "nombre": f"{tutor.usuario.user.first_name} {tutor.usuario.user.last_name} - Tutor",
            })
        
        for profesor in profesores:
            combined_users.append({
                "id": f"Profesor_{profesor.id}",  # ✅ Cambiar formato para coincidir con el POST
                "type": "Profesor", 
                "nombre": f"{profesor.usuario.user.first_name} {profesor.usuario.user.last_name} - Profesor",
            })

        context = {
            "Platillos": [
                {
                    "id": platillo.id,
                    "nombre": platillo.nombre,
                    "ingredientes": json.dumps([Ingredientes.objects.get(id=int(ing)).nombre for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') if ing]),
                    "precio": float(platillo.precio)
                } for platillo in platillos
            ],
            'user_type': 'admin',  # Enviar el tipo de usuario
            'is_tutor': False,
            'is_employee': False,
            'is_admin': True,
            "tutors": combined_users,
            "Alumnos": [
                {
                    "id": alumno.id,
                    "nombre": f"{alumno.nombre} {alumno.paterno} - {getChoiceLabel(NIVELEDUCATIVO,alumno.nivelEducativo.nivel)} - {getChoiceLabel(GRADO,alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO,alumno.nivelEducativo.grupo)}",
                    "tutor_id": f"Tutor_{alumno.tutorId.id}"
                } for alumno in students
            ],
        }
        
    return render(request, 'Orders/orders_form_view.html', context)

@csrf_exempt
def update_order_status(request):
    """
    Vista para actualizar el status de un pedido vía AJAX.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            order_id = data.get("order_id")
            new_status = data.get("new_status")

            if not order_id or not new_status:
                return JsonResponse({"success": False, "error": "Datos incompletos"}, status=400)

            status_map = {
                "pendiente": 0,
                "en preparacion": 1,
                "finalizado": 2,
                "entregado": 3,
                "cancelado": 4,
            }
            if new_status not in status_map:
                return JsonResponse({"success": False, "error": "Status inválido"}, status=400)
            
            pedido_id = int(order_id.replace("order-", ""))
            pedido = Pedido.objects.get(id=pedido_id)
            empleado = Empleados.objects.filter(usuario__email=request.user.username).exists()
            
            # Asigna el encargado solo si se encontró un empleado
            pedido.encargadoId = empleado
            
            pedido.status = status_map[new_status]
            pedido.save()

            # Devuelve el nombre del encargado para que el frontend lo actualice
            encargado_nombre = f"{empleado.usuario.nombre} {empleado.usuario.paterno}" if empleado else "No asignado"
            return JsonResponse({"success": True, "encargado": encargado_nombre})
            
        except Pedido.DoesNotExist:
            return JsonResponse({"success": False, "error": "Pedido no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

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
        # 1. Obtiene todos los platillos, sin procesarlos aún.
        all_saucers = Platillo.objects.all()

        # 2. Aplica la paginación a la lista completa de objetos.
        paginator = Paginator(all_saucers, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 3. Procesa solo los platillos de la página actual.
        saucers_for_template = []
        for platillo in page_obj:
            # Convierte la cadena de ingredientes en una lista de nombres.
            ingredient_ids = platillo.ingredientes.strip('[]').replace("'", "").split(', ')
            ingredient_names = [Ingredientes.objects.get(id=int(ing)).nombre for ing in ingredient_ids if ing]
            
            saucers_for_template.append({
                'id': platillo.id,
                'nombre': platillo.nombre,
                'ingredientes': ingredient_names,
                'precio': platillo.precio
            })
            
        context = {
            'saucers_list': saucers_for_template, # Lista procesada para el bucle
            'saucers_page_obj': page_obj          # Objeto de paginación
        }

        return render(request, 'Saucer/saucer_list_view.html', context)
    else:
        return redirect('core:signInUp')
    
def createSaucer(request):
    """
    Vista para crear un nuevo platillo.
    Esta vista se encarga de manejar la creación de un nuevo platillo.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige a la lista de platillos.
    """
    platillo_id = request.GET.get('id') or request.POST.get('id')
    platillo = None
    if platillo_id:
        try:
            platillo = Platillo.objects.get(id=platillo_id)
        except Platillo.DoesNotExist:
            platillo = None

    ingredientes = Ingredientes.objects.all()

    if request.method == "POST":
        nombre = request.POST.get("platillo")
        ingredientes_ids = request.POST.getlist("ingredientes")
        precio = request.POST.get("precio")
        if not precio:
            messages.error(request, "Por favor, ingresa un precio para el platillo.")
            return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo})
        if nombre and ingredientes_ids:
            if platillo:
                platillo.nombre = nombre
                platillo.precio = precio
                platillo.ingredientes = str(ingredientes_ids)
                platillo.save()
                messages.success(request, "Platillo actualizado exitosamente.")
            else:
                nuevoPlatillo = Platillo(nombre=nombre, precio=precio, ingredientes=str(ingredientes_ids))
                nuevoPlatillo.save()
                messages.success(request, "Platillo creado exitosamente.")
            return redirect('comedor:saucers')
        else:
            messages.error(request, "Por favor, ingresa un nombre para el platillo y selecciona ingredientes.")
        
        # Si hay error, mostrar el form con el contexto
        return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo})
    
    return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo})

def ejemplo_uso_reportes():
    """Ejemplos de cómo usar las funciones de reportes."""
    
    # 1. Generar reporte para el día actual
    print("Generando reporte para hoy...")
    archivo_hoy = generar_reporte_gastos_diarios()
    print(f"Reporte generado: {archivo_hoy}")
    
    # 2. Generar reporte para una fecha específica
    fecha_especifica = date(2025, 8, 20)
    print(f"Generando reporte para {fecha_especifica}...")
    archivo_fecha = generar_reporte_gastos_diarios(
        fecha_reporte=fecha_especifica,
        nombre_archivo="reporte_especial.xlsx"
    )
    print(f"Reporte generado: {archivo_fecha}")
    
    # 3. Generar reporte para un rango de fechas (última semana)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=7)
    print(f"Generando reporte desde {fecha_inicio} hasta {fecha_fin}...")
    archivo_rango = generar_reporte_rango_fechas(fecha_inicio, fecha_fin)
    print(f"Reporte generado: {archivo_rango}")

def generarReporte(request):
    """Vista para generar y descargar reporte desde Django."""
    try:
        # Generar reporte
        archivo = generar_reporte_gastos_diarios()
        
        # Servir archivo para descarga
        if os.path.exists(archivo):
            response = FileResponse(
                open(archivo, 'rb'),
                as_attachment=True,
                filename=os.path.basename(archivo)
            )
            return response
        else:
            messages.error(request, "No se pudo generar el reporte.")
            return redirect('comedor:credit')
    
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('comedor:credit')