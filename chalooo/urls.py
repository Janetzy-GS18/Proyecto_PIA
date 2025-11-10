"""Rutas de la aplicación Chalooo."""

from django.urls import path
from . import views

app_name = "chalooo" # pylint: disable=invalid-name

urlpatterns = [
    path('', views.index, name='index'),
    path('productos/', views.productos, name='productos'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/actualizar/', views.actualizar_carrito, name='actualizar_carrito'),  # pylint: disable=no-member
    path('carrito/eliminar/<int:producto_id>/',
        views.eliminar_del_carrito, name='eliminar_del_carrito'),  # pylint: disable=no-member
    path('recibo/<int:venta_id>/pdf/', views.recibo_pdf, name='recibo_pdf'),  # pylint: disable=no-member
    path('checkout/', views.checkout, name='checkout'),
    path('confirmacion/<int:venta_id>/', views.confirmacion, name='confirmacion'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('historial/', views.historial_compras, name='historial'), # pylint: disable=no-member
    path('anular/<int:venta_id>/', views.anular_venta, name='anular_venta') # pylint: disable=no-member
]
