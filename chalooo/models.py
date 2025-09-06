from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre_s, apellido_s, contrasena=None, **extra_fields):
        if not correo:
            raise ValueError("El usuario debe tener un correo electrónico")
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, nombre_s=nombre_s, apellido_s=apellido_s, **extra_fields)
        user.set_password(contrasena)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre_s, apellido_s, contrasena=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(correo, nombre_s, apellido_s, contrasena, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    idusuario = models.AutoField(primary_key=True)
    nombre_s = models.CharField(max_length=50)
    apellido_s = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    # Contraseña ya está incluida en AbstractBaseUser

    # Campos de control de Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre_s", "apellido_s"]

    def __str__(self):
        return f"{self.nombre_s} {self.apellido_s} ({self.correo})"
    
# ---------- Subtipo: Cliente ----------
class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return f"Cliente: {self.usuario.nombre_s}"


class TelefonoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)

    class Meta:
        unique_together = ('cliente', 'telefono')

    def __str__(self):
        return f"{self.cliente.usuario.nombre_s} - {self.telefono}"


# ---------- Subtipo: Empleado ----------
class Empleado(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    rol = models.CharField(max_length=20)

    def __str__(self):
        return f"Empleado: {self.usuario.nombre_s} ({self.rol})"


# ---------- Producto ----------
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    ruta_imagen = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre


# ---------- Venta ----------
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Venta {self.id_venta} - Cliente {self.cliente.usuario.nombre_s}"


# ---------- DetalleVenta ----------
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('venta', 'producto')

    def __str__(self):
        return f"Venta {self.venta.id_venta} - {self.producto.nombre} ({self.cantidad})"
