import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

st.set_page_config(page_title="App Compra de Frutas", layout="wide")

# Archivos
excel_file = "Reporte de compra de fruta (1).xlsx"
data_sheet = "Data"
pagos_sheet = "Pagos"

# Cargar o inicializar los datos
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file, sheet_name=data_sheet)
    try:
        pagos_df = pd.read_excel(excel_file, sheet_name=pagos_sheet)
    except:
        pagos_df = pd.DataFrame(columns=["Ra", "FECHA PAGO", "MONTO"])
else:
    df = pd.DataFrame(columns=[
        "Ra", "UBICACIÓN", "FECHA", "CAJAS", "PRECIO DE COMPRA", "TOTAL COMPRA",
        "EMPAQUE", "CULTIVO", "CLIENTE", "PRECIO DE VENTA"
    ])
    pagos_df = pd.DataFrame(columns=["Ra", "FECHA PAGO", "MONTO"])

# Sidebar
st.sidebar.image(
    "https://img.freepik.com/vector-premium/mercado-agricultores-logotipo-tienda-productos-agricolas_527952-76.jpg",
    use_container_width=True
)
st.sidebar.title("🌿 Menú Principal")
menu = st.sidebar.radio("Selecciona una opción", [
    "Registrar Compra", 
    "Ver Compras y Utilidades", 
    "Análisis y Gráficos",
    "Consulta por Agricultor",
    "Registro de Pagos"
])

# Registrar Compra
if menu == "Registrar Compra":
    st.header("📦 Registro de Compras de Fruta")
    with st.form("registro_compra"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("📅 Fecha", value=datetime.today())
            agricultor = st.text_input("👨‍🌾 Agricultor (Ra)")
            ubicacion = st.text_input("📍 Ubicación")
            producto = st.selectbox("🌾 Cultivo", options=sorted(df["CULTIVO"].dropna().unique().tolist() + ["Otro"]))
        with col2:
            empaque = st.selectbox("📦 Empaque", options=sorted(df["EMPAQUE"].dropna().unique().tolist() + ["Otro"]))
            cliente = st.selectbox("🛒 Cliente", options=sorted(df["CLIENTE"].dropna().unique().tolist() + ["Otro"]))
            cajas = st.number_input("🔢 Número de cajas", min_value=1, step=1)
            precio_compra = st.number_input("💰 Precio de compra por caja", min_value=0.0)
            precio_venta = st.number_input("🏷 Precio de venta por caja", min_value=0.0)
        submit = st.form_submit_button("✅ Registrar")

    if submit:
        if not agricultor or not ubicacion or not producto or not cliente:
            st.warning("Por favor completa todos los campos obligatorios.")
        else:
            total_compra = cajas * precio_compra
            nueva_fila = {
                "Ra": agricultor, "UBICACIÓN": ubicacion, "FECHA": fecha, "CAJAS": cajas,
                "PRECIO DE COMPRA": precio_compra, "TOTAL COMPRA": total_compra,
                "EMPAQUE": empaque, "CULTIVO": producto, "CLIENTE": cliente,
                "PRECIO DE VENTA": precio_venta
            }
            df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name=data_sheet, index=False)
                pagos_df.to_excel(writer, sheet_name=pagos_sheet, index=False)
            st.success("✅ Compra registrada exitosamente.")

# Ver Compras y Utilidades
elif menu == "Ver Compras y Utilidades":
    st.header("📊 Compras y Utilidades")
    if df.empty:
        st.info("No hay datos registrados aún.")
    else:
        df["UTILIDAD BRUTA"] = (df["PRECIO DE VENTA"] - df["PRECIO DE COMPRA"]) * df["CAJAS"]
        st.metric("💰 Total comprado", f"${df['TOTAL COMPRA'].sum():,.2f}")
        st.metric("📦 Total de cajas", int(df['CAJAS'].sum()))
        st.metric("📈 Utilidad bruta total", f"${df['UTILIDAD BRUTA'].sum():,.2f}")
        st.dataframe(df.sort_values("FECHA", ascending=False), use_container_width=True)

