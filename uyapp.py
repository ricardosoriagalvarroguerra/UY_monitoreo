import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt  # Se utiliza en otras secciones si es necesario
import plotly.express as px

# -----------------------------
# Función para cargar y normalizar la base de datos
# -----------------------------
@st.cache_data  # Cachea la carga para mejorar el rendimiento
def load_data():
    # Lee el archivo Parquet; asegúrate de tener instalado pyarrow o fastparquet
    df = pd.read_parquet("uy_procurements.parquet")
    
    # Normalización de la columna 'awarded_firm_country_name'
    if "awarded_firm_country_name" in df.columns:
        df["awarded_firm_country_name"] = df["awarded_firm_country_name"].astype(str).str.strip().str.title()
    
    return df

# Carga de datos (se realiza una sola vez)
data = load_data()

# -----------------------------
# Página Principal
# -----------------------------
def pagina_principal():
    st.title("Página Principal")
    st.write("Bienvenido a la aplicación de **UY_PROCUREMENT**.")
    st.write("""
    Aquí encontrarás un resumen general de la información disponible.
    
    Navega a:
    - **Tablas** para explorar los datos en formato tabular.
    - **Visualizaciones** para analizar gráficos y tendencias.
    """)

# -----------------------------
# Página de Tablas con subpáginas: Raw Data y Agregada
# -----------------------------
def pagina_tablas():
    st.title("Tablas")
    st.write("Visualización de los datos de la Base de Datos.")
    
    # -----------------------------
    # Filtros en el Sidebar para la pestaña Raw Data
    # -----------------------------
    st.sidebar.markdown("### Filtros para Raw Data")
    
    # Filtro para 'contract_type'
    if "contract_type" in data.columns:
        contract_type_values = sorted(data["contract_type"].dropna().unique())
        contract_type_filter = st.sidebar.multiselect("Selecciona Contract Type", contract_type_values)
    else:
        contract_type_filter = []
        
    # Filtro para 'status'
    if "status" in data.columns:
        status_values = sorted(data["status"].dropna().unique())
        status_filter = st.sidebar.multiselect("Selecciona Status", status_values)
    else:
        status_filter = []
    
    # Filtro para 'operation_type_name'
    if "operation_type_name" in data.columns:
        operation_type_name_values = sorted(data["operation_type_name"].dropna().unique())
        operation_type_name_filter = st.sidebar.multiselect("Selecciona Operation Type Name", operation_type_name_values)
    else:
        operation_type_name_filter = []
    
    # Filtro para 'operation_country_name'
    if "operation_country_name" in data.columns:
        operation_country_name_values = sorted(data["operation_country_name"].dropna().unique())
        operation_country_name_filter = st.sidebar.multiselect("Selecciona Operation Country Name", operation_country_name_values)
    else:
        operation_country_name_filter = []
    
    # Filtro para 'economic_sector_name'
    if "economic_sector_name" in data.columns:
        economic_sector_values = sorted(data["economic_sector_name"].dropna().unique())
        economic_sector_filter = st.sidebar.multiselect("Selecciona Economic Sector Name", economic_sector_values)
    else:
        economic_sector_filter = []
    
    # Filtro para 'procurement_type'
    if "procurement_type" in data.columns:
        procurement_type_values = sorted(data["procurement_type"].dropna().unique())
        procurement_type_filter = st.sidebar.multiselect("Selecciona Procurement Type", procurement_type_values)
    else:
        procurement_type_filter = []
    
    # Filtro para 'awarded_firm_country_name'
    if "awarded_firm_country_name" in data.columns:
        awarded_firm_country_name_values = sorted(data["awarded_firm_country_name"].dropna().unique())
        awarded_firm_country_name_filter = st.sidebar.multiselect("Selecciona Awarded Firm Country Name", awarded_firm_country_name_values)
    else:
        awarded_firm_country_name_filter = []
    
    # -----------------------------
    # Aplicar filtros al DataFrame para la pestaña Raw Data
    # -----------------------------
    filtered_data = data.copy()
    if contract_type_filter:
        filtered_data = filtered_data[filtered_data["contract_type"].isin(contract_type_filter)]
    if status_filter:
        filtered_data = filtered_data[filtered_data["status"].isin(status_filter)]
    if operation_type_name_filter:
        filtered_data = filtered_data[filtered_data["operation_type_name"].isin(operation_type_name_filter)]
    if operation_country_name_filter:
        filtered_data = filtered_data[filtered_data["operation_country_name"].isin(operation_country_name_filter)]
    if economic_sector_filter and "economic_sector_name" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["economic_sector_name"].isin(economic_sector_filter)]
    if procurement_type_filter and "procurement_type" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["procurement_type"].isin(procurement_type_filter)]
    if awarded_firm_country_name_filter and "awarded_firm_country_name" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["awarded_firm_country_name"].isin(awarded_firm_country_name_filter)]
    
    # -----------------------------
    # Crear pestañas: Raw Data y Agregada
    # -----------------------------
    tabs = st.tabs(["Raw Data", "Agregada"])
    
    # Pestaña Raw Data: Muestra la base de datos filtrada
    with tabs[0]:
        st.header("Raw Data")
        st.write("Datos en crudo de la base de datos con los filtros aplicados:")
        st.dataframe(filtered_data)
    
    # Pestaña Agregada: Muestra varias tablas agregadas de forma ordenada
    with tabs[1]:
        st.header("Agregada")
        st.write("Tablas agregadas y resúmenes:")
        
        # 1. Resumen por Tipo de Contrato (conteo y porcentaje)
        st.subheader("1. Resumen por Tipo de Contrato")
        if "contract_type" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_tipo = filtered_data.groupby("contract_type")["contract_id"].count().reset_index()
            df_tipo = df_tipo.rename(columns={"contract_id": "Cantidad"})
            total = df_tipo["Cantidad"].sum()
            df_tipo["Porcentaje (%)"] = (df_tipo["Cantidad"] / total * 100).round(2)
            st.dataframe(df_tipo)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        # 2. Resumen por Estado
        st.subheader("2. Resumen por Estado")
        if "status" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_estado = filtered_data.groupby("status")["contract_id"].count().reset_index()
            df_estado = df_estado.rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_estado)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        # 3. Distribución Geográfica
        st.subheader("3. Distribución Geográfica")
        # a) Por País de Operación
        if "operation_country_name" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_op = filtered_data.groupby("operation_country_name")["contract_id"].count().reset_index()
            df_op = df_op.rename(columns={"contract_id": "Cantidad"})
            st.write("**Por País de Operación**")
            st.dataframe(df_op)
        else:
            st.write("No se encontraron las columnas necesarias para País de Operación.")
        # b) Por País de la Firma Adjudicataria
        if "awarded_firm_country_name" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_aw = filtered_data.groupby("awarded_firm_country_name")["contract_id"].count().reset_index()
            df_aw = df_aw.rename(columns={"contract_id": "Cantidad"})
            st.write("**Por País de la Firma Adjudicataria**")
            st.dataframe(df_aw)
        else:
            st.write("No se encontraron las columnas necesarias para País de la Firma Adjudicataria.")
        
        # 4. Tendencia Temporal de Contratos
        st.subheader("4. Tendencia Temporal de Contratos")
        if "contract_year" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_tend = filtered_data.groupby("contract_year")["contract_id"].count().reset_index()
            df_tend = df_tend.rename(columns={"contract_id": "Cantidad"})
            df_tend = df_tend.sort_values("contract_year")
            st.dataframe(df_tend)
        elif "signature_date" in filtered_data.columns and "contract_id" in filtered_data.columns:
            filtered_data["signature_year"] = pd.to_datetime(filtered_data["signature_date"], errors="coerce").dt.year
            df_tend = filtered_data.groupby("signature_year")["contract_id"].count().reset_index()
            df_tend = df_tend.rename(columns={"contract_id": "Cantidad"})
            df_tend = df_tend.sort_values("signature_year")
            st.dataframe(df_tend)
        else:
            st.write("No se encontraron las columnas necesarias para este análisis.")
        
        # 5. Operaciones por Tipo
        st.subheader("5. Operaciones por Tipo")
        if "operation_type_name" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_op_type = filtered_data.groupby("operation_type_name")["contract_id"].count().reset_index()
            df_op_type = df_op_type.rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_op_type)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        # 6. Duración de Contratos
        st.subheader("6. Duración de Contratos")
        if "start_date" in filtered_data.columns and "stop_date" in filtered_data.columns:
            # Convertir a datetime y calcular la duración en días
            filtered_data["start_date"] = pd.to_datetime(filtered_data["start_date"], errors="coerce")
            filtered_data["stop_date"] = pd.to_datetime(filtered_data["stop_date"], errors="coerce")
            filtered_data["duration_days"] = (filtered_data["stop_date"] - filtered_data["start_date"]).dt.days
            if "contract_type" in filtered_data.columns:
                df_duration = filtered_data.groupby("contract_type")["duration_days"].agg(["min", "max", "mean"]).reset_index()
                df_duration = df_duration.rename(columns={"min": "Mínimo (días)",
                                                              "max": "Máximo (días)",
                                                              "mean": "Promedio (días)"})
                st.dataframe(df_duration)
            else:
                st.write("La columna 'contract_type' no se encuentra para agrupar la duración.")
        else:
            st.write("No se encontraron las columnas necesarias para calcular la duración de contratos.")
        
        # 7. Resumen por Sector Económico y Tipo de Adquisición
        st.subheader("7. Resumen por Sector Económico y Tipo de Adquisición")
        if ("economic_sector_name" in filtered_data.columns and 
            "procurement_type" in filtered_data.columns and 
            "contract_id" in filtered_data.columns):
            df_sector = filtered_data.groupby(["economic_sector_name", "procurement_type"])["contract_id"].count().reset_index()
            df_sector = df_sector.rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_sector)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        # 8. Tabla Combinada Multidimensional (Contract Type y Status)
        st.subheader("8. Tabla Combinada Multidimensional (Contract Type y Status)")
        if ("contract_type" in filtered_data.columns and 
            "status" in filtered_data.columns and 
            "contract_id" in filtered_data.columns):
            df_multi = filtered_data.groupby(["contract_type", "status"])["contract_id"].count().reset_index()
            df_multi = df_multi.rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_multi)
        else:
            st.write("No se encontraron las columnas necesarias para esta tabla combinada.")

