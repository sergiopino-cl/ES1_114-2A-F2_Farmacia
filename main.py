import streamlit as st
import pandas as pd
from conectar import crear_conexion
from servicios.miindicador import MiIndicador
from dao.vendedor_dao import VendedorDAO
from model.vendedor import Vendedor
from model.medicamento import Medicamento
from datetime import date
from dao.medicamento_dao import MedicamentoDAO
import sys

def main():

    st.title("Aplicacion venta de farmacia")
    st.set_page_config(page_title='Farmacia')
    st.sidebar.title("Aplicacion venta de farmacia")
    
    # Menú lateral ampliado
    opcion = st.sidebar.selectbox(
        "Selecciona una opción",
        ["Ver Medicamentos", "Registrar Vendedor", "Registrar Medicamento"]
    )

    conexion = crear_conexion()

    if conexion:
        vendedor_dao = VendedorDAO(conexion)
        vendedor_dao.crear_tabla()

        medicamento_dao = MedicamentoDAO(conexion)
        medicamento_dao.crear_tabla()

        try:
            indicador = MiIndicador()
            # Asumiendo que tu servicio MiIndicador tiene un método o atributo para obtener el dólar
            # Ejemplo: indicador.obtener_dolar() o indicador.dolar
            valor_dolar = indicador.obtener_valor("dolar") 

        except Exception as e:
            valor_dolar = 950.0  # Valor por defecto en caso de fallo de conexión/API
            st.warning(f"No se pudo consultar MiIndicador. Usando valor estimado del USD: ${valor_dolar}")

        st.sidebar.info(f"💵 **Dólar hoy:** ${valor_dolar:,.2f} CLP")

        try:
            if opcion == "Registrar Medicamento":
                st.subheader("Registro de Medicamento")
                st.info(f"💡 **Valor actual del Dólar:** ${valor_dolar:,.2f} CLP")

                with st.form("form_medicamento"):
                    nombre = st.text_input("Nombre del Medicamento *")
                    precio_venta = st.number_input("Precio de Venta ($ CLP) *", min_value=0, step=100)
                    
                    # Input para el precio de compra en USD
                    precio_compra_usd = st.number_input("Precio Compra (USD) *", min_value=0.0, format="%.2f", step=0.5)
                    
                    # Cálculo automático en Pesos Chilenos
                    precio_compra_peso = int(precio_compra_usd * valor_dolar)
                    st.write(f"**Precio de Compra Calculado en Pesos:** ${precio_compra_peso:,.0f} CLP")

                    fecha_ultima_compra = st.date_input("Fecha de Última Compra", value=date.today())
                    restringido = st.checkbox("¿Requiere receta médica (Restringido)?")

                    submit_button = st.form_submit_button("Guardar Medicamento")

                    if submit_button:
                        if not nombre.strip():
                            st.warning("El nombre del medicamento es obligatorio.")
                        else:
                            # 2. Instanciar el modelo Medicamento
                            nuevo_medicamento = Medicamento(
                                nombre=nombre,
                                precio_venta=int(precio_venta),
                                precio_compra_usd=float(precio_compra_usd),
                                precio_compra_peso=precio_compra_peso,
                                fecha_ultima_compra=str(fecha_ultima_compra),
                                restringido=restringido
                            )

                            # 3. Guardar en SQLite mediante el DAO
                            if medicamento_dao.insertar(nuevo_medicamento):
                                st.success(f"¡Medicamento '{nombre}' registrado exitosamente!")
                            else:
                                st.error("Error al registrar el medicamento en la base de datos.")
            elif opcion == "Ver Medicamentos":
                st.subheader("Lista de Medicamentos")
                df = medicamento_dao.obtener_todos()
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No hay medicamentos registrados.")

            elif opcion == "Registrar Vendedor":
                st.subheader("Registro de nuevo vendedor")
                
                # Creamos un formulario en Streamlit
                with st.form("form_vendedor"):
                    rut = st.text_input("RUT del Vendedor (ej. 12.345.678-9)")
                    nombre = st.text_input("Nombre Completo")
                    esfarmaceutico = st.checkbox("¿Es Químico Farmacéutico?")
                    
                    # Botón de envío del formulario
                    submit_button = st.form_submit_button("Guardar Vendedor")
                    
                    if submit_button:
                        if rut.strip() == "" or nombre.strip() == "":
                            st.warning("Por favor, completa todos los campos obligatorios.")
                        else:
                            # 1. Instanciamos el objeto Modelo
                            nuevo_vendedor = Vendedor(rut=rut, nombre=nombre, esfarmaceutico=esfarmaceutico)
                            
                            # 2. Usamos el DAO para guardarlo en la BD
                            exito = vendedor_dao.insertar(nuevo_vendedor)
                            
                            if exito:
                                st.success(f"¡Vendedor {nombre} registrado con éxito!")
                            else:
                                st.error("Error al registrar el vendedor (es probable que el RUT ya exista).")
                
                # Mostrar la lista actual de vendedores registrados
                st.divider()
                st.subheader("Vendedores Registrados en el Sistema")
                df_vendedores = vendedor_dao.obtener_todos()
                if not df_vendedores.empty:
                    st.dataframe(df_vendedores, use_container_width=True)
                else:
                    st.info("No hay vendedores registrados todavía.")
                    
            conexion.close()

        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")
            sys.exit(1)
    else:
        st.error("No se pudo conectar a la base de datos.")

if __name__ == "__main__":
    main()

