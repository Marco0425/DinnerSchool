from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
from django.db import transaction

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
                
                # Crear registro positivo en CreditoDiario
                creditoDiario = CreditoDiario.objects.create(
                    tutorId=tutor, 
                    monto=Decimal(credito),  # Positivo para créditos
                    fecha=date.today()
                )
                
                # Actualizar o crear el registro en Credito (saldo total)
                nuevoCredito, created = Credito.objects.get_or_create(
                    tutorId=tutor, 
                    defaults={'monto': credito, 'fecha': date.today()}
                )
                if not created:
                    # Si ya existía, sumar el nuevo monto al existente
                    nuevoCredito.monto += Decimal(str(credito))
                    nuevoCredito.fecha = date.today()  # Actualizar fecha
                    nuevoCredito.save()
                
                messages.success(request, f"Crédito de ${credito} asignado exitosamente. Saldo actual: ${nuevoCredito.monto}")
                return redirect('comedor:credit')
                
            except Tutor.DoesNotExist:
                messages.error(request, "Tutor no encontrado.")
                
        elif "profesor_" in tutor_id and credito:
            try:
                profesor = Empleados.objects.get(id=int(tutor_id.split('_')[1]))
                
                # Crear registro positivo en CreditoDiario
                creditoDiario = CreditoDiario.objects.create(
                    profesorId=profesor, 
                    monto=Decimal(credito),  # Positivo para créditos
                    fecha=date.today()
                )
                
                # Actualizar o crear el registro en Credito (saldo total)
                nuevoCredito, created = Credito.objects.get_or_create(
                    profesorId=profesor, 
                    defaults={'monto': credito, 'fecha': date.today()}
                )
                if not created:
                    # Si ya existía, sumar el nuevo monto al existente
                    nuevoCredito.monto += Decimal(str(credito))
                    nuevoCredito.fecha = date.today()  # Actualizar fecha
                    nuevoCredito.save()
                
                messages.success(request, f"Crédito de ${credito} asignado exitosamente. Saldo actual: ${nuevoCredito.monto}")
                return redirect('comedor:credit')
                
            except Empleados.DoesNotExist:
                messages.error(request, "Profesor no encontrado.")
        else:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect('comedor:createCredit')
    
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
    
    return render(request, 'Credit/credit_form_view.html', {'users': all_users})
    
def cancelOrder(request, pedido_id):
    """
    Vista para cancelar un pedido y reembolsar el crédito
    """
    try:
        with transaction.atomic():
            # Obtener el pedido
            pedido = get_object_or_404(Pedido, id=pedido_id)
            
            # Verificar que el pedido pertenezca al usuario actual
            user_email = request.user.username
            pedido_user_email = None
            
            if pedido.alumnoId:
                pedido_user_email = pedido.alumnoId.tutorId.usuario.email
            elif pedido.profesorId:
                pedido_user_email = pedido.profesorId.usuario.email
            
            if pedido_user_email != user_email:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes permisos para cancelar este pedido'
                }, status=403)
            
            # Verificar que el pedido se pueda cancelar (solo pendiente o en preparación)
            if pedido.status not in [0, 1]:  # 0=Pendiente, 1=En preparación
                return JsonResponse({
                    'success': False,
                    'message': 'No se puede cancelar un pedido que ya está completado o entregado'
                }, status=400)
            
            # Calcular el total a reembolsar
            total_reembolso = pedido.total
            
            # Buscar el crédito correspondiente
            credito = None
            if pedido.alumnoId:
                credito = Credito.objects.filter(tutorId=pedido.alumnoId.tutorId).first()
            elif pedido.profesorId:
                credito = Credito.objects.filter(profesorId=pedido.profesorId).first()
            
            if not credito:
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontró el crédito asociado al usuario'
                }, status=404)
            
            # Reembolsar el crédito
            credito.monto += Decimal(str(total_reembolso))
            credito.save()
            
            # Marcar el pedido como cancelado
            pedido.status = 4  # Asumiendo que 4 = Cancelado
            pedido.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Pedido #{pedido_id} cancelado exitosamente. Se reembolsaron ${total_reembolso} a tu cuenta.',
                'nuevo_credito': float(credito.monto),
                'total_reembolsado': float(total_reembolso)
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)
        
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

