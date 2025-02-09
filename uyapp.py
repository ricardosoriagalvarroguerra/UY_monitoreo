import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Funciones para cada página
# -----------------------------

def pagina_principal():
    st.title("Pagina Principal")
    st.write("Bienvenido a la aplicación de UY_PROCUREMENT")
    st.write("""
    En esta sección encontrarás un resumen general de la información disponible.
    Puedes navegar a las secciones de **Tablas** para ver los datos en formato tabular 
    o a **Visualizaciones** para analizar gráficos y tendencias.
    """)

def pagina_tablas():
    st.title("Tablas")
    st.write("Visualización de tablas y detalles de la Base de Datos.")

    # Ejemplo: Mostrar un DataFrame con parte del esquema de la base de datos
    data = {
        "Nombre de la Columna": [
            "contract_id", "contract_type", "project_number", "project_name", "status"
        ],
        "Tipo de Dato": [
            "object", "object", "object", "object", "object"
        ],
        "Valores Únicos": [
            3638, 6, 319, 319, 2
        ],
        "Valores Faltantes": [
            0, 0, 0, 0, 0
        ]
    }
    df_esquema = pd.DataFrame(data)
    st.dataframe(df_esquema)

def pagina_visualizaciones():
    st.title("Visualizaciones")
    st.write("Visualización de datos a través de gráficos.")

    # Ejemplo: Gráfico de barras simple
    data = {
        "Categoría": ["A", "B", "C", "D"],
        "Valores": [10, 15, 7, 20]
    }
    df = pd.DataFrame(data)

    fig, ax = plt.subplots()
    ax.bar(df["Categoría"], df["Valores"], color="skyblue")
    ax.set_xlabel("Categoría")
    ax.set_ylabel("Valores")
    ax.set_title("Gráfico de barras de ejemplo")

    st.pyplot(fig)

# -----------------------------
# Función principal de la aplicación
# -----------------------------

def main():
    # Barra lateral de navegación
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
