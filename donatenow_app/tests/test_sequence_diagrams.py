from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from donatenow_app.models import (
    Usuario, Donante, AdministradorSistema, OrganizacionBenefica,
    Categoria, Causa, ObjetivoRecaudacion, Campania, ProgresoRecaudacion,
    MetodoPago, Donacion, Transaccion, ReciboElectronico, EstadisticaDonaciones, Reporte
)
from donatenow_app.services import (
    AuthenticationService, TokenizacionService, PasarelaPagoService,
    ReciboService, ValidacionDocumentosService, ProgresoService,
    EstadisticasService, ReporteService
)

class SequenceDiagramsTestCase(TestCase):
    """
    CP-DS: Pruebas automatizadas de integración basadas en los 13 Diagramas de Secuencia (DS-01 a DS-13).
    """

    def setUp(self):
        self.client = Client()
        self.user_donante = Usuario.objects.create_user(
            username='donante_ds',
            email='donante_ds@test.com',
            password='password123',
            rol='DONANTE'
        )
        self.donante = Donante.objects.create(usuario=self.user_donante)

        self.user_admin = Usuario.objects.create_user(
            username='admin_ds',
            email='admin_ds@test.com',
            password='password123',
            rol='ADMINISTRADOR_SISTEMA'
        )
        self.admin_profile = AdministradorSistema.objects.create(usuario=self.user_admin)

        self.org = OrganizacionBenefica.objects.create(
            nombre='Fundación DS Test',
            nit='900777666-5',
            email='orgds@test.com',
            telefono='555-7777',
            direccion='Calle Diagrama 30',
            estado_verificacion='VERIFICADA'
        )
        self.cat = Categoria.objects.create(nombre='Protección Animal')
        self.objetivo = ObjetivoRecaudacion.objects.create(
            monto_objetivo=Decimal('8000.00'),
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date()
        )
        self.campania = Campania.objects.create(
            titulo='Refugio Canino 2026',
            descripcion='Alimento y atención médica para animales',
            organizacion=self.org,
            categoria=self.cat,
            objetivo=self.objetivo
        )

        token, ultimos_4 = TokenizacionService.tokenizar_tarjeta('4532111122223333', 'Donante DS')
        self.metodo_pago = MetodoPago.objects.create(
            donante=self.donante,
            tipo='TARJETA_CREDITO',
            titular='Donante DS',
            ultimos_digitos=ultimos_4,
            token=token,
            es_predeterminado=True
        )

    def test_ds_01_iniciar_sesion_flujo_completo(self):
        """DS-01: Verificación de secuencia de inicio de sesión."""
        response = self.client.post(reverse('login'), {
            'username_or_email': 'donante_ds',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user_donante.id)

    def test_ds_02_registrarse_flujo_completo(self):
        """DS-02: Verificación de secuencia de registro de donante con método de pago preferido."""
        response = self.client.post(reverse('registro'), {
            'username': 'nuevo_donante_ds',
            'email': 'nuevo_ds@test.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'nombre': 'Carlos',
            'apellido': 'López',
            'tipo_tarjeta': 'TARJETA_CREDITO',
            'titular_tarjeta': 'Carlos López',
            'numero_tarjeta': '4532999988887777'
        })
        self.assertRedirects(response, reverse('index'))
        user = Usuario.objects.get(username='nuevo_donante_ds')
        self.assertIsNotNone(user.perfil_donante)
        self.assertEqual(user.perfil_donante.metodos_pago.count(), 1)

    def test_ds_03_explorar_causas_flujo_completo(self):
        """DS-03: Verificación de secuencia de navegación y filtrado de campañas."""
        response = self.client.get(reverse('causas'), {'categoria': self.cat.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.campania, response.context['campanias'])

    def test_ds_04_realizar_donacion_flujo_completo(self):
        """DS-04: Verificación de secuencia completa de donación (Donante -> Form -> Pasarela -> Recibo)."""
        self.client.login(username='donante_ds', password='password123')
        response = self.client.post(reverse('realizar_donacion', kwargs={'campania_id': self.campania.id}), {
            'campania_id': self.campania.id,
            'monto': '250.00',
            'metodo_pago_id': self.metodo_pago.id,
            'es_anonima': False
        })

        donacion = Donacion.objects.filter(donante=self.donante, campania=self.campania).last()
        self.assertIsNotNone(donacion)
        self.assertEqual(donacion.estado, 'COMPLETADA')
        self.assertIsNotNone(donacion.transaccion)
        self.assertEqual(donacion.transaccion.estado, 'APROBADA')

        recibo = ReciboElectronico.objects.get(donacion=donacion)
        self.assertRedirects(response, reverse('ver_recibo', kwargs={'recibo_id': recibo.id}))

    def test_ds_05_seleccionar_metodo_pago_flujo(self):
        """DS-05: Verificación de secuencia de tokenización y guardado de método de pago."""
        self.client.login(username='donante_ds', password='password123')
        response = self.client.post(reverse('seleccionar_metodo_pago'), {
            'tipo': 'TARJETA_DEBITO',
            'titular': 'Donante DS Débito',
            'numero_tarjeta': '4532888877776666',
            'es_predeterminado': False
        })
        self.assertRedirects(response, reverse('seleccionar_metodo_pago'))
        self.assertEqual(self.donante.metodos_pago.count(), 2)

    def test_ds_06_procesar_transaccion_servicio(self):
        """DS-06: Verificación de secuencia de comunicación con PasarelaPagoService."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('100.00'),
            estado='PENDIENTE'
        )
        tx, exito = PasarelaPagoService.procesar_cobro(donacion, self.metodo_pago)
        self.assertTrue(exito)
        self.assertEqual(tx.estado, 'APROBADA')

    def test_ds_07_recibir_recibo_electronico_servicio(self):
        """DS-07: Verificación de secuencia de emisión de recibo electrónico."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('400.00'),
            estado='COMPLETADA'
        )
        recibo = ReciboService.generar_recibo(donacion)
        self.assertEqual(recibo.donacion, donacion)
        self.assertTrue(recibo.enviado_email)

    def test_ds_08_gestionar_organizaciones_flujo(self):
        """DS-08: Verificación de secuencia de administración y verificación de organizaciones."""
        self.client.login(username='admin_ds', password='password123')
        response = self.client.post(reverse('gestionar_organizaciones'), {
            'nombre': 'Fundación Nueva',
            'nit': '900555444-6',
            'email': 'nueva@org.com',
            'telefono': '555-1111',
            'direccion': 'Calle Nueva 1',
            'estado_verificacion': 'PENDIENTE'
        })
        self.assertRedirects(response, reverse('gestionar_organizaciones'))
        org_nueva = OrganizacionBenefica.objects.get(nit='900555444-6')
        
        # Verificar documento
        response_ver = self.client.get(reverse('verificar_organizacion', kwargs={'pk': org_nueva.id}))
        org_nueva.refresh_from_db()
        self.assertEqual(org_nueva.estado_verificacion, 'VERIFICADA')

    def test_ds_09_crear_campania_flujo(self):
        """DS-09: Verificación de secuencia de creación de campaña."""
        self.client.login(username='admin_ds', password='password123')
        today = timezone.now().date()
        response = self.client.post(reverse('crear_campania'), {
            'titulo': 'Campaña Sanitaria 2026',
            'descripcion': 'Atención médica rural',
            'organizacion': self.org.id,
            'categoria': self.cat.id,
            'causa': '',
            'monto_objetivo': '12000.00',
            'fecha_inicio': today,
            'fecha_fin': today,
            'urgencia': 'ALTA',
            'estado': 'ACTIVA'
        })
        self.assertRedirects(response, reverse('monitorear_progreso'))
        campania_creada = Campania.objects.get(titulo='Campaña Sanitaria 2026')
        self.assertIsNotNone(campania_creada.progreso)

    def test_ds_10_editar_campania_flujo(self):
        """DS-10: Verificación de secuencia de modificación de campaña."""
        self.client.login(username='admin_ds', password='password123')
        today = timezone.now().date()
        response = self.client.post(reverse('editar_campania', kwargs={'pk': self.campania.id}), {
            'titulo': 'Refugio Canino Modificado 2026',
            'descripcion': self.campania.descripcion,
            'organizacion': self.org.id,
            'categoria': self.cat.id,
            'causa': '',
            'monto_objetivo': '9500.00',
            'fecha_inicio': today,
            'fecha_fin': today,
            'urgencia': 'CRITICA',
            'estado': 'ACTIVA'
        })
        self.assertRedirects(response, reverse('monitorear_progreso'))
        self.campania.refresh_from_db()
        self.assertEqual(self.campania.titulo, 'Refugio Canino Modificado 2026')
        self.assertEqual(self.campania.urgencia, 'CRITICA')

    def test_ds_11_monitorear_progreso_flujo(self):
        """DS-11: Verificación de secuencia de monitoreo de progreso."""
        self.client.login(username='admin_ds', password='password123')
        response = self.client.get(reverse('monitorear_progreso'))
        self.assertEqual(response.status_code, 200)

    def test_ds_12_visualizar_estadisticas_flujo(self):
        """DS-12: Verificación de secuencia de cálculo y visualización de estadísticas."""
        self.client.login(username='admin_ds', password='password123')
        response = self.client.get(reverse('visualizar_estadisticas'))
        self.assertEqual(response.status_code, 200)

    def test_ds_13_generar_reportes_flujo(self):
        """DS-13: Verificación de secuencia de generación y exportación de reportes."""
        self.client.login(username='admin_ds', password='password123')
        response = self.client.post(reverse('generar_reportes'), {
            'titulo': 'Reporte Trimestral Q1',
            'tipo_reporte': 'CAMPANIAS',
            'parametros': 'Urgencia=CRITICA'
        })
        self.assertRedirects(response, reverse('generar_reportes'))
        reporte = Reporte.objects.get(titulo='Reporte Trimestral Q1')
        self.assertIsNotNone(reporte)
        self.assertEqual(reporte.generado_por, self.user_admin)