def orderHistory(request):
    """
    Vista para ver el historial de pedidos.
    Esta vista se encarga de mostrar el historial de pedidos realizados.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que redirige al dashboard.
    """ 
    if request.user.is_authenticated:
        is_tutor = request.user.groups.filter(name='Tutor').exists()
        is_profesor = Empleados.objects.filter(usuario__email=request.user.username, puesto='Profesor').exists()
        is_admin = request.user.is_staff
        """
        Vista para ver el historial de pedidos.
        Muestra el historial de pedidos filtrado por tipo de usuario, con paginación.
        """
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para ver el historial de pedidos.")
            return redirect("core:dashboard")
        
        user = request.user
        is_admin = user.is_staff
        is_profesor = False
        is_tutor = False
        pedidos_queryset = None
        
        # Profesor
        try:
            is_profesor = Empleados.objects.filter(usuario__email=user.username, puesto='Profesor').exists()
        except Exception:
            is_profesor = False
        # Tutor
        try:
            is_tutor = user.groups.filter(name='Tutor').exists()
        except Exception:
            is_tutor = False

        if is_admin:
            pedidos_queryset = Pedido.objects.select_related('alumnoId', 'profesorId', 'platillo').all().order_by('-fecha')
        elif is_profesor:
            empleado = Empleados.objects.filter(usuario__email=user.username, puesto='Profesor').first()
            pedidos_queryset = Pedido.objects.select_related('alumnoId', 'profesorId', 'platillo').filter(profesorId=empleado).order_by('-fecha')
        elif is_tutor:
            tutor = Tutor.objects.filter(usuario__email=user.username).first()
            alumnos = Alumnos.objects.filter(tutorId=tutor)
            pedidos_queryset = Pedido.objects.select_related('alumnoId', 'profesorId', 'platillo').filter(alumnoId__in=alumnos).order_by('-fecha')
        else:
            pedidos_queryset = Pedido.objects.none()

        # Paginación
        paginator = Paginator(pedidos_queryset, 10)
        page_number = request.GET.get('page')
        orders_page_obj = paginator.get_page(page_number)

        # Construir lista de pedidos para la tabla
        order_list = []
        for pedido in orders_page_obj:
            # Determinar nombre de usuario asociado
            if pedido.alumnoId:
                usuario_nombre = f"{pedido.alumnoId.nombre} {pedido.alumnoId.paterno}"
            elif pedido.profesorId:
                usuario_nombre = f"{pedido.profesorId.usuario.nombre} {pedido.profesorId.usuario.paterno}"
            else:
                usuario_nombre = "-"
            order_list.append({
                'id': pedido.id,
                'usuario': usuario_nombre,
                'platillo': pedido.platillo.nombre if pedido.platillo else '-',
                'cantidad': pedido.cantidad,
                'turno': pedido.get_turno_label() or pedido.turno,
                'fecha': pedido.fecha.strftime('%d/%m/%Y'),
                'status': pedido.get_status_label() or pedido.status,
                'total': pedido.total,
            })

        # Solo el admin puede eliminar
        can_delete = is_admin

        context = {
            'order_list': order_list,
            'orders_page_obj': orders_page_obj,
            'can_delete': can_delete,
        }
        return render(request, 'Orders/orders_history_view.html', context) 
    
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
                        total=subtotal,
                        fecha=date.today() if datetime.now().hour < 18 else date.today() + timedelta(days=1),
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
                    monto= -pedido.total,
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
    if creditoProfesor and creditoProfesor.monto < -1500:
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

