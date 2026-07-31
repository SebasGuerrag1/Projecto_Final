from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('causas/', views.explorar_causas_view, name='causas'),
    path('causas/<int:pk>/', views.detalle_campania_view, name='detalle_causa'),
    path('donar/<int:campania_id>/', views.realizar_donacion_view, name='realizar_donacion'),
    path('metodos-pago/', views.seleccionar_metodo_pago_view, name='seleccionar_metodo_pago'),
    path('recibo/<int:recibo_id>/', views.ver_recibo_view, name='ver_recibo'),
    
    # Rutas Administrativas
    path('admin-panel/organizaciones/', views.gestionar_organizaciones_view, name='gestionar_organizaciones'),
    path('admin-panel/organizaciones/<int:pk>/verificar/', views.verificar_organizacion_view, name='verificar_organizacion'),
    path('admin-panel/campania/crear/', views.crear_campania_view, name='crear_campania'),
    path('admin-panel/campania/<int:pk>/editar/', views.editar_campania_view, name='editar_campania'),
    path('admin-panel/progreso/', views.monitorear_progreso_view, name='monitorear_progreso'),
    path('admin-panel/estadisticas/', views.visualizar_estadisticas_view, name='visualizar_estadisticas'),
    path('admin-panel/reportes/', views.generar_reportes_view, name='generar_reportes'),
]
