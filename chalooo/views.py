"""Vistas principales del sistema de ventas (Chalooo)."""

from django.shortcuts import render
from .models import Usuario, Cliente, TelefonoCliente, Empleado, Producto, Venta, DetalleVenta


# Página principal
def index(request):
    """Página principal del sistema."""
    return render(request, "index.html")


# ---------- Usuarios ----------
def usuarios(request):
    """Muestra todos los usuarios registrados."""
    datos = {
        'usuarios': Usuario.objects.all()
    }
    return render(request, "chalooo/usuarios.html", context=datos)


# ---------- Clientes ----------
def clientes(request):
    """Muestra todos los clientes registrados."""
    datos = {
        'clientes': Cliente.objects.all() # pylint: disable=no-member
    }
    return render(request, "chalooo/clientes.html", context=datos)


# ---------- Teléfonos de clientes ----------
def telefonos(request):
    """Muestra todos los teléfonos registrados de los clientes."""
    datos = {
        'telefonos': TelefonoCliente.objects.all() # pylint: disable=no-member
    }
    return render(request, "chalooo/telefonos.html", context=datos)


# ---------- Empleados ----------
def empleados(request):
    """Muestra todos los empleados registrados."""
    datos = {
        'empleados': Empleado.objects.all() # pylint: disable=no-member
    }
    return render(request, "chalooo/empleados.html", context=datos)


# ---------- Productos ----------
def productos(request):
    """Muestra todos los productos disponibles."""
    datos = {
        'productos': Producto.objects.all() # pylint: disable=no-member
    }
    return render(request, "chalooo/productos.html", context=datos)


# ---------- Ventas y detalles ----------
def ventas(request):
    """Lista todas las ventas registradas."""
    datos = {
        'ventas': Venta.objects.all(), # pylint: disable=no-member
    }
    return render(request, "chalooo/ventas.html", context=datos)

# ---------- Detalles de Ventas ----------
def detalle_venta(request, venta_id):
    """Muestra los productos y detalles de una venta específica."""
    venta = Venta.objects.get(pk=venta_id)  # Busca la venta en la BD # pylint: disable=no-member
    detalles = DetalleVenta.objects.filter(venta=venta)  # Trae los productos de esa venta # pylint: disable=no-member
    return render(request, 'chalooo/detalle_venta.html', {'venta': venta, 'detalles': detalles})
