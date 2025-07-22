import googlemaps
from . import config
import time
import pandas as pd
import streamlit as st

# Inicializa o cliente uma vez para ser reutilizado
gmaps = googlemaps.Client(key=config.GOOGLE_MAPS_API_KEY)

def geocode_address(address):
    """
    Geocodifica um único endereço, restringindo a busca para Fortaleza, CE, Brasil.
    Retorna latitude, longitude e o endereço formatado encontrado pelo Google.
    """
    if not address or pd.isna(address):
        return None, None, None

    # CORRIGIDO: Define os componentes para restringir a busca geograficamente.
    # Isso é muito mais eficaz do que apenas anexar texto ao endereço.
    search_components = {
        "country": "BR",
        "administrative_area": "CE",
        "locality": "Fortaleza"
    }

    try:
        # Adiciona o parâmetro 'components' à chamada da API
        geocode_result = gmaps.geocode(address, components=search_components)
        
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            formatted_address = geocode_result[0]['formatted_address']
            return location['lat'], location['lng'], formatted_address
        else:
            return None, None, None
            
    except Exception as e:
        print(f"Erro ao geocodificar o endereço '{address}': {e}")
        return None, None, None

def apply_geocoding(df, address_column='treated_name'):
    """
    Aplica a geocodificação a um DataFrame, com barra de progresso e tratamento de erros.
    """
    if address_column not in df.columns:
        st.error(f"A coluna de endereço '{address_column}' não foi encontrada no DataFrame.")
        return df

    total_rows = len(df)
    progress_bar = st.progress(0)
    
    # Aplica a função de geocodificação e divide os resultados em três novas colunas
    results = df[address_column].apply(geocode_address)
    df[['latitude', 'longitude', 'google_address']] = pd.DataFrame(results.tolist(), index=df.index)

    # Atualiza a barra de progresso (simulação, pois .apply faz tudo de uma vez)
    progress_bar.progress(1.0)
    
    return df