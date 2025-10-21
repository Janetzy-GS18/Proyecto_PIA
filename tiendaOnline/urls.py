"""Rutas principales del proyecto TiendaOnline."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chalooo.urls')),
]
