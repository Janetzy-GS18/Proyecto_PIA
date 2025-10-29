"""Vistas principales del sistema de ventas (Chalooo)."""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistroClienteForm, LoginClienteForm

from .models import Producto, Venta, DetalleVenta, Cliente, Usuario


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
    carrito_items = request.session.get("carrito", {})
    carrito_items[str(producto_id)] = carrito_items.get(str(producto_id), 0) + 1
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
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('chalooo:carrito')

    # Verifica que el usuario esté registrado como cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)  # pylint: disable=no-member
    except Cliente.DoesNotExist:  # pylint: disable=no-member
        return render(request, "chalooo/checkout.html",
                        {"error": "Debes registrarte como cliente."})

    # Preparar los productos del carrito
    items = []
    total = Decimal('0.00')
    for producto_id, cantidad in carrito_items.items():
        producto = get_object_or_404(Producto, id_producto=producto_id)
        subtotal = producto.precio * cantidad
        items.append({'producto': producto, 'cantidad': cantidad, 'subtotal': subtotal})
        total += subtotal

    # Si se confirma la compra (método POST)
    if request.method == "POST":
        venta = Venta.objects.create(cliente=cliente, total=0)  # pylint: disable=no-member
        for item in items:
            DetalleVenta.objects.create(  # pylint: disable=no-member
                venta=venta,
                producto=item['producto'],
                cantidad=item['cantidad'],
                subtotal=item['subtotal']
            )
            # Actualiza stock
            item['producto'].stock -= item['cantidad']
            item['producto'].save()

        # Actualiza total
        venta.total = total
        venta.save()

        # Vaciar carrito
        request.session['carrito'] = {}
        messages.success(request, "¡Compra confirmada con éxito!")
        return redirect('chalooo:confirmacion')

    # Si es una vista GET (mostrar resumen antes de confirmar)
    contexto = {'items': items, 'total': total}
    return render(request, "chalooo/checkout.html", contexto)


# ------------------------- INICIO DE SESIÓN -------------------------

def login_view(request):
    """Permite iniciar sesión a clientes registrados."""
    if request.method == "POST":
        formulario = LoginClienteForm(request, data=request.POST)
        if formulario.is_valid():
            correo = formulario.cleaned_data.get("username")
            contrasena = formulario.cleaned_data.get("password")
            print("Intentando login:", correo)  # Debug temporal
            usuario = authenticate(request, username=correo, password=contrasena)
            if usuario is not None:
                login(request, usuario)
                messages.success(request, f"Bienvenido/a, {usuario.nombre_s}")
                return redirect("chalooo:index")
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
        else:
            messages.error(request, "Verifica tus datos.")
    else:
        formulario = LoginClienteForm()
    return render(request, "chalooo/login.html", {"formulario": formulario})


# ------------------------- CIERRE DE SESIÓN -------------------------

@login_required
def logout_view(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("chalooo:index")


# ------------------------- REGISTRO -------------------------

def registro(request):
    """Permite registrar nuevos clientes en el sistema."""
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["contrasena"] != form.cleaned_data["confirmar_contrasena"]:
                messages.error(request, "Las contraseñas no coinciden.")
            else:
                usuario = Usuario.objects.create_user(
                    correo=form.cleaned_data["correo"],
                    nombre_s=form.cleaned_data["nombre_s"],
                    apellido_s=form.cleaned_data["apellido_s"],
                    password=form.cleaned_data["contrasena"]
                )
                # Crear cliente vinculado
                Cliente.objects.create(usuario=usuario, direccion="") # pylint: disable=no-member
                # Iniciar sesión automática
                login(request, usuario)
                messages.success(request, "Registro exitoso. ¡Bienvenido!")
                return redirect("chalooo:index")
    else:
        form = RegistroClienteForm()

    return render(request, "chalooo/registro.html", {"form": form})
