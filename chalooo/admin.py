"""Configuración de modelos en el panel de administración de Django."""

import json
import csv # pylint: disable=unused-import
from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import Sum
from django.http import HttpResponse # pylint: disable=unused-import
from django.template.response import TemplateResponse # pylint: disable=unused-import
from django.urls import path # pylint: disable=unused-import
from django.db.models.functions import ExtractMonth, ExtractYear
from django.core.serializers.json import DjangoJSONEncoder

from .models import Usuario, Cliente, TelefonoCliente, Empleado, Producto, Venta, DetalleVenta

# --- Helpers de rol ---
def es_analista(user):
    """Usuario o empleado con rol 'analista'."""
    return hasattr(user, "empleado") and user.empleado.rol == "analista"

def es_admin_usuario(user):
    """Superuser o empleado con rol 'admin'."""
    return user.is_superuser or (hasattr(user, "empleado") and user.empleado.rol == "admin")


# --- Registrar Usuario con inline de Empleado para que admin cree empleados al crear usuarios ---
class EmpleadoInline(admin.StackedInline):
    """Configuración de ingreso de empleados."""
    model = Empleado
    can_delete = False
    verbose_name = "Empleado"
    verbose_name_plural = "Empleado"
    fk_name = 'usuario'


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    """Configuración del modelo Usuario en el panel admin."""
    list_display = ('idusuario', 'nombre_s', 'apellido_s', 'correo', 'is_staff')
    search_fields = ('nombre_s', 'apellido_s', 'correo')
    inlines = (EmpleadoInline,)

        # Solo superusuarios o admins pueden ver el modelo Usuario en el menú
    def has_module_permission(self, request):
        return es_admin_usuario(request.user)

    # Visualizar/editar usuarios: restringir según necesites
    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

    def has_change_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

    def has_add_permission(self, request):
        return es_admin_usuario(request.user)

    def has_delete_permission(self, request, obj=None):
        return es_admin_usuario(request.user)



