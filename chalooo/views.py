"""Vistas principales del sistema de ventas (Chalooo)."""

import os
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings

# Librerías para PDF y código de barras
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm

from .forms import RegistroClienteForm, LoginClienteForm
from .models import Producto, Venta, DetalleVenta, Cliente, TelefonoCliente


# ------------------------- PÁGINA PRINCIPAL -------------------------
def index(request):
    """Página principal del sistema."""
    return render(request, "index.html")


# ------------------------- PRODUCTOS -------------------------
def productos(request):
    """Muestra todos los productos del catálogo."""
    contexto = {"productos": Producto.objects.all()}  # pylint: disable=no-member
    return render(request, "chalooo/productos.html", context=contexto)


# ------------------------- CARRITO -------------------------

def agregar_al_carrito(request, producto_id):
    """Agrega producto al carrito verificando stock."""
    producto = get_object_or_404(Producto, id_producto=producto_id)
    carrito_agregar = request.session.get("carrito", {})
    cantidad_actual = carrito_agregar.get(str(producto_id), 0)

    if cantidad_actual + 1 > producto.stock:
        messages.warning(request, f"Solo hay {producto.stock} unidades de {producto.nombre}.")
        return redirect("chalooo:productos")

    carrito_agregar[str(producto_id)] = cantidad_actual + 1
    request.session["carrito"] = carrito_agregar
    messages.success(request, f"{producto.nombre} agregado al carrito.")
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


def actualizar_carrito(request):
    """Actualiza las cantidades del carrito desde el formulario."""
    if request.method == "POST":
        carrito_actualizar = request.session.get("carrito", {})
        for key, value in request.POST.items():
            if key.startswith("qty_"):
                prod_id = key.split("_")[1]
                try:
                    cantidad = int(value)
                    producto = get_object_or_404(Producto, id_producto=prod_id)

                    if cantidad <= 0:
                        carrito_actualizar.pop(str(prod_id), None)
                    elif cantidad > producto.stock:
                        carrito_actualizar[str(prod_id)] = producto.stock
                        messages.warning(request, f"Stock insuficiente para {producto.nombre}.")
                    else:
                        carrito_actualizar[str(prod_id)] = cantidad
                except ValueError:
                    continue
        request.session["carrito"] = carrito_actualizar
    return redirect("chalooo:carrito")


def eliminar_del_carrito(request, producto_id):
    """Elimina un producto del carrito."""
    carrito_eliminar = request.session.get("carrito", {})
    carrito_eliminar.pop(str(producto_id), None)
    request.session["carrito"] = carrito_eliminar
    messages.info(request, "Producto eliminado del carrito.")
    return redirect("chalooo:carrito")


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

        # Actualiza total
        venta.total = total
        venta.save()

        # Vaciar carrito
        request.session['carrito'] = {}
        messages.success(request, "¡Compra confirmada con éxito!")
        return redirect('chalooo:confirmacion', venta_id=venta.id_venta)

    return render(request, "chalooo/checkout.html", {'items': items, 'total': total})


# ------------------------- CONFIRMACIÓN -------------------------

@login_required
def confirmacion(request, venta_id):
    """Muestra confirmación de compra y opción de descargar recibo."""
    venta = get_object_or_404(Venta, id_venta=venta_id)
    return render(request, "chalooo/confirmacion.html", {"venta": venta})


# ------------------------- HISTORIAL -------------------------


@login_required
def historial_compras(request):
    """Muestra las ventas realizadas por el usuario."""
    cliente = get_object_or_404(Cliente, usuario=request.user)
    ventas = Venta.objects.filter(cliente=cliente).order_by('-fecha')  # pylint: disable=no-member
    return render(request, "chalooo/historial.html", {"ventas": ventas})


@login_required
def anular_venta(request, venta_id):
    """Permite al usuario anular su venta (si aún está completada)."""
    venta = get_object_or_404(Venta, id_venta=venta_id, cliente__usuario=request.user)
    if venta.estado == 'completada':
        venta.anular()
        messages.info(request, "La compra ha sido anulada y el stock fue restaurado.")
    else:
        messages.warning(request, "Esta venta ya está anulada.")
    return redirect('chalooo:historial')


