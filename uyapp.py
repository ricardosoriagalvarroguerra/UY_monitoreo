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

# Página Uruguay Nacional
def pagina_uruguay_nacional():
    st.title("Uruguay Nacional")
    
    # Filtrar contratos con operación en Uruguay
    data_nacional = data.copy()
    if "operation_country_name" in data_nacional.columns:
        data_nacional = data_nacional[data_nacional["operation_country_name"] == "Uruguay"]
    
    # Filtro de tiempo por año de contrato (si existe)
    if "contract_year" in data_nacional.columns:
        min_year = int(data_nacional["contract_year"].min())
        max_year = int(data_nacional["contract_year"].max())
        year_range = st.sidebar.slider("Año de Contrato", min_value=min_year, max_value=max_year, 
                                       value=(min_year, max_year), step=1)
        data_nacional = data_nacional[(data_nacional["contract_year"] >= year_range[0]) & 
                                      (data_nacional["contract_year"] <= year_range[1])]
    
    st.write("Mostrando contratos en Uruguay (Operación Nacional).")
    
    # Calcular métricas para los Value Boxes
    total_nacional = data_nacional.shape[0]
    local_awarded = data_nacional[data_nacional["awarded_firm_country_name"] == "Uruguay"].shape[0]
    percentage_local = (local_awarded / total_nacional * 100) if total_nacional > 0 else 0
    
    # Mostrar los Value Boxes en dos columnas (con menos espacio, pero textos más grandes)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style="background-color: #8ecae6; padding: 3px; border-radius: 5px; text-align: center; max-width: 200px; margin: auto;">
                <h3 style="color: white; margin: 0; font-size: 16px;">Contratos</h3>
                <h1 style="color: white; margin: 0; font-size: 28px;">{total_nacional}</h1>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background-color: #8ecae6; padding: 3px; border-radius: 5px; text-align: center; max-width: 200px; margin: auto;">
                <h3 style="color: white; margin: 0; font-size: 16px;">% Contratos Locales Ganados</h3>
                <h1 style="color: white; margin: 0; font-size: 28px;">{percentage_local:.1f}%</h1>
            </div>
            """, unsafe_allow_html=True)
    
    # Gráfico de barras horizontal: Top 15 de awarded_firm_country_name
    if "awarded_firm_country_name" in data_nacional.columns:
        df_freq = data_nacional["awarded_firm_country_name"].value_counts().reset_index()
        df_freq.columns = ["Empresa", "Frecuencia"]
        df_top15 = df_freq.sort_values("Frecuencia", ascending=False).head(15).sort_values("Frecuencia", ascending=True)
        colors = ["#669bbc" if empresa == "Uruguay" else "#003049" for empresa in df_top15["Empresa"]]
        fig = px.bar(
            df_top15,
            x="Frecuencia",
            y="Empresa",
            orientation="h",
            title="Top 15 Empresas (Awarded) en Contratos Nacionales",
            text="Frecuencia",
            labels={"Frecuencia": "Frecuencia", "Empresa": "Empresa"}
        )
        fig.update_traces(marker_color=colors, textposition='outside')
        altura = max(600, len(df_top15) * 40)
        fig.update_layout(height=altura)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("La columna 'awarded_firm_country_name' no se encuentra en los datos.")

# Página Uruguay en el Mundo
def pagina_uruguay_en_el_mundo():
    st.title("Uruguay en el Mundo")
    data_mundial = data.copy()
    # Filtrar contratos: empresas uruguayas que operan en el exterior
    if "awarded_firm_country_name" in data_mundial.columns:
        data_mundial = data_mundial[data_mundial["awarded_firm_country_name"] == "Uruguay"]
    if "operation_country_name" in data_mundial.columns:
        data_mundial = data_mundial[data_mundial["operation_country_name"] != "Uruguay"]
    # Filtro de tiempo por año de contrato
    if "contract_year" in data_mundial.columns:
        min_year = int(data_mundial["contract_year"].min())
        max_year = int(data_mundial["contract_year"].max())
        year_range = st.sidebar.slider("Año de Contrato", min_value=min_year, max_value=max_year, 
                                       value=(min_year, max_year), step=1)
        data_mundial = data_mundial[(data_mundial["contract_year"] >= year_range[0]) & (data_mundial["contract_year"] <= year_range[1])]
    st.write("Mostrando contratos donde empresas uruguayas operan en el exterior.")
    
    # Para cada Operation Type, generar subgráficos de barras horizontales (Top 5 + Otros)
    if "operation_type_name" in data_mundial.columns:
        op_types = list(data_mundial["operation_type_name"].dropna().unique())
        n_ops = len(op_types)
        if n_ops == 0:
            st.write("No se encontraron Operation Type en la data.")
        else:
            cols = 2
            rows = math.ceil(n_ops / cols)
            subplot_titles = op_types
            fig_sub = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles)
            bar_palette = ["#F28E2B", "#4E79A7", "#59A14F", "#E15759", "#EDC948",
                           "#B07AA1", "#76B7B2", "#FF9DA7", "#9C755F", "#BAB0AC"]
            for idx, op in enumerate(op_types):
                r = idx // cols + 1
                c = idx % cols + 1
                df_op = data_mundial[data_mundial["operation_type_name"] == op].copy()
                if "operation_country_name" in df_op.columns:
                    df_op_count = df_op["operation_country_name"].value_counts().reset_index()
                    df_op_count.columns = ["País de Operación", "Frecuencia"]
                    df_op_count = df_op_count.sort_values("Frecuencia", ascending=False)
                    # Lógica para Top 5: si "Uruguay" aparece, incluirlo y tomar 4 de los demás; de lo contrario, tomar 5.
                    if "Uruguay" in df_op_count["País de Operación"].values:
                        row_uruguay = df_op_count[df_op_count["País de Operación"] == "Uruguay"]
                        df_others = df_op_count[df_op_count["País de Operación"] != "Uruguay"]
                        top_others = df_others.head(4)
                        selected = pd.concat([row_uruguay, top_others])
                    else:
                        selected = df_op_count.head(5)
                    selected_countries = set(selected["País de Operación"])
                    remaining = df_op_count[~df_op_count["País de Operación"].isin(selected_countries)]
                    if not remaining.empty:
                        otros_frequency = remaining["Frecuencia"].sum()
                        df_otros = pd.DataFrame({"País de Operación": ["Otros"], "Frecuencia": [otros_frequency]})
                        final_df = pd.concat([selected, df_otros], ignore_index=True)
                    else:
                        final_df = selected.copy()
                    total_final = final_df["Frecuencia"].sum()
                    final_df["Porcentaje"] = (final_df["Frecuencia"] / total_final * 100).round(2)
                    bar_colors = []
                    palette_index = 0
                    for pais in final_df["País de Operación"]:
                        bar_colors.append(bar_palette[palette_index % len(bar_palette)])
                        palette_index += 1
                    trace = go.Bar(
                        x=final_df["Frecuencia"],
                        y=final_df["País de Operación"],
                        orientation="h",
                        text=final_df["Frecuencia"],
                        textposition="outside",
                        marker_color=bar_colors
                    )
                    fig_sub.add_trace(trace, row=r, col=c)
                    fig_sub.update_yaxes(autorange="reversed", row=r, col=c)
                else:
                    st.write("La columna 'operation_country_name' no se encuentra en la data para", op)
            fig_sub.update_layout(title_text="Distribución de Países de Operación por Operation Type (Top 5 + Otros)", height=400*rows)
            st.plotly_chart(fig_sub, use_container_width=True)
    else:
        st.write("La columna 'operation_type_name' no se encuentra en la data.")

def main():
    st.sidebar.title("Navegación")
    pagina = st.sidebar.selectbox("Selecciona una página:", ("Página Principal", "Uruguay Nacional", "Uruguay en el Mundo"))
    if pagina == "Página Principal":
        pagina_principal()
    elif pagina == "Uruguay Nacional":
        pagina_uruguay_nacional()
    elif pagina == "Uruguay en el Mundo":
        pagina_uruguay_en_el_mundo()

if __name__ == "__main__":
    main()
