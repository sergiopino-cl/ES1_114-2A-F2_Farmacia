import streamlit as st
import pandas as pd
from dao.venta_dao import VentaDAO

def ver_ventas(conexion):
    """
    Vista modular para consultar las ventas registradas en el sistema de farmacia
    y examinar el desglose detallado de cada una.
    """
    st.subheader("📋 Historial de Ventas y Detalles")

    venta_dao = VentaDAO(conexion)
    venta_dao.crear_tablas()

    df_ventas = venta_dao.obtener_todas()

    if df_ventas.empty:
        st.info("ℹ️ No existen ventas registradas en el sistema todavía.")
        return

    # ---------------------------------------------------------
    # 1. Métricas Principales (KPIs)
    # ---------------------------------------------------------
    total_ventas = len(df_ventas)
    monto_total = df_ventas['total'].sum()
    promedio_venta = df_ventas['total'].mean() if total_ventas > 0 else 0
    ventas_con_receta = df_ventas['numero_receta'].notna().sum()

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("Total de Ventas", f"{total_ventas}")
    with col_kpi2:
        st.metric("Recaudación Total", f"${monto_total:,.0f} CLP")
    with col_kpi3:
        st.metric("Ticket Promedio", f"${promedio_venta:,.0f} CLP")
    with col_kpi4:
        st.metric("Ventas con Receta", f"{ventas_con_receta}")

    st.divider()

    # ---------------------------------------------------------
    # 2. Filtros de Búsqueda
    # ---------------------------------------------------------
    with st.expander("🔎 Filtros de búsqueda", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            vendedores_disp = ["Todos"] + sorted(list(df_ventas['vendedor_nombre'].dropna().unique()))
            filtro_vendedor = st.selectbox("Filtrar por Vendedor", options=vendedores_disp)

        with col_f2:
            filtro_tipo = st.selectbox("Tipo de Venta", options=["Todas", "Con Receta Médica", "Venta Libre"])

        with col_f3:
            filtro_texto = st.text_input("Buscar por RUT o Nombre de Cliente", placeholder="Ej: 1-7 o Juan").strip().lower()

    # Aplicar filtros
    df_filtrado = df_ventas.copy()

    if filtro_vendedor != "Todos":
        df_filtrado = df_filtrado[df_filtrado['vendedor_nombre'] == filtro_vendedor]

    if filtro_tipo == "Con Receta Médica":
        df_filtrado = df_filtrado[df_filtrado['numero_receta'].notna()]
    elif filtro_tipo == "Venta Libre":
        df_filtrado = df_filtrado[df_filtrado['numero_receta'].isna()]

    if filtro_texto:
        df_filtrado = df_filtrado[
            df_filtrado['cliente_rut'].astype(str).str.lower().str.contains(filtro_texto) |
            df_filtrado['cliente_nombre'].astype(str).str.lower().str.contains(filtro_texto)
        ]

    # ---------------------------------------------------------
    # 3. Tabla Resumen de Ventas
    # ---------------------------------------------------------
    st.markdown(f"#### Ventas Encontradas ({len(df_filtrado)})")

    if df_filtrado.empty:
        st.warning("No se encontraron ventas con los filtros seleccionados.")
    else:
        df_resumen = pd.DataFrame({
            "Folio": df_filtrado['id_venta'],
            "Fecha": df_filtrado['fecha'],
            "RUT Cliente": df_filtrado['cliente_rut'],
            "Cliente": df_filtrado['cliente_nombre'],
            "Vendedor": df_filtrado.apply(
                lambda r: f"{r['vendedor_nombre']} {'(Farmacéutico)' if r['esfarmaceutico'] else '(Vendedor)'}", 
                axis=1
            ),
            "N° Receta": df_filtrado['numero_receta'].fillna("Sin receta"),
            "Total": df_filtrado['total'].apply(lambda x: f"${x:,.0f} CLP")
        })

        st.dataframe(df_resumen, use_container_width=True, hide_index=True)

    st.divider()

    # ---------------------------------------------------------
    # 4. Detalle Completo de una Venta Seleccionada
    # ---------------------------------------------------------
    st.markdown("### 🔍 Detalle Específico de Venta")

    lista_ids = df_ventas['id_venta'].tolist()
    
    opciones_selector = df_ventas.apply(
        lambda r: f"Folio #{r['id_venta']} | Fecha: {r['fecha']} | Cliente: {r['cliente_nombre']} | Total: ${r['total']:,.0f} CLP",
        axis=1
    ).to_dict()

    id_seleccionado = st.selectbox(
        "Seleccione una venta para visualizar sus ítems y comprobante:",
        options=lista_ids,
        format_func=lambda x: opciones_selector.get(x, f"Folio #{x}")
    )

    if id_seleccionado:
        venta_info = df_ventas[df_ventas['id_venta'] == id_seleccionado].iloc[0]

        # Encabezado informativo de la venta
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"**Folio de Venta:** `#{venta_info['id_venta']}`")
            st.markdown(f"**Fecha:** {venta_info['fecha']}")
            st.markdown(f"**Cliente:** {venta_info['cliente_nombre']} *(RUT: {venta_info['cliente_rut']})*")
        
        with col_info2:
            rol_vendedor = "Químico Farmacéutico" if venta_info['esfarmaceutico'] else "Vendedor General"
            st.markdown(f"**Vendedor:** {venta_info['vendedor_nombre']} *(RUT: {venta_info['vendedor_rut']})*")
            st.markdown(f"**Rol Vendedor:** `{rol_vendedor}`")
            if pd.notna(venta_info['numero_receta']) and str(venta_info['numero_receta']).strip():
                st.markdown(f"**Receta Médica:** N° `{venta_info['numero_receta']}` *(Emisión: {venta_info['fecha_receta']})*")
            else:
                st.markdown("**Receta Médica:** *No requirió receta médica*")

        # Líneas de Detalle de Productos
        df_detalles = venta_dao.obtener_detalles_por_venta(id_seleccionado)

        if not df_detalles.empty:
            st.markdown("##### 🛒 Medicamentos Vendidos")
            
            df_det_mostrar = pd.DataFrame({
                "Cód.": df_detalles['codigo_medicamento'],
                "Medicamento": df_detalles['nombre_medicamento'],
                "Tipo": df_detalles['restringido'].apply(lambda r: "Controlado (Receta)" if r else "Venta Libre"),
                "Cantidad": df_detalles['cantidad'],
                "Precio Unitario": df_detalles['precio_unitario'].apply(lambda p: f"${p:,.0f} CLP"),
                "Subtotal": df_detalles['subtotal'].apply(lambda s: f"${s:,.0f} CLP")
            })

            st.table(df_det_mostrar)

            st.markdown(f"### **Total Venta: ${venta_info['total']:,.0f} CLP**")
        else:
            st.warning("No se encontraron líneas de detalle registradas para esta venta.")
