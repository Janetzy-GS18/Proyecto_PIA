"""ASGI configuration for tiendaOnline project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tiendaOnline.settings')

application = get_asgi_application()
