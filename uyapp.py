import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Función para cargar y normalizar la base de datos
@st.cache_data
def load_data():
    df = pd.read_parquet("uy_procurements.parquet")
    if "awarded_firm_country_name" in df.columns:
        df["awarded_firm_country_name"] = df["awarded_firm_country_name"].astype(str).str.strip().str.title()
    if "operation_country_name" in df.columns:
        df["operation_country_name"] = df["operation_country_name"].astype(str).str.strip().str.title()
    return df

data = load_data()

def pagina_principal():
    st.title("Página Principal")
    st.write("Bienvenido a la aplicación de **UY_PROCUREMENT**.")
    st.write("""
    Aquí encontrarás un resumen general de la información disponible.
    Navega a:
    - **Tablas** para explorar los datos en formato tabular.
    - **Visualizaciones** para analizar gráficos y tendencias.
    """)

def pagina_tablas():
    st.title("Tablas")
    st.write("Visualización de los datos de la Base de Datos.")
    st.sidebar.markdown("### Filtros para Raw Data")
    contract_type_filter = st.sidebar.multiselect("Selecciona Contract Type", sorted(data["contract_type"].dropna().unique())) if "contract_type" in data.columns else []
    status_filter = st.sidebar.multiselect("Selecciona Status", sorted(data["status"].dropna().unique())) if "status" in data.columns else []
    operation_type_name_filter = st.sidebar.multiselect("Selecciona Operation Type Name", sorted(data["operation_type_name"].dropna().unique())) if "operation_type_name" in data.columns else []
    operation_country_name_filter = st.sidebar.multiselect("Selecciona Operation Country Name", sorted(data["operation_country_name"].dropna().unique())) if "operation_country_name" in data.columns else []
    economic_sector_filter = st.sidebar.multiselect("Selecciona Economic Sector Name", sorted(data["economic_sector_name"].dropna().unique())) if "economic_sector_name" in data.columns else []
    procurement_type_filter = st.sidebar.multiselect("Selecciona Procurement Type", sorted(data["procurement_type"].dropna().unique())) if "procurement_type" in data.columns else []
    awarded_firm_country_name_filter = st.sidebar.multiselect("Selecciona Awarded Firm Country Name", sorted(data["awarded_firm_country_name"].dropna().unique())) if "awarded_firm_country_name" in data.columns else []
    
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
    
    tabs = st.tabs(["Raw Data", "Agregada"])
    
    with tabs[0]:
        st.header("Raw Data")
        st.write("Datos en crudo de la base de datos con los filtros aplicados:")
        st.dataframe(filtered_data)
    
    with tabs[1]:
        st.header("Agregada")
        st.subheader("1. Resumen por Tipo de Contrato")
        if "contract_type" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_tipo = filtered_data.groupby("contract_type")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            total = df_tipo["Cantidad"].sum()
            df_tipo["Porcentaje (%)"] = (df_tipo["Cantidad"] / total * 100).round(2)
            st.dataframe(df_tipo)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        st.subheader("2. Resumen por Estado")
        if "status" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_estado = filtered_data.groupby("status")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_estado)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        st.subheader("3. Distribución Geográfica")
        if "operation_country_name" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_op = filtered_data.groupby("operation_country_name")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            st.write("**Por País de Operación**")
            st.dataframe(df_op)
        else:
            st.write("No se encontraron las columnas necesarias para País de Operación.")
        if "awarded_firm_country_name" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_aw = filtered_data.groupby("awarded_firm_country_name")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            st.write("**Por País de la Firma Adjudicataria**")
            st.dataframe(df_aw)
        else:
            st.write("No se encontraron las columnas necesarias para País de la Firma Adjudicataria.")
        
        st.subheader("4. Tendencia Temporal de Contratos")
        if "contract_year" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_tend = filtered_data.groupby("contract_year")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            df_tend = df_tend.sort_values("contract_year")
            st.dataframe(df_tend)
        elif "signature_date" in filtered_data.columns and "contract_id" in filtered_data.columns:
            filtered_data["signature_year"] = pd.to_datetime(filtered_data["signature_date"], errors="coerce").dt.year
            df_tend = filtered_data.groupby("signature_year")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            df_tend = df_tend.sort_values("signature_year")
            st.dataframe(df_tend)
        else:
            st.write("No se encontraron las columnas necesarias para este análisis.")
        
        st.subheader("5. Operaciones por Tipo")
        if "operation_type_name" in filtered_data.columns and "contract_id" in filtered_data.columns:
            df_op_type = filtered_data.groupby("operation_type_name")["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_op_type)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        st.subheader("6. Duración de Contratos")
        if "start_date" in filtered_data.columns and "stop_date" in filtered_data.columns:
            filtered_data["start_date"] = pd.to_datetime(filtered_data["start_date"], errors="coerce")
            filtered_data["stop_date"] = pd.to_datetime(filtered_data["stop_date"], errors="coerce")
            filtered_data["duration_days"] = (filtered_data["stop_date"] - filtered_data["start_date"]).dt.days
            if "contract_type" in filtered_data.columns:
                df_duration = filtered_data.groupby("contract_type")["duration_days"].agg(["min", "max", "mean"]).reset_index()
                df_duration = df_duration.rename(columns={"min": "Mínimo (días)", "max": "Máximo (días)", "mean": "Promedio (días)"})
                st.dataframe(df_duration)
            else:
                st.write("La columna 'contract_type' no se encuentra para agrupar la duración.")
        else:
            st.write("No se encontraron las columnas necesarias para calcular la duración de contratos.")
        
        st.subheader("7. Resumen por Sector Económico y Tipo de Adquisición")
        if ("economic_sector_name" in filtered_data.columns and "procurement_type" in filtered_data.columns and "contract_id" in filtered_data.columns):
            df_sector = filtered_data.groupby(["economic_sector_name", "procurement_type"])["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_sector)
        else:
            st.write("No se encontraron las columnas necesarias para este resumen.")
        
        st.subheader("8. Tabla Combinada Multidimensional (Contract Type y Status)")
        if ("contract_type" in filtered_data.columns and "status" in filtered_data.columns and "contract_id" in filtered_data.columns):
            df_multi = filtered_data.groupby(["contract_type", "status"])["contract_id"].count().reset_index().rename(columns={"contract_id": "Cantidad"})
            st.dataframe(df_multi)
        else:
            st.write("No se encontraron las columnas necesarias para esta tabla combinada.")

def pagina_visualizaciones():
    st.title("Visualizaciones")
    data_vis = data.copy()
    if "contract_type" in data_vis.columns:
        ct_values = sorted(data_vis["contract_type"].dropna().unique())
        ct_filter = st.sidebar.multiselect("Filt. Contract Type", ct_values)
        if ct_filter:
            data_vis = data_vis[data_vis["contract_type"].isin(ct_filter)]
    excluir_global = st.sidebar.checkbox("Excluir AWD=OP", value=True)
    tabs = st.tabs(["Descriptivo", "Tipo de Operación"])
    
    with tabs[0]:
        st.header("Descriptivo")
        st.write("Frecuencia de Contratos Ganados por País")
        if excluir_global and "operation_country_name" in data_vis.columns:
            data_filtrado = data_vis[data_vis["awarded_firm_country_name"] != data_vis["operation_country_name"]]
        else:
            data_filtrado = data_vis.copy()
        df_freq = data_filtrado["awarded_firm_country_name"].value_counts().reset_index()
        df_freq.columns = ["Pais", "Frecuencia"]
        df_top15 = df_freq.sort_values("Frecuencia", ascending=False).head(15).sort_values("Frecuencia", ascending=True)
        colors = ["#669bbc" if pais == "Uruguay" else "#003049" for pais in df_top15["Pais"]]
        fig = px.bar(
            df_top15,
            x="Frecuencia",
            y="Pais",
            orientation="h",
            title="Frecuencia de Contratos Ganados por País (Top 15)",
            labels={"Frecuencia": "Frecuencia", "Pais": "País"},
            text="Frecuencia"
        )
        fig.update_traces(marker_color=colors, textposition='outside')
        altura = max(600, len(df_top15) * 40)
        fig.update_layout(height=altura)
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.header("Tipo de Operación")
        st.write("Donut Chart en subgráficos por cada valor único de Operation Type, mostrando el % de AWD (Top 10, con 'Otros')")
        if "operation_type_name" in data_vis.columns:
            op_types = list(data_vis["operation_type_name"].dropna().unique())
            n_ops = len(op_types)
            if n_ops == 0:
                st.write("No se encontraron Operation Type en la data.")
            else:
                cols = 2
                rows = math.ceil(n_ops / cols)
                subplot_titles = op_types
                fig_sub = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles, specs=[[{'type':'domain'}]*cols for _ in range(rows)])
                non_uruguay_palette = ["#F28E2B", "#4E79A7", "#59A14F", "#E15759", "#EDC948",
                                       "#B07AA1", "#76B7B2", "#FF9DA7", "#9C755F", "#BAB0AC"]
                for idx, op in enumerate(op_types):
                    r = idx // cols + 1
                    c = idx % cols + 1
                    df_op = data_vis[data_vis["operation_type_name"] == op].copy()
                    if excluir_global and "operation_country_name" in df_op.columns:
                        df_op = df_op[df_op["awarded_firm_country_name"] != df_op["operation_country_name"]]
                    df_awd = df_op["awarded_firm_country_name"].value_counts().reset_index()
                    df_awd.columns = ["Pais", "Frecuencia"]
                    df_awd = df_awd.sort_values("Frecuencia", ascending=False)
                    if "Uruguay" in df_awd["Pais"].values:
                        row_uruguay = df_awd[df_awd["Pais"] == "Uruguay"]
                        df_others = df_awd[df_awd["Pais"] != "Uruguay"]
                        top_others = df_others.head(9)
                        selected = pd.concat([row_uruguay, top_others])
                    else:
                        selected = df_awd.head(10)
                    selected_countries = set(selected["Pais"])
                    remaining = df_awd[~df_awd["Pais"].isin(selected_countries)]
                    if not remaining.empty:
                        otros_frequency = remaining["Frecuencia"].sum()
                        df_otros = pd.DataFrame({"Pais": ["Otros"], "Frecuencia": [otros_frequency]})
                        final_df = pd.concat([selected, df_otros], ignore_index=True)
                    else:
                        final_df = selected.copy()
                    total_final = final_df["Frecuencia"].sum()
                    final_df["Porcentaje"] = (final_df["Frecuencia"] / total_final * 100).round(2)
                    donut_colors = []
                    palette_index = 0
                    for pais in final_df["Pais"]:
                        if pais == "Uruguay":
                            donut_colors.append("#669bbc")
                        else:
                            donut_colors.append(non_uruguay_palette[palette_index % len(non_uruguay_palette)])
                            palette_index += 1
                    trace = go.Pie(labels=final_df["Pais"],
                                   values=final_df["Frecuencia"],
                                   hole=0.4,
                                   textinfo="label+percent",
                                   marker=dict(colors=donut_colors),
                                   showlegend=False)
                    fig_sub.add_trace(trace, row=r, col=c)
                fig_sub.update_layout(title_text="Distribución de AWD por Operation Type (Top 10 + Otros)", height=400*rows)
                st.plotly_chart(fig_sub, use_container_width=True)
        else:
            st.write("La columna 'operation_type_name' no se encuentra en la data.")

def main():
    st.sidebar.title("Navegación")
    opcion_pagina = st.sidebar.radio("Selecciona una página:", ("Página Principal", "Tablas", "Visualizaciones"))
    if opcion_pagina == "Página Principal":
        pagina_principal()
    elif opcion_pagina == "Tablas":
        pagina_tablas()
    elif opcion_pagina == "Visualizaciones":
        pagina_visualizaciones()

if __name__ == "__main__":
    main()
