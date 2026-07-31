from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from donatenow_app.models import Usuario, Categoria, OrganizacionBenefica, MetodoPago
from donatenow_app.forms import (
    LoginForm, RegistroDonanteForm, DonacionForm, MetodoPagoForm, CampaniaForm
)

class FormTestCase(TestCase):
    """
    CP-FORMS: Pruebas unitarias de formularios y validaciones de datos de entrada.
    """

    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='userform',
            email='userform@test.com',
            password='password123'
        )
        self.org = OrganizacionBenefica.objects.create(
            nombre='Fundación Form Test',
            nit='900999888-2',
            email='org@test.com',
            telefono='555-0000',
            direccion='Calle Form 1'
        )
        self.cat = Categoria.objects.create(
            nombre='Educación Infantil',
            descripcion='Becas de estudio'
        )

    def test_login_form_valid(self):
        """CP-FORM-01: Formulario de Login con datos válidos."""
        form = LoginForm(data={
            'username_or_email': 'userform@test.com',
            'password': 'password123',
            'codigo_2fa': '',
            'recordar_sesion': True
        })
        self.assertTrue(form.is_valid())

    def test_registro_form_password_mismatch(self):
        """CP-FORM-02: Formulario de Registro con contraseñas que no coinciden."""
        form = RegistroDonanteForm(data={
            'username': 'nuevo_donante',
            'email': 'nuevo@test.com',
            'password': 'password123',
            'confirm_password': 'otra_password',
            'nombre': 'Juan',
            'apellido': 'Pérez'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('Las contraseñas no coinciden.', form.non_field_errors())

    def test_registro_form_duplicate_username(self):
        """CP-FORM-03: Formulario de Registro con nombre de usuario duplicado."""
        form = RegistroDonanteForm(data={
            'username': 'userform',
            'email': 'diferente@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'nombre': 'Ana',
            'apellido': 'Gómez'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_donacion_form_negative_amount(self):
        """CP-FORM-04: Formulario de Donación con monto menor o igual a cero."""
        form = DonacionForm(data={
            'campania_id': 1,
            'monto': Decimal('-10.00'),
            'metodo_pago_id': 1,
            'es_anonima': False
        })
        self.assertFalse(form.is_valid())
        self.assertIn('monto', form.errors)

    def test_metodo_pago_form_invalid_card(self):
        """CP-FORM-05: Formulario de Método de Pago con número de tarjeta inválido."""
        form = MetodoPagoForm(data={
            'tipo': 'TARJETA_CREDITO',
            'titular': 'Pedro Picapiedra',
            'numero_tarjeta': '12345',  # Menor a 13 dígitos
            'es_predeterminado': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('numero_tarjeta', form.errors)

    def test_campania_form_invalid_dates(self):
        """CP-FORM-06: Formulario de Campaña con fecha fin anterior a fecha inicio."""
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        form = CampaniaForm(data={
            'titulo': 'Campaña Fecha Inválida',
            'descripcion': 'Prueba de fechas',
            'organizacion': self.org.id,
            'categoria': self.cat.id,
            'causa': '',
            'monto_objetivo': Decimal('5000.00'),
            'fecha_inicio': today,
            'fecha_fin': yesterday,
            'urgencia': 'MEDIA',
            'estado': 'ACTIVA'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('La fecha de finalización no puede ser anterior a la fecha de inicio.', form.non_field_errors())
