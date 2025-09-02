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
import ast

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
        userCreditos = []
        creditos = Credito.objects.all()
        for user in creditos:
            userCreditos.append({
                'id': user.id,
                'nombre': user.tutorId.usuario.nombre if user.tutorId else user.profesorId.usuario.nombre,
                'paterno': user.tutorId.usuario.paterno if user.tutorId else user.profesorId.usuario.paterno,
                'materno': user.tutorId.usuario.materno if user.tutorId else user.profesorId.usuario.materno,
                'monto': float(user.monto) if isinstance(user.monto, Decimal) else '0.00',
                'tipo': 'Profesor' if user.profesorId else 'Tutor',
                'alumnos': Alumnos.objects.filter(tutorId=user.tutorId).all() if user.tutorId else '',
            })
        print(userCreditos)
        return render(request, 'Credit/credit_list_view.html', {'creditos': userCreditos})
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
        
        if "tutor_" in tutor_id and credito:
            try:
                tutor = Tutor.objects.get(id=int(tutor_id.split('_')[1]))
                nuevoCredito, created = Credito.objects.get_or_create(tutorId=tutor, defaults={'monto': credito})
                if created:
                    messages.success(request, "Crédito creado exitosamente.")
                else:
                    # Si ya existía, sumar el nuevo monto al existente
                    nuevoCredito.monto += Decimal(str(credito))
                    nuevoCredito.save()
                    messages.info(request, f"Crédito actualizado exitosamente. Nuevo saldo: ${nuevoCredito.monto}")
                return redirect('comedor:credit')
            except Tutor.DoesNotExist:
                messages.error(request, "Tutor no encontrado.")
        elif "profesor_" in tutor_id and credito:
            try:
                profesor = Empleados.objects.get(id=int(tutor_id.split('_')[1]))
                nuevoCredito, created = Credito.objects.get_or_create(profesorId=profesor, defaults={'monto': credito})
                if created:
                    messages.success(request, "Crédito creado exitosamente.")
                else:
                    # Si ya existía, sumar el nuevo monto al existente
                    nuevoCredito.monto += Decimal(str(credito))
                    nuevoCredito.save()
                    messages.info(request, f"Crédito actualizado exitosamente. Nuevo saldo: ${nuevoCredito.monto}")
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
        alumnos = Alumnos.objects.filter(tutorId=tutor.id).all()
        strAlumnos = ", ".join([f"{alumno.nombre} {alumno.paterno} {alumno.materno} - {getChoiceLabel(NIVELEDUCATIVO,alumno.nivelEducativo.nivel)} - {getChoiceLabel(GRADO,alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO,alumno.nivelEducativo.grupo)}" for alumno in alumnos])
        all_users.append({
            'id': f'tutor_{tutor.id}',
            'nombre': f"{strAlumnos}",
            'tipo': 'Tutor'
        })
    
    # Agregar profesores
    for profesor in profesores:
        all_users.append({
            'id': f'profesor_{profesor.id}',
            'nombre': f"{profesor.usuario.nombre} {profesor.usuario.paterno}",
            'tipo': 'Profesor'
        })
    
    print(all_users)
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
    Vista para manejar los pedidos agrupados por usuario, turno y fecha.
    Esta vista se encarga de mostrar y gestionar los pedidos realizados agrupados como órdenes.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la vista kanban con órdenes agrupadas.
    """
    if request.user.is_authenticated:
        grouped_orders = []
        
        today = date.today()
        
        status_map = {
            0: "pendiente",
            1: "en preparacion",
            2: "finalizado",
            3: "entregado",
        }
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()
                
        try:
            # Obtener todos los pedidos del día
            pedidos_hoy = Pedido.objects.filter(fecha=today).order_by('fecha', 'turno', 'alumnoId', 'profesorId')
            
            # Diccionario para agrupar pedidos
            orders_dict = {}
            
            for pedido in pedidos_hoy:
                is_profesor = pedido.profesorId is not None
                
                # Crear clave única para agrupar: usuario + turno + fecha
                if is_profesor:
                    user_key = f"profesor_{pedido.profesorId.id}"
                    user_name = f"{pedido.profesorId.usuario.nombre} {pedido.profesorId.usuario.paterno}"
                    user_level = "Profesor"
                else:
                    user_key = f"alumno_{pedido.alumnoId.id}"
                    user_name = f"{pedido.alumnoId.nombre} {pedido.alumnoId.paterno}"
                    user_level = getChoiceLabel(NIVELEDUCATIVO, pedido.nivelEducativo.nivel)
                
                group_key = f"{user_key}_{pedido.turno}_{pedido.fecha}"
                
                # Si el grupo no existe, crearlo
                if group_key not in orders_dict:
                    orders_dict[group_key] = {
                        "id": group_key,
                        "user_name": user_name,
                        "user_level": user_level,
                        "turno": pedido.get_turno_label(),
                        "turno_num": pedido.turno,
                        "fecha": pedido.fecha,
                        "is_profesor": is_profesor,
                        "is_employee": is_employee,
                        "status": status_map.get(pedido.status, "pendiente"),
                        "status_num": pedido.status,
                        "encargado": f"{pedido.encargadoId.usuario.nombre} {pedido.encargadoId.usuario.paterno}" if pedido.encargadoId else "No asignado",
                        "encargado_id": pedido.encargadoId.id if pedido.encargadoId else None,
                        "platillos": [],
                        "total_cantidad": 0,
                        "total_precio": Decimal('0'),
                        "pedido_ids": []  # Para trackear los IDs individuales
                    }
                
                # Agregar platillo al grupo
                pedido.ingredientePlatillo = ast.literal_eval(pedido.ingredientePlatillo)
                platillo_info = {
                    "id": pedido.id,
                    "nombre": pedido.platillo.nombre,
                    "ingredientes": pedido.ingredientePlatillo,
                    "nota": pedido.nota,
                    "cantidad": pedido.cantidad if hasattr(pedido, 'cantidad') else 1,
                    "precio": pedido.total
                }
                
                orders_dict[group_key]["platillos"].append(platillo_info)
                orders_dict[group_key]["total_cantidad"] += platillo_info["cantidad"]
                orders_dict[group_key]["total_precio"] += platillo_info["precio"]
                orders_dict[group_key]["pedido_ids"].append(pedido.id)
                
                # El status de la orden será el menor status de todos los pedidos
                # (si hay uno pendiente, toda la orden está pendiente)
                if pedido.status < orders_dict[group_key]["status_num"]:
                    orders_dict[group_key]["status"] = status_map.get(pedido.status, "pendiente")
                    orders_dict[group_key]["status_num"] = pedido.status
            
            # Convertir diccionario a lista y ordenar
            grouped_orders = list(orders_dict.values())
            
            # Ordenar por: estado, turno, fecha de creación
            grouped_orders.sort(key=lambda x: (x["status_num"], x["turno_num"], x["fecha"]))
            
            return render(request, 'Orders/orders_kanban_view.html', {'orders': grouped_orders})
            
        except Exception as e:
            print("Error en la vista order:")
            print(f"Error: {str(e)}")
            traceback.print_exc()
            return render(request, 'Orders/orders_kanban_view.html', {'orders': []})
    else:
        return redirect('core:signInUp')
    
def createOrder(request):
    """
    Vista para crear un nuevo pedido desde carrito de compras.
    Esta vista se encarga de manejar la creación de múltiples pedidos desde un carrito.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige al dashboard.
    """    
    if request.method == "POST":
        try:
            # Obtener datos del carrito
            cart_data = request.POST.get("cart_data")
            alumno_id = request.POST.get("alumno")
            tutor_profesor = request.POST.get("tutor")
            total_carrito = Decimal(request.POST.get("total", "0"))
            
            if not cart_data:
                messages.error(request, "El carrito está vacío.")
                return redirect('comedor:createOrder')
            
            # Parsear datos del carrito
            cart_items = json.loads(cart_data)
            
            if not cart_items:
                messages.error(request, "No hay items en el carrito.")
                return redirect('comedor:createOrder')
            
            # Determinar tipo de usuario
            is_profesor = Empleados.objects.filter(usuario__email=request.user.username, puesto='Profesor').exists()
            is_admin = request.user.is_staff
            
            # Variables para el usuario actual
            profesorRequest = Empleados.objects.get(usuario__email=request.user.username) if is_profesor else None
            tutor_actual, profesor_actual = None, None
            
            # Procesar información del usuario según el tipo
            if is_admin and tutor_profesor:
                if tutor_profesor.startswith("Tutor_"):
                    tutor_actual = Tutor.objects.get(id=tutor_profesor.split("_")[1])
                elif tutor_profesor.startswith("Profesor_"):
                    profesor_actual = Empleados.objects.get(id=tutor_profesor.split("_")[1])
            elif not is_admin:
                if is_profesor:
                    profesor_actual = profesorRequest
                else:
                    tutor_actual = Tutor.objects.get(usuario__email=request.user.username)
            
            # Obtener alumno si aplica
            alumno_obj = None
            if alumno_id and (tutor_actual or not is_profesor):
                alumno_obj = Alumnos.objects.get(id=alumno_id)
            
            # Lista para almacenar los pedidos creados
            pedidos_creados = []
            total_calculado = Decimal('0')
            
            # Crear cada pedido del carrito
            for item in cart_items:
                try:
                    platillo = Platillo.objects.get(id=item['platillo_id'])
                    subtotal = Decimal(str(item['subtotal']))
                    total_calculado += subtotal
                    
                    # Crear el pedido
                    nuevo_pedido = Pedido(
                        platillo=platillo,
                        ingredientePlatillo=item.get('ingredientes', ''),
                        nota=item.get('notas', ''),
                        cantidad=item['cantidad'],  # Asumiendo que tienes este campo
                        alumnoId=alumno_obj if not is_profesor else None,
                        nivelEducativo=alumno_obj.nivelEducativo if alumno_obj else None,
                        profesorId=profesor_actual if profesor_actual else None,
                        turno=item['turno'],
                        total=subtotal
                    )
                    nuevo_pedido.save()
                    pedidos_creados.append(nuevo_pedido)
                    
                except Platillo.DoesNotExist:
                    messages.error(request, f"Platillo con ID {item['platillo_id']} no encontrado.")
                    return redirect('comedor:createOrder')
                except Exception as e:
                    messages.error(request, f"Error al crear pedido: {str(e)}")
                    return redirect('comedor:createOrder')
            
            # Verificar que el total calculado coincida
            if abs(total_calculado - total_carrito) > Decimal('0.01'):
                messages.error(request, "Error en el cálculo del total del carrito.")
                return redirect('comedor:createOrder')
            
            # Crear los créditos diarios para cada pedido
            for pedido in pedidos_creados:
                CreditoDiario.objects.create(
                    pedido=pedido,
                    tutorId=tutor_actual,
                    profesorId=profesor_actual,
                    monto=pedido.total,
                    fecha=date.today()
                )
            
            # Actualizar crédito total (descontar el total del carrito)
            try:
                if is_admin:
                    credito_usuario = (Credito.objects.get(profesorId=profesor_actual) 
                                     if profesor_actual 
                                     else Credito.objects.get(tutorId=tutor_actual))
                else:
                    credito_usuario = (Credito.objects.get(profesorId=profesorRequest) 
                                     if is_profesor 
                                     else Credito.objects.get(tutorId=tutor_actual))
                
                credito_usuario.monto -= total_carrito
                credito_usuario.save()
                
                # Mensajes de advertencia sobre el crédito
                if credito_usuario.monto <= 0:
                    messages.warning(request, "Tu crédito ha llegado a 0 o es negativo. Es necesario recargar para futuros pedidos.")
                elif 0 < credito_usuario.monto <= 100:
                    messages.info(request, f"Tu crédito actual es ${credito_usuario.monto}. Te recomendamos recargar pronto.")
                
            except Credito.DoesNotExist:
                messages.error(request, "No se encontró crédito disponible para este usuario.")
                # Eliminar pedidos creados si no hay crédito
                for pedido in pedidos_creados:
                    pedido.delete()
                return redirect('comedor:createOrder')
            
            messages.success(request, f"¡Orden creada exitosamente! Se procesaron {len(pedidos_creados)} platillos por un total de ${total_carrito}.")
            return redirect('core:dashboard')
            
        except json.JSONDecodeError:
            messages.error(request, "Error al procesar los datos del carrito.")
            return redirect('comedor:createOrder')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('comedor:createOrder')
    
    # GET request - código existente para mostrar el formulario
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
            'user_type': 'tutor',
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
            'user_type': 'profesor',
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
                "id": f"Tutor_{tutor.id}",
                "type": "Tutor",
                "nombre": f"{tutor.usuario.user.first_name} {tutor.usuario.user.last_name} - Tutor",
            })
        
        for profesor in profesores:
            combined_users.append({
                "id": f"Profesor_{profesor.id}",
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
            'user_type': 'admin',
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
            }
            if new_status not in status_map:
                return JsonResponse({"success": False, "error": "Status inválido"}, status=400)
            
            pedido_id = int(order_id.replace("order-", ""))
            pedido = Pedido.objects.get(id=pedido_id)
            empleado = Empleados.objects.filter(usuario__email=request.user.username).first()
            
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
    archivo_hoy = generar_reporte_gastos_diarios()
    
    # 2. Generar reporte para una fecha específica
    fecha_especifica = date(2025, 8, 20)
    archivo_fecha = generar_reporte_gastos_diarios(
        fecha_reporte=fecha_especifica,
        nombre_archivo="reporte_especial.xlsx"
    )
    
    # 3. Generar reporte para un rango de fechas (última semana)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(days=7)
    archivo_rango = generar_reporte_rango_fechas(fecha_inicio, fecha_fin)

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