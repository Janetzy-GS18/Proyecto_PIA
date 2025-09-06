from django.shortcuts import render
from .models import Usuario, Cliente, TelefonoCliente, Empleado, Producto, Venta, DetalleVenta


# Página principal
def index(request):
    return render(request, "index.html")


# ---------- Usuarios ----------
def usuarios(request):
    datos = {
        'usuarios': Usuario.objects.all()
    }
    return render(request, "usuarios.html", context=datos)


# ---------- Clientes ----------
def clientes(request):
    datos = {
        'clientes': Cliente.objects.all()
    }
    return render(request, "clientes.html", context=datos)


# ---------- Teléfonos de clientes ----------
def telefonos(request):
    datos = {
        'telefonos': TelefonoCliente.objects.all()
    }
    return render(request, "telefonos.html", context=datos)


# ---------- Empleados ----------
def empleados(request):
    datos = {
        'empleados': Empleado.objects.all()
    }
    return render(request, "empleados.html", context=datos)


# ---------- Productos ----------
def productos(request):
    datos = {
        'productos': Producto.objects.all()
    }
    return render(request, "productos.html", context=datos)


# ---------- Ventas y detalles ----------
def ventas(request):
    datos = {
        'ventas': Venta.objects.all(),
    }
    return render(request, "ventas.html", context=datos)

# ---------- Detalles de Ventas ----------
def detalle_venta(request, venta_id):
    venta = Venta.objects.get(pk=venta_id)  # Busca la venta en la BD
    detalles = DetalleVenta.objects.filter(venta=venta)  # Trae los productos de esa venta
    return render(request, 'detalle_venta.html', {'venta': venta, 'detalles': detalles})

