from django.http import HttpResponse
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

from comedor.models import Ingredientes, Platillo, Pedido, Credito, CreditoDiario, Noticias
from core.models import Alumnos, Usuarios, Tutor, Empleados
from core.choices import *
from .choices import *
from core.herramientas import *

import json

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
            return redirect('comedor:ingredients')
        else:
            messages.error(request, "Por favor, ingresa un nombre para el ingrediente.")
        return render(request, 'Ingredients/ingredients_form_view.html', {'ingrediente': ingrediente})
    else:
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
        return render(request, 'credit/credit_list_view.html')
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
        if tutor_id and credito:
            tutor = Tutor.objects.get(id=tutor_id)
            nuevoCredito = CreditoDiario(tutor=tutor, credito=credito)
            nuevoCredito.save()
            messages.success(request, "Crédito creado exitosamente.")
            return redirect('comedor:credit')
        else:
            messages.error(request, "Por favor, completa todos los campos.")
    else:
        tutors = Tutor.objects.all()
        return render(request, 'credit/credit_form_view.html', {'tutors': tutors})
    
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
            else:
                try:
                    usuario = Usuarios.objects.get(user=request.user)
                except Usuarios.DoesNotExist:
                    messages.error(request, "No existe un perfil de usuario asociado a este usuario. Contacta al administrador.")
                    return render(request, 'Ads/ads_form_view.html', {'noticia': None})
                nueva_noticia = Noticias(
                    titulo=titulo,
                    contenido=contenido,
                    activo=True,
                    autor=usuario,
                )
                nueva_noticia.save()
                print('Nueva noticia creada:', nueva_noticia)
                messages.success(request, "Anuncio creado exitosamente.")
            return redirect('comedor:ads')
        else:
            messages.error(request, "Por favor, completa todos los campos.")
        context = {'noticia': noticia}
        return render(request, 'Ads/ads_form_view.html', context)
    else:
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
        
        from datetime import date
        today = date.today()
        status_map = {
            0: "pendiente",
            1: "en preparacion",
            2: "finalizado",
            3: "entregado",
            4: "cancelado",
        }
        for pedido in Pedido.objects.filter(fecha=today):
            is_profesor = pedido.profesorId is not None
            order = {
                "id": f"order-{pedido.id}",
                "platillo": pedido.platillo.nombre,
                "ingredientes": pedido.ingredientePlatillo,
                "nota": pedido.nota,
                "is_profesor": is_profesor,
                "alumno": f"{pedido.alumnoId.nombre} {pedido.alumnoId.paterno}" if not is_profesor else f"{pedido.profesorId.usuario} {pedido.profesorId.usuario.paterno}",
                "nivel": getChoiceLabel(NIVELEDUCATIVO, pedido.nivelEducativo.nivel) if not is_profesor else "Profesor",
                "turno": pedido.get_turno_label(),
                "status": status_map.get(pedido.status, "pendiente"),
                "encargado": f"{pedido.encargadoId.usuario.nombre} {pedido.encargadoId.usuario.paterno}" if pedido.encargadoId else "No asignado"
            }
            orders.append(order)
        print(orders)
        return render(request, 'Orders/orders_kanban_view.html', {'orders': orders})
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

        platillo = Platillo.objects.get(id=orden)
        nuevaOrden = Pedido.objects.update_or_create(
            platillo=platillo,
            ingredientePlatillo=", ".join(ordenIngredientes),
            nota=ordenNotas,
            alumnoId=Alumnos.objects.get(id=ordenAlumno) if not is_profesor else None,
            nivelEducativo=Alumnos.objects.get(id=ordenAlumno).nivelEducativo if not is_profesor else None,
            profesorId=Empleados.objects.get(usuario__email=request.user.username) if is_profesor else None,
            turno=ordenTurno,
            total=float(precio)
        )
        
        return redirect('core:dashboard')
    else:
        platillos = Platillo.objects.all()
        if request.user.groups.filter(name='Tutor').exists():
            tutor = Tutor.objects.get(usuario=Usuarios.objects.get(user=request.user))
            students = Alumnos.objects.filter(tutorId=tutor)
            context = {
                "Platillos": [
                    {
                        "id": platillo.id,
                        "nombre": platillo.nombre,
                        "ingredientes":json.dumps([Ingredientes.objects.get(id=int(ing)).nombre for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') if ing]),
                        "precio": float(platillo.precio)
                    } for platillo in platillos
                ],
                "Alumnos": [
                    {
                        "id": alumno.id,
                        "nombre": f"{alumno.nombre} {alumno.paterno} - {getChoiceLabel(NIVELEDUCATIVO,alumno.nivelEducativo.nivel)} - {getChoiceLabel(GRADO,alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO,alumno.nivelEducativo.grupo)}",
                        
                    } for alumno in students
                ],
                'is_tutor': request.user.groups.filter(name='Tutor').exists(),
                'is_employee': request.user.groups.filter(name='Employee').exists(),
                'is_admin': request.user.is_staff,
            }
        else:
            tutors = Tutor.objects.all()
            students = Alumnos.objects.all()
            context = {
                "Platillos": [
                    {
                        "id": platillo.id,
                        "nombre": platillo.nombre,
                        "ingredientes":json.dumps([Ingredientes.objects.get(id=int(ing)).nombre for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') if ing]),
                        "precio": float(platillo.precio)
                    } for platillo in platillos
                ],
                'is_tutor': request.user.groups.filter(name='Tutor').exists(),
                'is_employee': request.user.groups.filter(name='Employee').exists(),
                'is_admin': request.user.is_staff,
                "tutors": [
                    {
                        "id": tutor.id,
                        "nombre": tutor.usuario.user.first_name + " " + tutor.usuario.user.last_name,
                    } for tutor in tutors
                ],
                "Alumnos": [
                    {
                        "id": alumno.id,
                        "nombre": f"{alumno.nombre} {alumno.paterno} - {getChoiceLabel(NIVELEDUCATIVO,alumno.nivelEducativo.nivel)} - {getChoiceLabel(GRADO,alumno.nivelEducativo.grado)}{getChoiceLabel(GRUPO,alumno.nivelEducativo.grupo)}",
                        "tutor_id": alumno.tutorId.id
                    } for alumno in students
                ],
            }
        
        return render(request, 'Orders/orders_form_view.html', context)

@csrf_exempt
def update_order_status(request):
    """
    Vista para actualizar el status de un pedido vía AJAX.
    Espera POST con 'order_id' (ej: 'order-5') y 'new_status' (pendiente, en preparacion, finalizado).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            order_id = data.get("order_id")
            new_status = data.get("new_status")
            if not order_id or not new_status:
                return JsonResponse({"success": False, "error": "Datos incompletos"}, status=400)

            # Mapear status string a valor entero de STATUSPEDIDO
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
            from comedor.models import Pedido
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.status = status_map[new_status]
            pedido.save()
            return JsonResponse({"success": True})
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
        saucers = Platillo.objects.all()
        platillos = []
        for platillo in saucers:
            platillos.append({
                'id': platillo.id,
                'nombre': platillo.nombre,
                'ingredientes': [Ingredientes.objects.get(id=int(ing)).nombre for ing in platillo.ingredientes.strip('[]').replace("'", "").split(', ') if ing],
                'precio': platillo.precio
            })

        print(platillos)
        return render(request, 'Saucer/saucer_list_view.html', {'saucers': platillos})
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
        return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo})
    else:
        return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes, 'platillo': platillo})
