"""Modelos principales del sistema de ventas."""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# ---------- MANAGER PERSONALIZADO PARA USUARIO ----------
class UsuarioManager(BaseUserManager):
    """Gestor personalizado para crear usuarios y superusuarios."""

    def create_user(self, correo, nombre_s, apellido_s, password=None, **extra_fields):
        """Crea un nuevo usuario estándar."""
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico")
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, nombre_s=nombre_s, apellido_s=apellido_s, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre_s, apellido_s, password=None, **extra_fields):
        """Crea un superusuario con permisos de administrador."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(correo, nombre_s, apellido_s, password, **extra_fields)

# ---------- Usuario ----------
class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo base de usuario del sistema."""
    idusuario = models.AutoField(primary_key=True)
    nombre_s = models.CharField(max_length=50)
    apellido_s = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre_s", "apellido_s"]

    def __str__(self):
        return f"{self.nombre_s} {self.apellido_s} ({self.correo})"

# ---------- Subtipo: Cliente ----------
class Cliente(models.Model):
    """Subtipo de Usuario que representa a un cliente."""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        """Retorna el nombre del cliente."""
        return f"Cliente: {self.usuario.nombre_s}" # pylint: disable=no-member


class TelefonoCliente(models.Model):
    """Modelo para manejar múltiples teléfonos asociados a un cliente."""
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)

    class Meta:
        """Representación de la PK concatenada telefonoCliente."""
        unique_together = ('cliente', 'telefono')

    def __str__(self):
        """Representación del teléfono del cliente."""
        return f"{self.cliente.usuario.nombre_s} - {self.telefono}" # pylint: disable=no-member


# ---------- Subtipo: Empleado ----------
class Empleado(models.Model):
    """Subtipo de Usuario que representa a un empleado."""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    rol = models.CharField(max_length=20)

    def __str__(self):
        """Devuelve el nombre del empleado y su rol."""
        return f"Empleado: {self.usuario.nombre_s} ({self.rol})" # pylint: disable=no-member


# ---------- Producto ----------
class Producto(models.Model):
    """Modelo que representa un producto disponible para la venta."""
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        """Retorna el nombre del producto."""
        return str(self.nombre)


# ---------- Venta ----------
class Venta(models.Model):
    """Modelo que representa una venta realizada por un cliente."""
    id_venta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def actualizar_total(self):
        """Recalcula el total sumando los subtotales de sus detalles."""
        total = sum(det.subtotal for det in self.detalleventa_set.all()) # pylint: disable=no-member
        self.total = total
        self.save(update_fields=["total"])

    def __str__(self):
        """Muestra el ID de venta y el cliente."""
        return f"Venta {self.id_venta} - Cliente {self.cliente.usuario.nombre_s}"  # pylint: disable=no-member


# ---------- DetalleVenta ----------
class DetalleVenta(models.Model):
    """Modelo que representa los productos individuales de una venta."""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        """Representación de la PK concatenada DetalleVenta."""
        unique_together = ('venta', 'producto')

    def save(self, *args, **kwargs):
        """Calcula el subtotal, actualiza el stock y el total de la venta."""
        # recalcular subtotal
        self.subtotal = self.producto.precio * self.cantidad  # pylint: disable=no-member

        # Si es nuevo, descontar stock
        if self._state.adding:
            if self.cantidad > self.producto.stock:  # pylint: disable=no-member
                raise ValueError(f"Stock insuficiente para el producto {self.producto.nombre}")  # pylint: disable=no-member
            self.producto.stock -= self.cantidad  # pylint: disable=no-member
        else:
            # Si se edita, primero restaurar el stock anterior
            original = DetalleVenta.objects.get(pk=self.pk) # pylint: disable=no-member
            diferencia = self.cantidad - original.cantidad
            if diferencia > 0 and diferencia > self.producto.stock:  # pylint: disable=no-member
                raise ValueError(f"Stock insuficiente para el producto {self.producto.nombre}")  # pylint: disable=no-member
            self.producto.stock -= diferencia  # pylint: disable=no-member

        self.producto.save()  # pylint: disable=no-member
        super().save(*args, **kwargs)

        # actualizar total de la venta
        self.venta.actualizar_total() # pylint: disable=no-member

    def delete(self, *args, **kwargs):
        """Restaura el stock y actualiza el total al eliminar un detalle."""
        self.producto.stock += self.cantidad  # pylint: disable=no-member
        self.producto.save()  # pylint: disable=no-member
        super().delete(*args, **kwargs)
        self.venta.actualizar_total() # pylint: disable=no-member

    def __str__(self):
        """Representación legible del detalle de venta."""
        return f"{self.producto.nombre} x{self.cantidad} (${self.subtotal})"  # pylint: disable=no-member
