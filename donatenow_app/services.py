import uuid
import random
import hashlib
from decimal import Decimal
from django.utils import timezone
from .models import (
    Usuario, Donante, AdministradorSistema, MetodoPago, Donacion,
    Transaccion, ReciboElectronico, ProgresoRecaudacion, EstadisticaDonaciones,
    Reporte, OrganizacionBenefica, Campania
)

class AuthenticationService:
    @staticmethod
    def validar_2fa(usuario, codigo):
        if not usuario.requiere_2fa:
            return True
        return usuario.codigo_2fa == codigo

    @staticmethod
    def generar_codigo_2fa(usuario):
        codigo = f"{random.randint(100000, 999999)}"
        usuario.codigo_2fa = codigo
        usuario.save()
        return codigo

class TokenizacionService:
    @staticmethod
    def tokenizar_tarjeta(numero_tarjeta, titular):
        clean_num = str(numero_tarjeta).replace(" ", "").replace("-", "")
        ultimos_4 = clean_num[-4:] if len(clean_num) >= 4 else "0000"
        raw_str = f"{clean_num}-{titular}-{uuid.uuid4()}"
        token = f"TOK-{hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:24].upper()}"
        return token, ultimos_4

class PasarelaPagoService:
    @staticmethod
    def procesar_cobro(donacion, metodo_pago):
        if not metodo_pago or not metodo_pago.activo:
            tx = Transaccion.objects.create(
                donacion=donacion,
                metodo_pago=metodo_pago,
                codigo_transaccion=f"TX-FAIL-{uuid.uuid4().hex[:8].upper()}",
                monto=donacion.monto,
                estado='RECHAZADA',
                mensaje_error='Método de pago inválido o inactivo'
            )
            donacion.estado = 'FALLIDA'
            donacion.save()
            return tx, False

        # Simular fallo de cobro si monto es mayor a 50,000 (fondos insuficientes)
        if donacion.monto > Decimal('50000.00'):
            tx = Transaccion.objects.create(
                donacion=donacion,
                metodo_pago=metodo_pago,
                codigo_transaccion=f"TX-RECH-{uuid.uuid4().hex[:8].upper()}",
                monto=donacion.monto,
                estado='RECHAZADA',
                mensaje_error='Fondos insuficientes en la tarjeta'
            )
            donacion.estado = 'FALLIDA'
            donacion.save()
            return tx, False

        # Transacción exitosa
        tx = Transaccion.objects.create(
            donacion=donacion,
            metodo_pago=metodo_pago,
            codigo_transaccion=f"TX-OK-{uuid.uuid4().hex[:8].upper()}",
            monto=donacion.monto,
            estado='APROBADA',
            mensaje_error=''
        )
        donacion.estado = 'COMPLETADA'
        donacion.save()

        # Actualizar Progreso y Estadísticas de la campaña
        ProgresoService.actualizar_progreso(donacion.campania)
        EstadisticasService.actualizar_estadisticas(donacion.campania)

        return tx, True

class ReciboService:
    @staticmethod
    def generar_recibo(donacion):
        recibo, created = ReciboElectronico.objects.get_or_create(
            donacion=donacion,
            defaults={
                'pdf_path': f"/recibos/REC_{donacion.id}.pdf",
                'enviado_email': True
            }
        )
        return recibo

class ValidacionDocumentosService:
    @staticmethod
    def verificar_organizacion(organizacion, documento=None):
        if documento:
            organizacion.documento_verificacion = documento
        organizacion.estado_verificacion = 'VERIFICADA'
        organizacion.save()
        return True

class ProgresoService:
    @staticmethod
    def actualizar_progreso(campania):
        progreso, created = ProgresoRecaudacion.objects.get_or_create(campania=campania)
        progreso.actualizar()
        return progreso

class EstadisticasService:
    @staticmethod
    def actualizar_estadisticas(campania):
        estadistica, created = EstadisticaDonaciones.objects.get_or_create(campania=campania)
        estadistica.recalcular()
        return estadistica

class ReporteService:
    @staticmethod
    def generar_reporte(titulo, tipo_reporte, parametros='', usuario=None):
        reporte = Reporte.objects.create(
            titulo=titulo,
            tipo_reporte=tipo_reporte,
            parametros=parametros,
            archivo_url=f"/media/reportes/Reporte_{tipo_reporte}_{uuid.uuid4().hex[:6]}.pdf",
            generado_por=usuario
        )
        return reporte
