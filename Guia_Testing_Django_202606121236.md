# Introducción al Testing en Django

## Guía Práctica

# ¿Por qué hacer pruebas en Django?

Las pruebas (tests) permiten verificar que tu aplicación funciona correctamente. Django incluye un sistema de pruebas propio, basado en unittest de Python, que facilita probar modelos, vistas, formularios y URLs de forma automática.

Con los tests puedes: \- Detectar errores antes de que lleguen a producción. \- Refactorizar código con confianza. \- Documentar el comportamiento esperado de tu aplicación.

---

# Estructura básica de un test en Django

Django busca automáticamente los tests en el archivo tests.py de cada aplicación, o en cualquier archivo cuyo nombre empiece por test\_.

*\# mi\_app/tests.py*  
**from** django.test **import** TestCase

**class** MiPrimerTest(TestCase):  
    **def** test\_suma\_simple(self):  
        resultado \= 2 \+ 2  
        self.assertEqual(resultado, 4)

Para ejecutar los tests:

python manage.py test

Para ejecutar solo los tests de una aplicación específica:

python manage.py test mi\_app

---

# Configuración del proyecto

Antes de los ejemplos, esta es la estructura mínima del proyecto Django que se asume:

mi\_proyecto/  
├── manage.py  
├── mi\_proyecto/  
│   ├── \_\_init\_\_.py  
│   ├── settings.py  
│   ├── urls.py  
│   └── wsgi.py  
└── mi\_app/  
    ├── \_\_init\_\_.py  
    ├── admin.py  
    ├── apps.py  
    ├── forms.py  
    ├── models.py  
    ├── urls.py  
    ├── views.py  
    ├── templates/  
    │   └── mi\_app/  
    │       ├── base.html  
    │       ├── lista\_productos.html  
    │       └── crear\_producto.html  
    └── tests/  
        ├── \_\_init\_\_.py  
        ├── test\_models.py  
        ├── test\_views.py  
        ├── test\_forms.py  
        └── test\_urls.py

En mi\_proyecto/settings.py, asegúrate de tener:

INSTALLED\_APPS \= \[  
    ...  
    'mi\_app',  
\]

TEMPLATES \= \[{  
    'BACKEND': 'django.template.backends.django.DjangoTemplates',  
    'DIRS': \[\],  
    'APP\_DIRS': True,  
    'OPTIONS': {  
        'context\_processors': \[  
            'django.template.context\_processors.debug',  
            'django.template.context\_processors.request',  
            'django.contrib.auth.context\_processors.auth',  
            'django.contrib.messages.context\_processors.messages',  
        \],  
    },  
}\]

*\# Requerido para usar el framework de mensajes en las vistas*  
MESSAGE\_STORAGE \= 'django.contrib.messages.storage.session.SessionStorage'

En mi\_proyecto/urls.py:

**from** django.contrib **import** admin  
**from** django.urls **import** path, include

urlpatterns \= \[  
    path('admin/', admin.site.urls),  
    path('', include('mi\_app.urls')),  
\]

---

# Ejemplo 01 — Probando Modelos: Creación, lectura y lógica de negocio

Este ejemplo cubre el pipeline completo para el modelo Producto.

## mi\_app/models.py

**from** django.db **import** models  
**from** django.core.validators **import** MinValueValidator  
**from** decimal **import** Decimal

**class** Producto(models.Model):  
    nombre \= models.CharField(max\_length\=100)  
    precio \= models.DecimalField(  
        max\_digits\=10,  
        decimal\_places\=2,  
        validators\=\[MinValueValidator(Decimal('0.01'))\]  
    )  
    stock \= models.PositiveIntegerField(default\=0)  
    creado\_en \= models.DateTimeField(auto\_now\_add\=True)

    **class** Meta:  
        ordering \= \['nombre'\]  
        verbose\_name \= 'Producto'  
        verbose\_name\_plural \= 'Productos'

    **def** \_\_str\_\_(self):  
        **return** self.nombre

    **def** tiene\_precio\_valido(self):  
        **return** self.precio \> 0

    **def** hay\_stock(self):  
        **return** self.stock \> 0

## mi\_app/admin.py

**from** django.contrib **import** admin  
**from** .models **import** Producto

@admin.register(Producto)  
**class** ProductoAdmin(admin.ModelAdmin):  
    list\_display \= \['nombre', 'precio', 'stock', 'creado\_en'\]  
    list\_filter \= \['creado\_en'\]  
    search\_fields \= \['nombre'\]

## mi\_app/tests/test\_models.py

**from** django.test **import** TestCase  
**from** django.core.exceptions **import** ValidationError  
**from** mi\_app.models **import** Producto

