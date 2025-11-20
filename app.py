# PRUEBA SOLEMNE N°3
# INGE B001 TALLER DE PROGRAMACIÓN II - NRC: 3776

# --------------------------------------------------- ////// ---------------------------------------------------

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DE PÁGINA (Componente 1) ---

# --------------------------------------------------- ////// ---------------------------------------------------

# --- 2. FUNCIÓN DE DATOS (API REST) ---

# API CoinGecko: Gratis y no requiere Key
url = "https://api.coingecko.com/api/v3/coins/markets"
# Agrega parámetros para especificar la moneda
params = {
    'vs_currency': 'usd',  
    'order': 'market_cap_desc',
    'per_page': 10, 
    'page': 1
}

resp = requests.get(url, params=params)
print(resp)