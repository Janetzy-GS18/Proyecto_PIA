"""Formularios de registro e inicio de sesión de clientes."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Cliente


class RegistroClienteForm(forms.ModelForm):
    """Formulario para registrar nuevos clientes."""
    contrasena = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    confirmar_contrasena = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        """Formulario para registrar nuevos usuarios clientes."""
        model = Usuario
        fields = ["nombre_s", "apellido_s", "correo"]
        labels = {
            "nombre_s": "Nombre(s)",
            "apellido_s": "Apellidos",
            "correo": "Correo electrónico",
        }

    def clean(self):
        """Verifica que ambas contraseñas coincidan."""
        datos = super().clean()
        contrasena = datos.get("contraseña")
        confirmar = datos.get("confirmar_contraseña")

        if contrasena and confirmar and contrasena != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return datos

    def save(self, commit=True):
        """Crea el usuario y su cliente asociado."""
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["contraseña"])
        if commit:
            usuario.save()
            Cliente.objects.create(usuario=usuario, direccion="Sin dirección registrada") # pylint: disable=no-member
        return usuario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})



class LoginClienteForm(AuthenticationForm):
    """Formulario para iniciar sesión con correo."""
    username = forms.CharField(label="Correo electrónico",
                                widget=forms.EmailInput(
                                    attrs={"class": "form-control"}))
    password = forms.CharField(label="Contraseña",
                                widget=forms.PasswordInput(
                                    attrs={"class": "form-control"}))
