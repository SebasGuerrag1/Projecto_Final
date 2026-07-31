Implementa una aplicación web funcional basada en el diagrama de secuencia proporcionado, respetando las convenciones de Django y modificando todos los archivos necesarios para que el proyecto funcione correctamente.

---

## 1\. Plantillas globales del proyecto

### base.html

En el directorio global templates, crea o modifica el archivo base.html.

Requisitos:

* Debe definir la estructura visual común de todo el sitio.

* Debe incluir: \<head\> completo, título configurable mediante bloques, barra de navegación, área principal de contenido, pie de página y bloques Django ({% block %}) para permitir herencia.

* Utiliza HTML semántico y diseño limpio.

* Aplica un estilo moderno y consistente utilizando CSS integrado o archivos estáticos del proyecto.

### index.html

En el directorio global templates, crea o modifica el archivo index.html.

Requisitos:

* Debe heredar de base.html.

* Debe representar la página principal del sistema.

* Debe mostrar enlaces de navegación hacia los módulos disponibles.

* Debe utilizar los bloques definidos en base.html.

### Configuración de URLs

Modifica la configuración global de URLs del proyecto para que la ruta raíz (/) muestre index.html y mantenga correctamente las rutas de las aplicaciones existentes.

---

## 2\. Caso de uso: Registrar Autor

Analiza el caso de uso contenido en el archivo Registrar\_Autor\_CU\_001.md y el diagrama de secuencia contenido en el archivo Registrar\_Autor\_DS\_001.puml.

A partir de dichos artefactos implementa completamente el caso de uso en la aplicación app\_autor.

### Requisitos

Determina e implementa todo lo necesario según el flujo descrito:

* Modelos (models.py)

* Formularios (forms.py)

* Vistas (views.py)

* URLs (urls.py)

* Plantillas

* Validaciones

* Mensajes al usuario

* Redirecciones

* Persistencia de datos

* Configuración administrativa (admin.py) cuando corresponda

### Plantillas

Utiliza exclusivamente la carpeta app\_autor/templates/app\_autor.

Crea todas las plantillas necesarias para el flujo completo. Las plantillas deben:

* Heredar de base.html.

* Mostrar errores de validación.

* Mostrar mensajes de éxito.

* Mantener una interfaz consistente con el resto del sitio.

---

## 3\. Integración del Proyecto

Realiza todas las modificaciones necesarias para que el proyecto funcione correctamente:

* Configuración de URLs globales.

* Registro de aplicaciones.

* Configuración de plantillas.

* Configuración de archivos estáticos.

* Migraciones necesarias.

* Imports faltantes.

* Configuración del panel de administración.

No dejes código incompleto, pseudocódigo ni secciones marcadas como TODO.

---

## 4\. Resultado Esperado

Entrega una implementación completamente funcional. Para cada archivo creado o modificado:

1. Indica la ruta completa del archivo.

2. Muestra el contenido completo del archivo.

3. Explica brevemente el propósito de los cambios realizados.

Verifica que el código generado sea consistente, ejecutable y compatible con Django.