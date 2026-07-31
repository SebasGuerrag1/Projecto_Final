# 💖 Sistema de Donaciones en Línea "DonateNow"

Plataforma web integral desarrollada en **Django** para conectar donantes individuales con fundaciones y organizaciones benéficas verificadas. Permite la exploración de causas por categorías y nivel de urgencia, donaciones seguras con tokenización de tarjetas, emisión de recibos electrónicos con firma digital SHA-256, monitoreo de progreso en tiempo real y generación de reportes formales.

---

## 🔑 Credenciales del Administrador

Para acceder al **Panel Admin** de la plataforma y al administrador de Django:

- **URL de Login en la App**: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- **URL Admin Django**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Usuario / Email**: `admin` / `admin@donatenow.com`
- **Contraseña**: `admin123`
- **Rol**: Administrador del Sistema

---

## 🚀 Instrucciones de Ejecución

### 1. Activar el Entorno Virtual (`venv`)

El proyecto incluye un entorno virtual pré-configurado con Django 6.0.7:

**En Windows (PowerShell / CMD):**
```cmd
venv\Scripts\activate
```

---

### 2. Ejecutar el Servidor de Desarrollo

Con el entorno virtual activo:

```cmd
python manage.py runserver
```

O directamente ejecutando desde el binario del entorno virtual:

```cmd
venv\Scripts\python.exe manage.py runserver
```

Abre tu navegador en: **`http://127.0.0.1:8000/`**

---

### 3. Ejecutar la Suite de Pruebas Automatizadas

El proyecto incluye 33 pruebas unitarias y de integración que cubren los 13 Casos de Uso y sus Diagramas de Secuencia:

```cmd
python manage.py test donatenow_app
```

---

## 📋 Lista de Casos de Uso Implementados (CU-01 a CU-13)

| Identificador | Caso de Uso | Descripción y Funcionalidad |
|---|---|---|
| **CU-01** | Iniciar Sesión | Autenticación con soporte para 2FA, recuerdo de sesión y alternador de visibilidad de contraseña (ojo/ocultar). |
| **CU-02** | Registrarse | Registro de nuevos donantes con contraseña visible/oculta y tokenización de método de pago preferido. |
| **CU-03** | Explorar Causas | Catálogo de campañas filtrables por categoría, urgencia (Baja, Media, Alta, Crítica) y texto libre. |
| **CU-04** | Realizar Donación | Flujo de contribución económica con chips de monto ($5.000, $10.000, $25.000, $50.000) o libre y opción anónima. |
| **CU-05** | Seleccionar Método de Pago | Registro y tokenización segura de tarjetas de crédito/débito. |
| **CU-06** | Procesar Transacción | Integración con pasarela de pagos, manejo de cobros aprobados o rechazados por fondos. |
| **CU-07** | Recibir Recibo Electrónico | Generación automática de comprobantes con número de recibo y hash de verificación SHA-256. |
| **CU-08** | Gestionar Organizaciones | Panel administrativo para registro y verificación de fundaciones y ONGs. |
| **CU-09** | Crear Campaña | Alta de nuevas campañas de recaudación con definición de objetivos financieros y plazo. |
| **CU-10** | Editar Campaña | Modificación de datos, metas, urgencias y estados de campañas existentes. |
| **CU-11** | Monitorear Progreso | Tablero de control en tiempo real de recaudación vs meta. |
| **CU-12** | Visualizar Estadísticas | Métricas agregadas de total recaudado, promedio por donación y máximos. |
| **CU-13** | Generar Reportes | Exportación e historial de informes formales para rendición de cuentas. |

---

## 🎨 Sistema de Diseño (Figma Mockups)

- **Paleta de Colores**: Verde Teal (`#0f5945` / `#10b981`), fondo claro cálido (`#f4f6f8`) y tarjetas blancas con sombras suaves.
- **Iconografía**: Bootstrap Icons integrados.
- **Tipografía**: *Plus Jakarta Sans*.
- **Ocultar/Mostrar Contraseña**: Botón interactivo con icono de ojo (`bi-eye`) en todos los formularios de contraseña.
