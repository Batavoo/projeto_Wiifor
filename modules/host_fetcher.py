# host_fetcher.py
import pandas as pd
from . import zabbix_connector
from . import name_parser
from . import location_categorizer
from . import spatial_analyzer
from . import geocoder
from . import metrics_fetcher
import numpy as np
import os
import sys
import streamlit as st # Importa o streamlit


def fetch_treat_and_categorize_hosts():
    """
    Busca os hosts, trata os nomes para padronizar endereços e os categoriza.
    """
    # ... (código existente para buscar e tratar os nomes) ...
    hosts_df = fetch_and_treat_hosts() # Supondo que a função anterior ainda exista
    if hosts_df is None:
        return None
    
    # 3. Aplica a função de categorização na coluna 'treated_name'
    print("Categorizando os locais com base nos nomes tratados...")
    hosts_df['category'] = hosts_df['treated_name'].apply(location_categorizer.categorize_location)
    print("Categorização concluída.")

    return hosts_df

# Função auxiliar para manter a lógica separada
def fetch_and_treat_hosts():
    api = zabbix_connector.connect_to_zabbix()
    if not api:
        return None
    try:
        hosts_data = api.host.get(output=["hostid", "name"])
    except Exception as e:
        print(f"Ocorreu um erro ao buscar os hosts: {e}")
        return None
    hosts_df = pd.DataFrame(hosts_data)
    hosts_df['treated_name'] = hosts_df['name'].apply(name_parser.standardize_address_name)
    return hosts_df

# REMOVA o decorador @st.cache_data daqui. O cache será gerenciado no app.py.
@st.cache_data(show_spinner="Processando dados (Zabbix, Geocoding, etc)...")
def run_update_pipeline():
    """
    Executa a pipeline de atualização de dados.
    - O resultado desta função é cacheado em memória pelo Streamlit.
    """
    GEOCODED_FILENAME = "zabbix_hosts_geocoded.xlsx"
    
    # Passo 1: Busca dados do Zabbix (sempre executa para obter status mais recente)
    current_hosts_df = fetch_treat_and_categorize_hosts()
    
    if current_hosts_df is None:
        st.error("Falha ao buscar hosts do Zabbix. Abortando.")
        return None

    # Passo 2: Busca as métricas de desempenho
    all_host_ids = current_hosts_df['hostid'].tolist()
    if all_host_ids:
        metrics_df = metrics_fetcher.get_latest_metrics(all_host_ids)
        if not metrics_df.empty:
            current_hosts_df['hostid'] = current_hosts_df['hostid'].astype(str)
            metrics_df['hostid'] = metrics_df['hostid'].astype(str)
            current_hosts_df = pd.merge(current_hosts_df, metrics_df, on='hostid', how='left')

    # Passo 3: Geocodificação usando o cache do arquivo .xlsx
    if os.path.exists(GEOCODED_FILENAME):
        cached_df = pd.read_excel(GEOCODED_FILENAME)
        cached_df = cached_df[['hostid', 'latitude', 'longitude', 'google_address']]
        
        current_hosts_df['hostid'] = current_hosts_df['hostid'].astype(str)
        cached_df['hostid'] = cached_df['hostid'].astype(str)
        current_hosts_df = pd.merge(current_hosts_df, cached_df, on='hostid', how='left')
    else:
        st.warning(f"Arquivo de cache '{GEOCODED_FILENAME}' não encontrado. A geolocalização não será exibida.")
        current_hosts_df['latitude'] = np.nan
        current_hosts_df['longitude'] = np.nan
        current_hosts_df['google_address'] = None
    
    # Geocodifica APENAS os hosts que não estavam no cache (novos hosts)
    needs_geocoding = current_hosts_df[current_hosts_df['latitude'].isna()]
    if not needs_geocoding.empty:
        # Esta chamada agora só acontece se um host novo for adicionado ao Zabbix
        # e não estiver no seu arquivo .xlsx.
        geocoded_subset = geocoder.apply_geocoding(needs_geocoding.copy(), address_column='treated_name')
        current_hosts_df.update(geocoded_subset)
        
        # Salva o cache de volta. No Streamlit Cloud, isso é temporário,
        # mas útil se novos hosts forem adicionados durante a sessão.
        geocache_df = current_hosts_df[['hostid', 'name', 'latitude', 'longitude', 'google_address']].copy()
        geocache_df.to_excel(GEOCODED_FILENAME, index=False)
    
    # Passo 4: Análise espacial
    hosts_dataframe = spatial_analyzer.apply_spatial_analysis(current_hosts_df)
    
    return hosts_dataframe