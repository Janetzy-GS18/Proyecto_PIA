"""Formularios de registro e inicio de sesión de clientes."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Cliente,  TelefonoCliente


class RegistroClienteForm(forms.ModelForm):
    """Formulario para registrar nuevos clientes."""
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    confirmar_contrasena = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    direccion = forms.CharField(
        label="Dirección",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True
    )
    telefonos = forms.CharField(
        label="Teléfonos (separados por coma)",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: 5551234567, 5587654321"
        }),
        required=False
    )

    class Meta:
        """Configuración de campos y etiquetas del formulario."""
        model = Usuario
        fields = ["nombre_s", "apellido_s", "correo"]
        labels = {
            "nombre_s": "Nombre(s)",
            "apellido_s": "Apellidos",
            "correo": "Correo electrónico",
        }
        widgets = {
            "nombre_s": forms.TextInput(attrs={"class": "form-control"}),
            "apellido_s": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        """Verifica que ambas contraseñas coincidan."""
        datos = super().clean()
        contrasena = datos.get("contrasena")
        confirmar = datos.get("confirmar_contrasena")

        if contrasena and confirmar and contrasena != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return datos

    def save(self, commit=True):
        """Crea el usuario, su cliente asociado y los teléfonos."""
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["contrasena"])
        if commit:
            usuario.save()
            cliente = Cliente.objects.create( # pylint: disable=no-member
                usuario=usuario,
                direccion=self.cleaned_data.get("direccion", "Sin dirección registrada")
            )

            telefonos_str = self.cleaned_data.get("telefonos", "")
            if telefonos_str:
                telefonos_list = [t.strip() for t in telefonos_str.split(",") if t.strip()]
                for tel in telefonos_list:
                    TelefonoCliente.objects.create( # pylint: disable=no-member
                        cliente=cliente,
                        telefono=tel
                    )

        return usuario


class LoginClienteForm(AuthenticationForm):
    """Formulario para iniciar sesión con correo."""
    username = forms.CharField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
