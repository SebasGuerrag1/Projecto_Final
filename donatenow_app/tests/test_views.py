from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from donatenow_app.models import (
    Usuario, Donante, AdministradorSistema, OrganizacionBenefica,
    Categoria, Causa, ObjetivoRecaudacion, Campania, MetodoPago, Donacion, ReciboElectronico
)

class ViewTestCase(TestCase):
    """
    CP-VIEWS: Pruebas de integración de Vistas, URLs y Plantillas.
    """

    def setUp(self):
        self.client = Client()
        self.user_donante = Usuario.objects.create_user(
            username='donanteview',
            email='donanteview@test.com',
            password='password123',
            rol='DONANTE'
        )
        self.donante = Donante.objects.create(usuario=self.user_donante)
        self.user_admin = Usuario.objects.create_user(
            username='adminview',
            email='adminview@test.com',
            password='password123',
            rol='ADMINISTRADOR_SISTEMA'
        )

        self.org = OrganizacionBenefica.objects.create(
            nombre='Org View Test',
            nit='999000111-4',
            email='orgview@test.com',
            telefono='555-8888',
            direccion='Calle View 20',
            estado_verificacion='VERIFICADA'
        )
        self.cat = Categoria.objects.create(nombre='Medio Ambiente')
        self.objetivo = ObjetivoRecaudacion.objects.create(
            monto_objetivo=Decimal('15000.00'),
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date()
        )
        self.campania = Campania.objects.create(
            titulo='Reforestación 2026',
            descripcion='Siembra de árboles',
            organizacion=self.org,
            categoria=self.cat,
            objetivo=self.objetivo
        )
        self.metodo_pago = MetodoPago.objects.create(
            donante=self.donante,
            tipo='TARJETA_CREDITO',
            titular='Donante View',
            ultimos_digitos='9999',
            token='TOK-VIEW-TEST-123456',
            es_predeterminado=True
        )

    def test_index_view(self):
        """CP-VIEW-01: Carga de página principal (index)."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('campanias_destacadas', response.context)

    def test_explorar_causas_view(self):
        """CP-VIEW-02: Carga de vista de exploración de causas."""
        response = self.client.get(reverse('causas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donatenow_app/causas.html')

    def test_detalle_campania_view(self):
        """CP-VIEW-03: Detalle de campaña activa."""
        response = self.client.get(reverse('detalle_causa', kwargs={'pk': self.campania.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donatenow_app/detalle_causa.html')

    def test_realizar_donacion_redirect_anonymous(self):
        """CP-VIEW-04: Redirección al login si un usuario anónimo intenta donar."""
        response = self.client.get(reverse('realizar_donacion', kwargs={'campania_id': self.campania.id}))
        self.assertEqual(response.status_code, 302)

    def test_realizar_donacion_donante_autenticado(self):
        """CP-VIEW-05: Carga del formulario de donación para donante autenticado."""
        self.client.login(username='donanteview', password='password123')
        response = self.client.get(reverse('realizar_donacion', kwargs={'campania_id': self.campania.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donatenow_app/donar.html')

    def test_admin_views_access_control(self):
        """CP-VIEW-06: Control de acceso en vistas de administrador."""
        # Intento de acceso con usuario donante -> Debe denegar/redireccionar
        self.client.login(username='donanteview', password='password123')
        response = self.client.get(reverse('monitorear_progreso'))
        self.assertEqual(response.status_code, 302)

        # Acceso con usuario admin -> Debe permitir (200)
        self.client.login(username='adminview', password='password123')
        response = self.client.get(reverse('monitorear_progreso'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'donatenow_app/progreso.html')
