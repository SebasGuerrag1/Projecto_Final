from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from donatenow_app.models import (
    Usuario, Donante, AdministradorSistema, OrganizacionBenefica, Categoria,
    Causa, ObjetivoRecaudacion, Campania, MetodoPago, Donacion, Transaccion,
    ReciboElectronico, ProgresoRecaudacion, EstadisticaDonaciones, Reporte
)
from donatenow_app.services import (
    AuthenticationService, TokenizacionService, PasarelaPagoService,
    ReciboService, ValidacionDocumentosService, ProgresoService,
    EstadisticasService, ReporteService
)

class ServiceTestCase(TestCase):
    """
    CP-SERVICES: Pruebas unitarias para los servicios de lógica de negocio (Pasarela, 2FA, Tokenización, Recibos, Reportes).
    """

    def setUp(self):
        self.user_donante = Usuario.objects.create_user(
            username='donanteservice',
            email='donanteservice@test.com',
            password='password123',
            rol='DONANTE'
        )
        self.donante = Donante.objects.create(usuario=self.user_donante)
        self.user_admin = Usuario.objects.create_user(
            username='adminservice',
            email='adminservice@test.com',
            password='password123',
            rol='ADMINISTRADOR_SISTEMA'
        )

        self.org = OrganizacionBenefica.objects.create(
            nombre='Fundación Servicio',
            nit='800111222-3',
            email='orgservice@test.com',
            telefono='555-4321',
            direccion='Calle Servicio 10'
        )
        self.cat = Categoria.objects.create(nombre='Salud Global')
        self.objetivo = ObjetivoRecaudacion.objects.create(
            monto_objetivo=Decimal('20000.00'),
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date()
        )
        self.campania = Campania.objects.create(
            titulo='Campaña Salud 2026',
            descripcion='Equipos médicos',
            organizacion=self.org,
            categoria=self.cat,
            objetivo=self.objetivo
        )

        token, ultimos_4 = TokenizacionService.tokenizar_tarjeta('4532123456789010', 'Donante Service')
        self.metodo_pago = MetodoPago.objects.create(
            donante=self.donante,
            tipo='TARJETA_CREDITO',
            titular='Donante Service',
            ultimos_digitos=ultimos_4,
            token=token,
            es_predeterminado=True
        )

    def test_2fa_generation_and_validation(self):
        """CP-SERV-01: Generación y verificación de código 2FA."""
        self.user_donante.requiere_2fa = True
        self.user_donante.save()

        codigo = AuthenticationService.generar_codigo_2fa(self.user_donante)
        self.assertEqual(len(codigo), 6)
        self.assertTrue(AuthenticationService.validar_2fa(self.user_donante, codigo))
        self.assertFalse(AuthenticationService.validar_2fa(self.user_donante, '000000'))

    def test_pasarela_pago_exitoso(self):
        """CP-SERV-02: Procesamiento exitoso de cobro a través de PasarelaPagoService."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('500.00'),
            estado='PENDIENTE'
        )
        tx, exito = PasarelaPagoService.procesar_cobro(donacion, self.metodo_pago)

        self.assertTrue(exito)
        self.assertEqual(tx.estado, 'APROBADA')
        self.assertEqual(donacion.estado, 'COMPLETADA')

        # Verificar progreso actualizado
        progreso = ProgresoRecaudacion.objects.get(campania=self.campania)
        self.assertEqual(progreso.monto_recaudado, Decimal('500.00'))

    def test_pasarela_pago_fondos_insuficientes(self):
        """CP-SERV-03: Rechazo de cobro en PasarelaPagoService por fondos insuficientes (monto > 50,000)."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('60000.00'),
            estado='PENDIENTE'
        )
        tx, exito = PasarelaPagoService.procesar_cobro(donacion, self.metodo_pago)

        self.assertFalse(exito)
        self.assertEqual(tx.estado, 'RECHAZADA')
        self.assertEqual(donacion.estado, 'FALLIDA')

    def test_generacion_recibo(self):
        """CP-SERV-04: Generación automática de recibo electrónico con ReciboService."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('150.00'),
            estado='COMPLETADA'
        )
        recibo = ReciboService.generar_recibo(donacion)

        self.assertIsNotNone(recibo.numero_recibo)
        self.assertEqual(recibo.donacion, donacion)

    def test_reporte_service_generacion(self):
        """CP-SERV-05: Generación de reporte con ReporteService."""
        reporte = ReporteService.generar_reporte(
            titulo='Reporte Anual 2026',
            tipo_reporte='DONACIONES',
            parametros='Año=2026',
            usuario=self.user_admin
        )
        self.assertEqual(reporte.titulo, 'Reporte Anual 2026')
        self.assertEqual(reporte.tipo_reporte, 'DONACIONES')
        self.assertTrue(reporte.archivo_url.endswith('.pdf'))
