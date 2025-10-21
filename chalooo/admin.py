"""Configuración de modelos en el panel de administración de Django."""

from django.contrib import admin
from .models import Usuario, Cliente, TelefonoCliente, Empleado, Producto, Venta, DetalleVenta

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(TelefonoCliente)
admin.site.register(Empleado)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Configuración del modelo Usuario en el panel admin."""
    list_display = ('idusuario', 'nombre_s', 'apellido_s', 'correo', 'is_staff')
    search_fields = ('nombre_s', 'apellido_s', 'correo')
    list_filter = ('is_staff',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Configuración del modelo Cliente."""
    list_display = ('usuario', 'direccion')
    search_fields = ('usuario__nombre_s',)


@admin.register(TelefonoCliente)
class TelefonoClienteAdmin(admin.ModelAdmin):
    """Configuración del modelo TelefonoCliente."""
    list_display = ('cliente', 'telefono')
    search_fields = ('cliente__usuario__nombre_s', 'telefono')


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    """Configuración del modelo Empleado."""
    list_display = ('usuario', 'rol')
    search_fields = ('usuario__nombre_s', 'rol')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración del modelo Producto."""
    list_display = ('nombre', 'precio', 'stock')
    search_fields = ('nombre',)
    list_filter = ('precio',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """Configuración del modelo Venta."""
    list_display = ('id_venta', 'cliente', 'fecha', 'total')
    list_filter = ('fecha',)
    search_fields = ('cliente__usuario__nombre_s',)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    """Configuración del modelo DetalleVenta."""
    list_display = ('venta', 'producto', 'cantidad', 'subtotal')
    search_fields = ('producto__nombre',)
