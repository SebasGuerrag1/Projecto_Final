from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from decimal import Decimal
from django.http import HttpResponse, Http404

from .models import (
    Usuario, Donante, AdministradorSistema, OrganizacionBenefica,
    Categoria, Causa, ObjetivoRecaudacion, Campania, ProgresoRecaudacion,
    MetodoPago, Donacion, Transaccion, ReciboElectronico, EstadisticaDonaciones, Reporte
)
from .forms import (
    LoginForm, RegistroDonanteForm, FiltroCausasForm, DonacionForm,
    MetodoPagoForm, OrganizacionForm, CampaniaForm, ReporteForm
)
from .services import (
    AuthenticationService, TokenizacionService, PasarelaPagoService,
    ReciboService, ValidacionDocumentosService, ProgresoService,
    EstadisticasService, ReporteService
)

def index_view(request):
    campanias_destacadas = Campania.objects.filter(estado='ACTIVA').order_by('-urgencia', '-creada_en')[:6]
    total_recaudado = ProgresoRecaudacion.objects.aggregate(total=Sum('monto_recaudado'))['total'] or Decimal('0.00')
    total_donaciones = Donacion.objects.filter(estado='COMPLETADA').count()
    total_organizaciones = OrganizacionBenefica.objects.filter(estado_verificacion='VERIFICADA').count()

    context = {
        'campanias_destacadas': campanias_destacadas,
        'total_recaudado': total_recaudado,
        'total_donaciones': total_donaciones,
        'total_organizaciones': total_organizaciones,
    }
    return render(request, 'index.html', context)

# CU-01: Iniciar Sesión
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            codigo_2fa = form.cleaned_data.get('codigo_2fa')

            # Buscar usuario por username o email
            user_obj = Usuario.objects.filter(username=username_or_email).first()
            if not user_obj:
                user_obj = Usuario.objects.filter(email=username_or_email).first()

            if user_obj:
                user = authenticate(username=user_obj.username, password=password)
                if user is not None:
                    if user.requiere_2fa and not AuthenticationService.validar_2fa(user, codigo_2fa):
                        messages.error(request, "Código 2FA incorrecto o no proporcionado.")
                        return render(request, 'donatenow_app/login.html', {'form': form})
                    
                    login(request, user)
                    messages.success(request, f"¡Bienvenido de nuevo, {user.get_full_name() or user.username}!")
                    return redirect('index')
            messages.error(request, "Credenciales de acceso inválidas.")
    else:
        form = LoginForm()

    return render(request, 'donatenow_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('index')

# CU-02: Registrarse
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegistroDonanteForm(request.POST)
        if form.is_valid():
            user = Usuario.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['nombre'],
                last_name=form.cleaned_data['apellido'],
                rol='DONANTE'
            )
            donante = Donante.objects.create(
                usuario=user,
                direccion=form.cleaned_data.get('direccion', ''),
                telefono=form.cleaned_data.get('telefono', '')
            )

            # Si registró un método de pago preferido
            tipo_tarjeta = form.cleaned_data.get('tipo_tarjeta')
            numero_tarjeta = form.cleaned_data.get('numero_tarjeta')
            titular_tarjeta = form.cleaned_data.get('titular_tarjeta')

            if tipo_tarjeta and numero_tarjeta and titular_tarjeta:
                token, ultimos_4 = TokenizacionService.tokenizar_tarjeta(numero_tarjeta, titular_tarjeta)
                MetodoPago.objects.create(
                    donante=donante,
                    tipo=tipo_tarjeta,
                    titular=titular_tarjeta,
                    ultimos_digitos=ultimos_4,
                    token=token,
                    es_predeterminado=True
                )

            login(request, user)
            messages.success(request, "¡Registro completado exitosamente! Ahora eres parte de DonateNow.")
            return redirect('index')
    else:
        form = RegistroDonanteForm()

    return render(request, 'donatenow_app/registro.html', {'form': form})

# CU-03: Explorar Causas Benéficas
def explorar_causas_view(request):
    campanias = Campania.objects.filter(estado='ACTIVA')
    form = FiltroCausasForm(request.GET)

    if form.is_valid():
        categoria = form.cleaned_data.get('categoria')
        urgencia = form.cleaned_data.get('urgencia')
        q = form.cleaned_data.get('q')

        if categoria:
            campanias = campanias.filter(categoria=categoria)
        if urgencia:
            campanias = campanias.filter(urgencia=urgencia)
        if q:
            campanias = campanias.filter(titulo__icontains=q) | campanias.filter(descripcion__icontains=q)

    context = {
        'campanias': campanias,
        'form': form,
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'donatenow_app/causas.html', context)

def detalle_campania_view(request, pk):
    campania = get_object_or_404(Campania, pk=pk)
    progreso, created = ProgresoRecaudacion.objects.get_or_create(campania=campania)
    progreso.actualizar()
    donaciones_recientes = campania.donaciones.filter(estado='COMPLETADA').order_by('-fecha')[:5]

    context = {
        'campania': campania,
        'progreso': progreso,
        'donaciones_recientes': donaciones_recientes,
    }
    return render(request, 'donatenow_app/detalle_causa.html', context)

