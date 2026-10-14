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

# Opciones de menu
from menu_editar_medicamento import editar_medicamento
from menu_ver_ventas import ver_ventas

def main():
    st.set_page_config(page_title='Farmacia', layout='wide')
    st.title("Aplicacion venta de farmacia")
    st.sidebar.title("Aplicacion venta de farmacia")
    
    # Menú lateral ampliado
    opcion = st.sidebar.selectbox(
        "Selecciona una opción",
        ["Ver Medicamentos", "Registrar Vendedor", 
         "Registrar Medicamento", "Editar Medicamento", 
         "Realizar Venta", "Ver Ventas Realizadas", "Opcion de prueba"]
    )

    try:
        indicador = MiIndicador()
        # Asumiendo que tu servicio MiIndicador tiene un método o atributo para obtener el dólar
        # Ejemplo: indicador.obtener_dolar() o indicador.dolar
        valor_dolar = indicador.obtener_valor("dolar") 

    except Exception as e:
        valor_dolar = 0.0  # Valor por defecto en caso de fallo de conexión/API
        st.warning(f"No se pudo consultar Valor del dólar. NO se permitirá la edición hasta solucionar el problema, reintente mas tarde.")

    st.sidebar.info(f"💵 **Dólar hoy:** ${valor_dolar:,.2f} CLP")

    conexion = crear_conexion()

    if conexion:
        vendedor_dao = VendedorDAO(conexion)
        vendedor_dao.crear_tabla()

        medicamento_dao = MedicamentoDAO(conexion)
        medicamento_dao.crear_tabla()

        try:
            if opcion == "Opcion de prueba":
                st.error("Opción de menú inexistente")

            elif opcion == "Editar Medicamento":
                editar_medicamento( valor_dolar, conexion )

            elif opcion == "Realizar Venta":
                st.subheader("🛒 Venta de Medicamentos")

                # Inicializar carrito en session_state
                if "carrito" not in st.session_state:
                    st.session_state.carrito = []

                # Cargar DAOs
                med_dao = MedicamentoDAO(conexion)
                vendedor_dao = VendedorDAO(conexion)
                venta_dao = VentaDAO(conexion)
                venta_dao.crear_tablas()

                # 1. Datos Generales de la Venta
                col1, col2 = st.columns(2)
                with col1:
                    client_rut = st.text_input("RUT Cliente *", placeholder="Ej: 12.345.678-9 o 1-9")
                    client_nombre = st.text_input("Nombre Cliente *", placeholder="Ej: Juan Pérez")
                with col2:
                    lista_vendedores = vendedor_dao.obtener_todos_objetos()
                    if lista_vendedores:
                        vendedor_sel = st.selectbox(
                            "Vendedor *", 
                            options=lista_vendedores,
                            format_func=lambda v: f"{v.nombre} ({'Químico Farmacéutico' if v.esfarmaceutico else 'Vendedor General'}) - RUT: {v.rut}"
                        )
                    else:
                        vendedor_sel = None
                        st.warning("No hay vendedores disponibles registrados en el sistema.")

                st.divider()

                # 2. Selección de Medicamentos
                st.markdown("##### Agregar Productos al Carrito")
                df_meds = med_dao.obtener_todos()
                if not df_meds.empty:
                    # Buscamos medicamentos activos
                    med_id = st.selectbox(
                        "Seleccionar Medicamento", 
                        options=df_meds['codigo'].tolist(),
                        format_func=lambda x: (
                            f"{df_meds[df_meds['codigo']==x]['nombre'].values[0]} - "
                            f"${df_meds[df_meds['codigo']==x]['precio_venta'].values[0]:,.0f} CLP "
                            f"(Stock: {df_meds[df_meds['codigo']==x]['stock'].values[0]}) "
                            f"{'[Controlado/Receta]' if df_meds[df_meds['codigo']==x]['restringido'].values[0] else '[Venta Libre]'}"
                        )
                    )
                    
                    fila_med = df_meds[df_meds['codigo'] == med_id].iloc[0]
                    stock_disponible = int(fila_med['stock'])
                    
                    col_q1, col_q2 = st.columns([2, 1])
                    with col_q1:
                        cantidad = st.number_input(
                            "Cantidad", 
                            min_value=1, 
                            max_value=max(1, stock_disponible), 
                            step=1, 
                            value=1,
                            disabled=(stock_disponible <= 0)
                        )
                    with col_q2:
                        st.write("")
                        st.write("")
                        btn_agregar = st.button("➕ Agregar al Carrito", disabled=(stock_disponible <= 0))

                    if stock_disponible <= 0:
                        st.error("⚠️ Este medicamento se encuentra agotado (Stock: 0).")

                    if btn_agregar:
                        med_obj = med_dao.obtener_por_codigo(med_id)
                        if not med_obj:
                            st.error("No se pudo cargar el medicamento seleccionado.")
                        else:
                            # Validar que la suma acumulada en el carrito no sobrepase el stock
                            cant_en_carrito = sum(d.cantidad for d in st.session_state.carrito if d.medicamento.codigo == med_obj.codigo)
                            if cant_en_carrito + cantidad > med_obj.stock:
                                st.error(f"Stock insuficiente para '{med_obj.nombre}'. Disponible: {med_obj.stock}, ya en carrito: {cant_en_carrito}.")
                            else:
                                try:
                                    detalle = DetalleVenta(med_obj, int(cantidad), float(med_obj.precio_venta))
                                    st.session_state.carrito.append(detalle)
                                    st.success(f"Agregado al carrito: {med_obj.nombre} x{cantidad}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al agregar producto: {e}")

                # 3. Display del Carrito
                if st.session_state.carrito:
                    st.markdown("##### Detalle del Carrito")
                    requiere_receta = any(getattr(d.medicamento, 'restringido', False) for d in st.session_state.carrito)
                
                    datos_tabla = []
                    total = 0.0
                    for idx, d in enumerate(st.session_state.carrito):
                        sub = d.calcular_subtotal()
                        total += sub
                        datos_tabla.append({
                            "N°": idx + 1,
                            "Producto": d.medicamento.nombre,
                            "Cantidad": d.cantidad,
                            "Precio U.": f"${d.precio_unitario:,.0f} CLP",
                            "Subtotal": f"${sub:,.0f} CLP",
                            "Tipo": "Controlado (Receta)" if getattr(d.medicamento, 'restringido', False) else "Venta Libre"
                        })
                    st.table(datos_tabla)
                    st.markdown(f"### **Total: ${total:,.0f} CLP**")

                    if st.button("🗑️ Vaciar Carrito"):
                        st.session_state.carrito = []
                        st.rerun()

                    # 4. Control de Receta Médica y Regla de Químico Farmacéutico
                    num_receta, fecha_receta = None, None
                    bloquear_por_rol = False

                    if requiere_receta:
                        st.warning("⚠️ El carrito contiene productos controlados. Debe ingresar la Receta Médica retenida.")
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            num_receta = st.text_input("Número de Receta *")
                        with col_r2:
                            fecha_receta = st.date_input("Fecha Emisión Receta", value=date.today())

                        # Verificación estricta de regla de negocio: Rol Químico Farmacéutico
                        if vendedor_sel is not None and not vendedor_sel.esfarmaceutico:
                            bloquear_por_rol = True
                            st.error(
                                f"⛔ **Operación no autorizada:** El vendedor seleccionado ({vendedor_sel.nombre}) es Vendedor General. "
                                "Por normativa de farmacia, SOLO un **Químico Farmacéutico** puede aprobar y registrar la venta de medicamentos controlados. "
                                "Por favor, seleccione un Químico Farmacéutico como vendedor responsable para poder procesar la venta."
                            )

                    # 5. Finalizar Venta
                    if st.button("💾 Confirmar y Procesar Venta", disabled=bloquear_por_rol):
                        if not client_rut.strip() or not client_nombre.strip():
                            st.error("Por favor complete el RUT y Nombre del cliente.")
                        elif not vendedor_sel:
                            st.error("Debe seleccionar un vendedor responsable.")
                        elif requiere_receta and (not num_receta or not num_receta.strip()):
                            st.error("Debe ingresar el número de la receta médica para medicamentos controlados.")
                        else:
                            try:
                                cliente = Cliente(client_rut.strip(), client_nombre.strip())
                                receta_obj = RecetaMedica(num_receta.strip(), str(fecha_receta)) if (requiere_receta and num_receta) else None
                                
                                venta = Venta(
                                    fecha=str(date.today()),
                                    cliente=cliente,
                                    vendedor=vendedor_sel,
                                    receta_medica=receta_obj
                                )
                                for d in st.session_state.carrito:
                                    venta.agregar_detalle(d)

                                valido, mensaje_validacion = venta.verificar_reglas()
                                if not valido:
                                    st.error(f"Error de validación: {mensaje_validacion}")
                                else:
                                    if venta_dao.guardar_venta(venta, tasa_dolar=valor_dolar):
                                        st.success(f"¡Venta #{venta.id} procesada exitosamente! Se actualizó el inventario de medicamentos.")
                                        st.session_state.carrito = [] # Limpiar carrito
                                        st.rerun()
                                    else:
                                        st.error(f"Ocurrió un problema al registrar la venta: {venta_dao.ultimo_error}")
                            except Exception as e:
                                st.error(f"Error al procesar la venta: {e}")

            elif opcion == "Ver Ventas Realizadas":
                ver_ventas(conexion)

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

