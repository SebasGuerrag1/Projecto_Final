from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import (
    Usuario, Donante, OrganizacionBenefica, Categoria, Causa,
    Campania, MetodoPago, Donacion, Reporte
)

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Usuario o Correo Electrónico",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. donante123 o user@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    codigo_2fa = forms.CharField(
        label="Código 2FA (si está habilitado)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de 6 dígitos'})
    )
    recordar_sesion = forms.BooleanField(
        label="Recordar sesión",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class RegistroDonanteForm(forms.Form):
    username = forms.CharField(
        label="Nombre de Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    confirm_password = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    nombre = forms.CharField(
        label="Nombre",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    direccion = forms.CharField(
        label="Dirección",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Método de Pago Preferido (Opcional en registro)
    tipo_tarjeta = forms.ChoiceField(
        label="Tipo de Tarjeta Preferida",
        choices=[('', 'Seleccionar método de pago (opcional)')] + list(MetodoPago.TIPOS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    titular_tarjeta = forms.CharField(
        label="Titular de la Tarjeta",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_tarjeta = forms.CharField(
        label="Número de Tarjeta (16 dígitos)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '4532 0000 0000 0000'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("El correo electrónico ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

class FiltroCausasForm(forms.Form):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las Categorías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    urgencia = forms.ChoiceField(
        choices=[('', 'Todas las Urgencias')] + list(Campania.URGENCIAS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    q = forms.CharField(
        required=False,
        label="Buscar Causa",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por título o palabra clave...'})
    )

class DonacionForm(forms.Form):
    campania_id = forms.IntegerField(widget=forms.HiddenInput())
    monto = forms.DecimalField(
        label="Monto a Donar ($ USD)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50.00', 'step': '0.01'})
    )
    metodo_pago_id = forms.IntegerField(
        label="Método de Pago",
        widget=forms.HiddenInput()
    )
    es_anonima = forms.BooleanField(
        label="Realizar esta donación de forma anónima",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is None or monto <= Decimal('0.00'):
            raise ValidationError("El monto de donación debe ser mayor a cero.")
        return monto

class MetodoPagoForm(forms.Form):
    tipo = forms.ChoiceField(
        label="Tipo de Método de Pago",
        choices=MetodoPago.TIPOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    titular = forms.CharField(
        label="Nombre del Titular",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Como aparece en la tarjeta'})
    )
    numero_tarjeta = forms.CharField(
        label="Número de Tarjeta",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '4532 1234 5678 9010'})
    )
    es_predeterminado = forms.BooleanField(
        label="Establecer como predeterminado",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_numero_tarjeta(self):
        num = self.cleaned_data.get('numero_tarjeta', '').replace(" ", "").replace("-", "")
        if not num.isdigit() or len(num) < 13 or len(num) > 19:
            raise ValidationError("Ingrese un número de tarjeta válido (13 a 19 dígitos).")
        return num

class OrganizacionForm(forms.ModelForm):
    class Meta:
        model = OrganizacionBenefica
        fields = ['nombre', 'nit', 'email', 'telefono', 'direccion', 'estado_verificacion', 'documento_verificacion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado_verificacion': forms.Select(attrs={'class': 'form-select'}),
            'documento_verificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ruta o nombre de documento de respaldo'}),
        }

class CampaniaForm(forms.Form):
    titulo = forms.CharField(
        label="Título de la Campaña",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    descripcion = forms.CharField(
        label="Descripción Detallada",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    organizacion = forms.ModelChoiceField(
        label="Organización Beneficiaria",
        queryset=OrganizacionBenefica.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    categoria = forms.ModelChoiceField(
        label="Categoría",
        queryset=Categoria.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    causa = forms.ModelChoiceField(
        label="Causa Específica (Opcional)",
        queryset=Causa.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    monto_objetivo = forms.DecimalField(
        label="Monto Objetivo de Recaudación ($ USD)",
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10000.00'})
    )
    fecha_inicio = forms.DateField(
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_fin = forms.DateField(
        label="Fecha de Finalización",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    urgencia = forms.ChoiceField(
        label="Nivel de Urgencia",
        choices=Campania.URGENCIAS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        label="Estado de la Campaña",
        choices=Campania.ESTADOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_inicio')
        fin = cleaned_data.get('fecha_fin')
        monto = cleaned_data.get('monto_objetivo')

        if inicio and fin and fin < inicio:
            raise ValidationError("La fecha de finalización no puede ser anterior a la fecha de inicio.")
        if monto and monto <= Decimal('0.00'):
            raise ValidationError("El monto objetivo debe ser mayor a cero.")
        return cleaned_data

class ReporteForm(forms.Form):
    titulo = forms.CharField(
        label="Título del Reporte",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Reporte Trimestral de Donaciones Q3'})
    )
    tipo_reporte = forms.ChoiceField(
        label="Tipo de Reporte",
        choices=Reporte.TIPOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    parametros = forms.CharField(
        label="Parámetros o Filtros Adicionales",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Periodo: 2026, Urgencia: ALTA'})
    )
