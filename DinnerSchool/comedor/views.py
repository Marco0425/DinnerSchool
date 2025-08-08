from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as django_logout
from comedor.models import Ingredientes, Platillo
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_POST
from django.apps import apps


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
        return render(request, 'ads/ads_list_view.html')
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
