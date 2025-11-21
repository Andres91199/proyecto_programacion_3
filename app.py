# PRUEBA SOLEMNE N°3
# INGE B001 TALLER DE PROGRAMACIÓN II

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt


def formato_miles(valor, decimales=2):
    """Formatea un número usando punto para miles y coma para decimales."""
    if pd.isna(valor):
        return "-"
    texto = f"{valor:,.{decimales}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto

# Configuración básica de la página
st.set_page_config(page_title="Dashboard de Criptomonedas", layout="wide")

st.title("Dashboard de Criptomonedas")
st.markdown("Aplicación para analizar el mercado actual utilizando la API de CoinGecko.")

# ------------------------------------------------------------------
# Barra lateral: parámetros que puede ajustar el usuario
# ------------------------------------------------------------------
st.sidebar.header("Configuración")

moneda_base = st.sidebar.selectbox(
    "Moneda base",
    ["USD", "EUR", "CLP"],
    help="Selecciona la moneda en la que quieres ver los precios."
)

tipo_orden = st.sidebar.radio(
    "Ordenar por",
    ["Capitalización", "Volumen"],
    help="Criterio de ordenamiento de las criptomonedas."
)

cantidad_monedas = st.sidebar.slider(
    "Cantidad de monedas a analizar",
    min_value=5,
    max_value=50,
    value=10
)

# ------------------------------------------------------------------
# Función para obtener datos desde la API de CoinGecko
# ------------------------------------------------------------------
@st.cache_data
def cargar_datos(cantidad, moneda="usd", orden="market_cap_desc"):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": moneda.lower(),
        "order": orden,
        "per_page": cantidad,
        "page": 1
    }

    try:
        respuesta = requests.get(url, params=params, timeout=10)

        if respuesta.status_code == 200:
            return pd.DataFrame(respuesta.json())
        else:
            st.error(f"Error {respuesta.status_code} al consultar la API.")
            return pd.DataFrame()

    except requests.exceptions.Timeout:
        st.error("La solicitud excedió el tiempo de espera.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"No se pudo completar la solicitud: {e}")
        return pd.DataFrame()

# Mapas para traducir las opciones de la interfaz a la API
moneda_map = {"USD": "usd", "EUR": "eur", "CLP": "clp"}
orden_map = {"Capitalización": "market_cap_desc", "Volumen": "volume_desc"}
simbolo_moneda = {"usd": "$", "eur": "€", "clp": "$"}[moneda_map[moneda_base]]

# Llamamos a la API con los parámetros del usuario
df = cargar_datos(cantidad_monedas, moneda_map[moneda_base], orden_map[tipo_orden])

# Si no llegan datos, se detiene la aplicación
if df.empty:
    st.warning("No se cargaron datos. Intenta recargar la página.")
    st.stop()

# ------------------------------------------------------------------
# Pestañas principales de la aplicación
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Datos crudos", "Gráficos interactivos", "Conclusiones"])

# ------------------------------------------------------------------
# Pestaña 1: datos en tabla
# ------------------------------------------------------------------
with tab1:
    st.header("Conjunto de datos")

    tabla = pd.DataFrame(
        {
            "Nombre": df["name"],
            "Símbolo": df["symbol"].str.upper(),
            "Precio": df["current_price"].apply(
                lambda x: f"{simbolo_moneda}{formato_miles(x, 2)}"
            ),
            "Capitalización": df["market_cap"].apply(
                lambda x: f"{simbolo_moneda}{formato_miles(x, 0)}"
            ),
            "Volumen 24h": df["total_volume"].apply(
                lambda x: f"{simbolo_moneda}{formato_miles(x, 0)}"
            ),
            "Cambio 24h": df["price_change_percentage_24h"].apply(
                lambda x: f"{x:.2f}%"
            ),
        }
    )
    tabla.index = range(1, len(tabla) + 1)
    st.dataframe(tabla, width='stretch')

    col1, col2 = st.columns(2)
    moneda_principal = df.iloc[0]

    col1.metric(
        "Moneda top #1",
        moneda_principal["name"],
        f"{simbolo_moneda}{formato_miles(moneda_principal['current_price'], 2)}"
    )
    col2.metric(
        "Cambio 24h (top 1)",
        f"{moneda_principal['price_change_percentage_24h']:.2f}%"
    )

# ------------------------------------------------------------------
# Pestaña 2: gráficos
# ------------------------------------------------------------------
with tab2:
    st.header("Análisis visual")

    # Gráfico 1: capitalización de mercado
    st.subheader("1. Capitalización de mercado (top monedas)")
    datos_market_cap = df.set_index("name")["market_cap"]
    st.bar_chart(datos_market_cap)

    # Gráfico 2: precio vs variación
    st.subheader("2. Relación precio vs variación (24h)")
    st.scatter_chart(
        df,
        x="current_price",
        y="price_change_percentage_24h",
        color="name"
    )

    st.markdown("---")

    # Gráfico 3: rangos de precio (máximo vs mínimo)
    st.subheader("3. Comparación de precios (máximo vs mínimo 24h)")

    monedas_seleccionadas = st.multiselect(
        "Selecciona monedas para comparar sus rangos:",
        df["name"].tolist(),
        default=df["name"].iloc[:3].tolist()
    )

    if monedas_seleccionadas:
        df_rangos = (
            df[df["name"].isin(monedas_seleccionadas)][["name", "high_24h", "low_24h"]]
            .set_index("name")
        )
        df_rangos = df_rangos.rename(
            columns={"high_24h": "Máximo 24h", "low_24h": "Mínimo 24h"}
        )
        st.bar_chart(df_rangos)
    else:
        st.warning("Selecciona al menos una moneda para ver este gráfico.")

    # Gráfico 4: distribución de volumen (top 5)
    st.subheader("4. Distribución de volumen (top 5)")

    if st.checkbox("Mostrar gráfico de torta"):
        top5 = df.head(5)
        fig, ax = plt.subplots()
        ax.pie(
            top5["total_volume"],
            labels=top5["symbol"].str.upper(),
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")
        st.pyplot(fig)

# ------------------------------------------------------------------
# Pestaña 3: conclusiones
# ------------------------------------------------------------------
with tab3:
    st.header("Conclusiones")

    mejor_moneda = df.loc[df["price_change_percentage_24h"].idxmax()]

    st.markdown(
        f"""
**Análisis preliminar**

1. La moneda con mayor capitalización es **{df.iloc[0]['name']}**, lo que indica su peso en el mercado.
2. La criptomoneda con mejor rendimiento en las últimas 24h es **{mejor_moneda['name']}** con un cambio de {mejor_moneda['price_change_percentage_24h']:.2f}%.
3. En el gráfico de dispersión se observa la relación entre precio y variación de cada criptomoneda.
4. El gráfico de torta muestra que las primeras 5 monedas concentran una parte importante del volumen de transacciones.
"""
    )

    with st.expander("Nota técnica"):
        st.info(
            "Los datos se obtienen en tiempo real desde la API pública de CoinGecko. "
            "La información se actualiza cada vez que se modifican los parámetros."
        )