@login_required
def order_details_api(request, order_id):
    """
    Vista para obtener los detalles de un pedido específico vía API.
    Esta vista se encarga de devolver la información completa de un pedido
    incluyendo sus items y totales.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
        order_id: ID del pedido a consultar.
    Returns:
        JsonResponse: Respuesta JSON con los detalles del pedido.
    """
    try:
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=order_id)
        
        # Verificar que el pedido pertenezca al usuario actual
        user_email = request.user.username
        pedido_user_email = None
        
        if pedido.alumnoId:
            pedido_user_email = pedido.alumnoId.tutorId.usuario.email
        elif pedido.profesorId:
            pedido_user_email = pedido.profesorId.usuario.email
        
        # Verificar permisos: el pedido debe pertenecer al usuario o ser admin/empleado
        is_admin = request.user.is_staff
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()
        
        if not is_admin and not is_employee and pedido_user_email != user_email:
            return JsonResponse({
                'error': 'No tienes permisos para ver este pedido'
            }, status=403)
        
        # Procesar ingredientes del platillo
        try:
            ingredientes_platillo = ast.literal_eval(pedido.ingredientePlatillo) if pedido.ingredientePlatillo else []
        except (ValueError, SyntaxError):
            ingredientes_platillo = []
        
        # Preparar datos del pedido
        order_data = {
            'id': pedido.id,
            'fecha': pedido.fecha.strftime('%d/%m/%Y'),
            'turno_label': pedido.get_turno_label(),
            'status_label': pedido.get_status_label(),
            'total': str(pedido.total),
            'items': [
                {
                    'platillo_nombre': pedido.platillo.nombre,
                    'cantidad': getattr(pedido, 'cantidad', 1),  # Cantidad por defecto 1 si no existe el campo
                    'subtotal': str(pedido.total),
                    'ingredientes': ingredientes_platillo,
                    'nota': pedido.nota or ''
                }
            ]
        }
        
        return JsonResponse(order_data)
        
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)

