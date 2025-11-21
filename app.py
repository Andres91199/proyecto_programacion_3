# PRUEBA SOLEMNE N°3
# INGE TALLER DE PROGRAMACIÓN II

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
# BLOQUE 1: CONFIGURACIÓN DE ENTORNO Y VISTA
# -----------------------------------------------------------------------------
# Inicialización de la configuración global de la aplicación.
# Se define 'layout="wide"' para maximizar el espacio horizontal disponible,
# optimizando la visualización de DataFrames extensos y gráficos comparativos.
st.set_page_config(
    page_title='Crypto Lab - Solemne 3', 
    layout='wide',
    initial_sidebar_state="expanded"
)

# Encabezado principal
st.title("💠 Crypto Lab: Análisis de Mercado")
st.markdown("Entorno de visualización de activos digitales mediante CoinGecko API.")

# -----------------------------------------------------------------------------
# BLOQUE 2: PARAMETRIZACIÓN E INTERFAZ DE CONTROL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Centro de Control")

# Selección de divisa base.
# Este input actúa como variable de estado para la conversión de precios en la API.
moneda_base = st.sidebar.selectbox(
    "Divisa de referencia:",
    ['USD', 'EUR', 'CLP'],
    index=0
)

# Selector de criterio de ordenamiento para la solicitud HTTP.
tipo_orden = st.sidebar.radio(
    "Criterio de clasificación:",
    ['Capitalización', 'Volumen']
)

# Control de volumen de datos.
# Permite limitar la carga (payload) para reducir latencia en la visualización.
cantidad_monedas = st.sidebar.slider("Alcance del análisis (N° monedas)", 5, 50, 10)

# Filtro de texto para búsqueda en tiempo real (Case-Insensitive).
filtro_nombre = st.sidebar.text_input("🔭 Rastrear activo específico:")

st.sidebar.markdown("---")
st.sidebar.caption("📡 Datos sincronizados con CoinGecko")

# -----------------------------------------------------------------------------
# BLOQUE 3: CAPA DE DATOS Y CONEXIÓN API
# -----------------------------------------------------------------------------

# Implementación de caché mediante decorador @st.cache_data.
# Objetivo: Evitar llamadas redundantes a la API en cada interacción de la UI,
# protegiendo la cuota de peticiones (Rate Limiting) y mejorando el rendimiento.
@st.cache_data
def cargar_datos(cantidad, moneda='usd', orden='market_cap_desc'):
    url = "https://api.coingecko.com/api/v3/coins/markets"

    # Construcción de parámetros para la solicitud GET.
    # Se utiliza un diccionario para garantizar la correcta codificación de la URL.
    params = {
        'vs_currency': moneda.lower(),
        'order': orden,
        'per_page': cantidad,
        'page': 1,
        'sparkline': False 
    }

    try:
        # Solicitud con timeout explícito (10s) para prevenir bloqueos indefinidos
        # en caso de latencia alta o caída del servicio externo.
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code == 200:
            return pd.DataFrame(resp.json())
        elif resp.status_code == 429:
            # Manejo específico de error 429 (Too Many Requests).
            st.warning("🚧 Tráfico denso en la API (Error 429). Reintentando enlace...")
            return pd.DataFrame()
        else:
            # Captura de errores de protocolo no críticos (4xx, 5xx).
            st.error(f"🚫 Fallo de protocolo {resp.status_code}")
            return pd.DataFrame()

    except Exception as e:
        # Manejo de excepciones críticas de red (DNS, desconexión, SSL).
        st.error(f"💀 Error fatal de conexión: {e}")
        return pd.DataFrame()

# Diccionarios de mapeo: Transforman la selección legible del usuario (UI)
# en parámetros técnicos aceptados por los endpoints de la API (Backend).
moneda_map = {'USD': 'usd', 'EUR': 'eur', 'CLP': 'clp'}
orden_map = {'Capitalización': 'market_cap_desc', 'Volumen': 'volume_desc'}
simbolo_moneda = {'usd': '$', 'eur': '€', 'clp': '$'}[moneda_map[moneda_base]]

