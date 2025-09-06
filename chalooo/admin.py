from django.contrib import admin
from .models import Usuario, Cliente, TelefonoCliente, Empleado, Producto, Venta, DetalleVenta

admin.site.register(Usuario)
admin.site.register(Cliente)
admin.site.register(TelefonoCliente)
admin.site.register(Empleado)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