**class** ProductoModelTest(TestCase):

    **def** test\_crear\_producto(self):  
        *"""Verifica que se puede crear un producto correctamente."""*  
        producto \= Producto.objects.create(nombre\="Café", precio\=5000, stock\=10)  
        self.assertEqual(producto.nombre, "Café")  
        self.assertEqual(str(producto), "Café")  
        self.assertEqual(producto.stock, 10)

    **def** test\_precio\_valido(self):  
        *"""Precio positivo debe retornar True."""*  
        producto \= Producto(nombre\="Té", precio\=3000)  
        self.assertTrue(producto.tiene\_precio\_valido())

    **def** test\_precio\_invalido(self):  
        *"""Precio de cero debe retornar False."""*  
        producto \= Producto(nombre\="Agua", precio\=0)  
        self.assertFalse(producto.tiene\_precio\_valido())

    **def** test\_hay\_stock(self):  
        *"""Stock mayor a cero debe retornar True."""*  
        producto \= Producto(nombre\="Pan", precio\=1500, stock\=5)  
        self.assertTrue(producto.hay\_stock())

    **def** test\_sin\_stock(self):  
        *"""Stock en cero debe retornar False."""*  
        producto \= Producto(nombre\="Pan", precio\=1500, stock\=0)  
        self.assertFalse(producto.hay\_stock())

    **def** test\_str\_retorna\_nombre(self):  
        *"""El método \_\_str\_\_ retorna el nombre del producto."""*  
        producto \= Producto(nombre\="Leche", precio\=2000)  
        self.assertEqual(str(producto), "Leche")

---

# Ejemplo 02 — Usando setUp para evitar repetición

El método setUp se ejecuta **antes de cada test**. Es ideal para crear objetos que se usan en múltiples pruebas.

## mi\_app/tests/test\_models.py (continuación)

**class** ProductoSetUpTest(TestCase):

    **def** setUp(self):  
        *"""Se ejecuta antes de cada test."""*  
        self.producto \= Producto.objects.create(  
            nombre\="Arroz",  
            precio\=2500,  
            stock\=100  
        )

    **def** test\_nombre\_correcto(self):  
        self.assertEqual(self.producto.nombre, "Arroz")

    **def** test\_precio\_correcto(self):  
        self.assertEqual(self.producto.precio, 2500)

    **def** test\_actualizar\_precio(self):  
        self.producto.precio \= 3000  
        self.producto.save()  
        producto\_actualizado \= Producto.objects.get(pk\=self.producto.pk)  
        self.assertEqual(producto\_actualizado.precio, 3000)

    **def** test\_actualizar\_stock(self):  
        self.producto.stock \= 50  
        self.producto.save()  
        self.assertEqual(Producto.objects.get(pk\=self.producto.pk).stock, 50)

    **def** test\_persistencia\_en\_base\_de\_datos(self):  
        *"""Verifica que el objeto fue guardado en la base de datos."""*  
        self.assertEqual(Producto.objects.count(), 1)  
        self.assertEqual(Producto.objects.first().nombre, "Arroz")

---

# Ejemplo 03 — Probando Formularios: validaciones y errores

## mi\_app/forms.py

**from** django **import** forms  
**from** .models **import** Producto

**class** ProductoForm(forms.ModelForm):  
    **class** Meta:  
        model \= Producto  
        fields \= \['nombre', 'precio', 'stock'\]  
        labels \= {  
            'nombre': 'Nombre del producto',  
            'precio': 'Precio (COP)',  
            'stock': 'Unidades disponibles',  
        }  
        widgets \= {  
            'nombre': forms.TextInput(attrs\={'class': 'form-control', 'placeholder': 'Ej: Café'}),  
            'precio': forms.NumberInput(attrs\={'class': 'form-control', 'min': '1'}),  
            'stock': forms.NumberInput(attrs\={'class': 'form-control', 'min': '0'}),  
        }

    **def** clean\_precio(self):  
        precio \= self.cleaned\_data.get('precio')  
        **if** precio **is** **not** None **and** precio \<= 0:  
            **raise** forms.ValidationError("El precio debe ser mayor que cero.")  
        **return** precio

    **def** clean\_nombre(self):  
        nombre \= self.cleaned\_data.get('nombre', '').strip()  
        **if** len(nombre) \< 2:  
            **raise** forms.ValidationError("El nombre debe tener al menos 2 caracteres.")  
        **return** nombre

## mi\_app/tests/test\_forms.py

**from** django.test **import** TestCase  
**from** mi\_app.forms **import** ProductoForm

**class** ProductoFormTest(TestCase):

    **def** test\_formulario\_valido(self):  
        *"""Datos correctos deben producir un formulario válido."""*  
        datos \= {'nombre': 'Maíz', 'precio': '1800', 'stock': '50'}  
        form \= ProductoForm(data\=datos)  
        self.assertTrue(form.is\_valid())

    **def** test\_formulario\_invalido\_precio\_cero(self):  
        *"""Precio de cero debe producir un error de validación."""*  
        datos \= {'nombre': 'Frijol', 'precio': '0', 'stock': '10'}  
        form \= ProductoForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('precio', form.errors)

    **def** test\_formulario\_invalido\_precio\_negativo(self):  
        *"""Precio negativo debe producir un error de validación."""*  
        datos \= {'nombre': 'Lentejas', 'precio': '-500', 'stock': '5'}  
        form \= ProductoForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('precio', form.errors)

    **def** test\_formulario\_invalido\_sin\_nombre(self):  
        *"""El campo nombre es obligatorio."""*  
        datos \= {'nombre': '', 'precio': '2000', 'stock': '10'}  
        form \= ProductoForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('nombre', form.errors)

    **def** test\_formulario\_invalido\_nombre\_muy\_corto(self):  
        *"""El nombre debe tener al menos 2 caracteres."""*  
        datos \= {'nombre': 'A', 'precio': '2000', 'stock': '10'}  
        form \= ProductoForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('nombre', form.errors)

    **def** test\_formulario\_sin\_stock\_usa\_default(self):  
        *"""El campo stock tiene valor por defecto (0) si se omite."""*  
        datos \= {'nombre': 'Sal', 'precio': '800', 'stock': '0'}  
        form \= ProductoForm(data\=datos)  
        self.assertTrue(form.is\_valid())

