"""Pruebas unitarias para la aplicación Chalooo."""

from django.test import TestCase
from django.urls import reverse
from .models import Usuario, Producto


class BasicViewsTests(TestCase):
    """Pruebas para verificar que las vistas principales cargan correctamente."""

    def setUp(self):
        """Crea datos de ejemplo para las pruebas."""
        self.usuario = Usuario.objects.create(
            idusuario=1,
            nombre_s="Juan",
            apellido_s="Pérez",
            correo="juan@gmail.com",
            contrasena="1234",
        )
        self.producto = Producto.objects.create( # pylint: disable=no-member
            nombre="Laptop", precio=15000, stock=5
        )

    def test_index_view(self):
        """Verifica que la página principal responda con éxito."""
        response = self.client.get(reverse("chalooo:index"))
        self.assertEqual(response.status_code, 200)

    def test_usuarios_view(self):
        """Verifica que la vista de usuarios cargue correctamente."""
        response = self.client.get(reverse("chalooo:usuarios"))
        self.assertEqual(response.status_code, 200)

    def test_productos_view(self):
        """Verifica que la vista de productos funcione correctamente."""
        response = self.client.get(reverse("chalooo:productos"))
        self.assertEqual(response.status_code, 200)
