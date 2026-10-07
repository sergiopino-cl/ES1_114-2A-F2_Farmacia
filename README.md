# **Farmacia**

Repositorio para la asignatura de Programación Orientada a Objetos Seguro.

**Profesor:** Michael Arjel

**Institución:** Inacap

**Carrera:** Analista programador

**Sede:** Puente alto

**Codigo:** TI3V21

**Fecha:** 07 de octubre del 2026

**Alumnos:**
Estefanía Loreto Antilao Lepín, 19.426.236-1
Sergio Patricio Pino González, 11.739.934-6

**1. El Problema**
La farmacia requiere un sistema de ventas que gestione tres tipos de medicamentos con reglas distintas:
venta libre, receta simple y controlados. El sistema debe diferenciar los permisos entre dos roles de
trabajadores: el Vendedor, quien puede realizar ventas generales, y el Químico Farmacéutico, único
autorizado para aprobar la venta de medicamentos controlados. Es fundamental validar formatos de
datos como el RUT del cliente y el número de receta médica, así como impedir la venta de productos
vencidos o controlados sin la documentación adecuada. Adicionalmente, una venta puede contener
múltiples productos (líneas de detalle) y los medicamentos importados deben calcular su precio
dinámicamente según la tasa del dólar del día.

**2. Clases**

Usuario -> Vendedor
        -> Farmaceutico
        -> Cliente

Medicamento -> 