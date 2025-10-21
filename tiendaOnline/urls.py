
"""Rutas principales del proyecto TiendaOnline."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # Import necesario para archivos multimedia

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chalooo.urls')),
]

# Esto permite servir imágenes (solo en modo DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
