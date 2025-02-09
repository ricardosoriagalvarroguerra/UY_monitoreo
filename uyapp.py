import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Función para cargar la base de datos
# -----------------------------
@st.cache_data  # Cachea la carga para mejorar el rendimiento
def load_data():
    # Asegúrate de tener instalado pyarrow o fastparquet para leer archivos Parquet
    return pd.read_parquet("uy_procurements.parquet")

# Carga de datos (se realizará una sola vez)
data = load_data()

# -----------------------------
# Página Principal
# -----------------------------
def pagina_principal():
    st.title("Pagina Principal")
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
    
    with tabs[0]:
        st.header("Raw Data")
        st.write("Datos en crudo de la base de datos con los filtros aplicados:")
        st.dataframe(filtered_data)  # Muestra la tabla filtrada
    
    with tabs[1]:
        st.header("Agregada")
        st.write("Datos agregados (ejemplo de conteo por tipo de contrato):")
        # Ejemplo de agregación: contar contratos por 'contract_type'
        if "contract_type" in filtered_data.columns and "contract_id" in filtered_data.columns:
            agregada = filtered_data.groupby("contract_type")["contract_id"].count().reset_index()
            agregada.columns = ["contract_type", "count"]
            st.dataframe(agregada)
        else:
            st.write("No se encontraron las columnas necesarias para realizar la agregación.")

# -----------------------------
# Página de Visualizaciones
# -----------------------------
def pagina_visualizaciones():
    st.title("Visualizaciones")
    st.write("Gráficos y análisis visual de la base de datos.")
    
    # Ejemplo: Gráfico de barras del conteo de contratos por 'contract_type'
    if "contract_type" in data.columns and "contract_id" in data.columns:
        agregada = data.groupby("contract_type")["contract_id"].count().reset_index()
        agregada.columns = ["contract_type", "count"]
        
        fig, ax = plt.subplots()
        ax.bar(agregada["contract_type"], agregada["count"], color="skyblue")
        ax.set_xlabel("Tipo de contrato")
        ax.set_ylabel("Cantidad de contratos")
        ax.set_title("Cantidad de contratos por tipo")
        st.pyplot(fig)
    else:
        st.write("No se encontraron las columnas necesarias para la visualización.")

# -----------------------------
# Función principal de la aplicación
# -----------------------------
def main():
    st.sidebar.title("Navegación")
    pagina = st.sidebar.radio("Selecciona una página:", 
                              ("Pagina Principal", "Tablas", "Visualizaciones"))

    if pagina == "Pagina Principal":
        pagina_principal()
    elif pagina == "Tablas":
        pagina_tablas()
    elif pagina == "Visualizaciones":
        pagina_visualizaciones()

if __name__ == "__main__":
    main()
