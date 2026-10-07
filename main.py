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

def main():

    st.title("Aplicacion venta de farmacia")
    st.set_page_config(page_title='Farmacia')
    st.sidebar.title("Aplicacion venta de farmacia")
    
    # Menú lateral ampliado
    opcion = st.sidebar.selectbox(
        "Selecciona una opción",
        ["Ver Medicamentos", "Registrar Vendedor", "Registrar Medicamento", "Editar Medicamento", "Realizar Venta"]
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
            if opcion == "Editar Medicamento":
                st.subheader("✏️ Editar Medicamento Existente")
                # Servicio de conversión de divisa
                indicador_service = MiIndicador()
                valor_dolar = indicador_service.obtener_valor("dolar") or 950.0

                med_dao = MedicamentoDAO(conexion)
                lista_meds = med_dao.obtener_todos_objetos()

                if not lista_meds:
                    st.warning("No hay medicamentos registrados en la base de datos para editar.")
                    return

                # 1. Selector para buscar el medicamento a editar
                med_actual = st.selectbox(
                    "Seleccione el medicamento a modificar:",
                    options=lista_meds,
                    format_func=lambda med: f"Código {med.codigo} - {med.nombre}"
                )
                st.info(f"Editando: **{med_actual.codigo} - {med_actual.nombre} - {med_actual.stock}**")

                # 2. Cargar objeto desde la base de datos
                med_editar = med_dao.obtener_por_codigo(med_actual.codigo)

                if med_editar:
                    st.info(f"Editando información de: **{med_actual.nombre}** (Tasa USD actual: ${valor_dolar:,.2f} CLP)")

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
                            nuevo_precio_venta = st.number_input("Precio Venta ($ CLP) *", min_value=0, value=int(med_actual.precio_venta), step=100)
                            nuevo_stock = st.number_input("Stock Disponible *", min_value=0, value=int(med_actual.stock), step=1)

                        with col2:
                            nuevo_precio_usd = st.number_input("Precio Compra (USD) *", min_value=0.0, value=float(med_actual.precio_compra_usd), format="%.2f", step=0.50)
                            
                            # Recálculo automático del valor en pesos según la tasa del Dólar hoy
                            nuevo_precio_peso = int(nuevo_precio_usd * valor_dolar)
                            st.caption(f"➔ Valor re-calculado en CLP: **${nuevo_precio_peso:,.0f} CLP**")

                            nueva_fecha = st.date_input("Fecha Última Compra", value=fecha_defecto)
                            nuevo_restringido = st.checkbox("¿Requiere Receta Médica?", value=med_actual.restringido)

                        submit_guardar = st.form_submit_button("💾 Guardar Cambios")

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

            elif opcion == "Ralizar Venta":
                st.subheader("🛒 Registrar Nueva Venta")
    
                # Inicializar carrito en session_state
                if "carrito" not in st.session_state:
                    st.session_state.carrito = []

                # Cargar servicios y DAOs
                indicador_service = MiIndicador()
                valor_dolar = indicador_service.obtener_valor("dolar") or 950.0

                med_dao = MedicamentoDAO(conexion)
                vendedor_dao = VendedorDAO(conexion)
                venta_dao = VentaDAO(conexion)
                venta_dao.crear_tablas()

                # 1. Datos Generales de la Venta
                col1, col2 = st.columns(2)
                with col1:
                    client_rut = st.text_input("RUT Cliente *")
                    client_nombre = st.text_input("Nombre Cliente *")
                with col2:
                    df_vendedores = vendedor_dao.obtener_todos()
                    vendedor_rut = st.selectbox(
                        "Vendedor *", 
                        options=df_vendedores['rut'].tolist() if not df_vendedores.empty else [""],
                        format_func=lambda x: f"RUT: {x}"
                    )

                st.divider()

                # 2. Selección de Medicamentos
                st.markdown("##### Agregar Productos al Carrito")
                df_meds = med_dao.obtener_todos()
                if not df_meds.empty:
                    med_id = st.selectbox(
                        "Seleccionar Medicamento", 
                        options=df_meds['codigo'].tolist(),
                        format_func=lambda x: f"{df_meds[df_meds['codigo']==x]['nombre'].values[0]} - ${df_meds[df_meds['codigo']==x]['precio_venta'].values[0]} CLP"
                    )
                    cantidad = st.number_input("Cantidad", min_value=1, step=1, value=1)
                    
                    if st.button("➕ Agregar al Carrito"):
                        med_sel = df_meds[df_meds['codigo'] == med_id].iloc[0]
                        # Creamos un objeto rápido para el carrito
                        class ObjMed: pass
                        m = ObjMed()
                        m.codigo = int(med_sel['codigo'])
                        m.nombre = str(med_sel['nombre'])
                        m.restringido = bool(med_sel['restringido'])
                        
                        detalle = DetalleVenta(m, int(cantidad), float(med_sel['precio_venta']))
                        st.session_state.carrito.append(detalle)
                        st.success(f"Agregado: {m.nombre} x{cantidad}")

                # Display del Carrito
                if st.session_state.carrito:
                    st.markdown("##### Detalle del Carrito")
                    requiere_receta = any(getattr(d.medicamento, 'restringido', False) for d in st.session_state.carrito)
                
                    datos_tabla = []
                    total = 0.0
                    for idx, d in enumerate(st.session_state.carrito):
                        sub = d.calcular_subtotal()
                        total += sub
                        datos_tabla.append({
                            "Producto": d.medicamento.nombre,
                            "Cantidad": d.cantidad,
                            "Precio U.": f"${d.precio_unitario:,.0f}",
                            "Subtotal": f"${sub:,.0f}",
                            "Restringido": "Sí" if getattr(d.medicamento, 'restringido', False) else "No"
                        })
                    st.table(datos_tabla)
                    st.markdown(f"### **Total: ${total:,.0f} CLP**")

                    # 3. Receta Médica si aplica
                    num_receta, fecha_receta = None, None
                    if requiere_receta:
                        st.warning("⚠️ El carrito contiene productos controlados. Debe ingresar la Receta Médica.")
                        num_receta = st.text_input("Número de Receta *")
                        fecha_receta = st.date_input("Fecha Emisión Receta", value=date.today())

                    # 4. Finalizar Venta
                    if st.button("💾 Confirmar y Procesar Venta"):
                        cliente = Cliente(client_rut, client_nombre)
                        receta_obj = RecetaMedica(num_receta, str(fecha_receta)) if requiere_receta and num_receta else None
                        
                        venta = Venta(
                            fecha=str(date.today()),
                            cliente=cliente,
                            vendedor_rut=vendedor_rut,
                            receta_medica=receta_obj
                        )
                        for d in st.session_state.carrito:
                            venta.agregar_detalle(d)

                        if not venta.validar_venta():
                            st.error("Error de validación: Verifique RUT del cliente, productos y datos de receta médica si aplica.")
                        else:
                            if venta_dao.guardar_venta(venta, tasa_dolar=valor_dolar):
                                st.success("¡Venta procesada exitosamente!")
                                st.session_state.carrito = [] # Limpiar carrito
                                st.rerun()
                            else:
                                st.error("Ocurrió un problema al registrar la venta en la base de datos.")
            elif opcion == "Registrar Medicamento":
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

                    stock_ingresado = st.number_input("Stock adquirido", min_value=0, step=10)

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
                                restringido=restringido,
                                stock=int(stock_ingresado)
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

