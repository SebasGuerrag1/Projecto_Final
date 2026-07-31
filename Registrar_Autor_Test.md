Actúa como experto en QA y testing de aplicaciones Django.

Analiza el caso de uso contenido en el archivo Registrar\_Autor\_CU\_001.md y el diagrama de secuencia contenido en el archivo Registrar\_Autor\_DS\_001.puml.

---

# 1\. Elaboración de casos de prueba

A partir de los artefactos proporcionados, genera el catálogo completo de casos de prueba que cubra:

* Todos los escenarios descritos en los criterios de aceptación.

* Todos los flujos alternativos del diagrama de secuencia.

* Todas las reglas de negocio definidas en el caso de uso.

Para cada caso de prueba especifica:

| Campo | Descripción |
| :---- | :---- |
| ID | Identificador único (ej. CP-001) |
| Caso de uso | Referencia al CU que prueba |
| Descripción | Qué se está verificando |
| Precondiciones | Estado del sistema antes de ejecutar |
| Datos de entrada | Valores concretos utilizados |
| Pasos | Secuencia de acciones a ejecutar |
| Resultado esperado | Comportamiento esperado del sistema |
| Tipo | Positivo / Negativo / Borde |

---

# 2\. Implementación de pruebas en Django

Implementa cada caso de prueba como una prueba automatizada en Django, ubicada en el archivo app\_autor/tests.py.

## Requisitos

* Utiliza django.test.TestCase como clase base.

* Organiza las pruebas en clases agrupadas por escenario o flujo.

* Cada método de prueba debe corresponder a exactamente un caso de prueba del catálogo anterior, referenciando su ID en el docstring.

* Cubre los siguientes niveles:

  * **Modelo:** validaciones, restricciones y comportamiento del ORM.

  * **Formulario:** validación de campos obligatorios, duplicados y datos inválidos.

  * **Vista:** respuestas HTTP, redirecciones, mensajes al usuario y renderizado de plantillas.

* Utiliza Client de Django para las pruebas de vista.

* No uses mocks salvo que el diagrama de secuencia muestre dependencias externas explícitas.

## Datos de prueba

* Define los datos de prueba como constantes o en el método setUp de cada clase, usando valores concretos y representativos.

* Para pruebas de duplicado, crea el registro previo dentro del setUp.

---

# 3\. Resultado esperado

Para cada archivo creado o modificado:

1. Indica la ruta completa del archivo.

2. Muestra el contenido completo del archivo.

3. Explica brevemente el propósito de cada clase de prueba.

Verifica que el código sea ejecutable con python manage.py test app\_autor sin errores y que la cobertura de los criterios de aceptación sea completa.