@login_required
def modify_order_view(request, order_id):
    """
    Vista para mostrar la página de modificación de un pedido.
    Esta vista se encarga de renderizar el formulario para modificar un pedido existente.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
        order_id: ID del pedido a modificar.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza el formulario de modificación.
    """
    try:
        # Obtener el pedido
        pedido = get_object_or_404(Pedido, id=order_id)
        
        # Verificar que el pedido pertenezca al usuario actual
        user_email = request.user.username
        pedido_user_email = None
        
        if pedido.alumnoId:
            pedido_user_email = pedido.alumnoId.tutorId.usuario.email
        elif pedido.profesorId:
            pedido_user_email = pedido.profesorId.usuario.email
        
        # Verificar permisos
        is_admin = request.user.is_staff
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()
        
        if not is_admin and not is_employee and pedido_user_email != user_email:
            messages.error(request, 'No tienes permisos para modificar este pedido.')
            return redirect('core:dashboard')
        
        # Verificar que el pedido se pueda modificar (solo pendiente)
        if pedido.status != 0:  # 0 = Pendiente
            messages.error(request, 'Solo se pueden modificar pedidos en estado pendiente.')
            return redirect('core:dashboard')
        
        # Obtener todos los platillos disponibles
        platillos = Platillo.objects.all()
        
        # Procesar ingredientes del pedido actual
        try:
            ingredientes_actuales = ast.literal_eval(pedido.ingredientePlatillo) if pedido.ingredientePlatillo else []
        except (ValueError, SyntaxError):
            ingredientes_actuales = []
        
        # Preparar contexto para el template
        context = {
            'pedido': pedido,
            'platillos': [
                {
                    "id": platillo.id,
                    "nombre": platillo.nombre,
                    "ingredientes": json.dumps([
                        Ingredientes.objects.get(id=int(ing)).nombre 
                        for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') 
                        if ing
                    ]),
                    "precio": float(platillo.precio)
                } for platillo in platillos
            ],
            'pedido_data': {
                'id': pedido.id,
                'platillo_id': pedido.platillo.id,
                'platillo_nombre': pedido.platillo.nombre,
                'ingredientes_seleccionados': ingredientes_actuales,
                'nota': pedido.nota or '',
                'cantidad': getattr(pedido, 'cantidad', 1),
                'turno': pedido.turno,
                'total_actual': float(pedido.total)
            },
            'is_modification': True,
            'user_type': 'tutor' if pedido.alumnoId else 'profesor'
        }
        
        # Procesar el POST para actualizar el pedido
        if request.method == "POST":
            try:
                with transaction.atomic():
                    # Obtener datos del formulario
                    nuevo_platillo_id = request.POST.get("platillo_id")
                    nuevos_ingredientes = request.POST.get("ingredientes", "[]")
                    nueva_nota = request.POST.get("nota", "")
                    nueva_cantidad = int(request.POST.get("cantidad", 1))
                    nuevo_turno = int(request.POST.get("turno"))
                    
                    # Obtener el nuevo platillo
                    nuevo_platillo = get_object_or_404(Platillo, id=nuevo_platillo_id)
                    
                    # Calcular el nuevo total
                    nuevo_total = nuevo_platillo.precio * nueva_cantidad
                    diferencia_precio = nuevo_total - pedido.total
                    
                    # Verificar crédito si el precio aumenta
                    if diferencia_precio > 0:
                        credito = None
                        if pedido.alumnoId:
                            credito = Credito.objects.filter(tutorId=pedido.alumnoId.tutorId).first()
                        elif pedido.profesorId:
                            credito = Credito.objects.filter(profesorId=pedido.profesorId).first()
                        
                        if not credito or credito.monto < diferencia_precio:
                            messages.error(request, 'No hay crédito suficiente para esta modificación.')
                            return render(request, 'Orders/modify_order_view.html', context)
                        
                        # Descontar la diferencia del crédito
                        credito.monto -= diferencia_precio
                        credito.save()
                    
                    elif diferencia_precio < 0:
                        # Si el precio disminuye, devolver la diferencia al crédito
                        credito = None
                        if pedido.alumnoId:
                            credito = Credito.objects.filter(tutorId=pedido.alumnoId.tutorId).first()
                        elif pedido.profesorId:
                            credito = Credito.objects.filter(profesorId=pedido.profesorId).first()
                        
                        if credito:
                            credito.monto += abs(diferencia_precio)
                            credito.save()
                    
                    # Actualizar el pedido
                    pedido.platillo = nuevo_platillo
                    pedido.ingredientePlatillo = nuevos_ingredientes
                    pedido.nota = nueva_nota
                    if hasattr(pedido, 'cantidad'):
                        pedido.cantidad = nueva_cantidad
                    pedido.turno = nuevo_turno
                    pedido.total = nuevo_total
                    pedido.save()
                    
                    # Actualizar el crédito diario si existe
                    try:
                        credito_diario = CreditoDiario.objects.get(pedido=pedido)
                        credito_diario.monto = -nuevo_total
                        credito_diario.save()
                    except CreditoDiario.DoesNotExist:
                        pass
                    
                    messages.success(request, f'Pedido #{pedido.id} modificado exitosamente.')
                    return redirect('core:dashboard')
                    
            except Exception as e:
                messages.error(request, f'Error al modificar el pedido: {str(e)}')
                return render(request, 'Orders/modify_order_view.html', context)
        
        return render(request, 'Orders/modify_order_view.html', context)
        
    except Pedido.DoesNotExist:
        messages.error(request, 'Pedido no encontrado.')
        return redirect('core:dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('core:dashboard')

def accountStatements(request):
    """
    Vista para manejar los estados de cuenta.
    Esta vista se encarga de mostrar los estados de cuenta de tutores y profesores.
    Args:
        request: Objeto HttpRequest que contiene la solicitud del usuario.
    Returns:
        HttpResponse: Respuesta HTTP que renderiza la vista de estados de cuenta.
    """
    if request.user.is_authenticated:
        # Obtener todos los tutores y profesores para los dropdowns
        tutores = Tutor.objects.all().order_by('usuario__nombre', 'usuario__paterno')
        profesores = Empleados.objects.filter(puesto='Profesor').order_by('usuario__nombre', 'usuario__paterno')
        
        # Crear lista combinada con estructura uniforme para el dropdown
        all_users = []
        
        # Agregar tutores con información de sus alumnos
        for tutor in tutores:
            alumnos = Alumnos.objects.filter(tutorId=tutor.id).all()
            if alumnos:
                # Crear string con información de los alumnos
                str_alumnos = ", ".join([
                    f"{alumno.nombre} {alumno.paterno} {alumno.materno or ''} - {getChoiceLabel(NIVELEDUCATIVO, alumno.nivelEducativo.nivel)} - {getChoiceLabel(GRADO, alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO, alumno.nivelEducativo.grupo)}"
                    for alumno in alumnos
                ])
                
                all_users.append({
                    'id': f'tutor_{tutor.id}',
                    'nombre': f"{tutor.usuario.nombre} {tutor.usuario.paterno} - Tutor",
                    'descripcion': str_alumnos,
                    'tipo': 'Tutor'
                })
            else:
                # Tutor sin alumnos
                all_users.append({
                    'id': f'tutor_{tutor.id}',
                    'nombre': f"{tutor.usuario.nombre} {tutor.usuario.paterno} - Tutor",
                    'descripcion': 'Sin alumnos asignados',
                    'tipo': 'Tutor'
                })
        
        # Agregar profesores
        for profesor in profesores:
            all_users.append({
                'id': f'profesor_{profesor.id}',
                'nombre': f"{profesor.usuario.nombre} {profesor.usuario.paterno} - Profesor",
                'descripcion': f"Profesor - {profesor.usuario.nombre} {profesor.usuario.paterno}",
                'tipo': 'Profesor'
            })
        
        context = {
            'tutores': tutores,  # Mantenemos esto por compatibilidad
            'profesores': profesores,  # Mantenemos esto por compatibilidad
            'all_users': all_users,  # Nueva estructura combinada
        }
        return render(request, 'accountStatements/estado_cuenta.html', context)
    else:
        return redirect('core:signInUp')

@csrf_exempt
def get_movimientos(request):
    """
    Vista AJAX para obtener los movimientos de un usuario específico.
    Esta vista se encarga de procesar las solicitudes AJAX para obtener 
    los movimientos financieros de tutores y profesores desde CreditoDiario.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    user_id = request.POST.get('user_id')
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')
    
    if not all([user_id, fecha_inicio, fecha_fin]):
        return JsonResponse({'success': False, 'message': 'Faltan parámetros requeridos'})
    
    # Parsear el user_id para determinar tipo y ID
    if user_id.startswith('tutor_'):
        user_type = 'tutor'
        user_pk = user_id.replace('tutor_', '')
    elif user_id.startswith('profesor_'):
        user_type = 'profesor'
        user_pk = user_id.replace('profesor_', '')
    else:
        return JsonResponse({'success': False, 'message': 'ID de usuario inválido'})
    
    # Convertir fechas
    try:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    except ValueError as e:
        return JsonResponse({'success': False, 'message': f'Formato de fecha inválido: {str(e)}'})
    
    try:
        movimientos = []
        user_info = {}
        
        if user_type == 'tutor':
            try:
                tutor = Tutor.objects.get(id=user_pk)
            except Tutor.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Tutor no encontrado'})
            
            user_info = {
                'nombre': f"{tutor.usuario.nombre} {tutor.usuario.paterno} {tutor.usuario.materno or ''}".strip(),
                'tipo': 'Tutor',
                'alumnos': []
            }
            
            # Obtener alumnos del tutor
            try:
                alumnos = Alumnos.objects.filter(tutorId=tutor)
                for alumno in alumnos:
                    nivel_info = 'N/A'
                    grado_info = 'N/A' 
                    grupo_info = 'N/A'
                    
                    if hasattr(alumno, 'nivelEducativo') and alumno.nivelEducativo:
                        if hasattr(alumno.nivelEducativo, 'nivel'):
                            nivel_info = getChoiceLabel(NIVELEDUCATIVO, alumno.nivelEducativo.nivel)
                        if hasattr(alumno.nivelEducativo, 'grado'):
                            grado_info = getChoiceLabel(GRADO, alumno.nivelEducativo.grado)
                        if hasattr(alumno.nivelEducativo, 'grupo'):
                            grupo_info = getChoiceLabel(GRUPO, alumno.nivelEducativo.grupo)
                    
                    user_info['alumnos'].append({
                        'nombre': f"{alumno.nombre} {alumno.paterno} {alumno.materno or ''}".strip(),
                        'nivel': nivel_info,
                        'grado': grado_info,
                        'grupo': grupo_info
                    })
            except Exception:
                pass  # Continuar sin alumnos si hay error
            
            # Obtener movimientos de CreditoDiario del tutor
            try:
                movimientos_credito = CreditoDiario.objects.filter(
                    tutorId=tutor,
                    fecha__range=[fecha_inicio, fecha_fin]
                ).order_by('fecha', 'id')
                
                for mov_credito in movimientos_credito:
                    if mov_credito.monto > 0:
                        tipo = 'credito'
                        tipo_display = 'Crédito Asignado'
                        descripcion = f"Crédito asignado de ${mov_credito.monto}"
                    else:
                        tipo = 'gasto'
                        tipo_display = 'Pedido'
                        if mov_credito.pedido:
                            descripcion = f"Pedido #{mov_credito.pedido.id}"
                            if mov_credito.pedido.platillo:
                                descripcion += f": {mov_credito.pedido.platillo.nombre}"
                            if mov_credito.pedido.alumnoId:
                                descripcion += f" (Alumno: {mov_credito.pedido.alumnoId.nombre})"
                        else:
                            descripcion = f"Gasto de ${abs(mov_credito.monto)}"
                    
                    movimientos.append({
                        'fecha': mov_credito.fecha,
                        'tipo': tipo,
                        'tipo_display': tipo_display,
                        'descripcion': descripcion,
                        'monto': float(mov_credito.monto),
                        'objeto': mov_credito,
                        'orden': 0 if mov_credito.monto > 0 else 1
                    })
            except Exception:
                pass  # Continuar si hay error
                
        else:  # profesor
            try:
                profesor = Empleados.objects.get(id=user_pk, puesto='Profesor')
            except Empleados.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Profesor no encontrado'})
            
            user_info = {
                'nombre': f"{profesor.usuario.nombre} {profesor.usuario.paterno} {profesor.usuario.materno or ''}".strip(),
                'tipo': 'Profesor',
                'alumnos': []
            }
            
            # Obtener movimientos de CreditoDiario del profesor
            try:
                movimientos_credito = CreditoDiario.objects.filter(
                    profesorId=profesor,
                    fecha__range=[fecha_inicio, fecha_fin]
                ).order_by('fecha', 'id')
                
                for mov_credito in movimientos_credito:
                    if mov_credito.monto > 0:
                        tipo = 'credito'
                        tipo_display = 'Crédito Asignado'
                        descripcion = f"Crédito asignado de ${mov_credito.monto}"
                    else:
                        tipo = 'gasto'
                        tipo_display = 'Pedido'
                        if mov_credito.pedido:
                            descripcion = f"Pedido #{mov_credito.pedido.id}"
                            if mov_credito.pedido.platillo:
                                descripcion += f": {mov_credito.pedido.platillo.nombre}"
                        else:
                            descripcion = f"Gasto de ${abs(mov_credito.monto)}"
                    
                    movimientos.append({
                        'fecha': mov_credito.fecha,
                        'tipo': tipo,
                        'tipo_display': tipo_display,
                        'descripcion': descripcion,
                        'monto': float(mov_credito.monto),
                        'objeto': mov_credito,
                        'orden': 0 if mov_credito.monto > 0 else 1
                    })
            except Exception:
                pass  # Continuar si hay error
        
        # Ordenar movimientos por fecha y tipo
        movimientos.sort(key=lambda x: (x['fecha'], x['orden'], x['objeto'].id))
        
        # Calcular saldo inicial
        saldo_inicial = 0.0
        try:
            if user_type == 'tutor':
                movimientos_anteriores = CreditoDiario.objects.filter(
                    tutorId=tutor,
                    fecha__lt=fecha_inicio
                )
            else:
                movimientos_anteriores = CreditoDiario.objects.filter(
                    profesorId=profesor,
                    fecha__lt=fecha_inicio
                )
            
            for mov_anterior in movimientos_anteriores:
                saldo_inicial += float(mov_anterior.monto)
        except Exception:
            pass  # Usar saldo inicial 0 si hay error
        
        # Procesar movimientos con saldos
        movimientos_procesados = []
        saldo_actual = saldo_inicial
        total_creditos = 0
        total_gastos = 0
        
        for mov in movimientos:
            saldo_anterior = saldo_actual
            saldo_actual += mov['monto']
            
            if mov['monto'] > 0:
                total_creditos += mov['monto']
            else:
                total_gastos += mov['monto']
            
            movimientos_procesados.append({
                'fecha': mov['fecha'].strftime('%d/%m/%Y'),
                'tipo': mov['tipo'],
                'tipo_display': mov['tipo_display'],
                'descripcion': mov['descripcion'],
                'monto': mov['monto'],
                'saldo_anterior': saldo_anterior,
                'saldo_final': saldo_actual
            })
        
        # Obtener saldo actual real
        saldo_actual_real = saldo_actual
        try:
            if user_type == 'tutor':
                credito_obj = Credito.objects.filter(tutorId=tutor).first()
            else:
                credito_obj = Credito.objects.filter(profesorId=profesor).first()
            
            if credito_obj:
                saldo_actual_real = float(credito_obj.monto)
        except Exception:
            pass  # Usar saldo calculado si hay error
        
        resumen = {
            'total_creditos': total_creditos,
            'total_gastos': total_gastos,
            'saldo_actual': saldo_actual_real
        }
        
        return JsonResponse({
            'success': True,
            'user_info': user_info,
            'movimientos': movimientos_procesados,
            'resumen': resumen
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error interno del servidor: {str(e)}'
        })