---

# Ejemplo 04 — Probando Vistas GET: listado de productos

## mi\_app/templates/mi\_app/base.html

\<\!DOCTYPE html\>  
\<**html** lang\="es"\>  
\<**head**\>  
    \<**meta** charset\="UTF-8"\>  
    \<**title**\>{% block title %}Mi Tienda{% endblock %}\</**title**\>  
\</**head**\>  
\<**body**\>  
    {% if messages %}  
        \<**ul** class\="messages"\>  
            {% for message in messages %}  
                \<**li** class\="{{ message.tags }}"\>{{ message }}\</**li**\>  
            {% endfor %}  
        \</**ul**\>  
    {% endif %}  
    {% block content %}{% endblock %}  
\</**body**\>  
\</**html**\>

## mi\_app/templates/mi\_app/lista\_productos.html

{% extends "mi\_app/base.html" %}

{% block title %}Lista de Productos{% endblock %}

{% block content %}  
\<**h1**\>Productos\</**h1**\>  
\<**a** href\="{% url 'crear\_producto' %}"\>Agregar producto\</**a**\>  
\<**ul**\>  
    {% for producto in productos %}  
        \<**li**\>{{ producto.nombre }} — ${{ producto.precio }}\</**li**\>  
    {% empty %}  
        \<**li**\>No hay productos registrados.\</**li**\>  
    {% endfor %}  
\</**ul**\>  
{% endblock %}

## mi\_app/views.py

**from** django.shortcuts **import** render, redirect, get\_object\_or\_404  
**from** django.contrib **import** messages  
**from** .models **import** Producto  
**from** .forms **import** ProductoForm

**def** lista\_productos(request):  
    productos \= Producto.objects.all()  
    **return** render(request, 'mi\_app/lista\_productos.html', {'productos': productos})

## mi\_app/urls.py

**from** django.urls **import** path  
**from** . **import** views

urlpatterns \= \[  
    path('productos/', views.lista\_productos, name\='lista\_productos'),  
    path('productos/crear/', views.crear\_producto, name\='crear\_producto'),  
    path('productos/\<int:pk\>/editar/', views.editar\_producto, name\='editar\_producto'),  
    path('productos/\<int:pk\>/eliminar/', views.eliminar\_producto, name\='eliminar\_producto'),  
\]

## mi\_app/tests/test\_views.py

**from** django.test **import** TestCase  
**from** django.urls **import** reverse  
**from** mi\_app.models **import** Producto

**class** ListaProductosViewTest(TestCase):

    **def** setUp(self):  
        Producto.objects.create(nombre\="Pan", precio\=1500, stock\=20)  
        Producto.objects.create(nombre\="Leche", precio\=4200, stock\=10)

    **def** test\_vista\_responde\_ok(self):  
        *"""La vista debe devolver HTTP 200."""*  
        respuesta \= self.client.get(reverse('lista\_productos'))  
        self.assertEqual(respuesta.status\_code, 200)

    **def** test\_vista\_usa\_template\_correcto(self):  
        *"""La vista debe usar el template lista\_productos.html."""*  
        respuesta \= self.client.get(reverse('lista\_productos'))  
        self.assertTemplateUsed(respuesta, 'mi\_app/lista\_productos.html')

    **def** test\_vista\_muestra\_productos(self):  
        *"""El contexto debe contener los productos creados."""*  
        respuesta \= self.client.get(reverse('lista\_productos'))  
        self.assertContains(respuesta, "Pan")  
        self.assertContains(respuesta, "Leche")

    **def** test\_contexto\_contiene\_productos(self):  
        *"""El contexto debe tener la clave 'productos'."""*  
        respuesta \= self.client.get(reverse('lista\_productos'))  
        self.assertIn('productos', respuesta.context)  
        self.assertEqual(respuesta.context\['productos'\].count(), 2)

    **def** test\_lista\_vacia(self):  
        *"""Si no hay productos, la vista debe indicarlo."""*  
        Producto.objects.all().delete()  
        respuesta \= self.client.get(reverse('lista\_productos'))  
        self.assertEqual(respuesta.status\_code, 200)  
        self.assertContains(respuesta, "No hay productos registrados.")

---

# Ejemplo 05 — Probando Vistas POST: creación con mensajes y redirección

## mi\_app/templates/mi\_app/crear\_producto.html

{% extends "mi\_app/base.html" %}

{% block title %}Crear Producto{% endblock %}

{% block content %}  
\<**h1**\>Nuevo Producto\</**h1**\>  
\<**form** method\="post"\>  
    {% csrf\_token %}  
    {{ form.as\_p }}  
    \<**button** type\="submit"\>Guardar\</**button**\>  
    \<**a** href\="{% url 'lista\_productos' %}"\>Cancelar\</**a**\>  
\</**form**\>  
{% endblock %}

## mi\_app/views.py (ampliado)

**def** crear\_producto(request):  
    **if** request.method \== 'POST':  
        form \= ProductoForm(request.POST)  
        **if** form.is\_valid():  
            form.save()  
            messages.success(request, "Producto creado exitosamente.")  
            **return** redirect('lista\_productos')  
        **else**:  
            messages.error(request, "Por favor corrige los errores del formulario.")  
    **else**:  
        form \= ProductoForm()  
    **return** render(request, 'mi\_app/crear\_producto.html', {'form': form})

## mi\_app/tests/test\_views.py (continuación)

**class** CrearProductoViewTest(TestCase):

    **def** test\_get\_muestra\_formulario(self):  
        *"""Un GET debe mostrar el formulario vacío."""*  
        respuesta \= self.client.get(reverse('crear\_producto'))  
        self.assertEqual(respuesta.status\_code, 200)  
        self.assertTemplateUsed(respuesta, 'mi\_app/crear\_producto.html')  
        self.assertIn('form', respuesta.context)

    **def** test\_post\_valido\_crea\_producto(self):  
        *"""Un POST válido debe crear un producto en la base de datos."""*  
        self.client.post(reverse('crear\_producto'), {  
            'nombre': 'Azúcar',  
            'precio': '2000',  
            'stock': '30'  
        })  
        self.assertEqual(Producto.objects.count(), 1)  
        self.assertEqual(Producto.objects.first().nombre, 'Azúcar')

    **def** test\_post\_valido\_redirige\_a\_lista(self):  
        *"""Después de crear exitosamente, debe redirigir a la lista."""*  
        respuesta \= self.client.post(reverse('crear\_producto'), {  
            'nombre': 'Sal',  
            'precio': '800',  
            'stock': '50'  
        })  
        self.assertRedirects(respuesta, reverse('lista\_productos'))

    **def** test\_post\_valido\_muestra\_mensaje\_exito(self):  
        *"""Un POST válido debe mostrar un mensaje de éxito al redirigir."""*  
        respuesta \= self.client.post(reverse('crear\_producto'), {  
            'nombre': 'Panela',  
            'precio': '3500',  
            'stock': '15'  
        }, follow\=True)  
        self.assertContains(respuesta, "Producto creado exitosamente.")

    **def** test\_post\_invalido\_no\_crea\_producto(self):  
        *"""Un POST con datos inválidos no debe crear el producto."""*  
        self.client.post(reverse('crear\_producto'), {  
            'nombre': '',  
            'precio': '-100',  
            'stock': '5'  
        })  
        self.assertEqual(Producto.objects.count(), 0)

    **def** test\_post\_invalido\_muestra\_formulario\_con\_errores(self):  
        *"""Un POST inválido debe volver al formulario mostrando errores."""*  
        respuesta \= self.client.post(reverse('crear\_producto'), {  
            'nombre': '',  
            'precio': '0',  
            'stock': '5'  
        })  
        self.assertEqual(respuesta.status\_code, 200)  
        self.assertTemplateUsed(respuesta, 'mi\_app/crear\_producto.html')  
        form \= respuesta.context\['form'\]  
        self.assertFalse(form.is\_valid())

---

# Ejemplo 06 — Probando Vistas de edición y eliminación

## mi\_app/templates/mi\_app/editar\_producto.html

{% extends "mi\_app/base.html" %}

{% block title %}Editar Producto{% endblock %}

{% block content %}  
\<**h1**\>Editar: {{ producto.nombre }}\</**h1**\>  
\<**form** method\="post"\>  
    {% csrf\_token %}  
    {{ form.as\_p }}  
    \<**button** type\="submit"\>Actualizar\</**button**\>  
    \<**a** href\="{% url 'lista\_productos' %}"\>Cancelar\</**a**\>  
\</**form**\>  
{% endblock %}

## mi\_app/views.py (ampliado)

**def** editar\_producto(request, pk):  
    producto \= get\_object\_or\_404(Producto, pk\=pk)  
    **if** request.method \== 'POST':  
        form \= ProductoForm(request.POST, instance\=producto)  
        **if** form.is\_valid():  
            form.save()  
            messages.success(request, f"Producto '{producto.nombre}' actualizado.")  
            **return** redirect('lista\_productos')  
        **else**:  
            messages.error(request, "Por favor corrige los errores del formulario.")  
    **else**:  
        form \= ProductoForm(instance\=producto)  
    **return** render(request, 'mi\_app/editar\_producto.html', {  
        'form': form,  
        'producto': producto  
    })

**def** eliminar\_producto(request, pk):  
    producto \= get\_object\_or\_404(Producto, pk\=pk)  
    **if** request.method \== 'POST':  
        nombre \= producto.nombre  
        producto.delete()  
        messages.success(request, f"Producto '{nombre}' eliminado.")  
        **return** redirect('lista\_productos')  
    **return** render(request, 'mi\_app/confirmar\_eliminar.html', {'producto': producto})

## mi\_app/tests/test\_views.py (continuación)

**class** EditarProductoViewTest(TestCase):

    **def** setUp(self):  
        self.producto \= Producto.objects.create(  
            nombre\="Harina",  
            precio\=3000,  
            stock\=40  
        )

    **def** test\_get\_muestra\_formulario\_con\_datos(self):  
        *"""El formulario GET debe estar precargado con datos del producto."""*  
        respuesta \= self.client.get(reverse('editar\_producto', args\=\[self.producto.pk\]))  
        self.assertEqual(respuesta.status\_code, 200)  
        self.assertContains(respuesta, "Harina")

    **def** test\_post\_valido\_actualiza\_producto(self):  
        *"""Un POST válido debe actualizar el producto en la base de datos."""*  
        self.client.post(  
            reverse('editar\_producto', args\=\[self.producto.pk\]),  
            {'nombre': 'Harina integral', 'precio': '3500', 'stock': '40'}  
        )  
        self.producto.refresh\_from\_db()  
        self.assertEqual(self.producto.nombre, 'Harina integral')  
        self.assertEqual(self.producto.precio, 3500)

    **def** test\_post\_valido\_redirige(self):  
        *"""Editar exitosamente debe redirigir a la lista."""*  
        respuesta \= self.client.post(  
            reverse('editar\_producto', args\=\[self.producto.pk\]),  
            {'nombre': 'Harina integral', 'precio': '3500', 'stock': '40'}  
        )  
        self.assertRedirects(respuesta, reverse('lista\_productos'))

    **def** test\_producto\_inexistente\_retorna\_404(self):  
        *"""Editar un producto que no existe debe retornar 404."""*  
        respuesta \= self.client.get(reverse('editar\_producto', args\=\[9999\]))  
        self.assertEqual(respuesta.status\_code, 404)

**class** EliminarProductoViewTest(TestCase):

    **def** setUp(self):  
        self.producto \= Producto.objects.create(  
            nombre\="Aceite",  
            precio\=8000,  
            stock\=12  
        )

    **def** test\_post\_elimina\_producto(self):  
        *"""Un POST debe eliminar el producto de la base de datos."""*  
        self.client.post(reverse('eliminar\_producto', args\=\[self.producto.pk\]))  
        self.assertEqual(Producto.objects.count(), 0)

    **def** test\_post\_redirige\_a\_lista(self):  
        *"""Después de eliminar, debe redirigir a la lista."""*  
        respuesta \= self.client.post(  
            reverse('eliminar\_producto', args\=\[self.producto.pk\])  
        )  
        self.assertRedirects(respuesta, reverse('lista\_productos'))

    **def** test\_get\_muestra\_confirmacion(self):  
        *"""Un GET debe mostrar la pantalla de confirmación, sin eliminar."""*  
        self.client.get(reverse('eliminar\_producto', args\=\[self.producto.pk\]))  
        self.assertEqual(Producto.objects.count(), 1)

---

# Ejemplo 07 — Probando URLs

Puedes verificar que las URLs apuntan a las vistas correctas usando reverse y resolve.

## mi\_app/tests/test\_urls.py

**from** django.urls **import** reverse, resolve  
**from** django.test **import** TestCase  
**from** mi\_app **import** views

**class** URLsProductoTest(TestCase):

    **def** test\_url\_lista\_es\_correcta(self):  
        *"""La URL de lista debe resolver correctamente."""*  
        url \= reverse('lista\_productos')  
        self.assertEqual(url, '/productos/')

    **def** test\_url\_lista\_resuelve\_vista\_correcta(self):  
        resolucion \= resolve('/productos/')  
        self.assertEqual(resolucion.func, views.lista\_productos)

    **def** test\_url\_crear\_es\_correcta(self):  
        url \= reverse('crear\_producto')  
        self.assertEqual(url, '/productos/crear/')

    **def** test\_url\_crear\_resuelve\_vista\_correcta(self):  
        resolucion \= resolve('/productos/crear/')  
        self.assertEqual(resolucion.func, views.crear\_producto)

    **def** test\_url\_editar\_con\_pk(self):  
        url \= reverse('editar\_producto', args\=\[1\])  
        self.assertEqual(url, '/productos/1/editar/')

    **def** test\_url\_editar\_resuelve\_vista\_correcta(self):  
        resolucion \= resolve('/productos/1/editar/')  
        self.assertEqual(resolucion.func, views.editar\_producto)

    **def** test\_url\_eliminar\_con\_pk(self):  
        url \= reverse('eliminar\_producto', args\=\[1\])  
        self.assertEqual(url, '/productos/1/eliminar/')

---

# Ejemplo 08 — Ejemplo Integrador Completo: modelo Tarea

Este ejemplo integra el pipeline completo: modelo → admin → formulario → vistas → URLs → plantillas → tests.

## mi\_app/models.py (modelo Tarea)

**class** Tarea(models.Model):  
    PRIORIDAD\_CHOICES \= \[  
        ('baja', 'Baja'),  
        ('media', 'Media'),  
        ('alta', 'Alta'),  
    \]

    titulo \= models.CharField(max\_length\=200)  
    descripcion \= models.TextField(blank\=True, default\='')  
    completada \= models.BooleanField(default\=False)  
    prioridad \= models.CharField(  
        max\_length\=10,  
        choices\=PRIORIDAD\_CHOICES,  
        default\='media'  
    )  
    creada\_en \= models.DateTimeField(auto\_now\_add\=True)

    **class** Meta:  
        ordering \= \['-creada\_en'\]  
        verbose\_name \= 'Tarea'  
        verbose\_name\_plural \= 'Tareas'

    **def** \_\_str\_\_(self):  
        **return** self.titulo

    **def** marcar\_completada(self):  
        self.completada \= True  
        self.save()

    **def** marcar\_pendiente(self):  
        self.completada \= False  
        self.save()

## mi\_app/admin.py (ampliado)

**from** .models **import** Tarea

@admin.register(Tarea)  
**class** TareaAdmin(admin.ModelAdmin):  
    list\_display \= \['titulo', 'prioridad', 'completada', 'creada\_en'\]  
    list\_filter \= \['completada', 'prioridad'\]  
    search\_fields \= \['titulo', 'descripcion'\]  
    list\_editable \= \['completada'\]  
    actions \= \['marcar\_completadas'\]

    **def** marcar\_completadas(self, request, queryset):  
        queryset.update(completada\=True)  
        self.message\_user(request, "Tareas marcadas como completadas.")  
    marcar\_completadas.short\_description \= "Marcar tareas seleccionadas como completadas"

## mi\_app/forms.py (ampliado)

**class** TareaForm(forms.ModelForm):  
    **class** Meta:  
        model \= Tarea  
        fields \= \['titulo', 'descripcion', 'prioridad'\]  
        labels \= {  
            'titulo': 'Título',  
            'descripcion': 'Descripción (opcional)',  
            'prioridad': 'Prioridad',  
        }  
        widgets \= {  
            'titulo': forms.TextInput(attrs\={  
                'class': 'form-control',  
                'placeholder': 'Ej: Estudiar Django'  
            }),  
            'descripcion': forms.Textarea(attrs\={  
                'class': 'form-control',  
                'rows': 3  
            }),  
            'prioridad': forms.Select(attrs\={'class': 'form-control'}),  
        }

    **def** clean\_titulo(self):  
        titulo \= self.cleaned\_data.get('titulo', '').strip()  
        **if** len(titulo) \< 3:  
            **raise** forms.ValidationError("El título debe tener al menos 3 caracteres.")  
        **return** titulo

## mi\_app/views.py (vistas para Tarea)

**from** .models **import** Tarea  
**from** .forms **import** TareaForm

**def** lista\_tareas(request):  
    tareas \= Tarea.objects.all()  
    **return** render(request, 'mi\_app/lista\_tareas.html', {'tareas': tareas})

**def** crear\_tarea(request):  
    **if** request.method \== 'POST':  
        form \= TareaForm(request.POST)  
        **if** form.is\_valid():  
            tarea \= form.save()  
            messages.success(request, f"Tarea '{tarea.titulo}' creada exitosamente.")  
            **return** redirect('lista\_tareas')  
        **else**:  
            messages.error(request, "Por favor corrige los errores del formulario.")  
    **else**:  
        form \= TareaForm()  
    **return** render(request, 'mi\_app/crear\_tarea.html', {'form': form})

**def** completar\_tarea(request, pk):  
    tarea \= get\_object\_or\_404(Tarea, pk\=pk)  
    **if** request.method \== 'POST':  
        tarea.marcar\_completada()  
        messages.success(request, f"Tarea '{tarea.titulo}' marcada como completada.")  
        **return** redirect('lista\_tareas')  
    **return** render(request, 'mi\_app/confirmar\_completar.html', {'tarea': tarea})

## mi\_app/urls.py (ampliado)

urlpatterns \= \[  
    *\# Productos*  
    path('productos/', views.lista\_productos, name\='lista\_productos'),  
    path('productos/crear/', views.crear\_producto, name\='crear\_producto'),  
    path('productos/\<int:pk\>/editar/', views.editar\_producto, name\='editar\_producto'),  
    path('productos/\<int:pk\>/eliminar/', views.eliminar\_producto, name\='eliminar\_producto'),

    *\# Tareas*  
    path('tareas/', views.lista\_tareas, name\='lista\_tareas'),  
    path('tareas/crear/', views.crear\_tarea, name\='crear\_tarea'),  
    path('tareas/\<int:pk\>/completar/', views.completar\_tarea, name\='completar\_tarea'),  
\]

## mi\_app/templates/mi\_app/lista\_tareas.html

{% extends "mi\_app/base.html" %}

{% block title %}Lista de Tareas{% endblock %}

{% block content %}  
\<**h1**\>Tareas\</**h1**\>  
\<**a** href\="{% url 'crear\_tarea' %}"\>Nueva tarea\</**a**\>  
\<**ul**\>  
    {% for tarea in tareas %}  
        \<**li**\>  
            \[{{ tarea.prioridad }}\]  
            {% if tarea.completada %}\<**s**\>{% endif %}  
            {{ tarea.titulo }}  
            {% if tarea.completada %}\</**s**\> ✓{% endif %}  
            {% if not tarea.completada %}  
                \<**form** method\="post" action\="{% url 'completar\_tarea' tarea.pk %}" style\="display:inline;"\>  
                    {% csrf\_token %}  
                    \<**button** type\="submit"\>Completar\</**button**\>  
                \</**form**\>  
            {% endif %}  
        \</**li**\>  
    {% empty %}  
        \<**li**\>No hay tareas pendientes.\</**li**\>  
    {% endfor %}  
\</**ul**\>  
{% endblock %}

## mi\_app/templates/mi\_app/crear\_tarea.html

{% extends "mi\_app/base.html" %}

{% block title %}Nueva Tarea{% endblock %}

{% block content %}  
\<**h1**\>Nueva Tarea\</**h1**\>  
\<**form** method\="post"\>  
    {% csrf\_token %}  
    {{ form.as\_p }}  
    \<**button** type\="submit"\>Guardar\</**button**\>  
    \<**a** href\="{% url 'lista\_tareas' %}"\>Cancelar\</**a**\>  
\</**form**\>  
{% endblock %}

## mi\_app/tests/test\_tarea.py

**from** django.test **import** TestCase  
**from** django.urls **import** reverse  
**from** mi\_app.models **import** Tarea  
**from** mi\_app.forms **import** TareaForm

*\# ─── Tests del Modelo ──────────────────────────────────────────────────────────*

**class** TareaModelTest(TestCase):

    **def** setUp(self):  
        self.tarea \= Tarea.objects.create(titulo\="Estudiar Django")

    **def** test\_tarea\_creada\_sin\_completar(self):  
        *"""Una tarea nueva debe estar pendiente por defecto."""*  
        self.assertFalse(self.tarea.completada)

    **def** test\_tarea\_creada\_con\_prioridad\_media(self):  
        *"""La prioridad por defecto debe ser 'media'."""*  
        self.assertEqual(self.tarea.prioridad, 'media')

    **def** test\_marcar\_completada(self):  
        *"""marcar\_completada() debe actualizar el campo en la base de datos."""*  
        self.tarea.marcar\_completada()  
        self.tarea.refresh\_from\_db()  
        self.assertTrue(self.tarea.completada)

    **def** test\_marcar\_pendiente(self):  
        *"""marcar\_pendiente() debe revertir el estado completado."""*  
        self.tarea.completada \= True  
        self.tarea.save()  
        self.tarea.marcar\_pendiente()  
        self.tarea.refresh\_from\_db()  
        self.assertFalse(self.tarea.completada)

    **def** test\_str\_retorna\_titulo(self):  
        *"""\_\_str\_\_ debe retornar el título de la tarea."""*  
        self.assertEqual(str(self.tarea), "Estudiar Django")

    **def** test\_persistencia(self):  
        *"""La tarea debe existir en la base de datos."""*  
        self.assertEqual(Tarea.objects.count(), 1)  
        self.assertEqual(Tarea.objects.first().titulo, "Estudiar Django")

*\# ─── Tests del Formulario ──────────────────────────────────────────────────────*

**class** TareaFormTest(TestCase):

    **def** test\_formulario\_valido(self):  
        datos \= {'titulo': 'Leer documentación', 'prioridad': 'alta'}  
        form \= TareaForm(data\=datos)  
        self.assertTrue(form.is\_valid())

    **def** test\_formulario\_invalido\_titulo\_vacio(self):  
        datos \= {'titulo': '', 'prioridad': 'media'}  
        form \= TareaForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('titulo', form.errors)

    **def** test\_formulario\_invalido\_titulo\_muy\_corto(self):  
        datos \= {'titulo': 'AB', 'prioridad': 'baja'}  
        form \= TareaForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('titulo', form.errors)

    **def** test\_formulario\_invalido\_prioridad\_incorrecta(self):  
        datos \= {'titulo': 'Mi tarea', 'prioridad': 'urgente'}  
        form \= TareaForm(data\=datos)  
        self.assertFalse(form.is\_valid())  
        self.assertIn('prioridad', form.errors)

*\# ─── Tests de las Vistas ───────────────────────────────────────────────────────*

**class** TareaViewTest(TestCase):

    **def** setUp(self):  
        self.tarea \= Tarea.objects.create(  
            titulo\="Leer documentación",  
            prioridad\='alta'  
        )

    **def** test\_lista\_tareas\_status\_200(self):  
        respuesta \= self.client.get(reverse('lista\_tareas'))  
        self.assertEqual(respuesta.status\_code, 200)

    **def** test\_lista\_tareas\_usa\_template\_correcto(self):  
        respuesta \= self.client.get(reverse('lista\_tareas'))  
        self.assertTemplateUsed(respuesta, 'mi\_app/lista\_tareas.html')

    **def** test\_lista\_tareas\_muestra\_titulo(self):  
        respuesta \= self.client.get(reverse('lista\_tareas'))  
        self.assertContains(respuesta, "Leer documentación")

    **def** test\_crear\_tarea\_get\_muestra\_formulario(self):  
        respuesta \= self.client.get(reverse('crear\_tarea'))  
        self.assertEqual(respuesta.status\_code, 200)  
        self.assertIn('form', respuesta.context)

    **def** test\_crear\_tarea\_post\_valido(self):  
        *"""Un POST válido debe persistir la tarea en la base de datos."""*  
        self.client.post(reverse('crear\_tarea'), {  
            'titulo': 'Hacer ejercicio',  
            'prioridad': 'media'  
        })  
        *\# setUp ya creó 1 tarea, ahora debe haber 2*  
        self.assertEqual(Tarea.objects.count(), 2)  
        self.assertTrue(Tarea.objects.filter(titulo\='Hacer ejercicio').exists())

    **def** test\_crear\_tarea\_post\_redirige(self):  
        *"""Un POST válido debe redirigir a la lista de tareas."""*  
        respuesta \= self.client.post(reverse('crear\_tarea'), {  
            'titulo': 'Meditar',  
            'prioridad': 'baja'  
        })  
        self.assertRedirects(respuesta, reverse('lista\_tareas'))

    **def** test\_crear\_tarea\_post\_muestra\_mensaje(self):  
        *"""Un POST válido debe mostrar mensaje de éxito."""*  
        respuesta \= self.client.post(reverse('crear\_tarea'), {  
            'titulo': 'Meditar',  
            'prioridad': 'baja'  
        }, follow\=True)  
        self.assertContains(respuesta, "creada exitosamente")

    **def** test\_crear\_tarea\_post\_invalido\_no\_persiste(self):  
        *"""Un POST inválido no debe crear la tarea."""*  
        self.client.post(reverse('crear\_tarea'), {  
            'titulo': '',  
            'prioridad': 'media'  
        })  
        self.assertEqual(Tarea.objects.count(), 1)

    **def** test\_completar\_tarea\_post(self):  
        *"""Un POST a completar\_tarea debe marcar la tarea como completada."""*  
        self.client.post(reverse('completar\_tarea', args\=\[self.tarea.pk\]))  
        self.tarea.refresh\_from\_db()  
        self.assertTrue(self.tarea.completada)

    **def** test\_completar\_tarea\_redirige(self):  
        *"""Completar una tarea debe redirigir a la lista."""*  
        respuesta \= self.client.post(  
            reverse('completar\_tarea', args\=\[self.tarea.pk\])  
        )  
        self.assertRedirects(respuesta, reverse('lista\_tareas'))

    **def** test\_completar\_tarea\_inexistente\_retorna\_404(self):  
        respuesta \= self.client.post(reverse('completar\_tarea', args\=\[9999\]))  
        self.assertEqual(respuesta.status\_code, 404)

---

# Métodos Assert más usados en Django

Además de los métodos estándar de unittest, Django agrega métodos específicos para pruebas web:

## Métodos heredados de unittest

| Método | Verifica que… |
| :---- | :---- |
| assertEqual(a, b) | a es igual a b |
| assertNotEqual(a, b) | a no es igual a b |
| assertTrue(x) | x es verdadero |
| assertFalse(x) | x es falso |
| assertIsNone(x) | x es None |
| assertIsNotNone(x) | x no es None |
| assertIn(a, b) | a está contenido en b |
| assertNotIn(a, b) | a no está contenido en b |
| assertRaises(exc, func) | func lanza la excepción exc |

## Métodos exclusivos de Django

| Método | Verifica que… |
| :---- | :---- |
| assertContains(resp, text) | La respuesta HTTP contiene el texto |
| assertNotContains(resp, text) | La respuesta HTTP no contiene el texto |
| assertTemplateUsed(resp, nombre) | La respuesta usó el template indicado |
| assertRedirects(resp, url) | La respuesta redirige a la URL indicada |
| assertFormError(form, campo, msg) | El formulario tiene ese error en ese campo |
| assertQuerySetEqual(qs, lista) | El QuerySet es igual a la lista esperada |

**Nota sobre follow=True:** Al pasar follow=True a self.client.get() o self.client.post(), el cliente sigue las redirecciones automáticamente. Esto es útil para verificar mensajes flash que solo aparecen tras la redirección.

---

# Organización recomendada de los tests

Para proyectos medianos o grandes, organiza los tests en una carpeta:

mi\_app/  
├── tests/  
│   ├── \_\_init\_\_.py  
│   ├── test\_models.py  
│   ├── test\_views.py  
│   ├── test\_forms.py  
│   └── test\_urls.py

Para ejecutar solo un archivo de tests:

python manage.py test mi\_app.tests.test\_models

Para ejecutar solo una clase:

python manage.py test mi\_app.tests.test\_models.ProductoModelTest

Para ejecutar solo un método:

python manage.py test mi\_app.tests.test\_models.ProductoModelTest.test\_crear\_producto

Para ejecutar con más detalle (verbosity):

python manage.py test mi\_app \--verbosity\=2

---