# Ejecución de la carga de datos.
df = cargar_datos(cantidad_monedas, moneda_map[moneda_base], orden_map[tipo_orden])

# Validación de integridad:
# Si el DataFrame está vacío (por error de API o red), se detiene la ejecución
# mediante st.stop() para prevenir errores en cascada en los bloques visuales.
if df.empty:
    st.warning("☁️ No se pudo establecer conexión con la nube de datos.")
    st.stop()

# Lógica de filtrado local:
# Aplica una máscara booleana sobre el DataFrame buscando coincidencias parciales
# en las columnas 'name' O 'symbol'.
if filtro_nombre:
    df = df[df['name'].str.contains(filtro_nombre, case=False) | df['symbol'].str.contains(filtro_nombre, case=False)]
    if df.empty:
        st.warning(f"👻 El activo '{filtro_nombre}' no fue detectado en el radar actual.")
        st.stop()

# -----------------------------------------------------------------------------
# BLOQUE 4: DASHBOARD Y VISUALIZACIÓN
# -----------------------------------------------------------------------------
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

if not df.empty:
    # Extracción del activo líder (fila 0) para métricas destacadas.
    top_coin = df.iloc[0]

    col_kpi1.metric("🚀 Activo Dominante", top_coin['name'])
    col_kpi2.metric("💳 Cotización", f"{simbolo_moneda}{top_coin['current_price']:,.2f}")

    # Indicador de variación porcentual con color dinámico (delta_color)
    # gestionado automáticamente por Streamlit según el signo del valor.
    col_kpi3.metric("🌊 Flujo 24h", f"{top_coin['price_change_percentage_24h']:.2f}%", 
                    delta_color="normal" if top_coin['price_change_percentage_24h'] >= 0 else "inverse")

st.markdown("---")

# Estructura de pestañas para segregar vistas: Datos crudos vs. Gráficos vs. Análisis.
tab1, tab2, tab3 = st.tabs(["🗃️ Bóveda de Datos", "📡 Radar Visual", "🧭 Hallazgos"])

