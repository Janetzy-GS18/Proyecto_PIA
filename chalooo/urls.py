from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('clientes/', views.clientes, name='clientes'),
    path('telefonos/', views.telefonos, name='telefonos'),
    path('empleados/', views.empleados, name='empleados'),
    path('productos/', views.productos, name='productos'),
    path('ventas/', views.ventas, name='ventas'),
    path('detalles/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
]
