from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.apps import apps
from django.core.paginator import Paginator
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from comedor.models import Ingredientes, Platillo, Pedido, Orden, Credito, CreditoDiario, Noticias
from django.db.models import Q
from core.models import Alumnos, Usuarios, Tutor, Empleados
from core.choices import *
from .choices import *
from core.herramientas import *
from .reports import generar_reporte_gastos_diarios, generar_reporte_rango_fechas
from .notifications import notificar_nuevo_pedido

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
        # Filtro por nombre
        nombre = request.GET.get('nombre', '').strip()
        ingredients = Ingredientes.objects.all()
        if nombre:
            ingredients = ingredients.filter(nombre__icontains=nombre)
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
        nombre = request.POST.get("ingrediente", "").title().strip()  # Capitalizar nombre
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
        creditos = Credito.objects.select_related(
            'tutorId__usuario',
            'profesorId__usuario',
        ).prefetch_related('tutorId__alumnos_set').all()
        for user in creditos:
            userCreditos.append({
                'id': user.id,
                'nombre': user.tutorId.usuario.nombre if user.tutorId else user.profesorId.usuario.nombre,
                'paterno': user.tutorId.usuario.paterno if user.tutorId else user.profesorId.usuario.paterno,
                'materno': user.tutorId.usuario.materno if user.tutorId else user.profesorId.usuario.materno,
                'monto': float(user.monto) if isinstance(user.monto, Decimal) else '0.00',
                'tipo': 'Profesor' if user.profesorId else 'Tutor',
                'alumnos': user.tutorId.alumnos_set.all() if user.tutorId else '',
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
                
            if pedido_user_email != user_email and not request.user.is_staff:
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
            credito.fecha = date.today()
            credito.save()
            
            # Marcar el pedido como cancelado
            pedido.status = 4  # Asumiendo que 4 = Cancelado
            pedido.save()
            # Registrar el movimiento en CreditoDiario como positivo (reembolso)
            CreditoDiario.objects.create(
                pedido=pedido,
                tutorId=pedido.alumnoId.tutorId if pedido.alumnoId else None,
                profesorId=pedido.profesorId if pedido.profesorId else None,
                monto=Decimal(str(total_reembolso)),
                fecha=date.today()
            )
            
            if request.user.is_staff:
                message = f'Pedido #{pedido_id} cancelado exitosamente por el administrador. Se reembolsaron ${total_reembolso} al usuario.'
                messages.success(request, message)
                return redirect('comedor:orderHistory')

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


@login_required
@require_POST
def cancelOrden(request, orden_id):
    """Cancela una Orden completa (todos sus Pedidos) y reembolsa el crédito."""
    try:
        with transaction.atomic():
            orden = get_object_or_404(
                Orden.objects.prefetch_related('items'),
                id=orden_id
            )

            owner_email = None
            if orden.alumnoId:
                owner_email = orden.alumnoId.tutorId.usuario.email
            elif orden.profesorId:
                owner_email = orden.profesorId.usuario.email

            if owner_email != request.user.username and not request.user.is_staff:
                return JsonResponse({'success': False, 'message': 'Sin permisos'}, status=403)

            if orden.status not in [0, 1]:
                return JsonResponse({'success': False, 'message': 'La orden no se puede cancelar en su estado actual'}, status=400)

            credito = None
            if orden.alumnoId:
                credito = Credito.objects.select_for_update().filter(tutorId=orden.alumnoId.tutorId).first()
            elif orden.profesorId:
                credito = Credito.objects.select_for_update().filter(profesorId=orden.profesorId).first()

            if not credito:
                return JsonResponse({'success': False, 'message': 'Crédito no encontrado'}, status=404)

            total_reembolso = orden.total
            tutor_obj = orden.alumnoId.tutorId if orden.alumnoId else None

            for pedido in orden.items.all():
                pedido.status = 4
                pedido.save(update_fields=['status'])
                CreditoDiario.objects.create(
                    pedido=pedido,
                    tutorId=tutor_obj,
                    profesorId=orden.profesorId,
                    monto=pedido.total,
                    fecha=date.today(),
                )

            credito.monto += total_reembolso
            credito.fecha = date.today()
            credito.save()

            orden.status = 4
            orden.save(update_fields=['status'])

            return JsonResponse({
                'success': True,
                'message': f'Orden #{orden_id} cancelada. Se reembolsaron ${total_reembolso} a tu cuenta.',
                'nuevo_credito': float(credito.monto),
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)


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
        titulo = request.POST.get("titulo", "").title().strip()  # Capitalizar título
        contenido = request.POST.get("contenido", "").strip()  # Solo quitar espacios del contenido
        imagen = request.FILES.get("imagen")
        
        # Procesar la imagen si existe
        if titulo and contenido:
            if noticia:
                noticia.titulo = titulo
                noticia.contenido = contenido
                noticia.activo = True if request.POST.get("estado") == "1" else False
                noticia.tipoAnuncio = request.POST.get("tipoAnuncio")
                # Solo actualizar la imagen si se subió una nueva
                if imagen:
                    noticia.rutaImagen = imagen
                noticia.save()
                messages.success(request, "Anuncio actualizado exitosamente.")
                return redirect('comedor:ads')
            else:
                try:
                    usuario = Usuarios.objects.get(user=request.user)
                    nueva_noticia = Noticias(
                        titulo=titulo,
                        contenido=contenido,
                        activo=True if request.POST.get("estado") == "1" else False,
                        autor=usuario,
                        tipoAnuncio=request.POST.get("tipoAnuncio"),
                        rutaImagen=imagen
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
        today = date.today()
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()

        status_map = {0: "pendiente", 1: "en preparacion", 2: "finalizado", 3: "entregado"}

        try:
            ordenes_hoy = (
                Orden.objects
                .filter(fecha=today, status__in=[0, 1, 2, 3])
                .select_related('alumnoId__nivelEducativo', 'profesorId__usuario', 'encargadoId__usuario')
                .prefetch_related('items__platillo')
                .order_by('turno', 'alumnoId', 'profesorId')
            )

            grouped_orders = []
            for orden in ordenes_hoy:
                is_profesor = orden.profesorId is not None
                if orden.esVentaDirecta:
                    user_name = orden.clienteNombre or "Venta Directa"
                    user_level = "Venta Directa"
                elif is_profesor:
                    user_name = f"{orden.profesorId.usuario.nombre} {orden.profesorId.usuario.paterno}"
                    user_level = "Profesor"
                else:
                    user_name = f"{orden.alumnoId.nombre} {orden.alumnoId.paterno}"
                    nv = orden.nivelEducativo
                    user_level = (
                        f"{getChoiceLabel(NIVELEDUCATIVO, nv.nivel)} - "
                        f"{getChoiceLabel(GRADO, nv.grado)}{getChoiceLabel(GRUPO, nv.grupo)}"
                        if nv else ""
                    )

                platillos = []
                for pedido in orden.items.all():
                    try:
                        ingredientes = ast.literal_eval(pedido.ingredientePlatillo) if pedido.ingredientePlatillo else []
                    except (ValueError, SyntaxError):
                        ingredientes = []
                    platillos.append({
                        "id": pedido.id,
                        "nombre": pedido.platillo.nombre,
                        "ingredientes": ingredientes,
                        "nota": pedido.nota,
                        "cantidad": pedido.cantidad,
                        "precio": pedido.total,
                    })

                grouped_orders.append({
                    "id": orden.id,
                    "orden_id": orden.id,
                    "user_name": user_name,
                    "user_level": user_level,
                    "turno": orden.get_turno_label(),
                    "turno_num": orden.turno,
                    "fecha": orden.fecha,
                    "is_profesor": is_profesor,
                    "is_venta_directa": orden.esVentaDirecta,
                    "is_employee": is_employee,
                    "status": status_map.get(orden.status, "pendiente"),
                    "status_num": orden.status,
                    "encargado": (
                        f"{orden.encargadoId.usuario.nombre} {orden.encargadoId.usuario.paterno}"
                        if orden.encargadoId else "No asignado"
                    ),
                    "encargado_id": orden.encargadoId.id if orden.encargadoId else None,
                    "platillos": platillos,
                    "total_cantidad": sum(p["cantidad"] for p in platillos),
                    "total_precio": orden.total,
                })

            return render(request, 'Orders/orders_kanban_view.html', {'orders': grouped_orders})

        except Exception as e:
            import traceback
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

        # Base queryset según tipo de usuario
        if is_admin:
            Pedidos = Pedido.objects.all()
        elif is_profesor:
            Pedidos = Pedido.objects.filter(profesorId__usuario__email=request.user.username)
        elif is_tutor:
            Pedidos = Pedido.objects.filter(alumnoId__tutorId__usuario__email=request.user.username)
        else:
            Pedidos = Pedido.objects.none()

        # Filtros por GET
        usuario = request.GET.get('usuario', '').strip()
        platillo = request.GET.get('platillo', '').strip()
        turno = request.GET.get('turno', '')
        estatus = request.GET.get('estatus', '')
        fecha_inicio = request.GET.get('fecha_inicio', '')
        fecha_fin = request.GET.get('fecha_fin', '')
        total_min = request.GET.get('total_min', '')
        total_max = request.GET.get('total_max', '')

        if usuario:
            usuario = usuario.strip()
            palabras = usuario.split()
            if len(palabras) == 2:
                nombre, apellido = palabras
                Pedidos = Pedidos.filter(
                    Q(alumnoId__nombre__iexact=nombre, alumnoId__paterno__iexact=apellido) |
                    Q(profesorId__usuario__nombre__iexact=nombre, profesorId__usuario__paterno__iexact=apellido) |
                    Q(alumnoId__tutorId__usuario__email__icontains=usuario) |
                    Q(profesorId__usuario__email__icontains=usuario)
                )
            else:
                Pedidos = Pedidos.filter(
                    Q(alumnoId__nombre__icontains=usuario) |
                    Q(alumnoId__paterno__icontains=usuario) |
                    Q(profesorId__usuario__nombre__icontains=usuario) |
                    Q(profesorId__usuario__paterno__icontains=usuario) |
                    Q(alumnoId__tutorId__usuario__email__icontains=usuario) |
                    Q(profesorId__usuario__email__icontains=usuario)
                )
        if platillo:
            Pedidos = Pedidos.filter(platillo__nombre__icontains=platillo)
        if turno != '':
            Pedidos = Pedidos.filter(turno=turno)
        if estatus != '':
            Pedidos = Pedidos.filter(status=estatus)
        if fecha_inicio:
            Pedidos = Pedidos.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            Pedidos = Pedidos.filter(fecha__lte=fecha_fin)
        if total_min:
            Pedidos = Pedidos.filter(total__gte=total_min)
        if total_max:
            Pedidos = Pedidos.filter(total__lte=total_max)

        Pedidos = Pedidos.order_by('-fecha')

        # Paginación
        paginator = Paginator(Pedidos, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Preservar filtros activos al paginar
        query_params = request.GET.copy()
        query_params.pop('page', None)
        query_string = query_params.urlencode()

        context = {
            'is_staff': is_admin,
            'order_list': page_obj,
            'page_obj': page_obj,
            'query_string': query_string,
        }

        return render(request, 'Orders/orders_history_view.html', context)
    else:
        return redirect('core:signInUp')


def _nombres_ingredientes(platillo, all_ingredients):
    if not platillo.ingredientes:
        return []
    ids = platillo.ingredientes.strip('[]').replace("'", "").split(', ')
    return [
        all_ingredients[int(ing)]
        for ing in ids
        if ing.strip() and ing.strip().lstrip('-').isdigit() and int(ing) in all_ingredients
    ]


def _crear_ordenes_desde_carrito(cart_items, fecha, orden_extra, pedido_extra_fn=None):
    items_por_turno = {}
    for item in cart_items:
        items_por_turno.setdefault(item['turno'], []).append(item)

    ordenes_creadas = []
    pedidos_creados = []

    for turno_num, items in items_por_turno.items():
        total_turno = sum(Decimal(str(i['subtotal'])) for i in items)
        orden = Orden.objects.create(
            turno=turno_num,
            fecha=fecha,
            total=total_turno,
            **orden_extra,
        )
        ordenes_creadas.append(orden)

        for item in items:
            platillo = Platillo.objects.get(id=item['platillo_id'])
            subtotal = Decimal(str(item['subtotal']))
            extra = pedido_extra_fn(item) if pedido_extra_fn else {}
            pedido = Pedido.objects.create(
                orden=orden,
                platillo=platillo,
                ingredientePlatillo=item.get('ingredientes', ''),
                nota=item.get('notas', ''),
                cantidad=item['cantidad'],
                turno=turno_num,
                total=subtotal,
                fecha=fecha,
                **extra,
            )
            pedidos_creados.append(pedido)

    return ordenes_creadas, pedidos_creados


def directSale(request):
    """
    Vista de Punto de Venta para ventas directas (mostrador), sin alumno,
    tutor ni profesor asociado. Reservada al administrador.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('core:dashboard')

    if request.method == "POST":
        try:
            cart_data = request.POST.get("cart_data")
            cliente_nombre = request.POST.get("cliente_nombre", "").strip()

            if not cart_data:
                messages.error(request, "El carrito está vacío.")
                return redirect('comedor:createDirectOrder')

            cart_items = json.loads(cart_data)
            if not cart_items:
                messages.error(request, "No hay items en el carrito.")
                return redirect('comedor:createDirectOrder')

            encargado_actual = Empleados.objects.filter(usuario__email=request.user.username).first()
            fecha_venta = date.today()

            with transaction.atomic():
                ordenes_creadas, pedidos_creados = _crear_ordenes_desde_carrito(
                    cart_items,
                    fecha_venta,
                    orden_extra={
                        'status': 3,
                        'encargadoId': encargado_actual,
                        'esVentaDirecta': True,
                        'clienteNombre': cliente_nombre or None,
                    },
                    pedido_extra_fn=lambda item: {
                        'status': 3,
                        'encargadoId': encargado_actual,
                        'esVentaDirecta': True,
                    },
                )
                total_venta = sum((orden.total for orden in ordenes_creadas), Decimal('0'))

            for orden in ordenes_creadas:
                notificar_nuevo_pedido(orden)

            messages.success(request, f"¡Venta directa registrada! {len(pedidos_creados)} platillo(s) — total ${total_venta}.")
            return redirect('comedor:createDirectOrder')

        except Platillo.DoesNotExist as e:
            messages.error(request, f"Platillo no encontrado: {str(e)}")
            return redirect('comedor:createDirectOrder')
        except json.JSONDecodeError:
            messages.error(request, "Error al procesar los datos del carrito.")
            return redirect('comedor:createDirectOrder')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('comedor:createDirectOrder')

    platillos = Platillo.objects.filter(disponible=True)
    all_ingredients = {ing.id: ing.nombre for ing in Ingredientes.objects.all()}

    context = {
        "Platillos": [
            {
                "id": platillo.id,
                "nombre": platillo.nombre,
                "ingredientes": json.dumps(_nombres_ingredientes(platillo, all_ingredients)),
                "precio": float(platillo.precio)
            } for platillo in platillos
        ],
    }
    return render(request, 'Orders/direct_sale_form_view.html', context)


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
            # Bloquear pedidos después de las 2:00 PM (excepto admins)
            if not request.user.is_staff and 14 <= timezone.localtime().hour < 20:
                messages.error(request, "El registro de pedidos está cerrado de 2:00 PM a 8:00 PM. Después de las 8:00 PM podrás registrar pedidos para el día siguiente.")
                return redirect('core:dashboard')

            # Obtener datos del carrito
            cart_data = request.POST.get("cart_data")
            alumno_id = request.POST.get("alumno")
            tutor_profesor = request.POST.get("tutor")
            total_carrito = Decimal(request.POST.get("total", "0"))
            fechaPedido = request.POST.get("fecha")
            
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
            
            # Verificar total antes de tocar la BD
            total_calculado = sum(Decimal(str(item['subtotal'])) for item in cart_items)
            if abs(total_calculado - total_carrito) > Decimal('0.01'):
                messages.error(request, "Error en el cálculo del total del carrito.")
                return redirect('comedor:createOrder')

            if fechaPedido:
                fecha_entrega = date.fromisoformat(fechaPedido)
            else:
                hora_actual = timezone.localtime().hour
                fecha_entrega = date.today() if hora_actual < 14 else date.today() + timedelta(days=1)

            try:
                with transaction.atomic():
                    ordenes_creadas, pedidos_creados = _crear_ordenes_desde_carrito(
                        cart_items,
                        fecha_entrega,
                        orden_extra={
                            'alumnoId': alumno_obj if not is_profesor else None,
                            'profesorId': profesor_actual if profesor_actual else None,
                            'nivelEducativo': alumno_obj.nivelEducativo if alumno_obj else None,
                        },
                        pedido_extra_fn=lambda item: {
                            'alumnoId': alumno_obj if not is_profesor else None,
                            'nivelEducativo': alumno_obj.nivelEducativo if alumno_obj else None,
                            'profesorId': profesor_actual if profesor_actual else None,
                        },
                    )

                    for pedido in pedidos_creados:
                        CreditoDiario.objects.create(
                            pedido=pedido,
                            tutorId=tutor_actual,
                            profesorId=profesor_actual,
                            monto=-pedido.total,
                            fecha=fecha_entrega
                        )

                    if is_admin:
                        credito_usuario = (Credito.objects.get(profesorId=profesor_actual)
                                         if profesor_actual
                                         else Credito.objects.get(tutorId=tutor_actual))
                    else:
                        credito_usuario = (Credito.objects.get(profesorId=profesorRequest)
                                         if is_profesor
                                         else Credito.objects.get(tutorId=tutor_actual))

                    credito_usuario.monto -= total_carrito
                    credito_usuario.fecha = date.today()
                    credito_usuario.save()

                for orden in ordenes_creadas:
                    notificar_nuevo_pedido(orden)

            except Platillo.DoesNotExist as e:
                messages.error(request, f"Platillo no encontrado: {str(e)}")
                return redirect('comedor:createOrder')
            except Credito.DoesNotExist:
                messages.error(request, "No se encontró crédito disponible para este usuario.")
                return redirect('comedor:createOrder')
            except Exception as e:
                messages.error(request, f"Error al crear la orden: {str(e)}")
                return redirect('comedor:createOrder')

            if credito_usuario.monto <= 0:
                messages.warning(request, "Tu crédito ha llegado a 0 o es negativo. Es necesario recargar para futuros pedidos.")
            elif 0 < credito_usuario.monto <= 100:
                messages.info(request, f"Tu crédito actual es ${credito_usuario.monto}. Te recomendamos recargar pronto.")

            messages.success(request, f"¡Orden creada exitosamente! {len(ordenes_creadas)} turno(s), {len(pedidos_creados)} platillos — total ${total_carrito}.")
            return redirect('core:dashboard')
            
        except json.JSONDecodeError:
            messages.error(request, "Error al procesar los datos del carrito.")
            return redirect('comedor:createOrder')
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return redirect('comedor:createOrder')
    
    # GET request - código existente para mostrar el formulario
    # Bloquear acceso al formulario después de las 2:00 PM (excepto admins)
    if not request.user.is_staff and 14 <= timezone.localtime().hour < 20:
        messages.error(request, "El registro de pedidos está cerrado de 2:00 PM a 8:00 PM. Después de las 8:00 PM podrás registrar pedidos para el día siguiente.")
        return redirect('core:dashboard')

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
    all_ingredients = {ing.id: ing.nombre for ing in Ingredientes.objects.all()}

    if is_tutor:
        platillos = Platillo.objects.all().filter(disponible=True)
        # Para tutores: solo mostrar sus alumnos, no el campo de selección de usuario
        tutor = Tutor.objects.get(usuario__email=request.user.username)
        students = Alumnos.objects.filter(tutorId=tutor)
        
        context = {
            "Platillos": [
                {
                    "id": platillo.id,
                    "nombre": platillo.nombre,
                    "ingredientes": json.dumps(_nombres_ingredientes(platillo, all_ingredients)),
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
        platillos = Platillo.objects.all().filter(disponible=True)
        # Para profesores: no mostrar campos de usuario ni alumnos
        context = {
            "Platillos": [
                {
                    "id": platillo.id,
                    "nombre": platillo.nombre,
                    "ingredientes": json.dumps(_nombres_ingredientes(platillo, all_ingredients)),
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
                    "ingredientes": json.dumps(_nombres_ingredientes(platillo, all_ingredients)),
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
    
    context["today"] = date.today().isoformat()
    return render(request, 'Orders/orders_form_view.html', context)

def update_order_status(request):
    """Actualiza el status de una Orden y todos sus Pedidos vía AJAX."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        orden_id = data.get("order_id")
        new_status = data.get("new_status")

        if not orden_id or not new_status:
            return JsonResponse({"success": False, "error": "Datos incompletos"}, status=400)

        status_map = {"pendiente": 0, "en preparacion": 1, "finalizado": 2, "entregado": 3}
        if new_status not in status_map:
            return JsonResponse({"success": False, "error": "Status inválido"}, status=400)

        status_num = status_map[new_status]
        empleado = Empleados.objects.filter(usuario__email=request.user.username).first()

        with transaction.atomic():
            orden = Orden.objects.get(id=int(orden_id))
            orden.status = status_num
            orden.encargadoId = empleado
            orden.save()
            orden.items.all().update(status=status_num, encargadoId=empleado)

        encargado_nombre = (
            f"{empleado.usuario.nombre} {empleado.usuario.paterno}" if empleado else "No asignado"
        )
        return JsonResponse({"success": True, "encargado": encargado_nombre})

    except Orden.DoesNotExist:
        return JsonResponse({"success": False, "error": "Orden no encontrada"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



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
        # Filtros por GET
        nombre = request.GET.get('nombre', '').strip()
        precio_min = request.GET.get('precio_min', '').strip()
        precio_max = request.GET.get('precio_max', '').strip()

        saucers_qs = Platillo.objects.all()
        if nombre:
            saucers_qs = saucers_qs.filter(nombre__icontains=nombre)
        if precio_min:
            saucers_qs = saucers_qs.filter(precio__gte=precio_min)
        if precio_max:
            saucers_qs = saucers_qs.filter(precio__lte=precio_max)

        paginator = Paginator(saucers_qs, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        all_ingredients = {ing.id: ing.nombre for ing in Ingredientes.objects.all()}
        saucers_for_template = []
        for platillo in page_obj:
            ingredient_ids = platillo.ingredientes.strip('[]').replace("'", "").split(', ')
            ingredient_names = [
                all_ingredients[int(ing)]
                for ing in ingredient_ids
                if ing.strip() and ing.strip().lstrip('-').isdigit() and int(ing) in all_ingredients
            ]
            saucers_for_template.append({
                'id': platillo.id,
                'nombre': platillo.nombre,
                'ingredientes': ingredient_names,
                'precio': str(platillo.precio).replace(",", "."),
                'disponible': platillo.disponible
            })

        context = {
            'saucers_list': saucers_for_template,
            'saucers_page_obj': page_obj
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
            platillo.precio = str(platillo.precio).replace(",", ".")
        except Platillo.DoesNotExist:
            platillo = None

    ingredientes = Ingredientes.objects.all()

    def _selected_ids(pl):
        if not pl or not pl.ingredientes:
            return []
        return [i.strip() for i in pl.ingredientes.strip('[]').replace("'", "").split(', ') if i.strip()]

    if request.method == "POST":
        nombre = request.POST.get("platillo", "").title().strip()  # Capitalizar nombre del platillo
        ingredientes_ids = request.POST.getlist("ingredientes")
        precio = request.POST.get("precio")
        disponible = False if request.POST.get("disponible") == None else True

        if not precio:
            messages.error(request, "Por favor, ingresa un precio para el platillo.")
            return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo, 'selected_ingredientes': ingredientes_ids})

        if nombre and ingredientes_ids:
            if platillo:
                platillo.nombre = nombre
                platillo.precio = precio
                platillo.ingredientes = str(ingredientes_ids)
                platillo.disponible = disponible
                platillo.save()
                messages.success(request, "Platillo actualizado exitosamente.")
            else:
                nuevoPlatillo = Platillo(nombre=nombre, precio=precio, ingredientes=str(ingredientes_ids), disponible=disponible)
                nuevoPlatillo.save()
                messages.success(request, "Platillo creado exitosamente.")
            return redirect('comedor:saucers')
        else:
            messages.error(request, "Por favor, ingresa un nombre para el platillo y selecciona ingredientes.")

        # Si hay error, mostrar el form con el contexto
        return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo, 'selected_ingredientes': ingredientes_ids})

    return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo, 'selected_ingredientes': _selected_ids(platillo)})

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
def order_details_api(request, orden_id):
    try:
        orden = get_object_or_404(
            Orden.objects.prefetch_related('items__platillo'),
            id=orden_id
        )

        is_admin = request.user.is_staff
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()

        owner_email = None
        if orden.alumnoId:
            owner_email = orden.alumnoId.tutorId.usuario.email
        elif orden.profesorId:
            owner_email = orden.profesorId.usuario.email

        if not is_admin and not is_employee and owner_email != request.user.username:
            return JsonResponse({'error': 'No tienes permisos para ver esta orden'}, status=403)

        items = []
        for pedido in orden.items.all():
            try:
                ings = ast.literal_eval(pedido.ingredientePlatillo) if pedido.ingredientePlatillo else []
            except (ValueError, SyntaxError):
                ings = []
            items.append({
                'platillo_nombre': pedido.platillo.nombre,
                'cantidad': pedido.cantidad,
                'subtotal': str(pedido.total),
                'ingredientes': ings,
                'nota': pedido.nota or '',
            })

        return JsonResponse({
            'id': orden.id,
            'fecha': orden.fecha.strftime('%d/%m/%Y'),
            'turno_label': orden.get_turno_label(),
            'status_label': orden.get_status_label(),
            'total': str(orden.total),
            'items': items,
        })

    except Exception as e:
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)

@login_required
def modify_order_view(request, orden_id):
    try:
        orden = get_object_or_404(
            Orden.objects.prefetch_related('items__platillo'),
            id=orden_id
        )

        is_admin = request.user.is_staff
        is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()

        owner_email = None
        if orden.alumnoId:
            owner_email = orden.alumnoId.tutorId.usuario.email
        elif orden.profesorId:
            owner_email = orden.profesorId.usuario.email

        if not is_admin and not is_employee and owner_email != request.user.username:
            messages.error(request, 'No tienes permisos para modificar esta orden.')
            return redirect('core:dashboard')

        if orden.status != 0:
            messages.error(request, 'Solo se pueden modificar órdenes en estado pendiente.')
            return redirect('core:dashboard')

        all_ingredients = {ing.id: ing.nombre for ing in Ingredientes.objects.all()}
        platillos = Platillo.objects.filter(disponible=True)

        items_data = []
        for pedido in orden.items.all():
            try:
                ings = ast.literal_eval(pedido.ingredientePlatillo) if pedido.ingredientePlatillo else []
            except (ValueError, SyntaxError):
                ings = []
            items_data.append({
                'platillo_id': pedido.platillo.id,
                'platillo_nombre': pedido.platillo.nombre,
                'precio': float(pedido.platillo.precio),
                'cantidad': pedido.cantidad,
                'nota': pedido.nota or '',
                'ingredientes': ings,
            })

        platillos_json = []
        for p in platillos:
            raw_ids = [i for i in p.ingredientes.strip('[]').replace("'", "").split(', ') if i]
            nombres_ings = [all_ingredients.get(int(i), '') for i in raw_ids if i.isdigit()]
            platillos_json.append({
                'id': p.id,
                'nombre': p.nombre,
                'precio': float(p.precio),
                'ingredientes': nombres_ings,
            })

        context = {
            'orden': orden,
            # No usar json.dumps(): |json_script ya serializa.
            'items_data_json': items_data,
            'platillos_json': platillos_json,
            'turno_label': orden.get_turno_label(),
        }

        if request.method == 'POST':
            try:
                cart = json.loads(request.POST.get('cart_json', '[]'))

                if not cart:
                    messages.error(request, 'El carrito no puede estar vacío.')
                    return render(request, 'Orders/modify_order_view.html', context)

                platillo_cache = {p.id: p for p in Platillo.objects.filter(
                    id__in=[item['platillo_id'] for item in cart]
                )}
                new_total = sum(
                    platillo_cache[item['platillo_id']].precio * int(item['cantidad'])
                    for item in cart
                )

                with transaction.atomic():
                    credito = None
                    if orden.alumnoId:
                        credito = Credito.objects.select_for_update().filter(
                            tutorId=orden.alumnoId.tutorId
                        ).first()
                    elif orden.profesorId:
                        credito = Credito.objects.select_for_update().filter(
                            profesorId=orden.profesorId
                        ).first()

                    if not credito:
                        messages.error(request, 'No se encontró el crédito asociado.')
                        return render(request, 'Orders/modify_order_view.html', context)

                    available = credito.monto + orden.total
                    if available < new_total:
                        messages.error(
                            request,
                            f'Crédito insuficiente. Disponible: ${available:.2f}, necesario: ${new_total:.2f}'
                        )
                        return render(request, 'Orders/modify_order_view.html', context)

                    # Delete old items (CreditoDiario cascade-deletes via FK)
                    orden.items.all().delete()

                    tutor_obj = orden.alumnoId.tutorId if orden.alumnoId else None
                    for item in cart:
                        pl = platillo_cache[item['platillo_id']]
                        cantidad = int(item['cantidad'])
                        subtotal = pl.precio * cantidad
                        pedido = Pedido.objects.create(
                            orden=orden,
                            platillo=pl,
                            ingredientePlatillo=item.get('ingredientes', '[]'),
                            nota=item.get('nota') or None,
                            alumnoId=orden.alumnoId,
                            profesorId=orden.profesorId,
                            nivelEducativo=orden.nivelEducativo,
                            total=subtotal,
                            fecha=orden.fecha,
                            status=orden.status,
                            turno=orden.turno,
                            cantidad=cantidad,
                        )
                        CreditoDiario.objects.create(
                            fecha=orden.fecha,
                            monto=-subtotal,
                            tutorId=tutor_obj,
                            profesorId=orden.profesorId,
                            pedido=pedido,
                        )

                    credito.monto = available - new_total
                    credito.save()
                    orden.total = new_total
                    orden.save()

                messages.success(request, f'Orden #{orden.id} modificada exitosamente.')
                return redirect('core:dashboard')

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                messages.error(request, f'Datos inválidos: {str(e)}')
                return render(request, 'Orders/modify_order_view.html', context)
            except Exception as e:
                messages.error(request, f'Error al modificar la orden: {str(e)}')
                return render(request, 'Orders/modify_order_view.html', context)

        return render(request, 'Orders/modify_order_view.html', context)

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
            alumnos = Alumnos.objects.filter(tutorId=tutor.id).select_related('nivelEducativo')
            alumnos_list = []
            str_alumnos_parts = []
            for alumno in alumnos:
                alumnos_list.append({'id': alumno.id, 'nombre': f"{alumno.nombre} {alumno.paterno} {alumno.materno or ''}".strip()})
                str_alumnos_parts.append(
                    f"{alumno.nombre} {alumno.paterno} {alumno.materno or ''} - "
                    f"{getChoiceLabel(NIVELEDUCATIVO, alumno.nivelEducativo.nivel)} - "
                    f"{getChoiceLabel(GRADO, alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO, alumno.nivelEducativo.grupo)}"
                )
            all_users.append({
                'id': f'tutor_{tutor.id}',
                'nombre': f"{tutor.usuario.nombre} {tutor.usuario.paterno} - Tutor",
                'descripcion': ", ".join(str_alumnos_parts) if str_alumnos_parts else 'Sin alumnos asignados',
                'tipo': 'Tutor',
                'alumnos': alumnos_list,
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
    alumno_id = request.POST.get('alumno_id', '').strip() or None

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
                from django.db.models import Q as _Q
                movimientos_credito = CreditoDiario.objects.filter(
                    tutorId=tutor,
                    fecha__range=[fecha_inicio, fecha_fin]
                ).order_by('fecha', 'id')
                if alumno_id:
                    movimientos_credito = movimientos_credito.filter(
                        _Q(pedido__isnull=True) | _Q(pedido__alumnoId_id=alumno_id)
                    )
                
                for mov_credito in movimientos_credito:
                    if mov_credito.monto > 0 and mov_credito.pedido == None:  # Incluir solo créditos asignados o gastos con pedido
                        tipo = 'credito'
                        tipo_display = 'Crédito Asignado'
                        descripcion = f"Crédito asignado de ${mov_credito.monto}"
                    elif mov_credito.monto < 0 and mov_credito.pedido == None:  # Incluir deudas actualizadas sin pedido
                        tipo = 'Deuda'
                        tipo_display = 'Deuda'
                        descripcion = f"Deuda de ${abs(mov_credito.monto)}"
                    else:
                        tipo = 'gasto'
                        tipo_display = 'Pedido'
                        if mov_credito.pedido.status != 4:  # Excluir pedidos cancelados
                            descripcion = f"Pedido #{mov_credito.pedido.id}"
                            if mov_credito.pedido.platillo:
                                descripcion += f": {mov_credito.pedido.platillo.nombre}"
                            if mov_credito.pedido.alumnoId:
                                descripcion += f" (Alumno: {mov_credito.pedido.alumnoId.nombre})"
                        else:
                            if mov_credito.monto < 0:
                                tipo = 'Pedido Cancelado'
                                tipo_display = 'Pedido Cancelado'
                                descripcion = f"Pedido #{mov_credito.pedido.id}"
                                if mov_credito.pedido.platillo:
                                    descripcion += f": {mov_credito.pedido.platillo.nombre}"
                                if mov_credito.pedido.alumnoId:
                                    descripcion += f" (Alumno: {mov_credito.pedido.alumnoId.nombre})"
                            else:
                                tipo = 'Reembolso'
                                tipo_display = 'Reembolso'
                                descripcion = f"Pedido #{mov_credito.pedido.id}"
                                if mov_credito.pedido.alumnoId:
                                    descripcion += f" (Alumno: {mov_credito.pedido.alumnoId.nombre}) "
                                descripcion += f" Reembolso de ${abs(mov_credito.monto)} por pedido cancelado"
                    
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
                    if mov_credito.monto > 0 and mov_credito.pedido == None:  # Incluir solo créditos asignados o gastos con pedido
                        tipo = 'credito'
                        tipo_display = 'Crédito Asignado'
                        descripcion = f"Crédito asignado de ${mov_credito.monto}"
                        
                    elif mov_credito.monto < 0 and mov_credito.pedido == None:  # Incluir deudas actualizadas sin pedido
                        tipo = 'Deuda'
                        tipo_display = 'Deuda'
                        descripcion = f"Deuda de ${abs(mov_credito.monto)}"
                    else:
                        tipo = 'gasto'
                        tipo_display = 'Pedido'
                        if mov_credito.pedido.status != 4:
                            descripcion = f"Pedido #{mov_credito.pedido.id}"
                            if mov_credito.pedido.platillo:
                                descripcion += f": {mov_credito.pedido.platillo.nombre}"
                        else:
                            if mov_credito.monto < 0:
                                tipo = 'Pedido Cancelado'
                                tipo_display = 'Pedido Cancelado'
                                descripcion = f"Pedido #{mov_credito.pedido.id}"
                                if mov_credito.pedido.platillo:
                                    descripcion += f": {mov_credito.pedido.platillo.nombre}"
                            else:
                                tipo = 'Reembolso'
                                tipo_display = 'Reembolso'
                                descripcion = f" Reembolso de ${abs(mov_credito.monto)} por pedido cancelado #{mov_credito.pedido.id}"
                    
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
        
        # Calcular saldo inicial basado en el saldo actual real
        saldo_inicial = 0.0
        saldo_actual_real = 0.0
        
        try:
            # Obtener saldo actual real del modelo Credito
            if user_type == 'tutor':
                credito_obj = Credito.objects.filter(tutorId=tutor).first()
            else:
                credito_obj = Credito.objects.filter(profesorId=profesor).first()
            
            if credito_obj:
                saldo_actual_real = float(credito_obj.monto)
            
            # Calcular saldo inicial restando los movimientos posteriores al rango de fechas
            movimientos_posteriores = 0.0
            if user_type == 'tutor':
                movimientos_post = CreditoDiario.objects.filter(
                    tutorId=tutor,
                    fecha__gt=fecha_fin
                )
            else:
                movimientos_post = CreditoDiario.objects.filter(
                    profesorId=profesor,
                    fecha__gt=fecha_fin
                )
            
            for mov_post in movimientos_post:
                movimientos_posteriores += float(mov_post.monto)
            
            # Calcular saldo al final del período (sin movimientos posteriores)
            saldo_fin_periodo = saldo_actual_real - movimientos_posteriores
            
            # Calcular saldo inicial restando los movimientos del período seleccionado
            movimientos_periodo = 0.0
            if user_type == 'tutor':
                movimientos_per = CreditoDiario.objects.filter(
                    tutorId=tutor,
                    fecha__range=[fecha_inicio, fecha_fin]
                )
            else:
                movimientos_per = CreditoDiario.objects.filter(
                    profesorId=profesor,
                    fecha__range=[fecha_inicio, fecha_fin]
                )
            
            for mov_per in movimientos_per:
                movimientos_periodo += float(mov_per.monto)
            
            saldo_inicial = saldo_fin_periodo - movimientos_periodo
            
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
        
        # El saldo actual real ya se calculó arriba
        # saldo_actual_real ya contiene el valor correcto del modelo Credito
        
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
        
# Endpoint AJAX para órdenes agrupadas por estado (Kanban)
@require_GET
def kanban_orders_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)

    today = date.today()
    status_map = {0: "pendiente", 1: "en preparacion", 2: "finalizado", 3: "entregado"}
    is_employee = Empleados.objects.filter(usuario__email=request.user.username).exists()

    ordenes_hoy = (
        Orden.objects
        .filter(fecha=today, status__in=[0, 1, 2, 3])
        .select_related('alumnoId__nivelEducativo', 'profesorId__usuario', 'encargadoId__usuario')
        .prefetch_related('items__platillo')
        .order_by('turno', 'alumnoId', 'profesorId')
    )

    result = {"pendiente": [], "en preparacion": [], "finalizado": [], "entregado": [], "turno_activo": None}

    for orden in ordenes_hoy:
        is_profesor = orden.profesorId is not None
        if orden.esVentaDirecta:
            user_name = orden.clienteNombre or "Venta Directa"
            user_level = "Venta Directa"
        elif is_profesor:
            user_name = f"{orden.profesorId.usuario.nombre} {orden.profesorId.usuario.paterno}"
            user_level = "Profesor"
        else:
            user_name = f"{orden.alumnoId.nombre} {orden.alumnoId.paterno}"
            nv = orden.nivelEducativo
            user_level = (
                f"{getChoiceLabel(NIVELEDUCATIVO, nv.nivel)} - "
                f"{getChoiceLabel(GRADO, nv.grado)}{getChoiceLabel(GRUPO, nv.grupo)}"
                if nv else ""
            )

        platillos = []
        for pedido in orden.items.all():
            try:
                ingredientes = ast.literal_eval(pedido.ingredientePlatillo) if pedido.ingredientePlatillo else []
            except (ValueError, SyntaxError):
                ingredientes = []
            platillos.append({
                "id": pedido.id,
                "nombre": pedido.platillo.nombre,
                "ingredientes": ingredientes,
                "nota": pedido.nota,
                "cantidad": pedido.cantidad,
                "precio": float(pedido.total),
            })

        entry = {
            "id": orden.id,
            "orden_id": orden.id,
            "user_name": user_name,
            "user_level": user_level,
            "turno": orden.get_turno_label(),
            "turno_num": orden.turno,
            "fecha": str(orden.fecha),
            "is_profesor": is_profesor,
            "is_venta_directa": orden.esVentaDirecta,
            "is_employee": is_employee,
            "status": status_map.get(orden.status, "pendiente"),
            "status_num": orden.status,
            "encargado": (
                f"{orden.encargadoId.usuario.nombre} {orden.encargadoId.usuario.paterno}"
                if orden.encargadoId else "No asignado"
            ),
            "encargado_id": orden.encargadoId.id if orden.encargadoId else None,
            "platillos": platillos,
            "total_cantidad": sum(p["cantidad"] for p in platillos),
            "total_precio": float(orden.total),
        }
        status_label = status_map.get(orden.status, "pendiente")
        result[status_label].append(entry)

    return JsonResponse(result)
