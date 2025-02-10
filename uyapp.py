import math
import streamlit as st
import pandas as pd
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

# Página Principal
def pagina_principal():
    st.title("Página Principal")
    st.write("Bienvenido a la aplicación de **UY_PROCUREMENT**.")
    st.write("""
Esta aplicación permite explorar los contratos de acuerdo a su ámbito:

- **Uruguay Nacional:** Contratos con operaciones en Uruguay.
- **Uruguay en el Mundo:** Contratos en los que empresas uruguayas operan en el exterior.
- **Tabla Pivot:** Tabla resumen por País de la Operación con indicadores clave.
""")

# Página Uruguay Nacional
def pagina_uruguay_nacional():
    st.title("Uruguay Nacional")
    
    # Filtrar contratos con operación en Uruguay
    data_nacional = data.copy()
    if "operation_country_name" in data_nacional.columns:
        data_nacional = data_nacional[data_nacional["operation_country_name"] == "Uruguay"]
    
    # Filtro de tiempo por año de contrato
    if "contract_year" in data_nacional.columns:
        min_year = int(data_nacional["contract_year"].min())
        max_year = int(data_nacional["contract_year"].max())
        year_range = st.sidebar.slider("Año de Contrato", min_value=min_year, max_value=max_year,
                                       value=(min_year, max_year), step=1)
        data_nacional = data_nacional[(data_nacional["contract_year"] >= year_range[0]) & 
                                      (data_nacional["contract_year"] <= year_range[1])]
    
    # Filtros adicionales: Tipo de Contrato, Tipo de Operación y Sector Económico
    if "contract_type" in data_nacional.columns:
        contract_types = sorted(data_nacional["contract_type"].dropna().unique())
        selected_contract_type = st.sidebar.selectbox("Tipo de Contrato", ["Todos"] + contract_types)
        if selected_contract_type != "Todos":
            data_nacional = data_nacional[data_nacional["contract_type"] == selected_contract_type]
    if "operation_type_name" in data_nacional.columns:
        op_types = sorted(data_nacional["operation_type_name"].dropna().unique())
        selected_op_type = st.sidebar.selectbox("Tipo de Operación", ["Todos"] + op_types)
        if selected_op_type != "Todos":
            data_nacional = data_nacional[data_nacional["operation_type_name"] == selected_op_type]
    if "economic_sector_name" in data_nacional.columns:
        sectors = sorted(data_nacional["economic_sector_name"].dropna().unique())
        selected_sector = st.sidebar.selectbox("Sector Económico", ["Todos"] + sectors)
        if selected_sector != "Todos":
            data_nacional = data_nacional[data_nacional["economic_sector_name"] == selected_sector]
    
    st.write("Mostrando contratos en Uruguay (Operación Nacional).")
    
    total_nacional = data_nacional.shape[0]
    local_awarded = data_nacional[data_nacional["awarded_firm_country_name"] == "Uruguay"].shape[0]
    percentage_local = (local_awarded / total_nacional * 100) if total_nacional > 0 else 0
    
    # Gráfico de montos: Suma de idb_amount por año con color "gray" y sin gridlines
    if "contract_year" in data_nacional.columns and "idb_amount" in data_nacional.columns:
        df_bar = data_nacional.groupby("contract_year")["idb_amount"].sum().reset_index()
        fig_bar = px.bar(
            df_bar,
            x="contract_year",
            y="idb_amount",
            labels={"contract_year": "Año", "idb_amount": "Monto IDB"}
        )
        fig_bar.update_traces(marker_color="gray")
        fig_bar.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
    else:
        fig_bar = None

    col_left, col_right = st.columns([0.3, 0.7])
    with col_left:
        st.markdown(f"""
<div style="max-width: 150px; background-color: gray; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
    <h3 style="color: white; font-size: 20px; font-weight: bold;">Contratos</h3>
    <h1 style="color: white; font-size: 28px;">{total_nacional:,}</h1>
</div>
""", unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
<div style="max-width: 200px;">
    <h3 style="color: white; margin-bottom: 10px; font-size: 16px; font-weight: bold;">% Locales Ganados</h3>
</div>
""", unsafe_allow_html=True)
        donut_data = pd.DataFrame({
            "Categoría": ["Locales", "No Locales"],
            "Valor": [percentage_local, 100 - percentage_local]
        })
        donut_fig = px.pie(
            donut_data,
            values="Valor",
            names="Categoría",
            hole=0.7,
            color_discrete_map={"Locales": "#669bbc", "No Locales": "#cccccc"}
        )
        donut_fig.update_traces(textinfo="none", hoverinfo="label+percent")
        donut_fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            width=250,
            annotations=[dict(text=f"{percentage_local:.1f}%", x=0.5, y=0.5,
                              font_size=28, font_color="white", showarrow=False)]
        )
        st.plotly_chart(donut_fig, use_container_width=False)
    
    with col_right:
        if "contract_year" in data_nacional.columns:
            df_total = data_nacional.groupby("contract_year").size().reset_index(name="Total Contratos")
            df_local = data_nacional[data_nacional["awarded_firm_country_name"] == "Uruguay"]\
                        .groupby("contract_year").size().reset_index(name="Contratos Uruguay")
            fig_freq = go.Figure()
            fig_freq.add_trace(go.Bar(
                x=df_total["contract_year"],
                y=df_total["Total Contratos"],
                name="Total Contratos",
                marker_color="#003049"
            ))
            fig_freq.add_trace(go.Scatter(
                x=df_local["contract_year"],
                y=df_local["Contratos Uruguay"],
                name="Contratos Uruguay",
                mode="lines+markers",
                line=dict(color="#669bbc"),
                yaxis="y2"
            ))
            fig_freq.update_layout(
                title=dict(text="Frecuencia de Contratos por Año", x=0.5, pad=dict(b=40)),
                legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5),
                xaxis_title="",
                height=220,
                margin=dict(l=10, r=10, t=60, b=10),
                yaxis=dict(title="Total Contratos", side="left", showgrid=False),
                yaxis2=dict(title="Contratos Uruguay", overlaying="y", side="right", showgrid=False),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.write("No se encontró información para el gráfico de frecuencia.")
        
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No se encontró la información necesaria para el gráfico de montos.")

# Página Uruguay en el Mundo
def pagina_uruguay_en_el_mundo():
    st.title("Uruguay en el Mundo")
    
    data_mundial = data.copy()
    if "operation_country_name" in data_mundial.columns:
        data_mundial = data_mundial[data_mundial["operation_country_name"] != "Uruguay"]
    
    if "contract_year" in data_mundial.columns:
        min_year = int(data_mundial["contract_year"].min())
        max_year = int(data_mundial["contract_year"].max())
        year_range = st.sidebar.slider("Año de Contrato", min_value=min_year, max_value=max_year,
                                       value=(min_year, max_year), step=1)
        data_mundial = data_mundial[(data_mundial["contract_year"] >= year_range[0]) & 
                                    (data_mundial["contract_year"] <= year_range[1])]
    
    if "contract_type" in data_mundial.columns:
        contract_types = sorted(data_mundial["contract_type"].dropna().unique())
        selected_contract_type = st.sidebar.selectbox("Tipo de Contrato", ["Todos"] + contract_types)
        if selected_contract_type != "Todos":
            data_mundial = data_mundial[data_mundial["contract_type"] == selected_contract_type]
    if "operation_type_name" in data_mundial.columns:
        op_types = sorted(data_mundial["operation_type_name"].dropna().unique())
        selected_op_type = st.sidebar.selectbox("Tipo de Operación", ["Todos"] + op_types)
        if selected_op_type != "Todos":
            data_mundial = data_mundial[data_mundial["operation_type_name"] == selected_op_type]
    if "economic_sector_name" in data_mundial.columns:
        sectors = sorted(data_mundial["economic_sector_name"].dropna().unique())
        selected_sector = st.sidebar.selectbox("Sector Económico", ["Todos"] + sectors)
        if selected_sector != "Todos":
            data_mundial = data_mundial[data_mundial["economic_sector_name"] == selected_sector]
    
    if "operation_country_name" in data_mundial.columns:
        unique_countries = sorted(data_mundial["operation_country_name"].dropna().unique())
        op_country_options = ["Todos", "Mercosur"] + unique_countries
        selected_op_country = st.sidebar.selectbox("País de Operación", op_country_options)
        if selected_op_country != "Todos":
            if selected_op_country == "Mercosur":
                mercosur_countries = ["Argentina", "Bolivia", "Brazil", "Paraguay"]
                data_mundial = data_mundial[data_mundial["operation_country_name"].isin(mercosur_countries)]
            else:
                data_mundial = data_mundial[data_mundial["operation_country_name"] == selected_op_country]
    
    eliminar_iguales = st.sidebar.checkbox("Eliminar observaciones donde 'Operación' y 'Adjudicatario' sean iguales", value=False)
    if eliminar_iguales:
        data_mundial = data_mundial[data_mundial["operation_country_name"] != data_mundial["awarded_firm_country_name"]]
    
    st.write("Mostrando contratos en otros países, donde se evalúa la participación de empresas uruguayas.")
    
    total_mundial = data_mundial.shape[0]
    total_mundial_str = f"{total_mundial:,}"
    
    uruguayan_contracts = data_mundial[data_mundial["awarded_firm_country_name"] == "Uruguay"].shape[0]
    percentage_uruguayan = (uruguayan_contracts / total_mundial * 100) if total_mundial > 0 else 0
    
    if "contract_year" in data_mundial.columns and "idb_amount" in data_mundial.columns:
        df_bar = data_mundial.groupby("contract_year")["idb_amount"].sum().reset_index()
        fig_bar = px.bar(
            df_bar,
            x="contract_year",
            y="idb_amount",
            labels={"contract_year": "Año", "idb_amount": "Monto IDB"}
        )
        fig_bar.update_traces(marker_color="gray")
        fig_bar.update_layout(width=600, height=250, margin=dict(l=10, r=10, t=10, b=10),
                              xaxis=dict(showgrid=False),
                              yaxis=dict(showgrid=False))
    else:
        fig_bar = None

    col_left, col_right = st.columns([0.3, 0.7])
    with col_left:
        st.markdown(f"""
<div style="max-width: 150px; background-color: gray; padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
    <h3 style="color: white; font-size: 20px; font-weight: bold;">Contratos</h3>
    <h1 style="color: white; font-size: 28px;">{total_mundial_str}</h1>
</div>
""", unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
<div style="max-width: 200px;">
    <h3 style="color: white; margin-bottom: 10px; font-size: 16px; font-weight: bold;">% Empresa Uruguaya</h3>
</div>
""", unsafe_allow_html=True)
        donut_data = pd.DataFrame({
            "Categoría": ["Uruguay", "Otros"],
            "Valor": [percentage_uruguayan, 100 - percentage_uruguayan]
        })
        # Se asignan los colores solicitados: #669bbc para Uruguay y #003049 para Otros
        donut_fig = px.pie(
            donut_data,
            values="Valor",
            names="Categoría",
            hole=0.7,
            color_discrete_map={"Uruguay": "#669bbc", "Otros": "#003049"}
        )
        donut_fig.update_traces(textinfo="none", hoverinfo="label+percent")
        donut_fig.update_layout(margin=dict(l=10, r=10, t=10, b=10),
                                height=200,
                                width=250,
                                annotations=[dict(text=f"{percentage_uruguayan:.1f}%", x=0.5, y=0.5,
                                                  font_size=28, font_color="white", showarrow=False)])
        st.plotly_chart(donut_fig, use_container_width=False)
    
    with col_right:
        if "contract_year" in data_mundial.columns:
            df_total = data_mundial.groupby("contract_year").size().reset_index(name="Total Contratos")
            df_uruguayan = data_mundial[data_mundial["awarded_firm_country_name"] == "Uruguay"]\
                           .groupby("contract_year").size().reset_index(name="Contratos Uruguay")
            fig_freq = go.Figure()
            fig_freq.add_trace(go.Bar(
                x=df_total["contract_year"],
                y=df_total["Total Contratos"],
                name="Total Contratos",
                marker_color="#003049"
            ))
            fig_freq.add_trace(go.Scatter(
                x=df_uruguayan["contract_year"],
                y=df_uruguayan["Contratos Uruguay"],
                name="Contratos Uruguay",
                mode="lines+markers",
                line=dict(color="#669bbc"),
                yaxis="y2"
            ))
            fig_freq.update_layout(
                title=dict(text="Frecuencia de Contratos por Año", x=0.5, pad=dict(b=40)),
                legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5),
                xaxis_title="",
                height=260,  # Altura incrementada
                margin=dict(l=10, r=10, t=60, b=10),
                yaxis=dict(title="Total Contratos", side="left", showgrid=False),
                yaxis2=dict(title="Contratos Uruguay", overlaying="y", side="right", showgrid=False),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.write("No se encontró información para el gráfico de frecuencia.")
        
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No se encontró la información necesaria para el gráfico de montos.")