# -----------------------------------------------------------------------------
# PESTAÑA 1: REPRESENTACIÓN TABULAR
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Inventario de Activos")

    cols_to_show = ['image', 'name', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']

    # Renderizado de tabla interactiva.
    # Se utiliza column_config para formatear datos crudos (imágenes, monedas, porcentajes)
    # directamente en la vista sin alterar los tipos de datos subyacentes en el DataFrame.
    st.dataframe(
        df[cols_to_show],
        column_config={
            "image": st.column_config.ImageColumn("Token"),
            "name": "Identificador",
            "symbol": "Ticker",
            "current_price": st.column_config.NumberColumn(f"Valor ({moneda_base})", format=f"{simbolo_moneda}%.2f"),
            "market_cap": st.column_config.NumberColumn("Cap. Global", format=f"{simbolo_moneda}%.0f"),
            "total_volume": st.column_config.NumberColumn("Volumen Op.", format=f"{simbolo_moneda}%.0f"),
            "price_change_percentage_24h": st.column_config.NumberColumn("Delta 24h", format="%.2f%%", help="Volatilidad diaria")
        },
        use_container_width=True,
        hide_index=True
    )

    # Serialización a CSV para funcionalidad de descarga.
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💿 Exportar Dataset (CSV)", csv, 'crypto_lab_data.csv', 'text/csv')

# -----------------------------------------------------------------------------
# PESTAÑA 2: ANALÍTICA GRÁFICA
# -----------------------------------------------------------------------------
with tab2:
    st.header("Telemétrica de Mercado")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Dominio de Capitalización")
        # Gráfico de barras simple utilizando el índice del DataFrame ('name') como eje X.
        st.bar_chart(df.head(10).set_index('name')['market_cap'])

    with col_g2:
        st.subheader("Correlación Precio / Volatilidad")
        criterio_color = st.toggle("🖌️ Pigmentar por Dimensión (Cap)", value=True)
        color_chart = 'market_cap' if criterio_color else None

        # Diagrama de dispersión multivariable (Bubble Chart).
        # Relaciona Precio (X), Variación (Y) y Capitalización (Tamaño/Color).
        st.scatter_chart(df, x='current_price', y='price_change_percentage_24h', color=color_chart, size='market_cap')

    # Visualización de Rangos (High/Low).
    # Permite comparar la volatilidad intra-día de activos seleccionados.
    st.subheader("Amplitud Térmica (Máx vs Mín 24h)")
    monedas_default = df['name'].iloc[:3].tolist()
    seleccion = st.multiselect("Comparativa de activos:", df['name'].tolist(), default=monedas_default)

    if seleccion:
        df_r = df[df['name'].isin(seleccion)].set_index('name')[['low_24h', 'high_24h']]
        st.bar_chart(df_r)

    st.markdown("---")

    # Integración Avanzada con Matplotlib (Donut Chart).
    st.subheader("Participación de Volumen (Top 5)")

    col_chart, col_txt = st.columns([2, 1])

    with col_chart:
        top5 = df.head(5).copy()

        # Función auxiliar para limpieza visual: oculta etiquetas en segmentos menores al 5%.
        def mostrar_valor(pct):
            return f'{pct:.1f}%' if pct > 5 else ''

        fig, ax = plt.subplots(figsize=(6, 6))

        # Configuración de transparencia (alpha=0) para compatibilidad visual
        # con los temas Claro/Oscuro nativos de Streamlit.
        fig.patch.set_alpha(0.0) 
        ax.patch.set_alpha(0.0)

        colors = plt.cm.Set3(np.linspace(0, 1, len(top5)))

        # Creación del gráfico de anillo mediante la propiedad 'wedgeprops'.
        wedges, texts, autotexts = ax.pie(
            top5['total_volume'], 
            labels=None,            
            autopct=mostrar_valor, 
            startangle=90,
            colors=colors,
            pctdistance=0.80,       
            wedgeprops=dict(width=0.5, edgecolor='white')
        )

        plt.setp(autotexts, size=10, weight="bold", color="black")
        ax.text(0, 0, 'VOLUMEN\nTOTAL', ha='center', va='center', fontsize=10, fontweight='bold')

        # Leyenda externa calculada manualmente para mostrar proporciones exactas.
        total = top5['total_volume'].sum()
        etiquetas_leyenda = [f"{row['name']} ({(row['total_volume']/total)*100:.1f}%)" for index, row in top5.iterrows()]

        ax.legend(wedges, etiquetas_leyenda,
                  title="Tokens",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

        st.pyplot(fig)

    with col_txt:
        st.markdown("""
        **Interpretación del Radar:**

        Este diagrama de anillo ilustra la liquidez relativa entre los activos dominantes.

        *Renderizado vía motor Matplotlib.*
        """)

# -----------------------------------------------------------------------------
# PESTAÑA 3: INSIGHTS AUTOMATIZADOS
# -----------------------------------------------------------------------------
with tab3:
    st.header("Síntesis de Inteligencia")
    # Identificación de extremos (máximos y mínimos) en la variación diaria
    # utilizando métodos vectorizados de Pandas (idxmax/idxmin).
    mejor = df.loc[df['price_change_percentage_24h'].idxmax()]
    peor = df.loc[df['price_change_percentage_24h'].idxmin()]

    st.info(f"⚡ **Flash Insight:** El activo con mayor tracción alcista hoy es **{mejor['name']}** (+{mejor['price_change_percentage_24h']:.2f}%).")

    st.markdown(f"""
    ### 🧬 Diagnóstico de Mercado
    1. **Hegemonía:** {df.iloc[0]['name']} mantiene la supremacía con un valor de {simbolo_moneda}{df.iloc[0]['current_price']:,.2f}.
    2. **Zona Fría:** El desempeño más bajo del clúster lo presenta **{peor['name']}** ({peor['price_change_percentage_24h']:.2f}%).
    3. **Liquidez:** Verifica el diagrama radial en la pestaña anterior para confirmar dónde se agrupa el capital.
    """)
