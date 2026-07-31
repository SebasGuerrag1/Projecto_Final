from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
import hashlib

class Usuario(AbstractUser):
    ROLES = (
        ('DONANTE', 'Donante'),
        ('ADMINISTRADOR_SISTEMA', 'Administrador del Sistema'),
    )
    rol = models.CharField(max_length=30, choices=ROLES, default='DONANTE')
    codigo_2fa = models.CharField(max_length=6, blank=True, null=True)
    requiere_2fa = models.BooleanField(default=False)

    def es_donante(self):
        return self.rol == 'DONANTE'

    def es_admin(self):
        return self.rol == 'ADMINISTRADOR_SISTEMA' or self.is_superuser

class Donante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_donante')
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Donante: {self.usuario.get_full_name() or self.usuario.username}"

class AdministradorSistema(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_admin')
    departamento = models.CharField(max_length=100, default='Administración General')
    nivel_acceso = models.CharField(max_length=50, default='TOTAL')

    def __str__(self):
        return f"Admin: {self.usuario.username}"

class OrganizacionBenefica(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADA', 'Verificada'),
        ('RECHAZADA', 'Rechazada'),
    )
    nombre = models.CharField(max_length=150)
    nit = models.CharField(max_length=30, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30)
    direccion = models.CharField(max_length=255)
    estado_verificacion = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    documento_verificacion = models.CharField(max_length=255, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.estado_verificacion})"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Causa(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='causas')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre}"

class ObjetivoRecaudacion(models.Model):
    monto_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return f"Objetivo: ${self.monto_objetivo:,.2f} ({self.fecha_inicio} a {self.fecha_fin})"

class Campania(models.Model):
    ESTADOS = (
        ('ACTIVA', 'Activa'),
        ('PAUSADA', 'Pausada'),
        ('FINALIZADA', 'Finalizada'),
    )
    URGENCIAS = (
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    organizacion = models.ForeignKey(OrganizacionBenefica, on_delete=models.CASCADE, related_name='campanias')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='campanias')
    causa = models.ForeignKey(Causa, on_delete=models.SET_NULL, null=True, blank=True, related_name='campanias')
    objetivo = models.OneToOneField(ObjetivoRecaudacion, on_delete=models.CASCADE, related_name='campania')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVA')
    urgencia = models.CharField(max_length=20, choices=URGENCIAS, default='MEDIA')
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class ProgresoRecaudacion(models.Model):
    campania = models.OneToOneField(Campania, on_delete=models.CASCADE, related_name='progreso')
    monto_recaudado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cantidad_donaciones = models.PositiveIntegerField(default=0)
    porcentaje_alcanzado = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def actualizar(self):
        total_donado = self.campania.donaciones.filter(estado='COMPLETADA').aggregate(
            total=models.Sum('monto'),
            count=models.Count('id')
        )
        monto = total_donado['total'] or Decimal('0.00')
        count = total_donado['count'] or 0
        self.monto_recaudado = monto
        self.cantidad_donaciones = count
        if self.campania.objetivo and self.campania.objetivo.monto_objetivo > 0:
            porcentaje = (monto / self.campania.objetivo.monto_objetivo) * Decimal('100.00')
            self.porcentaje_alcanzado = min(porcentaje, Decimal('100.00'))
        self.save()

    def __str__(self):
        return f"{self.campania.titulo}: ${self.monto_recaudado} ({self.porcentaje_alcanzado}%)"

class MetodoPago(models.Model):
    TIPOS = (
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('PAYPAL', 'PayPal'),
    )
    donante = models.ForeignKey(Donante, on_delete=models.CASCADE, related_name='metodos_pago')
    tipo = models.CharField(max_length=30, choices=TIPOS, default='TARJETA_CREDITO')
    titular = models.CharField(max_length=150)
    ultimos_digitos = models.CharField(max_length=4)
    token = models.CharField(max_length=100, unique=True)
    es_predeterminado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - **** {self.ultimos_digitos} ({self.titular})"

class Donacion(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('FALLIDA', 'Fallida'),
    )
    donante = models.ForeignKey(Donante, on_delete=models.CASCADE, related_name='donaciones')
    campania = models.ForeignKey(Campania, on_delete=models.CASCADE, related_name='donaciones')
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    fecha = models.DateTimeField(auto_now_add=True)
    es_anonima = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        donante_str = "Anónimo" if self.es_anonima else self.donante.usuario.username
        return f"Donación ${self.monto} de {donante_str} a {self.campania.titulo}"

class Transaccion(models.Model):
    ESTADOS = (
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('EN_PROCESO', 'En Proceso'),
    )
    donacion = models.OneToOneField(Donacion, on_delete=models.CASCADE, related_name='transaccion')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_transaccion = models.CharField(max_length=100, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='EN_PROCESO')
    mensaje_error = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TX {self.codigo_transaccion}: {self.estado} (${self.monto})"

class ReciboElectronico(models.Model):
    donacion = models.OneToOneField(Donacion, on_delete=models.CASCADE, related_name='recibo')
    numero_recibo = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    hash_verificacion = models.CharField(max_length=64)
    pdf_path = models.CharField(max_length=255, blank=True)
    enviado_email = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.numero_recibo:
            self.numero_recibo = f"REC-{uuid.uuid4().hex[:8].upper()}"
        if not self.hash_verificacion:
            base_str = f"{self.numero_recibo}-{self.donacion_id}-{self.donacion.monto}"
            self.hash_verificacion = hashlib.sha256(base_str.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recibo {self.numero_recibo} - Donación #{self.donacion.id}"

class EstadisticaDonaciones(models.Model):
    campania = models.OneToOneField(Campania, on_delete=models.CASCADE, related_name='estadistica')
    total_donaciones = models.PositiveIntegerField(default=0)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    donacion_promedio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    donacion_maxima = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def recalcular(self):
        donaciones = self.campania.donaciones.filter(estado='COMPLETADA')
        agg = donaciones.aggregate(
            total_count=models.Count('id'),
            total_sum=models.Sum('monto'),
            max_monto=models.Max('monto'),
            avg_monto=models.Avg('monto')
        )
        self.total_donaciones = agg['total_count'] or 0
        self.monto_total = agg['total_sum'] or Decimal('0.00')
        self.donacion_maxima = agg['max_monto'] or Decimal('0.00')
        self.donacion_promedio = agg['avg_monto'] or Decimal('0.00')
        self.save()

    def __str__(self):
        return f"Estadísticas {self.campania.titulo}: Total ${self.monto_total}"

class Reporte(models.Model):
    TIPOS = (
        ('DONACIONES', 'Reporte de Donaciones'),
        ('CAMPANIAS', 'Reporte de Campañas'),
        ('ORGANIZACIONES', 'Reporte de Organizaciones'),
    )
    titulo = models.CharField(max_length=200)
    tipo_reporte = models.CharField(max_length=30, choices=TIPOS)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    parametros = models.TextField(blank=True)
    archivo_url = models.CharField(max_length=255, blank=True)
    generado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Reporte: {self.titulo} ({self.get_tipo_reporte_display()})"
