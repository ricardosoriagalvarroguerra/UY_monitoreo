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
    """)

# Página Uruguay Nacional (estructura y filtros de una sola opción)
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
    
    # Filtros adicionales (una sola opción, por defecto "Todos")
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
    
    # Cálculo de métricas para los Value Boxes
    total_nacional = data_nacional.shape[0]
    local_awarded = data_nacional[data_nacional["awarded_firm_country_name"] == "Uruguay"].shape[0]
    percentage_local = (local_awarded / total_nacional * 100) if total_nacional > 0 else 0
    
    # Gráfico de montos: Suma de idb_amount por año
    if "contract_year" in data_nacional.columns and "idb_amount" in data_nacional.columns:
        df_bar = data_nacional.groupby("contract_year")["idb_amount"].sum().reset_index()
        fig_bar = px.bar(
            df_bar,
            x="contract_year",
            y="idb_amount",
            labels={"contract_year": "Año", "idb_amount": "Monto IDB"}
        )
        fig_bar.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10)
        )
    else:
        fig_bar = None

    # Distribución en dos columnas
    col_left, col_right = st.columns([0.3, 0.7])
    
    with col_left:
        # Value Box de Contratos
        st.markdown(f"""
            <div style="max-width: 150px; margin: 0; background-color: gray; padding: 5px;
                        border-radius: 5px; text-align: center; margin-bottom: 20px;">
                <h3 style="color: white; margin: 0; font-size: 20px; line-height: 1; font-weight: bold;">
                    Contratos
                </h3>
                <h1 style="color: white; margin: 0; font-size: 28px; line-height: 1; font-weight: normal;">
                    {total_nacional}
                </h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        
        # Título y gráfico donut de % Locales Ganados
        st.markdown(f"""
            <div style="max-width: 200px; margin: 0;">
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 16px; 
                           line-height: 1; font-weight: bold;">% Locales Ganados</h3>
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
        # Gráfico combinado de frecuencia: barras (total contratos) y línea (contratos ganados por Uruguay)
        if "contract_year" in data_nacional.columns:
            df_total = data_nacional.groupby("contract_year").size().reset_index(name="Total Contratos")
            df_local = data_nacional[data_nacional["awarded_firm_country_name"] == "Uruguay"] \
                        .groupby("contract_year").size().reset_index(name="Contratos Uruguay")
            fig_freq = go.Figure()
            # Traza de barras en el eje primario
            fig_freq.add_trace(go.Bar(
                x=df_total["contract_year"],
                y=df_total["Total Contratos"],
                name="Total Contratos",
                marker_color="#003049"
            ))
            # Traza de líneas asignada al eje secundario (yaxis2)
            fig_freq.add_trace(go.Scatter(
                x=df_local["contract_year"],
                y=df_local["Contratos Uruguay"],
                name="Contratos Uruguay",
                mode="lines+markers",
                line=dict(color="#669bbc"),
                yaxis="y2"
            ))
            # Configuración de ejes duales: eje primario a la izquierda y eje secundario a la derecha
            fig_freq.update_layout(
                title=dict(
                    text="Frecuencia de Contratos por Año",
                    x=0.5,
                    xanchor="center",
                    pad=dict(b=40)
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.0,
                    xanchor="center",
                    x=0.5
                ),
                xaxis_title="",
                height=220,
                margin=dict(l=10, r=10, t=60, b=10),
                yaxis=dict(
                    title="Total Contratos",
                    side="left"
                ),
                yaxis2=dict(
                    title="Contratos Uruguay",
                    overlaying="y",
                    side="right"
                )
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.write("No se encontró información para el gráfico de frecuencia.")
        
        # Gráfico de montos
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No se encontró la información necesaria para el gráfico de montos.")

# Página Uruguay en el Mundo (enfoque: contratos fuera de Uruguay y empresa uruguaya ganadora)
def pagina_uruguay_en_el_mundo():
    st.title("Uruguay en el Mundo")
    
    # Seleccionamos contratos cuya operación no sea en Uruguay
    data_mundial = data.copy()
    if "operation_country_name" in data_mundial.columns:
        data_mundial = data_mundial[data_mundial["operation_country_name"] != "Uruguay"]
    
    # Filtro de tiempo por año de contrato
    if "contract_year" in data_mundial.columns:
        min_year = int(data_mundial["contract_year"].min())
        max_year = int(data_mundial["contract_year"].max())
        year_range = st.sidebar.slider("Año de Contrato", min_value=min_year, max_value=max_year,
                                       value=(min_year, max_year), step=1)
        data_mundial = data_mundial[(data_mundial["contract_year"] >= year_range[0]) & 
                                    (data_mundial["contract_year"] <= year_range[1])]
    
    # Filtros adicionales (contrato, tipo de operación y sector económico)
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
    
    # NUEVO FILTRO: País de Operación
    if "operation_country_name" in data_mundial.columns:
        # Obtenemos los países únicos (ya sin Uruguay)
        unique_countries = sorted(data_mundial["operation_country_name"].dropna().unique())
        # Se agrega la opción "Mercosur"
        op_country_options = ["Todos", "Mercosur"] + unique_countries
        selected_op_country = st.sidebar.selectbox("País de Operación", op_country_options)
        if selected_op_country != "Todos":
            if selected_op_country == "Mercosur":
                mercosur_countries = ["Argentina", "Bolivia", "Brazil", "Paraguay"]
                data_mundial = data_mundial[data_mundial["operation_country_name"].isin(mercosur_countries)]
            else:
                data_mundial = data_mundial[data_mundial["operation_country_name"] == selected_op_country]
    
    st.write("Mostrando contratos en otros países, donde se evalúa la participación de empresas uruguayas.")
    
    # Cálculo de métricas:
    total_mundial = data_mundial.shape[0]
    # Cantidad de contratos en que la empresa ganadora es de Uruguay
    uruguayan_contracts = data_mundial[data_mundial["awarded_firm_country_name"] == "Uruguay"].shape[0]
    percentage_uruguayan = (uruguayan_contracts / total_mundial * 100) if total_mundial > 0 else 0
    
    # Gráfico de montos: Suma de idb_amount por año (contratos fuera de Uruguay)
    if "contract_year" in data_mundial.columns and "idb_amount" in data_mundial.columns:
        df_bar = data_mundial.groupby("contract_year")["idb_amount"].sum().reset_index()
        fig_bar = px.bar(
            df_bar,
            x="contract_year",
            y="idb_amount",
            labels={"contract_year": "Año", "idb_amount": "Monto IDB"}
        )
        fig_bar.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10)
        )
    else:
        fig_bar = None

    # Distribución en dos columnas
    col_left, col_right = st.columns([0.3, 0.7])
    
    with col_left:
        # Value Box de Contratos (contratos fuera de Uruguay)
        st.markdown(f"""
            <div style="max-width: 150px; margin: 0; background-color: gray;
                        padding: 5px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                <h3 style="color: white; margin: 0; font-size: 20px; line-height: 1; font-weight: bold;">
                    Contratos
                </h3>
                <h1 style="color: white; margin: 0; font-size: 28px; line-height: 1; font-weight: normal;">
                    {total_mundial}
                </h1>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        
        # Título del donut chart: % Empresa Uruguaya
        st.markdown(f"""
            <div style="max-width: 200px; margin: 0;">
                <h3 style="color: white; margin: 0 0 10px 0; font-size: 16px;
                           line-height: 1; font-weight: bold;">% Empresa Uruguaya</h3>
            </div>
            """, unsafe_allow_html=True)
        donut_data = pd.DataFrame({
            "Categoría": ["Uruguay", "Otros"],
            "Valor": [percentage_uruguayan, 100 - percentage_uruguayan]
        })
        donut_fig = px.pie(
            donut_data,
            values="Valor",
            names="Categoría",
            hole=0.7,
            color_discrete_map={"Uruguay": "#669bbc", "Otros": "#cccccc"}
        )
        donut_fig.update_traces(textinfo="none", hoverinfo="label+percent")
        donut_fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            width=250,
            annotations=[dict(text=f"{percentage_uruguayan:.1f}%", x=0.5, y=0.5,
                              font_size=28, font_color="white", showarrow=False)]
        )
        st.plotly_chart(donut_fig, use_container_width=False)
    
    with col_right:
        # Gráfico de frecuencia: barras (total contratos) y línea (contratos ganados por Uruguay)
        if "contract_year" in data_mundial.columns:
            df_total = data_mundial.groupby("contract_year").size().reset_index(name="Total Contratos")
            df_uruguayan = data_mundial[data_mundial["awarded_firm_country_name"] == "Uruguay"] \
                           .groupby("contract_year").size().reset_index(name="Contratos Uruguay")
            fig_freq = go.Figure()
            # Traza de barras en el eje primario
            fig_freq.add_trace(go.Bar(
                x=df_total["contract_year"],
                y=df_total["Total Contratos"],
                name="Total Contratos",
                marker_color="#003049"
            ))
            # Traza de líneas asignada al eje secundario (yaxis2)
            fig_freq.add_trace(go.Scatter(
                x=df_uruguayan["contract_year"],
                y=df_uruguayan["Contratos Uruguay"],
                name="Contratos Uruguay",
                mode="lines+markers",
                line=dict(color="#669bbc"),
                yaxis="y2"
            ))
            # Configuración de ejes duales: eje primario a la izquierda y eje secundario a la derecha
            fig_freq.update_layout(
                title=dict(
                    text="Frecuencia de Contratos por Año",
                    x=0.5,
                    xanchor="center",
                    pad=dict(b=40)
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.0,
                    xanchor="center",
                    x=0.5
                ),
                xaxis_title="",
                height=220,
                margin=dict(l=10, r=10, t=60, b=10),
                yaxis=dict(
                    title="Total Contratos",
                    side="left"
                ),
                yaxis2=dict(
                    title="Contratos Uruguay",
                    overlaying="y",
                    side="right"
                )
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.write("No se encontró información para el gráfico de frecuencia.")
        
        # Gráfico de montos
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No se encontró la información necesaria para el gráfico de montos.")

def main():
    st.sidebar.title("Navegación")
    pagina = st.sidebar.selectbox("Selecciona una página:", 
                                  ("Página Principal", "Uruguay Nacional", "Uruguay en el Mundo"))
    if pagina == "Página Principal":
        pagina_principal()
    elif pagina == "Uruguay Nacional":
        pagina_uruguay_nacional()
    elif pagina == "Uruguay en el Mundo":
        pagina_uruguay_en_el_mundo()

if __name__ == "__main__":
    main()
