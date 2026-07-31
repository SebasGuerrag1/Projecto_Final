# Guía Didáctica: Tu Primera App con Django

### Registro de Números de Lotería  Paso a Paso

---

## Tabla de Contenidos

1. [El Pipeline de Django](#bookmark=id.gzwcp7rmbb6x)

2. [Preparar el entorno](#bookmark=id.hurx6or1v1ph)

3. [Crear el proyecto](#bookmark=id.p0onaf7mfnp)

4. [Crear la aplicación](#bookmark=id.kq7halg48z5d)

5. [Registrar la app en settings.py](#bookmark=id.hinwan6twdsq)

6. [Definir el modelo](#bookmark=id.7ajab22nkex2)

7. [Crear y aplicar las migraciones](#bookmark=id.9lo4jejm3dp2)

8. [Crear la vista](#bookmark=id.8dcr7o2b9nqc)

9. [Crear el formulario](#bookmark=id.8iswz4flqp54)

10. [Configurar las URLs](#bookmark=id.u10scjwhf2r1)

11. [Crear el template HTML](#bookmark=id.cqqexwzeror4)

12. [Probar la aplicación](#bookmark=id.llwny1a3sjnb)

13. [Diagrama del Pipeline](#bookmark=id.ve9pm1kseqgt)

---

## 1\. El Pipeline de Django

Antes de escribir una sola línea de código, entiende el orden. Django sigue un flujo muy específico. Si te saltas un paso o lo haces en el orden incorrecto, el proyecto no funciona.

ENTORNO VIRTUAL  
    ?  
PROYECTO Django (django-admin startproject)  
    ?  
APP dentro del proyecto (python manage.py startapp)  
    ?  
Registrar la APP en settings.py  
    ?  
MODEL (la estructura de datos en la base de datos)  
    ?  
MIGRATIONS (traduce el model a tablas SQL)  
    ?  
FORM (valida y recibe los datos del usuario)  
    ?  
VIEW (lógica: qué hacer con los datos)  
    ?  
URL (qué dirección web activa esa vista)  
    ?  
TEMPLATE (HTML que el usuario ve)

**Nota:** Este orden no es sugerido  es obligatorio. Un modelo sin migración no existe en la base de datos. Una vista sin URL no tiene cómo ser llamada. Una URL sin template no tiene nada que mostrar.

---

## 2\. Preparar el entorno

### ¿Por qué un entorno virtual?

Porque cada proyecto puede necesitar versiones distintas de las mismas librerías. El entorno virtual aísla las dependencias de tu proyecto del resto del sistema.

### Comandos

*\# Crear el entorno virtual (solo una vez por proyecto)*  
python \-m venv venv

*\# Activar el entorno virtual*  
*\# En Windows:*  
venv\\Scripts\\activate  
*\# En Mac/Linux:*  
source venv/bin/activate

*\# Instalar Django dentro del entorno activo*  
pip install django

**Error común:** Instalar Django sin activar el entorno virtual primero. Si no ves (venv) al inicio de tu terminal, el entorno no está activo.

### Verificación

python \-m django \--version

Debe mostrar algo como 4.2.x o 5.x.x. Si da error, Django no está instalado correctamente.

---

## 3\. Crear el proyecto

### ¿Qué es un “proyecto” en Django?

El **proyecto** es el contenedor principal. Maneja la configuración global: base de datos, apps instaladas, rutas principales, etc. Solo hay un proyecto, pero puede tener muchas apps.

### Comando

django-admin startproject loteria\_project .

**El punto (.) al final es importante.** Sin él, Django crea una carpeta extra innecesaria. El punto indica “crea el proyecto en el directorio actual”.

### Estructura generada

loteria\_project/          Carpeta de configuración del proyecto  
    \_\_init\_\_.py           Le dice a Python que esta carpeta es un módulo  
    settings.py           Configuración global (base de datos, apps, etc.)  
    urls.py               Rutas principales del proyecto  
    wsgi.py               Punto de entrada para servidores de producción  
manage.py                 Herramienta de línea de comandos para gestionar el proyecto

### Verificación

python manage.py runserver

Abre http://127.0.0.1:8000 en tu navegador. Debes ver la página de bienvenida de Django con un cohete. Detén el servidor con Ctrl \+ C.

---

## 4\. Crear la aplicación

### ¿Qué es una “app” en Django?

Una **app** es un módulo con una responsabilidad específica dentro del proyecto. El proyecto puede tener muchas apps (usuarios, pagos, reportes…). En nuestro caso, crearemos una app llamada loteria que se encarga del registro.

### Comando

python manage.py startapp loteria

### Estructura generada

loteria/  
    migrations/           Aquí Django guardará los archivos de migración (cambios al DB)  
        \_\_init\_\_.py  
    \_\_init\_\_.py  
    admin.py              Para registrar modelos en el panel de administración  
    apps.py               Configuración de la app  
    models.py             Define la estructura de los datos (tablas)  
    tests.py              Para pruebas automatizadas  
    views.py              La lógica de cada página

**Error común:** Crear la app fuera del entorno virtual activo, o crear la app sin haber creado primero el proyecto.

### Verificación

Confirma que la carpeta loteria/ existe al mismo nivel que manage.py y que contiene los archivos listados arriba.

---

## 5\. Registrar la app en settings.py

### ¿Por qué es necesario?

Django no detecta automáticamente las apps que creas. Debes decirle explícitamente “esta app existe y forma parte de este proyecto”. Sin este paso, los modelos no se migran, los templates no se encuentran y la app simplemente no existe para Django.

### Archivo a modificar: loteria\_project/settings.py

Busca la lista INSTALLED\_APPS y agrega 'loteria' al final:

INSTALLED\_APPS \= \[  
    'django.contrib.admin',  
    'django.contrib.auth',  
    'django.contrib.contenttypes',  
    'django.contrib.sessions',  
    'django.contrib.messages',  
    'django.contrib.staticfiles',  
    'loteria',  *\# AGREGA ESTA LÍNEA*  
\]

**Error común:** Escribir mal el nombre de la app ('Loteria' con mayúscula o 'loteria\_app'). Debe coincidir exactamente con el nombre de la carpeta creada.

### Verificación

python manage.py check

Si no hay errores, la app está registrada correctamente.

---

## 6\. Definir el modelo

### ¿Qué es un modelo?

El **modelo** es la representación de tus datos en Python. Django lo traduce automáticamente a una tabla en la base de datos. Cada clase \= una tabla. Cada atributo \= una columna.

### Archivo a modificar: loteria/models.py

Abre el archivo y reemplaza su contenido con:

**from** django.db **import** models

*\# La clase RegistroLoteria representa una tabla en la base de datos.*  
*\# Cada instancia de esta clase \= una fila en esa tabla.*  
**class** RegistroLoteria(models.Model):

    *\# Campo para el número de lotería (entero positivo)*  
    numero \= models.PositiveIntegerField(  
        verbose\_name\="Número de Lotería"  
    )

    *\# Campo para la fecha del sorteo*  
    fecha \= models.DateField(  
        verbose\_name\="Fecha del Sorteo"  
    )

    *\# Este método controla cómo se muestra el objeto en texto*  
    **def** \_\_str\_\_(self):  
        **return** f"Número {self.numero} \- {self.fecha}"

### Explicación de cada parte

| Elemento | ¿Qué hace? |
| :---- | :---- |
| models.Model | Le dice a Django que esta clase es un modelo de base de datos |
| PositiveIntegerField | Columna que solo acepta números enteros positivos |
| DateField | Columna de tipo fecha (YYYY-MM-DD) |
| verbose\_name | Nombre legible para humanos, se usa en formularios y el admin |
| \_\_str\_\_ | Representación en texto del objeto |

**Error común:** Olvidar heredar de models.Model. Sin eso, Django no reconoce la clase como un modelo y no creará la tabla.

### Verificación

python manage.py check

Sin errores \= modelo bien definido.

---

## 7\. Crear y aplicar las migraciones

### ¿Qué son las migraciones?

El modelo existe solo en Python. Las **migraciones** son el puente entre tu código Python y la base de datos real. Son dos pasos:

1. makemigrations Lee tu modelo y genera un archivo Python que describe los cambios.

2. migrate Ejecuta ese archivo y crea/modifica las tablas en la base de datos.

### Comandos

*\# Paso 1: Generar el archivo de migración*  
python manage.py makemigrations loteria

*\# Paso 2: Aplicar la migración a la base de datos*  
python manage.py migrate

### ¿Qué pasa después?

Aparecerá el archivo loteria/migrations/0001\_initial.py. **No lo edites manualmente.** Es generado por Django.

**Error común \#1:** Correr migrate sin haber corrido makemigrations primero. El archivo de migración debe existir antes de aplicarse.

**Error común \#2:** Modificar el modelo y olvidar volver a correr makemigrations. Cada vez que cambies models.py, debes volver a hacer ambos pasos.

### Verificación

python manage.py showmigrations loteria

Debe mostrar:

loteria  
 \[X\] 0001\_initial

La \[X\] indica que la migración fue aplicada exitosamente.

---

## 8\. Crear la vista

### ¿Qué es una vista?

La **vista** contiene la lógica de tu página. Recibe una petición HTTP del usuario, procesa los datos y devuelve una respuesta (generalmente un HTML renderizado). Es el cerebro de cada página.

### Archivo a modificar: loteria/views.py

Reemplaza el contenido con:

**from** django.shortcuts **import** render, redirect  
**from** .forms **import** RegistroLoteriaForm  *\# Importamos el formulario (lo creamos en el siguiente paso)*

**def** registrar\_numero(request):  
    *"""*  
    *Vista para registrar un número de lotería.*  
    *Maneja dos situaciones:*  
    *\- GET: El usuario llega a la página mostrar el formulario vacío.*  
    *\- POST: El usuario envió el formulario validar y guardar los datos.*  
    *"""*

    **if** request.method \== 'POST':  
        *\# El usuario envió datos creamos el formulario con esos datos*  
        form \= RegistroLoteriaForm(request.POST)

        **if** form.is\_valid():  
            *\# Los datos son válidos guardar en la base de datos*  
            form.save()  
            *\# Redirigir para evitar doble envío al refrescar la página*  
            **return** redirect('registro\_exitoso')

    **else**:  
        *\# El usuario llegó por primera vez mostrar formulario vacío*  
        form \= RegistroLoteriaForm()

    *\# Enviamos el formulario al template para renderizarlo*  
    **return** render(request, 'loteria/registro.html', {'form': form})

**def** registro\_exitoso(request):  
    *"""*  
    *Vista simple que confirma que el registro fue exitoso.*  
    *"""*  
    **return** render(request, 'loteria/exito.html')

**Error común:** No manejar el redirect después de un POST exitoso. Sin él, si el usuario refresca la página, el formulario se enviará dos veces, creando registros duplicados.

### Verificación

El archivo no debe generar errores de sintaxis. Puedes verificar con:

python manage.py check

---

## 9\. Crear el formulario

### ¿Qué es un formulario en Django?

Django tiene un sistema de formularios que hace tres cosas automáticamente: genera el HTML del formulario, valida los datos que llegan, y puede guardar directamente en la base de datos (usando ModelForm).

### Archivo a crear: loteria/forms.py

Este archivo **no existe aún**  debes crearlo manualmente:

**from** django **import** forms  
**from** .models **import** RegistroLoteria

*\# ModelForm genera automáticamente el formulario basado en el modelo*  
**class** RegistroLoteriaForm(forms.ModelForm):

    **class** Meta:  
        *\# Le decimos a Django en qué modelo se basa este formulario*  
        model \= RegistroLoteria

        *\# Qué campos del modelo incluir en el formulario*  
        fields \= \['numero', 'fecha'\]

        *\# Personalizar los widgets (cómo se renderiza cada campo en HTML)*  
        widgets \= {  
            'numero': forms.NumberInput(attrs\={  
                'class': 'form-control',  
                'placeholder': 'Ej: 4521'  
            }),  
            'fecha': forms.DateInput(attrs\={  
                'class': 'form-control',  
                'type': 'date'  *\# Activa el selector de fecha del navegador*  
            }),  
        }

### ¿Por qué ModelForm y no Form?

Con ModelForm y un solo form.save() guardas los datos directamente en la base de datos. Con Form regular tendrías que extraer cada campo manualmente y crear el objeto del modelo tú mismo.

**Error común:** Olvidar incluir el campo en la lista fields. Aunque el campo existe en el modelo, si no está en fields, el formulario no lo mostrará ni lo procesará.

### Verificación

python manage.py check

Sin errores \= formulario bien definido.

---

## 10\. Configurar las URLs

### ¿Qué hacen las URLs en Django?

Las URLs mapean una dirección web a una vista. Sin este paso, no hay forma de llegar a tu vista desde el navegador.

Django usa **dos niveles de URLs**: \- loteria\_project/urls.py URLs del proyecto (punto de entrada principal) \- loteria/urls.py URLs específicas de la app loteria (debes crearlo)

### Paso 10a: Crear loteria/urls.py

Este archivo **no existe**  créalo manualmente:

**from** django.urls **import** path  
**from** . **import** views  *\# Importamos las vistas de esta misma app*

*\# 'app\_name' permite usar namespaces para evitar conflictos con otras apps*  
app\_name \= 'loteria'

urlpatterns \= \[  
    *\# Dirección: /loteria/registrar/   llama a la vista registrar\_numero*  
    path('registrar/', views.registrar\_numero, name\='registrar'),

    *\# Dirección: /loteria/exito/   llama a la vista registro\_exitoso*  
    path('exito/', views.registro\_exitoso, name\='registro\_exitoso'),  
\]

### Paso 10b: Modificar loteria\_project/urls.py

Abre el archivo y agrégale la referencia a las URLs de la app:

**from** django.contrib **import** admin  
**from** django.urls **import** path, include  *\# Asegúrate de importar 'include'*

urlpatterns \= \[  
    path('admin/', admin.site.urls),

    *\# Cualquier URL que empiece con 'loteria/' será manejada por la app loteria*  
    path('loteria/', include('loteria.urls')),  
\]

### ¿Cómo se construye la URL completa?

http://127.0.0.1:8000/loteria/registrar/  
                      ^^^^^^^  ^^^^^^^^^  
                      (urls.py del proyecto)  (urls.py de la app)

**Error común:** Olvidar importar include en el urls.py del proyecto. Es necesario para delegar URLs a las apps.

### Verificación

python manage.py check

Sin errores \= URLs correctamente configuradas.

---

## 11\. Crear el template HTML

### ¿Qué es un template?

El **template** es el HTML que el usuario ve. Django usa su propio lenguaje de plantillas ({{ variable }} para mostrar datos, {% tag %} para lógica).

### Paso 11a: Crear la estructura de carpetas

Django busca templates en una carpeta muy específica. Créala manualmente:

loteria/  
    templates/  
        loteria/  
            registro.html    Formulario de registro  
            exito.html       Página de confirmación

**Error común:** Poner los templates directamente en loteria/templates/ sin la subcarpeta loteria/. La subcarpeta con el nombre de la app es necesaria para evitar conflictos entre apps con templates del mismo nombre.

### Paso 11b: Crear loteria/templates/loteria/registro.html

\<\!DOCTYPE html\>  
\<**html** lang\="es"\>  
\<**head**\>  
    \<**meta** charset\="UTF-8"\>  
    \<**meta** name\="viewport" content\="width=device-width, initial-scale=1.0"\>  
    \<**title**\>Registro de Lotería\</**title**\>  
    \<**style**\>  
        body {  
            **font-family**: Arial, sans-serif;  
            **max-width**: 500px;  
            **margin**: 60px auto;  
            **padding**: 0 20px;  
            **background-color**: \#f5f5f5;  
        }  
        h1 { **color**: \#333; }  
        .form-group { **margin-bottom**: 20px; }  
        label { **display**: block; **font-weight**: bold; **margin-bottom**: 5px; }  
        .form-control {  
            **width**: 100%;  
            **padding**: 10px;  
            **border**: 1px solid \#ccc;  
            **border-radius**: 4px;  
            **font-size**: 16px;  
            **box-sizing**: border-box;  
        }  
        .btn {  
            **background-color**: \#007bff;  
            **color**: white;  
            **padding**: 12px 24px;  
            **border**: none;  
            **border-radius**: 4px;  
            **font-size**: 16px;  
            **cursor**: pointer;  
        }  
        .btn***:hover*** { **background-color**: \#0056b3; }  
        .errorlist { **color**: red; **list-style**: none; **padding**: 0; }  
    \</**style**\>  
\</**head**\>  
\<**body**\>

    \<**h1**\>?? Registro de Número de Lotería\</**h1**\>

    *\<\!-- El atributo 'action' vacío envía al mismo URL actual \--\>*  
    *\<\!-- 'method="post"' indica que los datos se envían de forma segura \--\>*  
    \<**form** method\="post" action\=""\>

        *\<\!-- Token de seguridad OBLIGATORIO en todo formulario POST de Django \--\>*  
        {% csrf\_token %}

        *\<\!-- Iteramos cada campo del formulario \--\>*  
        {% for field in form %}  
            \<**div** class\="form-group"\>

                *\<\!-- Etiqueta del campo (viene del verbose\_name del modelo) \--\>*  
                {{ field.label\_tag }}

                *\<\!-- El campo en sí (input, select, etc.) \--\>*  
                {{ field }}

                *\<\!-- Errores de validación (aparecen si el campo tiene datos inválidos) \--\>*  
                {% if field.errors %}  
                    \<**ul** class\="errorlist"\>  
                        {% for error in field.errors %}  
                            \<**li**\>{{ error }}\</**li**\>  
                        {% endfor %}  
                    \</**ul**\>  
                {% endif %}

            \</**div**\>  
        {% endfor %}

        \<**button** type\="submit" class\="btn"\>Guardar Registro\</**button**\>

    \</**form**\>

\</**body**\>  
\</**html**\>

### Paso 11c: Crear loteria/templates/loteria/exito.html

\<\!DOCTYPE html\>  
\<**html** lang\="es"\>  
\<**head**\>  
    \<**meta** charset\="UTF-8"\>  
    \<**title**\>Registro Exitoso\</**title**\>  
    \<**style**\>  
        body {  
            **font-family**: Arial, sans-serif;  
            **max-width**: 500px;  
            **margin**: 60px auto;  
            **text-align**: center;  
        }  
        .exito { **color**: \#28a745; **font-size**: 48px; }  
        h1 { **color**: \#333; }  
        a {  
            **display**: inline-block;  
            **margin-top**: 20px;  
            **padding**: 12px 24px;  
            **background-color**: \#007bff;  
            **color**: white;  
            **text-decoration**: none;  
            **border-radius**: 4px;  
        }  
        a***:hover*** { **background-color**: \#0056b3; }  
    \</**style**\>  
\</**head**\>  
\<**body**\>

    \<**p** class\="exito"\>?\</**p**\>  
    \<**h1**\>¡Registro Exitoso\!\</**h1**\>  
    \<**p**\>El número de lotería fue guardado correctamente.\</**p**\>

    *\<\!-- 'url' genera automáticamente la URL correcta según el nombre definido en urls.py \--\>*  
    \<**a** href\="{% url 'loteria:registrar' %}"\>Registrar otro número\</**a**\>

\</**body**\>  
\</**html**\>

**Error común:** Olvidar {% csrf\_token %} dentro del formulario. Django bloqueará el envío del formulario con un error 403 (Forbidden) si falta este token de seguridad.

### Verificación

python manage.py check

Sin errores \= templates en la ubicación correcta y código válido.

---

## 12\. Probar la aplicación

### Ejecutar el servidor

python manage.py runserver

### Probar en el navegador

Abre: http://127.0.0.1:8000/loteria/registrar/

**Flujo esperado:** 1\. Debes ver el formulario con dos campos: “Número de Lotería” y “Fecha del Sorteo”. 2\. Ingresa un número (ej: 4521) y selecciona una fecha. 3\. Haz clic en “Guardar Registro”. 4\. Debes ser redirigido a la página de éxito con el mensaje “¡Registro Exitoso\!”. 5\. Al hacer clic en “Registrar otro número”, regresarás al formulario vacío.

### Verificar en el panel de administración (opcional)

Para ver los registros guardados en la base de datos:

**Paso 1:** Registrar el modelo en loteria/admin.py:

**from** django.contrib **import** admin  
**from** .models **import** RegistroLoteria

admin.site.register(RegistroLoteria)

**Paso 2:** Crear un superusuario:

python manage.py createsuperuser

**Paso 3:** Acceder a http://127.0.0.1:8000/admin/ con tus credenciales.

**Error 404:** Si ves “Page not found”, verifica que la URL sea exactamente /loteria/registrar/ y que las URLs estén correctamente configuradas en ambos archivos urls.py.

**Error 500:** Revisa la terminal donde corre el servidor. El traceback te dirá exactamente en qué línea y qué archivo ocurrió el error.

### Verificación final

La aplicación está completa si puedes: \- \[x\] Ver el formulario en /loteria/registrar/ \- \[x\] Enviar el formulario sin errores \- \[x\] Ver la página de éxito después del registro \- \[x\] Volver al formulario desde la página de éxito

---

## 13\. Diagrama del Pipeline

Este es el recorrido completo que seguiste para construir el proyecto:

\+---------------------------------------------------------+  
¦                  PIPELINE DE DJANGO                     ¦  
¦               (Proyecto: Lotería)                       ¦  
\+---------------------------------------------------------+

  \[1\] ENTORNO VIRTUAL  
       python \-m venv venv \+ pip install django  
             ¦  
             ?  
  \[2\] PROYECTO  
       django-admin startproject loteria\_project .  
       \+-- loteria\_project/settings.py  Configuración global  
       \+-- loteria\_project/urls.py      Router principal  
             ¦  
             ?  
  \[3\] APP  
       python manage.py startapp loteria  
       \+-- loteria/                     Módulo de la app  
             ¦  
             ?  
  \[4\] REGISTRAR APP  
       settings.py INSTALLED\_APPS 'loteria'  
             ¦  
             ?  
  \[5\] MODEL  (loteria/models.py)  
       class RegistroLoteria(models.Model)  
       \+-- numero \= PositiveIntegerField  
       \+-- fecha  \= DateField  
             ¦  
             ?  
  \[6\] MIGRATIONS  
       makemigrations 0001\_initial.py (archivo generado)  
       migrate        Tabla creada en db.sqlite3  
             ¦  
             ?  
  \[7\] FORM  (loteria/forms.py)  ARCHIVO CREADO MANUALMENTE  
       class RegistroLoteriaForm(ModelForm)  
             ¦  
             ?  
  \[8\] VIEW  (loteria/views.py)  
       def registrar\_numero(request)  
       def registro\_exitoso(request)  
             ¦  
             ?  
  \[9\] URLs APP  (loteria/urls.py)  ARCHIVO CREADO MANUALMENTE  
       path('registrar/', views.registrar\_numero)  
       path('exito/',     views.registro\_exitoso)  
             ¦  
             ?  
  \[10\] URLs PROYECTO  (loteria\_project/urls.py)  
        path('loteria/', include('loteria.urls'))  
             ¦  
             ?  
  \[11\] TEMPLATES  (loteria/templates/loteria/)  
        registro.html  Formulario  
        exito.html     Confirmación  
             ¦  
             ?  
  \[12\] PRUEBA  
        python manage.py runserver  
        http://127.0.0.1:8000/loteria/registrar/

\-----------------------------------------------------------  
FLUJO DE UNA PETICIÓN HTTP EN TIEMPO DE EJECUCIÓN:

  Navegador  
     ¦  GET /loteria/registrar/  
     ?  
  urls.py (proyecto)   urls.py (app loteria)  
     ¦  
     ?  
  views.py registrar\_numero()  
     ¦  \[GET\]  crea formulario vacío  
     ¦  \[POST\] valida guarda redirect  
     ?  
  template: registro.html  ó  redirect a exito.html  
     ¦  
     ?  
  Respuesta HTML al navegador  
\-----------------------------------------------------------

---

## Resumen de Archivos

| Archivo | Acción | Descripción |
| :---- | :---- | :---- |
| loteria\_project/settings.py | **Modificar** | Agregar 'loteria' a INSTALLED\_APPS |
| loteria\_project/urls.py | **Modificar** | Incluir las URLs de la app |
| loteria/models.py | **Modificar** | Definir el modelo RegistroLoteria |
| loteria/forms.py | **Crear** | Crear RegistroLoteriaForm |
| loteria/views.py | **Modificar** | Agregar las dos vistas |
| loteria/urls.py | **Crear** | Definir las rutas de la app |
| loteria/templates/loteria/registro.html | **Crear** | Template del formulario |
| loteria/templates/loteria/exito.html | **Crear** | Template de confirmación |