# Análisis y Gráficos con Filtros
elif menu == "Análisis y Gráficos":
    st.header("📈 Análisis y Gráficos")
    if df.empty:
        st.info("No hay datos registrados aún.")
    else:
        df["UTILIDAD BRUTA"] = (df["PRECIO DE VENTA"] - df["PRECIO DE COMPRA"]) * df["CAJAS"]
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_agricultor = st.multiselect("👨‍🌾 Filtrar por Agricultor", df["Ra"].unique())
        with col2:
            filtro_cultivo = st.multiselect("🌾 Filtrar por Cultivo", df["CULTIVO"].unique())
        with col3:
            filtro_cliente = st.multiselect("🛒 Filtrar por Cliente", df["CLIENTE"].unique())

        filtrado = df.copy()
        if filtro_agricultor:
            filtrado = filtrado[filtrado["Ra"].isin(filtro_agricultor)]
        if filtro_cultivo:
            filtrado = filtrado[filtrado["CULTIVO"].isin(filtro_cultivo)]
        if filtro_cliente:
            filtrado = filtrado[filtrado["CLIENTE"].isin(filtro_cliente)]

        st.subheader("💵 Utilidad bruta por agricultor")
        fig1 = px.bar(filtrado.groupby("Ra")["UTILIDAD BRUTA"].sum().reset_index(), 
                      x="UTILIDAD BRUTA", y="Ra", orientation="h",
                      color="UTILIDAD BRUTA", color_continuous_scale="Greens",
                      labels={"Ra": "Agricultor", "UTILIDAD BRUTA": "Utilidad ($)"})
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📦 Cajas por cultivo")
        fig2 = px.bar(filtrado.groupby("CULTIVO")["CAJAS"].sum().reset_index(), 
                      x="CULTIVO", y="CAJAS", color="CAJAS", color_continuous_scale="Blues")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("🏷 Precio promedio de venta por cliente")
        fig3 = px.bar(filtrado.groupby("CLIENTE")["PRECIO DE VENTA"].mean().reset_index(), 
                      x="CLIENTE", y="PRECIO DE VENTA", color="PRECIO DE VENTA", color_continuous_scale="Oranges")
        st.plotly_chart(fig3, use_container_width=True)

# Consulta por Agricultor
elif menu == "Consulta por Agricultor":
    st.header("🔍 Consulta por Agricultor")
    if df.empty:
        st.info("No hay datos registrados aún.")
    else:
        selected = st.selectbox("Selecciona un agricultor", sorted(df["Ra"].unique()))
        compras = df[df["Ra"] == selected]
        pagos = pagos_df[pagos_df["Ra"] == selected]
        total_cajas = compras["CAJAS"].sum()
        precio_prom = compras["PRECIO DE COMPRA"].mean()
        total_compra = compras["TOTAL COMPRA"].sum()
        total_pago = pagos["MONTO"].sum()
        saldo = total_compra - total_pago

        st.metric("📦 Total de cajas", total_cajas)
        st.metric("💸 Precio promedio de compra", f"${precio_prom:.2f}")
        st.metric("💰 Total comprado", f"${total_compra:.2f}")
        st.metric("✅ Total pagado", f"${total_pago:.2f}")
        st.metric("❗ Saldo pendiente", f"${saldo:.2f}")

# Registro de Pagos
elif menu == "Registro de Pagos":
    st.header("💰 Registro de Pagos a Agricultores")
    agricultores = sorted(df["Ra"].dropna().unique())

    if agricultores:
        with st.form("form_pago"):
            col1, col2 = st.columns(2)
            with col1:
                ra_pago = st.selectbox("👨‍🌾 Selecciona agricultor", options=agricultores)
            with col2:
                fecha_pago = st.date_input("📅 Fecha del pago", value=datetime.today())
                monto_pago = st.number_input("💵 Monto del pago", min_value=0.0)
            submit_pago = st.form_submit_button("Registrar Pago")

        if submit_pago:
            nuevo_pago = {"Ra": ra_pago, "FECHA PAGO": fecha_pago, "MONTO": monto_pago}
            pagos_df = pd.concat([pagos_df, pd.DataFrame([nuevo_pago])], ignore_index=True)
            with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name=data_sheet, index=False)
                pagos_df.to_excel(writer, sheet_name=pagos_sheet, index=False)
            st.success("✅ Pago registrado correctamente.")

        st.subheader("📄 Pagos registrados")
        st.dataframe(pagos_df.sort_values("FECHA PAGO", ascending=False), use_container_width=True)
    else:
        st.warning("⚠️ No hay agricultores registrados aún.")