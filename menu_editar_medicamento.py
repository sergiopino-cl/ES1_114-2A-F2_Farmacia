import streamlit as st
import pandas as pd
from conectar import crear_conexion
from servicios.miindicador import MiIndicador
from dao.vendedor_dao import VendedorDAO
from model.vendedor import Vendedor
from model.medicamento import Medicamento
from datetime import date
from dao.medicamento_dao import MedicamentoDAO
from dao.venta_dao import VentaDAO
from model.cliente import Cliente
from model.receta_medica import RecetaMedica
from model.detalle_venta import DetalleVenta
from model.venta import Venta
import sys


# opcion == "Editar Medicamento"
def editar_medicamento( indicador: float, conexion:  sqlite3.Connection ):

    st.empty

    st.subheader("✏️ Editar Medicamentos")
    # Servicio de conversión de divisa

    if indicador < 1: # NO hay valor válido de cambio dólar, no se puede editar
        st.error("No se tiene valor cambio dólar, no se pueden editar medicamentos")
        return

    med_dao = MedicamentoDAO(conexion)
    lista_meds = med_dao.obtener_todos_objetos()

    if not lista_meds:
        st.warning("No hay medicamentos registrados en la base de datos para editar.")
        return

    # 1. Selector para buscar el medicamento a editar
    med_actual = st.selectbox(
        "Seleccione el medicamento a modificar o eliminar:",
        options=lista_meds,
        format_func=lambda med: f"Código {med.codigo} - {med.nombre}"
    )

    # st.info(f"Editando: **{med_actual.codigo} - {med_actual.nombre} - {med_actual.stock}**")

    # 2. Cargar objeto desde la base de datos
    #med_editar = med_dao.obtener_por_codigo(med_actual.codigo)
    #st.write( med_editar)

    if med_actual.codigo > 0:
        # Convertir fecha almacenada (str 'YYYY-MM-DD') a datetime.date para el picker
        try:
            fecha_defecto = datetime.strptime(med_actual.fecha_ultima_compra, "%Y-%m-%d").date()
        except Exception:
            fecha_defecto = date.today()

        # 3. Formulario con los datos precargados
        with st.form("form_editar_medicamento"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_nombre = st.text_input("Nombre del Medicamento *", value=med_actual.nombre)
                nuevo_precio_venta = st.number_input("Precio Venta ($ CLP) *", min_value=0, value=int(med_actual.precio_venta), step=100, format="%d")
                nuevo_stock = st.number_input("Stock Disponible *", min_value=0, value=int(med_actual.stock), step=1, format="%d")

            with col2:
                nuevo_precio_usd = st.number_input("Precio Compra (USD) *", min_value=0.0, value=float(med_actual.precio_compra_usd), format="%.2f", step=0.50)
                
                # Recálculo automático del valor en pesos según la tasa del Dólar hoy
                nuevo_precio_peso = int(nuevo_precio_usd * indicador)
                st.caption(f"➔ Valor re-calculado en CLP: **${nuevo_precio_peso:,.0f} CLP**")

                nueva_fecha = st.date_input("Fecha Última Compra", value=fecha_defecto)
                nuevo_restringido = st.checkbox("¿Requiere Receta Médica?", value=med_actual.restringido)

            if indicador > 0:
                submit_guardar = st.form_submit_button("💾 Guardar Cambios", type="primary")

            if submit_guardar:
                if not nuevo_nombre.strip():
                    st.warning("El nombre del medicamento no puede estar vacío.")
                else:
                    # Crear el objeto con los datos modificados manteniendo el código original
                    medicamento_editado = Medicamento(
                        codigo=med_actual.codigo,
                        nombre=nuevo_nombre,
                        precio_venta=int(nuevo_precio_venta),
                        precio_compra_usd=float(nuevo_precio_usd),
                        precio_compra_peso=nuevo_precio_peso,
                        fecha_ultima_compra=str(nueva_fecha),
                        restringido=nuevo_restringido,
                        stock=int(nuevo_stock)
                    )

                    # Guardar mediante el DAO
                    if med_dao.actualizar(medicamento_editado):
                        st.success(f"¡El medicamento '{nuevo_nombre}' ha sido actualizado exitosamente!")
                        st.rerun()
                    else:
                        st.error("No se pudo actualizar la información en la base de datos.")
        # 3. Sección de Eliminación (Fuera del st.form para usar confirmaciones directas)
        with st.expander("🗑️ Zona de Peligro - Eliminar Medicamento"):
            st.warning(f"¿Estás seguro de que deseas eliminar permanentemente **{med_actual.nombre}**?")
            
            confirmar = st.checkbox(f"Sí, confirmo que deseo eliminar el código {med_actual.codigo}")
            
            if st.button("❌ Eliminar Definitivamente", disabled=not confirmar):
                if med_dao.eliminar(med_actual.codigo):
                    st.success(f"El medicamento '{med_actual.nombre}' ha sido eliminado.")
                    st.rerun()
                else:
                    st.error("No se pudo eliminar el medicamento de la base de datos.")    
