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
]
