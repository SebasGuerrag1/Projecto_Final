from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from donatenow_app.models import (
    Usuario, Donante, AdministradorSistema, OrganizacionBenefica,
    Categoria, Causa, ObjetivoRecaudacion, Campania, ProgresoRecaudacion,
    MetodoPago, Donacion, Transaccion, ReciboElectronico, EstadisticaDonaciones, Reporte
)

class ModelTestCase(TestCase):
    """
    CP-MODELS: Pruebas unitarias de creación, relaciones y métodos en los modelos de dominio.
    """

    def setUp(self):
        self.user_donante = Usuario.objects.create_user(
            username='donante1',
            email='donante1@test.com',
            password='password123',
            rol='DONANTE'
        )
        self.donante = Donante.objects.create(
            usuario=self.user_donante,
            direccion='Calle 123',
            telefono='555-1234'
        )
        self.user_admin = Usuario.objects.create_user(
            username='admin1',
            email='admin1@test.com',
            password='password123',
            rol='ADMINISTRADOR_SISTEMA'
        )
        self.admin_profile = AdministradorSistema.objects.create(
            usuario=self.user_admin,
            departamento='Sistemas'
        )
        self.org = OrganizacionBenefica.objects.create(
            nombre='Fundación Esperanza',
            nit='900123456-1',
            email='contacto@esperanza.org',
            telefono='555-9999',
            direccion='Av Principal 45',
            estado_verificacion='VERIFICADA'
        )
        self.cat = Categoria.objects.create(
            nombre='Salud y Nutrición',
            descripcion='Causas relacionadas con servicios médicos'
        )
        self.causa = Causa.objects.create(
            categoria=self.cat,
            nombre='Hospital Infantil',
            descripcion='Construcción de pabellón médico'
        )
        self.objetivo = ObjetivoRecaudacion.objects.create(
            monto_objetivo=Decimal('10000.00'),
            fecha_inicio=timezone.now().date(),
            fecha_fin=timezone.now().date()
        )
        self.campania = Campania.objects.create(
            titulo='Ayuda Infantil 2026',
            descripcion='Recaudación para medicamentos infantiles',
            organizacion=self.org,
            categoria=self.cat,
            causa=self.causa,
            objetivo=self.objetivo,
            urgencia='ALTA',
            estado='ACTIVA'
        )

    def test_usuario_roles_and_methods(self):
        """CP-MOD-01: Verificar roles y métodos de ayuda en el modelo Usuario."""
        self.assertTrue(self.user_donante.es_donante())
        self.assertFalse(self.user_donante.es_admin())
        self.assertTrue(self.user_admin.es_admin())
        self.assertFalse(self.user_admin.es_donante())

    def test_donacion_and_progreso_calculation(self):
        """CP-MOD-02: Verificar actualización automática de progreso y estadísticas en donaciones completadas."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('2500.00'),
            estado='COMPLETADA'
        )
        progreso, _ = ProgresoRecaudacion.objects.get_or_create(campania=self.campania)
        progreso.actualizar()

        self.assertEqual(progreso.monto_recaudado, Decimal('2500.00'))
        self.assertEqual(progreso.cantidad_donaciones, 1)
        self.assertEqual(progreso.porcentaje_alcanzado, Decimal('25.00'))

        estadistica, _ = EstadisticaDonaciones.objects.get_or_create(campania=self.campania)
        estadistica.recalcular()

        self.assertEqual(estadistica.monto_total, Decimal('2500.00'))
        self.assertEqual(estadistica.donacion_maxima, Decimal('2500.00'))
        self.assertEqual(estadistica.donacion_promedio, Decimal('2500.00'))

    def test_recibo_electronico_hash_generation(self):
        """CP-MOD-03: Verificar generación de hash SHA-256 único y número de recibo."""
        donacion = Donacion.objects.create(
            donante=self.donante,
            campania=self.campania,
            monto=Decimal('100.00'),
            estado='COMPLETADA'
        )
        recibo = ReciboElectronico.objects.create(donacion=donacion)
        self.assertTrue(recibo.numero_recibo.startswith('REC-'))
        self.assertEqual(len(recibo.hash_verificacion), 64)
