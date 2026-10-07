# **Farmacia**


Repositorio para la asignatura de Programación Orientada a Objetos Seguro.

https://github.com/sergiopino-cl/ES1_114-2A-F2_Farmacia

**Profesor:** Michael Arjel

**Institución:** Inacap

**Carrera:** Analista programador

**Sede:** Puente alto

**Codigo:** TI3V21

**Fecha:** 07 de octubre del 2026

**Alumnos:**
Estefanía Loreto Antilao Lepín, 19.426.236-1
Sergio Patricio Pino González, 11.739.934-6

----
Para ejecutar la aplicación
----
Python version: 3.14.8

-- **Para instalar los requerimientos**:

python -m pip install -r requirements.txt

**Para ejecutar aplicacion Web con streamlit**:

**python3 -m streamlit run main.py**


  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.7:8501

----

**1. El Problema**
La farmacia requiere un sistema de ventas que gestione tres tipos de medicamentos con reglas distintas:
venta libre, receta simple y controlados. El sistema debe diferenciar los permisos entre dos roles de
trabajadores: el Vendedor, quien puede realizar ventas generales, y el Químico Farmacéutico, único
autorizado para aprobar la venta de medicamentos controlados. Es fundamental validar formatos de
datos como el RUT del cliente y el número de receta médica, así como impedir la venta de productos
vencidos o controlados sin la documentación adecuada. Adicionalmente, una venta puede contener
múltiples productos (líneas de detalle) y los medicamentos importados deben calcular su precio
dinámicamente según la tasa del dólar del día.

Uso de I.A.

Se utilizaron diversas I.A.s, tanto en modalidad LLM como CLI, para analizar el problema, ademas de recibir indicaciones acerca de la interfaz mas eficiente y simple, lo que ayudo a investigar acerca de Streamlit y revisar la documentacion y videos de capacitacion en Youtube para implementarla en la aplicación.

Ademas se utilizó I.A. para realizar las tareas repetitivas y tediosas de la programacion de las clases, tambien como apoyo en la depuración y testing.

En nuestro caso NO dejamos a la I.A. avanzar totalmente sola para ir entendiendo la programación y la sintaxis de Python.

Finalmente le pedimos a AGY que revisara y nos diera recomendaciones para poder avanzar con el módulo y las clases de ventas.

----
NOTAS Para el desarrollador
----

-- Para documentar los requerimientos:

python -m pip freeze > requirements.txt

-- Para subir los cambios a GitHub:

git add .

git commit -m "Etapa, comentario u observacion"

git push -u origin main