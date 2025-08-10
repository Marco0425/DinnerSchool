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

from comedor.models import Ingredientes, Platillo, Pedido, Credito, CreditoDiario, Noticias
from core.models import Alumnos, Usuarios, Tutor
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
    if request.method == "POST":
        nombre = request.POST.get("ingrediente")
        if nombre:
            nuevoIngrediente = Ingredientes(nombre=nombre)
            nuevoIngrediente.save()
            messages.success(request, "Ingrediente creado exitosamente.")
            return redirect('comedor:ingredients')
        else:
            messages.error(request, "Por favor, ingresa un nombre para el ingrediente.")
    else:
        return render(request, 'Ingredients/ingredients_form_view.html')

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
        return render(request, 'Ads/ads_list_view.html')
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
    if request.method == "POST":
        pass
        titulo = request.POST.get("titulo")
        contenido = request.POST.get("contenido")

        crearNoticia = Noticias(
            tipo=titulo, 
            contenido=contenido,
            activo=True,
            autor=Usuarios.objects.get(user=request.user),
        )
    else:
        messages.error(request, "Por favor, completa todos los campos.")
    return render(request, 'Ads/ads_form_view.html')

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
        
        for pedido in Pedido.objects.all():
            order = {
                "id": f"order-{pedido.id}",
                "platillo": pedido.platillo.nombre,
                "ingredientes": pedido.ingredientePlatillo,
                "nota": pedido.nota,
                "alumno": f"{pedido.alumnoId.nombre} {pedido.alumnoId.paterno}",
                "nivel": getChoiceLabel(NIVELEDUCATIVO, pedido.nivelEducativo.nivel),
                "turno": "Comida",
                "status": "pendiente",
            }
            orders.append(order)
        print(orders)
        return render(request, 'orders/orders_kanban_view.html', {'orders': orders})
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
        print(request.POST)
        orden = request.POST.get("platillo")
        ordenIngredientes = request.POST.getlist("ingredientes")
        ordenNotas = request.POST.get("notas")
        ordenAlumno = request.POST.get("alumno")
        ordenTurno = request.POST.get("turno")
        precio = request.POST.get("precio")
        print("ordenTurno", ordenTurno)

        platillo = Platillo.objects.get(id=orden)
        nuevaOrden = Pedido.objects.update_or_create(
            platillo=platillo,
            ingredientePlatillo=", ".join(ordenIngredientes),
            nota=ordenNotas,
            alumnoId=Alumnos.objects.get(id=ordenAlumno),
            nivelEducativo=Alumnos.objects.get(id=ordenAlumno).nivelEducativo,
            turno=ordenTurno,
            total=float(precio)
        )
        
        return redirect('core:dashboard')
    else:
        platillos = Platillo.objects.all()
        
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
                    ]
                }
        
        return render(request, 'orders/orders_form_view.html', context)

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
    if request.method == "POST":
        nombre = request.POST.get("platillo")
        ingredientes = request.POST.getlist("ingredientes")
        precio = request.POST.get("precio")
        if nombre and ingredientes:
            nuevoPlatillo = Platillo(nombre=nombre, precio=precio, ingredientes= str(ingredientes))
            nuevoPlatillo.save()
            messages.success(request, "Platillo creado exitosamente.")
            return redirect('comedor:saucers')
        else:
            messages.error(request, "Por favor, ingresa un nombre para el platillo.")
    else:
        ingredientes = Ingredientes.objects.all()
        return render(request, 'Saucer/saucer_form_view.html', {'ingredientes': ingredientes})
