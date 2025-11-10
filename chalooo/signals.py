"""Señales del modelo Empleado para asignar grupos y permisos automáticamente."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import Empleado

@receiver(post_save, sender=Empleado)
def asignar_grupo_y_permisos(sender, instance, created, **kwargs): # pylint: disable=unused-argument
    """Configuracion de Grupo y Permisos de los Empleados"""
    if not created:
        return

    usuario = instance.usuario
    rol = instance.rol

    admin_group, _ = Group.objects.get_or_create(name="Administradores")
    analista_group, _ = Group.objects.get_or_create(name="Analistas")

    usuario.groups.clear()

    if rol == "admin":
        permisos = Permission.objects.all()
        admin_group.permissions.set(permisos)
        usuario.groups.add(admin_group)
        usuario.is_staff = True

    elif rol == "analista":
        # permisos view_ solo para modelos específicos (excluir Usuario)
        permisos_ver = Permission.objects.filter(
            codename__startswith="view_",
            content_type__app_label="chalooo"
        ).exclude(codename__in=["view_usuario"])  # <- excluye ver Usuarios

        analista_group.permissions.set(permisos_ver)
        usuario.groups.add(analista_group)
        usuario.is_staff = True

    usuario.save()