# CU-04: Realizar Donación
@login_required
def realizar_donacion_view(request, campania_id):
    campania = get_object_or_404(Campania, pk=campania_id)
    donante = getattr(request.user, 'perfil_donante', None)

    if not donante:
        messages.error(request, "Solo los usuarios registrados como Donantes pueden realizar donaciones.")
        return redirect('index')

    metodos_pago = donante.metodos_pago.filter(activo=True)

    if request.method == 'POST':
        form = DonacionForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            metodo_pago_id = form.cleaned_data['metodo_pago_id']
            es_anonima = form.cleaned_data['es_anonima']

            metodo_pago = get_object_or_404(MetodoPago, pk=metodo_pago_id, donante=donante)

            donacion = Donacion.objects.create(
                donante=donante,
                campania=campania,
                monto=monto,
                es_anonima=es_anonima,
                estado='PENDIENTE'
            )

            # CU-06: Procesar Transacción
            tx, exito = PasarelaPagoService.procesar_cobro(donacion, metodo_pago)

            if exito:
                # CU-07: Recibir Recibo Electrónico
                recibo = ReciboService.generar_recibo(donacion)
                messages.success(request, f"¡Donación procesada con éxito! Tu número de recibo es {recibo.numero_recibo}.")
                return redirect('ver_recibo', recibo_id=recibo.id)
            else:
                messages.error(request, f"La transacción fue rechazada: {tx.mensaje_error}")
                return redirect('detalle_causa', pk=campania.id)
    else:
        form = DonacionForm(initial={'campania_id': campania.id})

    context = {
        'campania': campania,
        'form': form,
        'metodos_pago': metodos_pago,
    }
    return render(request, 'donatenow_app/donar.html', context)

# CU-05: Seleccionar / Agregar Método de Pago
@login_required
def seleccionar_metodo_pago_view(request):
    donante = getattr(request.user, 'perfil_donante', None)
    if not donante:
        messages.error(request, "Perfil de donante no encontrado.")
        return redirect('index')

    metodos = donante.metodos_pago.filter(activo=True)
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            titular = form.cleaned_data['titular']
            num_tarjeta = form.cleaned_data['numero_tarjeta']
            es_predet = form.cleaned_data['es_predeterminado']

            token, ultimos_4 = TokenizacionService.tokenizar_tarjeta(num_tarjeta, titular)

            if es_predet:
                donante.metodos_pago.update(es_predeterminado=False)

            MetodoPago.objects.create(
                donante=donante,
                tipo=tipo,
                titular=titular,
                ultimos_digitos=ultimos_4,
                token=token,
                es_predeterminado=es_predet
            )
            messages.success(request, "Nuevo método de pago agregado correctamente.")
            return redirect('seleccionar_metodo_pago')
    else:
        form = MetodoPagoForm()

    return render(request, 'donatenow_app/metodo_pago.html', {'metodos': metodos, 'form': form})

# CU-07: Ver Recibo Electrónico
@login_required
def ver_recibo_view(request, recibo_id):
    recibo = get_object_or_404(ReciboElectronico, pk=recibo_id)

    # Verificar permisos (solo el donante o un admin puede ver el recibo)
    if not request.user.es_admin() and recibo.donacion.donante.usuario != request.user:
        messages.error(request, "No tienes permiso para ver este recibo.")
        return redirect('index')

    return render(request, 'donatenow_app/recibo.html', {'recibo': recibo})

# CU-08: Gestionar Organizaciones Benéficas (Admin)
@login_required
def gestionar_organizaciones_view(request):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores del Sistema.")
        return redirect('index')

    organizaciones = OrganizacionBenefica.objects.all().order_by('-creada_en')
    if request.method == 'POST':
        form = OrganizacionForm(request.POST)
        if form.is_valid():
            org = form.save()
            messages.success(request, f"Organización '{org.nombre}' guardada exitosamente.")
            return redirect('gestionar_organizaciones')
    else:
        form = OrganizacionForm()

    return render(request, 'donatenow_app/organizaciones.html', {'organizaciones': organizaciones, 'form': form})

@login_required
def verificar_organizacion_view(request, pk):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores.")
        return redirect('index')

    org = get_object_or_404(OrganizacionBenefica, pk=pk)
    ValidacionDocumentosService.verificar_organizacion(org)
    messages.success(request, f"La organización {org.nombre} ha sido verificada exitosamente.")
    return redirect('gestionar_organizaciones')

