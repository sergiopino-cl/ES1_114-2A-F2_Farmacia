import streamlit as st
import pandas as pd
from conectar import crear_conexion
from servicios.miindicador import MiIndicador
from dao.vendedor_dao import VendedorDAO
from model.vendedor import Vendedor
import sys

def main():

    st.title("Aplicacion venta de farmacia")
    st.set_page_config(page_title='Farmacia')
    st.sidebar.title("Aplicacion venta de farmacia")
    
    # Menú lateral ampliado
    opcion = st.sidebar.selectbox(
        "Selecciona una opción",
        ["Ver Inventario", "Gestionar Inventario", "Registrar Vendedor"]
    )

    conexion = crear_conexion()

    if conexion:
        vendedor_dao = VendedorDAO(conexion)
        vendedor_dao.crear_tabla()

        try:
            if opcion == "Registrar Vendedor":
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

