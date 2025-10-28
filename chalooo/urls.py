"""Rutas de la aplicación Chalooo."""

from django.urls import path
from . import views

app_name = "chalooo" # pylint: disable=invalid-name

urlpatterns = [
    path('', views.index, name='index'),
    path('productos/', views.productos, name='productos'),
    path('carrito/', views.carrito, name='carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmacion/', views.confirmacion, name='confirmacion'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
]