# Página Tabla Pivot (Resumen por País de la Operación)
def tabla_pivot():
    st.title("Tabla Pivot")
    df = data.copy()
    if "contract_type" in df.columns:
        contract_types = sorted(df["contract_type"].dropna().unique())
        selected_contract_type = st.sidebar.selectbox("Tipo de Contrato", ["Todos"] + contract_types)
        if selected_contract_type != "Todos":
            df = df[df["contract_type"] == selected_contract_type]
    if "status" in df.columns:
        statuses = sorted(df["status"].dropna().unique())
        selected_status = st.sidebar.selectbox("Estado", ["Todos"] + statuses)
        if selected_status != "Todos":
            df = df[df["status"] == selected_status]
    if "operation_type_name" in df.columns:
        op_types = sorted(df["operation_type_name"].dropna().unique())
        selected_op_type = st.sidebar.selectbox("Tipo de Operación", ["Todos"] + op_types)
        if selected_op_type != "Todos":
            df = df[df["operation_type_name"] == selected_op_type]
    if "economic_sector_name" in df.columns:
        sectors = sorted(df["economic_sector_name"].dropna().unique())
        selected_sector = st.sidebar.selectbox("Sector Económico", ["Todos"] + sectors)
        if selected_sector != "Todos":
            df = df[df["economic_sector_name"] == selected_sector]
    
    summary = df.groupby("operation_country_name").apply(lambda g: pd.Series({
         "Total Contratos": g.shape[0],
         "Contratos Ganados por Empresas Uruguayas": (g["awarded_firm_country_name"] == "Uruguay").sum(),
         "Monto Total Adjudicado (USD)": g["idb_amount"].sum(),
         "Monto a Uruguay (USD)": g.loc[g["awarded_firm_country_name"] == "Uruguay", "idb_amount"].sum()
    })).reset_index()
    
    summary["% Contratos a Empresas UY"] = (summary["Contratos Ganados por Empresas Uruguayas"] / summary["Total Contratos"] * 100).round(2)
    summary["% Monto a Uruguay"] = (summary["Monto a Uruguay (USD)"] / summary["Monto Total Adjudicado (USD)"] * 100).round(2)
    
    total_contratos = summary["Total Contratos"].sum()
    total_contratos_uy = summary["Contratos Ganados por Empresas Uruguayas"].sum()
    total_monto_total = summary["Monto Total Adjudicado (USD)"].sum()
    total_monto_uy = summary["Monto a Uruguay (USD)"].sum()
    pct_contratos = round((total_contratos_uy / total_contratos * 100),2) if total_contratos > 0 else 0
    pct_monto = round((total_monto_uy / total_monto_total * 100),2) if total_monto_total > 0 else 0
    
    summary["Monto Total Adjudicado (USD)"] = summary["Monto Total Adjudicado (USD)"].apply(lambda x: f"${x:,.0f}")
    summary["Monto a Uruguay (USD)"] = summary["Monto a Uruguay (USD)"].apply(lambda x: f"${x:,.0f}")
    summary["% Contratos a Empresas UY"] = summary["% Contratos a Empresas UY"].astype(str) + "%"
    summary["% Monto a Uruguay"] = summary["% Monto a Uruguay"].astype(str) + "%"
    
    summary = summary.rename(columns={"operation_country_name": "País de la Operación"})
    summary = summary[["País de la Operación", "Total Contratos", "Contratos Ganados por Empresas Uruguayas",
                       "% Contratos a Empresas UY", "Monto Total Adjudicado (USD)", "Monto a Uruguay (USD)", "% Monto a Uruguay"]]
    
    total_row = pd.DataFrame({
         "País de la Operación": ["Total"],
         "Total Contratos": [total_contratos],
         "Contratos Ganados por Empresas Uruguayas": [total_contratos_uy],
         "% Contratos a Empresas UY": [f"{pct_contratos}%"],
         "Monto Total Adjudicado (USD)": [f"${total_monto_total:,.0f}"],
         "Monto a Uruguay (USD)": [f"${total_monto_uy:,.0f}"],
         "% Monto a Uruguay": [f"{pct_monto}%"]
    })
    summary = pd.concat([summary, total_row], ignore_index=True)
    
    header_values = list(summary.columns)
    cell_values = [summary[col].tolist() for col in summary.columns]
    
    n_rows = len(summary)
    row_colors = ['#222222' if i % 2 == 0 else '#333333' for i in range(n_rows)]
    fill_colors = [row_colors] * len(header_values)
    
    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=header_values,
            fill_color="#444444",
            font=dict(color="white", size=16),
            align="center"
        ),
        cells=dict(
            values=cell_values,
            fill_color=fill_colors,
            font=dict(color="white", size=14),
            align="center",
            height=35
        )
    )])
    fig_table.update_layout(margin=dict(l=10, r=10, t=10, b=10),
                            paper_bgcolor="#000000",
                            plot_bgcolor="#000000")
    st.plotly_chart(fig_table, use_container_width=True)

# Función principal de navegación
def main():
    st.sidebar.title("Navegación")
    pagina = st.sidebar.selectbox("Selecciona una página:", 
                                  ("Página Principal", "Uruguay Nacional", "Uruguay en el Mundo", "Tabla Pivot"))
    if pagina == "Página Principal":
        pagina_principal()
    elif pagina == "Uruguay Nacional":
        pagina_uruguay_nacional()
    elif pagina == "Uruguay en el Mundo":
        pagina_uruguay_en_el_mundo()
    elif pagina == "Tabla Pivot":
        tabla_pivot()

if __name__ == "__main__":
    main()