@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    """Configuración del modelo Empleado."""
    list_display = ('usuario', 'rol')
    list_filter = ('rol',)
    search_fields = ('usuario__nombre_s', 'usuario__apellido_s', 'usuario__correo')

    # Solo admin (superuser o rol admin) puede ver y editar empleados
    def has_module_permission(self, request):
        return es_admin_usuario(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

    def has_change_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

    def has_add_permission(self, request):
        return es_admin_usuario(request.user)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Configuración del modelo Cliente."""
    list_display = ('usuario', 'direccion')
    search_fields = ('usuario__nombre_s',)

    # Solo admin gestiona clientes desde admin
    def has_module_permission(self, request):
        return es_admin_usuario(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user)


@admin.register(TelefonoCliente)
class TelefonoClienteAdmin(admin.ModelAdmin):
    """Configuración del modelo TelefonoCliente."""
    list_display = ('cliente', 'telefono')
    search_fields = ('cliente__usuario__nombre_s', 'telefono')

    def has_module_permission(self, request):
        return es_admin_usuario(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración del modelo Producto."""
    list_display = ('nombre', 'precio', 'stock')
    search_fields = ('nombre',)
    list_filter = ('precio',)

    def has_module_permission(self, request):
        # Admin y analista pueden ver productos
        return es_admin_usuario(request.user) or es_analista(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user) or es_analista(request.user)

    def has_change_permission(self, request, obj=None):
        # Solo admin puede editar
        return es_admin_usuario(request.user)

    def has_add_permission(self, request):
        # Solo admin puede agregar
        return es_admin_usuario(request.user)

    def has_delete_permission(self, request, obj=None):
        # Solo admin puede eliminar
        return es_admin_usuario(request.user)


# --- Filtro por rango de fechas (simple) ---

class FechaPersonalizadaFilter(admin.SimpleListFilter):
    """Filtro avanzado con campos de fecha personalizada."""
    title = 'Rango de fechas personalizado'
    parameter_name = 'rango_fecha'

    def lookups(self, request, model_admin):
        return []  # no se necesitan opciones predefinidas

    def queryset(self, request, queryset):
        desde = request.GET.get('fecha_desde')
        hasta = request.GET.get('fecha_hasta')

        if desde and hasta:
            try:
                desde = datetime.strptime(desde, '%Y-%m-%d')
                hasta = datetime.strptime(hasta, '%Y-%m-%d') + timedelta(days=1)
                return queryset.filter(fecha__range=(desde, hasta))
            except ValueError:
                pass  # si hay error en formato, ignora el filtro

        return queryset


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    """Configuración del modelo Venta con filtros, gráfico y exportación."""
    list_display = ('id_venta', 'cliente', 'fecha', 'total', 'estado')
    list_filter = (FechaPersonalizadaFilter,)
    ordering = ('-fecha',)
    change_list_template = "admin/chalooo/ventas_change_list.html"

    # --- permisos ---
    def has_module_permission(self, request):
        return es_admin_usuario(request.user) or es_analista(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user) or es_analista(request.user)

    def has_change_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

    def has_add_permission(self, request):
        return es_admin_usuario(request.user)

    def has_delete_permission(self, request, obj=None):
        return es_admin_usuario(request.user)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        fecha_desde_raw = request.GET.get('fecha_desde')
        fecha_hasta_raw = request.GET.get('fecha_hasta')

    # Convertir a datetime si es válido
        try:
            if fecha_desde_raw:
                fecha_desde = datetime.strptime(fecha_desde_raw, '%Y-%m-%d')
                qs = qs.filter(fecha__gte=fecha_desde)
            if fecha_hasta_raw:
                fecha_hasta = datetime.strptime(fecha_hasta_raw, '%Y-%m-%d') + timedelta(days=1)
                qs = qs.filter(fecha__lt=fecha_hasta)
        except ValueError:
            pass  # Si hay error en formato, ignoramos el filtro
        return qs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # --- LEEMOS filtros de fechas en crudo ---
        fecha_desde_raw = request.GET.get('fecha_desde')
        fecha_hasta_raw = request.GET.get('fecha_hasta')

        # --- Construimos el queryset filtrado usando get_queryset (fuente única) ---
        qs_filtrado = self.get_queryset(request)

        # --- Si se solicita export, atendemos aquí usando qs_filtrado ---
        if request.GET.get('export') == 'csv':
            qs_export = qs_filtrado.exclude(estado='anulada').order_by('-fecha')

            response_csv = HttpResponse(content_type='text/csv; charset=utf-8')
            response_csv.write('\ufeff')  # BOM para Excel
            response_csv['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'

            # Ajusta delimitador según preferencia local (',' o ';')
            writer = csv.writer(
                response_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL
            )

            # Encabezados
            writer.writerow(['ID Venta', 'Fecha', 'Cliente', 'Total', 'Estado'])

            total_general = 0
            for venta in qs_export:
                writer.writerow([
                    venta.id_venta,
                    venta.fecha.strftime('%Y-%m-%d %H:%M'),
                    f"{venta.cliente.usuario.nombre_s} {venta.cliente.usuario.apellido_s}",
                    f"{venta.total:.2f}",
                    venta.estado
                ])
                total_general += float(venta.total or 0)

            writer.writerow([])
            writer.writerow(['', '', 'TOTAL VENTAS (excluyendo anuladas):', f"{total_general:.2f}"])

            return response_csv

        # --- No es export: construimos datos del chart sobre qs_filtrado ---
        resumen = (
            qs_filtrado
            .annotate(year=ExtractYear('fecha'), month=ExtractMonth('fecha'))
            .values('year', 'month')
            .annotate(total=Sum('total'))
            .order_by('year', 'month')
        )

        chart_data = json.dumps(list(resumen), cls=DjangoJSONEncoder)

        # rellenamos extra_context para que la plantilla muestre los inputs con valor
        extra_context['chart_data'] = chart_data
        extra_context['fecha_desde'] = fecha_desde_raw or ''
        extra_context['fecha_hasta'] = fecha_hasta_raw or ''

        # ahora obtenemos la respuesta normal del admin y fusionamos el context
        response = super().changelist_view(request, extra_context=extra_context)
        if hasattr(response, 'context_data'):
            response.context_data.update(extra_context)

        return response

    # pylint: disable=missing-function-docstring
    def exportar_csv(self, request):
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')

        queryset = Venta.objects.filter(estado='completada').order_by('-fecha')  # pylint: disable=no-member
        if fecha_desde:
            queryset = queryset.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha__date__lte=fecha_hasta)

        # Nombre de archivo con rango (opcional)
        nombre = "reporte_ventas"
        if fecha_desde or fecha_hasta:
            nombre += f"_{fecha_desde or 'start'}_a_{fecha_hasta or 'end'}"
        nombre += ".csv"

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{nombre}"'

        # Usar ; como separador
        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        # encabezados
        writer.writerow(['ID Venta',
                        'Cliente',
                        'Fecha',
                        'Producto',
                        'Cantidad',
                        'Subtotal',
                        'Total de la Venta'])

        grand_total = 0
        for venta in queryset:
            detalles = DetalleVenta.objects.filter(venta=venta) # pylint: disable=no-member
            grand_total += float(venta.total or 0)
            if detalles.exists():
                for d in detalles:
                    writer.writerow([
                        venta.id_venta,
                        str(venta.cliente.usuario) if venta.cliente else "—",
                        venta.fecha.strftime("%Y-%m-%d %H:%M"),
                        d.producto.nombre,
                        d.cantidad,
                        f"{float(d.subtotal):.2f}",
                        f"{float(venta.total):.2f}"
                    ])
            else:
                writer.writerow([
                    venta.id_venta,
                    str(venta.cliente.usuario) if venta.cliente else "—",
                    venta.fecha.strftime("%Y-%m-%d %H:%M"),
                    "(Sin detalles)",
                    "-",
                    "-",
                    f"{float(venta.total):.2f}"
                ])

        # fila final con total agregado
        writer.writerow([])
        writer.writerow(['', '', '', '', '', 'TOTAL GENERAL:', f"{grand_total:.2f}"])

        return response


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    """Configuración del modelo DetalleVenta."""
    list_display = ('venta', 'producto', 'cantidad', 'subtotal')
    search_fields = ('producto__nombre',)
    readonly_fields = ('subtotal',)

    def has_module_permission(self, request):
        # Admin y analista pueden ver detalle de venta
        return es_admin_usuario(request.user) or es_analista(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin_usuario(request.user) or es_analista(request.user)

    def has_change_permission(self, request, obj=None):
        # Solo admin puede editar
        return es_admin_usuario(request.user)

    def has_add_permission(self, request):
        # Solo admin puede agregar
        return es_admin_usuario(request.user)

    def has_delete_permission(self, request, obj=None):
        # Solo admin puede eliminar
        return es_admin_usuario(request.user)