# ------------------------- RECIBO PDF -------------------------


@login_required
def recibo_pdf(request, venta_id):  # pylint: disable=unused-argument
    """Genera un recibo en PDF con código de barras, logo y datos del cliente."""
    venta = get_object_or_404(Venta, id_venta=venta_id)
    detalles = venta.detalleventa_set.all()

    # Crear respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="recibo_venta_{venta_id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    _, height = A4

    # ---------------- Encabezado ----------------
    logo_path = os.path.join(
        settings.BASE_DIR, 'chalooo', 'static', 'chalooo', 'img', 'logoEsloganBlanco.png')

    # Verificar si la imagen existe
    if os.path.exists(logo_path):
        try:
            pdf.drawImage(
                logo_path, 40, height - 100, width=90, height=60, preserveAspectRatio=True)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    else:
        print(f"⚠️ No se encontró el logo en: {logo_path}")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(150, height - 70, "Recibo de Compra")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(150, height - 90, "Gracias por tu compra. ¡Esperamos verte pronto!")

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(150, height - 105, f"Estado: {venta.estado.capitalize()}")

    # ---------------- Datos del Cliente ----------------
    y = height - 130
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Datos del Cliente:")

    pdf.setFont("Helvetica", 11)
    cliente = venta.cliente
    usuario = cliente.usuario

    pdf.drawString(60, y - 15, f"Nombre: {usuario.nombre_s} {usuario.apellido_s}")
    pdf.drawString(60, y - 30, f"Correo: {usuario.correo}")
    pdf.drawString(60, y - 45, f"Dirección: {cliente.direccion or 'No registrada'}")

    # Obtener todos los teléfonos asociados
    telefonos = TelefonoCliente.objects.filter(cliente=cliente) # pylint: disable=no-member
    if telefonos.exists():
        tel_texto = ", ".join([t.telefono for t in telefonos])
    else:
        tel_texto = "No registrados"

    pdf.drawString(60, y - 60, f"Teléfonos: {tel_texto}")

    # ---------------- Código de barras ----------------
    barcode_value = str(venta.id_venta).zfill(8)
    barcode = code128.Code128(barcode_value, barHeight=20 * mm, barWidth=0.5)
    barcode.drawOn(pdf, 400, y - 70)

    # ---------------- Tabla de Productos ----------------
    y -= 100
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Producto")
    pdf.drawString(300, y, "Cantidad")
    pdf.drawString(380, y, "Subtotal")

    pdf.setFont("Helvetica", 10)
    y -= 20
    for det in detalles:
        pdf.drawString(40, y, det.producto.nombre[:40])
        pdf.drawString(310, y, str(det.cantidad))
        pdf.drawString(380, y, f"${det.subtotal:.2f}")
        y -= 15

        if y < 100:
            pdf.showPage()
            y = height - 80
            pdf.setFont("Helvetica", 10)

    # ---------------- Total ----------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y - 10, f"Total de la compra: ${venta.total:.2f}")

    # ---------------- Pie ----------------
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(40, 40, "Gracias por comprar en Chalooo.")
    pdf.drawString(40, 25, "Este documento sirve como comprobante de compra.")

    pdf.showPage()
    pdf.save()
    return response


# ------------------------- INICIO DE SESIÓN -------------------------

def login_view(request):
    """Permite iniciar sesión a clientes registrados."""
    if request.method == "POST":
        formulario = LoginClienteForm(request, data=request.POST)
        if formulario.is_valid():
            correo = formulario.cleaned_data.get("username")
            contrasena = formulario.cleaned_data.get("password")
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


def logout_view(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("chalooo:index")


# ------------------------- REGISTRO -------------------------

def registro(request):
    """Registra nuevos clientes con dirección y teléfonos múltiples."""
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["contrasena"] != form.cleaned_data["confirmar_contrasena"]:
                messages.error(request, "Las contraseñas no coinciden.")
            else:
                usuario = form.save()  # crea Usuario + Cliente
                login(request, usuario)
                messages.success(request, "Registro exitoso. ¡Bienvenido!")
                return redirect("chalooo:index")
    else:
        form = RegistroClienteForm()

    return render(request, "chalooo/registro.html", {"form": form})
