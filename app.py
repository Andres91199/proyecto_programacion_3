# PRUEBA SOLEMNE N°3
# INGE B001 TALLER DE PROGRAMACIÓN II

# --------------------------------------------------- ////// ---------------------------------------------------

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title='Crypto Dashboard - Solemne 3', layout='wide')

st.title("Dashboard de Criptomonedas")
st.markdown("Aplicación para analizar el mercado actual utilizando la API de CoinGecko.")

# --------------------------------------------------- ////// ---------------------------------------------------

# --- 2. BARRA LATERAL ---
# Aquí el usuario puede ajustar los parámetros de búsqueda
st.sidebar.header("Configuración")
st.sidebar.write("Ajusta los parámetros de la API:")

# Selector de moneda base
moneda_base = st.sidebar.selectbox(
    "Moneda base:",
    ['USD', 'EUR', 'CLP'],
    help="Selecciona la moneda para ver los precios"
)

# Tipo de ordenamiento
tipo_orden = st.sidebar.radio(
    "Ordenar por:",
    ['Capitalización', 'Volumen'],
    help="Criterio de ordenamiento de las criptomonedas"
)

# Cantidad de monedas a mostrar
cantidad_monedas = st.sidebar.slider("Cantidad de monedas a analizar", min_value=5, max_value=50, value=10)

# --------------------------------------------------- ////// ---------------------------------------------------

# --- 3. FUNCIÓN PARA OBTENER DATOS DE LA API ---
# Esta función trae información de criptomonedas desde CoinGecko
# Usamos @st.cache_data para no llamar a la API cada vez que cambiamos algo
@st.cache_data
def cargar_datos(cantidad, moneda='usd', orden='market_cap_desc'):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    # Nota: La API usa per_page que cuenta desde 1, no desde 0
    params = {
        'vs_currency': moneda.lower(),
        'order': orden,
        'per_page': cantidad,  # La API devuelve exactamente esta cantidad
        'page': 1
    }
    try:
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            return pd.DataFrame(resp.json())
        else:
            st.error(f"Error {resp.status_code} en la API")
            return pd.DataFrame() # Retorna vacío si falla
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# Convertir selecciones del usuario a formato de la API
moneda_map = {'USD': 'usd', 'EUR': 'eur', 'CLP': 'clp'}
orden_map = {'Capitalización': 'market_cap_desc', 'Volumen': 'volume_desc'}

# Llamamos a la función con los parámetros seleccionados
df = cargar_datos(cantidad_monedas, moneda_map[moneda_base], orden_map[tipo_orden])

# Verificamos que el df no venga vacío antes de seguir
if df.empty:
    st.warning("No se cargaron datos. Intenta recargar la página.")
    st.stop()
else:
    st.sidebar.success("Datos actualizados correctamente")

# --------------------------------------------------- ////// ---------------------------------------------------

# --- 4. VISUALIZACIÓN Y ANÁLISIS ---
# Organizamos la información en pestañas para mejor navegación

tab1, tab2, tab3 = st.tabs(["Datos Crudos", "Gráficos Interactivos", "Conclusiones"])

# --- PESTAÑA 1: DATOS ---
# Aquí mostramos los datos en formato de tabla
with tab1:
    st.header("Conjunto de Datos")
    
    if st.checkbox("Mostrar tabla de datos completa", value=True):
        # Mostramos la tabla con las columnas más importantes
        simbolo_moneda = {'usd': '$', 'eur': '€', 'clp': '$'}[moneda_map[moneda_base]]
        st.dataframe(
            df[['name', 'symbol', 'current_price', 'market_cap', 'price_change_percentage_24h']],
            column_config={
                "current_price": st.column_config.NumberColumn(f"Precio ({moneda_base})", format=f"{simbolo_moneda}%.2f"),
                "market_cap": st.column_config.NumberColumn("Market Cap", format=f"{simbolo_moneda}%d"),
                "price_change_percentage_24h": st.column_config.NumberColumn("Cambio 24h", format="%.2f%%")
            },
            use_container_width=True
        )
    
    # Mostramos métricas de la moneda principal
    col1, col2 = st.columns(2)
    moneda_principal = df.iloc[0]
    simbolo_moneda = {'usd': '$', 'eur': '€', 'clp': '$'}[moneda_map[moneda_base]]
    col1.metric("Moneda Top #1", moneda_principal['name'], f"{simbolo_moneda}{moneda_principal['current_price']:,.2f}")
    col2.metric("Cambio 24h (Top 1)", f"{moneda_principal['price_change_percentage_24h']:.2f}%")

# --- PESTAÑA 2: GRÁFICOS ---
# Aquí mostramos diferentes gráficos para analizar los datos
with tab2:
    st.header("Análisis Visual")

    # --- Gráfico 1: Capitalización de Mercado ---
    st.subheader("1. Capitalización de Mercado (Top Monedas)")
    datos_market_cap = df.set_index('name')['market_cap']
    st.bar_chart(datos_market_cap)

    # --- Gráfico 2: Dispersión Precio vs Variación ---
    st.subheader("2. Relación Precio vs Variación (24h)")
    st.scatter_chart(df, x='current_price', y='price_change_percentage_24h', color='name')

    st.markdown("---")

    # --- Gráfico 3: Comparación de Rangos de Precio ---
    st.subheader("3. Comparación de Precios (High vs Low 24h)")

    # Permitimos seleccionar qué monedas comparar
    monedas_seleccionadas = st.multiselect(
        "Selecciona monedas para comparar sus rangos:",
        df['name'].tolist(),
        default=df['name'].iloc[:3].tolist()
    )

    if monedas_seleccionadas:
        df_filtrado = df[df['name'].isin(monedas_seleccionadas)]
        df_rangos = df_filtrado[['name', 'high_24h', 'low_24h']].set_index('name')
        st.bar_chart(df_rangos)
    else:
        st.warning("Selecciona al menos una moneda para ver el gráfico.")
    
    # --- Gráfico 4: Distribución de Volumen (Gráfico de Torta) ---
    st.subheader("4. Distribución de Volumen (Top 5)")
    
    if st.checkbox("Mostrar gráfico de torta"):
        # Creamos un gráfico circular con matplotlib
        fig, ax = plt.subplots()
        top5 = df.head(5)
        ax.pie(top5['total_volume'], labels=top5['symbol'].str.upper(), autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

# --- PESTAÑA 3: CONCLUSIONES ---
# Aquí interpretamos los resultados obtenidos
with tab3:
    st.header("Interpretación de Resultados")
    
    # Encontramos la moneda con mejor rendimiento
    mejor_moneda = df.loc[df['price_change_percentage_24h'].idxmax()]
    
    st.markdown(f"""
    **Análisis preliminar:**
    
    1. La moneda con mayor capitalización es **{df.iloc[0]['name']}**, lo que indica su dominancia en el mercado.
    2. La criptomoneda con mejor rendimiento en las últimas 24h es **{mejor_moneda['name']}** con un cambio de {mejor_moneda['price_change_percentage_24h']:.2f}%.
    3. En el gráfico de dispersión se puede observar la relación entre precio y volatilidad de cada criptomoneda.
    4. El gráfico de torta muestra que las top 5 monedas concentran la mayor parte del volumen de transacciones.
    """)
    
    with st.expander("Ver nota técnica"):
        st.info("Los datos son obtenidos en tiempo real mediante la API REST de CoinGecko. Se actualiza la información cada vez que se modifican los parámetros.")
