from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Donante, AdministradorSistema, OrganizacionBenefica,
    Categoria, Causa, ObjetivoRecaudacion, Campania, ProgresoRecaudacion,
    MetodoPago, Donacion, Transaccion, ReciboElectronico, EstadisticaDonaciones, Reporte
)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'requiere_2fa', 'is_staff', 'is_superuser']
    list_filter = ['rol', 'requiere_2fa', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Información DonateNow', {'fields': ('rol', 'codigo_2fa', 'requiere_2fa')}),
    )

@admin.register(Donante)
class DonanteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'direccion', 'telefono']
    search_fields = ['usuario__username', 'usuario__email']

@admin.register(AdministradorSistema)
class AdministradorSistemaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'departamento', 'nivel_acceso']

@admin.register(OrganizacionBenefica)
class OrganizacionBeneficaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'email', 'telefono', 'estado_verificacion', 'creada_en']
    list_filter = ['estado_verificacion', 'creada_en']
    search_fields = ['nombre', 'nit', 'email']

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']

@admin.register(Causa)
class CausaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria']
    list_filter = ['categoria']

@admin.register(ObjetivoRecaudacion)
class ObjetivoRecaudacionAdmin(admin.ModelAdmin):
    list_display = ['monto_objetivo', 'fecha_inicio', 'fecha_fin']

@admin.register(Campania)
class CampaniaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'organizacion', 'categoria', 'urgencia', 'estado', 'creada_en']
    list_filter = ['estado', 'urgencia', 'categoria', 'organizacion']
    search_fields = ['titulo', 'descripcion']

@admin.register(ProgresoRecaudacion)
class ProgresoRecaudacionAdmin(admin.ModelAdmin):
    list_display = ['campania', 'monto_recaudado', 'cantidad_donaciones', 'porcentaje_alcanzado', 'ultima_actualizacion']

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['donante', 'tipo', 'titular', 'ultimos_digitos', 'es_predeterminado', 'activo']
    list_filter = ['tipo', 'es_predeterminado', 'activo']

@admin.register(Donacion)
class DonacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'donante', 'campania', 'monto', 'estado', 'es_anonima', 'fecha']
    list_filter = ['estado', 'es_anonima', 'fecha']

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['codigo_transaccion', 'donacion', 'monto', 'estado', 'fecha']
    list_filter = ['estado', 'fecha']
    search_fields = ['codigo_transaccion']

@admin.register(ReciboElectronico)
class ReciboElectronicoAdmin(admin.ModelAdmin):
    list_display = ['numero_recibo', 'donacion', 'fecha_emision', 'enviado_email']
    search_fields = ['numero_recibo', 'hash_verificacion']

@admin.register(EstadisticaDonaciones)
class EstadisticaDonacionesAdmin(admin.ModelAdmin):
    list_display = ['campania', 'monto_total', 'total_donaciones', 'donacion_promedio', 'donacion_maxima']

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_reporte', 'fecha_generacion', 'generado_por']
    list_filter = ['tipo_reporte', 'fecha_generacion']