# -----------------------------
# Página de Visualizaciones con subpáginas
# -----------------------------
def pagina_visualizaciones():
    st.title("Visualizaciones")
    tabs = st.tabs(["Descriptivo"])  # Se pueden agregar más pestañas si se requiere
    
    with tabs[0]:
        st.header("Descriptivo")
        st.write("Frecuencia de Contratos Ganados por País")
        
        # Para calcular la frecuencia, primero se excluyen los registros donde
        # awarded_firm_country_name y operation_country_name sean iguales.
        if "operation_country_name" in data.columns:
            data_filtrado = data[data["awarded_firm_country_name"] != data["operation_country_name"]]
        else:
            data_filtrado = data.copy()
        
        # Agrupar y contar la frecuencia de países en awarded_firm_country_name
        df_freq = data_filtrado["awarded_firm_country_name"].value_counts().reset_index()
        df_freq.columns = ["Pais", "Frecuencia"]
        
        # Seleccionar el top 15 países (según mayor frecuencia)
        df_top15 = df_freq.sort_values("Frecuencia", ascending=False).head(15)
        # Para que en el gráfico horizontal la barra de mayor frecuencia aparezca en la parte superior,
        # se ordena de forma ascendente
        df_top15 = df_top15.sort_values("Frecuencia", ascending=True)
        
        # Asignar colores: si el país es "Uruguay" se usa #669bbc, para los demás #003049
        colors = ["#669bbc" if pais == "Uruguay" else "#003049" for pais in df_top15["Pais"]]
        
        # Crear gráfico de barras horizontal con Plotly
        fig = px.bar(
            df_top15,
            x="Frecuencia",
            y="Pais",
            orientation="h",
            title="Frecuencia de Contratos Ganados por País (Top 15)",
            labels={"Frecuencia": "Frecuencia", "Pais": "País"}
        )
        # Actualizar colores de las barras
        fig.update_traces(marker_color=colors)
        
        # Calcular una altura dinámica: 40 píxeles por cada barra, mínimo 600 píxeles
        altura = max(600, len(df_top15) * 40)
        fig.update_layout(height=altura)
        
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Función principal de la aplicación
# -----------------------------
def main():
    st.sidebar.title("Navegación")
    opcion_pagina = st.sidebar.radio(
        "Selecciona una página:",
        ("Página Principal", "Tablas", "Visualizaciones")
    )
    
    if opcion_pagina == "Página Principal":
        pagina_principal()
    elif opcion_pagina == "Tablas":
        pagina_tablas()
    elif opcion_pagina == "Visualizaciones":
        pagina_visualizaciones()

if __name__ == "__main__":
    main()
