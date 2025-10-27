"""Vistas principales del sistema de ventas (Chalooo)."""

from django.shortcuts import render
from .models import Producto

def index(request):
    """Página principal del sistema."""
    return render(request, "index.html")

def productos(request):
    """Muestra todos los productos del catalogo."""
    datos = {'productos': Producto.objects.all()}  # pylint: disable=no-member
    return render(request, "chalooo/productos.html", context=datos)

def carrito(request):
    """Muestra todos los productos dentro del carrito."""
    return render(request, "chalooo/carrito.html")

def checkout(request):
    """Muestra todos los..."""
    return render(request, "chalooo/checkout.html")

def confirmacion(request):
    """Muestra todos los..."""
    return render(request, "chalooo/confirmacion.html")