# CU-09: Crear Campaña (Admin)
@login_required
def crear_campania_view(request):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores del Sistema.")
        return redirect('index')

    if request.method == 'POST':
        form = CampaniaForm(request.POST)
        if form.is_valid():
            objetivo = ObjetivoRecaudacion.objects.create(
                monto_objetivo=form.cleaned_data['monto_objetivo'],
                fecha_inicio=form.cleaned_data['fecha_inicio'],
                fecha_fin=form.cleaned_data['fecha_fin']
            )

            campania = Campania.objects.create(
                titulo=form.cleaned_data['titulo'],
                descripcion=form.cleaned_data['descripcion'],
                organizacion=form.cleaned_data['organizacion'],
                categoria=form.cleaned_data['categoria'],
                causa=form.cleaned_data['causa'],
                objetivo=objetivo,
                urgencia=form.cleaned_data['urgencia'],
                estado=form.cleaned_data['estado']
            )

            ProgresoService.actualizar_progreso(campania)
            EstadisticasService.actualizar_estadisticas(campania)

            messages.success(request, f"Campaña '{campania.titulo}' creada con éxito.")
            return redirect('monitorear_progreso')
    else:
        form = CampaniaForm()

    return render(request, 'donatenow_app/crear_campania.html', {'form': form})

# CU-10: Editar Campaña (Admin)
@login_required
def editar_campania_view(request, pk):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores.")
        return redirect('index')

    campania = get_object_or_404(Campania, pk=pk)
    if request.method == 'POST':
        form = CampaniaForm(request.POST)
        if form.is_valid():
            campania.titulo = form.cleaned_data['titulo']
            campania.descripcion = form.cleaned_data['descripcion']
            campania.organizacion = form.cleaned_data['organizacion']
            campania.categoria = form.cleaned_data['categoria']
            campania.causa = form.cleaned_data['causa']
            campania.urgencia = form.cleaned_data['urgencia']
            campania.estado = form.cleaned_data['estado']

            campania.objetivo.monto_objetivo = form.cleaned_data['monto_objetivo']
            campania.objetivo.fecha_inicio = form.cleaned_data['fecha_inicio']
            campania.objetivo.fecha_fin = form.cleaned_data['fecha_fin']
            campania.objetivo.save()
            campania.save()

            ProgresoService.actualizar_progreso(campania)
            messages.success(request, f"Campaña '{campania.titulo}' actualizada correctamente.")
            return redirect('monitorear_progreso')
    else:
        initial_data = {
            'titulo': campania.titulo,
            'descripcion': campania.descripcion,
            'organizacion': campania.organizacion,
            'categoria': campania.categoria,
            'causa': campania.causa,
            'monto_objetivo': campania.objetivo.monto_objetivo if campania.objetivo else 0,
            'fecha_inicio': campania.objetivo.fecha_inicio if campania.objetivo else None,
            'fecha_fin': campania.objetivo.fecha_fin if campania.objetivo else None,
            'urgencia': campania.urgencia,
            'estado': campania.estado,
        }
        form = CampaniaForm(initial=initial_data)

    return render(request, 'donatenow_app/editar_campania.html', {'form': form, 'campania': campania})

# CU-11: Monitorear Progreso de Recaudación (Admin)
@login_required
def monitorear_progreso_view(request):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores.")
        return redirect('index')

    campanias = Campania.objects.all().order_by('-creada_en')
    for c in campanias:
        ProgresoService.actualizar_progreso(c)

    return render(request, 'donatenow_app/progreso.html', {'campanias': campanias})

# CU-12: Visualizar Estadísticas de Donaciones (Admin)
@login_required
def visualizar_estadisticas_view(request):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores.")
        return redirect('index')

    total_donado = Donacion.objects.filter(estado='COMPLETADA').aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
    promedio_donado = Donacion.objects.filter(estado='COMPLETADA').aggregate(Avg('monto'))['monto__avg'] or Decimal('0.00')
    count_donaciones = Donacion.objects.filter(estado='COMPLETADA').count()

    estadisticas_campanias = EstadisticaDonaciones.objects.all().order_by('-monto_total')

    context = {
        'total_donado': total_donado,
        'promedio_donado': promedio_donado,
        'count_donaciones': count_donaciones,
        'estadisticas_campanias': estadisticas_campanias,
    }
    return render(request, 'donatenow_app/estadisticas.html', context)

# CU-13: Generar Reportes (Admin)
@login_required
def generar_reportes_view(request):
    if not request.user.es_admin():
        messages.error(request, "Acceso restringido a Administradores.")
        return redirect('index')

    reportes = Reporte.objects.all().order_by('-fecha_generacion')
    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid():
            reporte = ReporteService.generar_reporte(
                titulo=form.cleaned_data['titulo'],
                tipo_reporte=form.cleaned_data['tipo_reporte'],
                parametros=form.cleaned_data.get('parametros', ''),
                usuario=request.user
            )
            messages.success(request, f"Reporte '{reporte.titulo}' generado correctamente.")
            return redirect('generar_reportes')
    else:
        form = ReporteForm()

    return render(request, 'donatenow_app/reportes.html', {'reportes': reportes, 'form': form})
