"""Modelo principal del sistema de ventas."""

from django.apps import AppConfig

# pylint: disable=C0415, W0611

class ChaloooConfig(AppConfig):
    """Configuración principal de la aplicación Chalooo."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chalooo'

    def ready(self):
        import chalooo.signals
