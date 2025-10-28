"""Vistas principales del sistema de ventas (Chalooo)."""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegistroClienteForm, LoginClienteForm

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


# ------------------------- INICIO DE SESIÓN -------------------------

def iniciar_sesion(request):
    """Permite iniciar sesión a clientes registrados."""
    if request.method == "POST":
        formulario = LoginClienteForm(request, data=request.POST)
        if formulario.is_valid():
            correo = formulario.cleaned_data.get("username")
            contraseña = formulario.cleaned_data.get("password")
            usuario = authenticate(request, username=correo, password=contraseña)
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

# ------------------------- AUTENTICACIÓN -------------------------

def login_view(request):
    """Permite iniciar sesión con correo y contraseña."""
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")

        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect("chalooo:index")
        else:
            return render(request, "chalooo/login.html",
                        {"error": "Correo o contraseña incorrectos."})
    return render(request, "chalooo/login.html")


# ------------------------- REGISTRO -------------------------

def registro(request):
    """Permite registrar un nuevo cliente."""
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            contrasena = datos["contrasena"]
            confirmar = datos["confirmar_contrasena"]

            if contrasena != confirmar:
                messages.error(request, "Las contraseñas no coinciden.")
                return render(request, "chalooo/registro.html", {"form": form})

            # Crear usuario
            usuario = Usuario.objects.create_user(
                correo=datos["correo"],
                nombre_s=datos["nombre_s"],
                apellido_s=datos["apellido_s"],
                password=contrasena
            )

            # Crear cliente asociado
            Cliente.objects.create(usuario=usuario, direccion="Sin dirección definida") # pylint: disable=no-member

            messages.success(request, "Tu cuenta fue creada exitosamente.")
            return redirect("chalooo:login")
    else:
        form = RegistroClienteForm()

    return render(request, "chalooo/registro.html", {"form": form})
