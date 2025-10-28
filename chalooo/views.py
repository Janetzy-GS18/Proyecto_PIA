"""Vistas principales del sistema de ventas (Chalooo)."""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Producto, Venta, DetalleVenta, Cliente


# ------------------------- PÁGINA PRINCIPAL -------------------------
def index(request):
    """Página principal del sistema."""
    return render(request, "index.html")


# ------------------------- PRODUCTOS -------------------------
def productos(request):
    """Muestra todos los productos del catálogo."""
    contexto = {"productos": Producto.objects.all()}  # pylint: disable=no-member
    return render(request, "chalooo/productos.html", context=contexto)

# ------------------------- CARRITO ITEMS-------------------------

def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito de sesión."""
    producto_sesion = get_object_or_404(Producto, id_producto=producto_id)  # pylint: disable=unused-variable
    carrito_items  = request.session.get("carrito", {})
    carrito_items [str(producto_id)] = carrito_items .get(str(producto_id), 0) + 1
    request.session["carrito"] = carrito_items

    return redirect("chalooo:carrito")

def carrito(request):
    """Muestra el contenido actual del carrito."""
    carrito_sesion = request.session.get('carrito', {})
    items = []
    total = Decimal('0.00')

    for producto_id, cantidad in carrito_sesion.items():
        producto = get_object_or_404(Producto, id_producto=producto_id)
        subtotal = producto.precio * cantidad
        items.append({'producto': producto, 'cantidad': cantidad, 'subtotal': subtotal})
        total += subtotal

    contexto = {'items': items, 'total': total}
    return render(request, "chalooo/carrito.html", contexto)

# ------------------------- CHECKOUT -------------------------

@login_required
def checkout(request):
    """Confirma la compra y genera una venta."""
    carrito_items = request.session.get('carrito', {})
    if not carrito_items:
        return redirect('chalooo:carrito')

    # Verifica que el usuario sea cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user) # pylint: disable=no-member
    except Cliente.DoesNotExist: # pylint: disable=no-member
        return render(
            request, "chalooo/checkout.html",
            {"error": "Debes registrarte como cliente."})

    # Crea la venta
    venta = Venta.objects.create(cliente=cliente, total=0) # pylint: disable=no-member

    total = Decimal('0.00')
    for producto_id, cantidad in carrito.items(): # pylint: disable=no-member
        producto = get_object_or_404(Producto, id_producto=producto_id)
        detalle = DetalleVenta.objects.create( # pylint: disable=no-member
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            subtotal=producto.precio * cantidad
        )
        total += detalle.subtotal

    # Actualiza el total y limpia carrito
    venta.total = total
    venta.save()
    request.session['carrito'] = {}

    return redirect('chalooo:confirmacion')

def confirmacion(request):
    """Pantalla final de compra"""
    return render(request, "chalooo/confirmacion.html")
