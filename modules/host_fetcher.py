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

def run_update_pipeline(force_zabbix_refresh=True):
    """
    Executa a pipeline de atualização de dados.
    - Sempre busca dados novos do Zabbix (por padrão)
    - Usa o cache apenas para geocodificação
    
    Args:
        force_zabbix_refresh (bool): Se True, busca novos dados do Zabbix.
    """
    GEOCODED_FILENAME = "zabbix_hosts_geocoded.xlsx"
    cache_exists = os.path.exists(GEOCODED_FILENAME)

    # Inicia a pipeline de atualização
    # Passo 1: Busca dados do Zabbix (sempre)
    current_hosts_df = fetch_treat_and_categorize_hosts()
    
    if current_hosts_df is None:
        st.error("Falha ao buscar hosts do Zabbix. Abortando.")
        return None

    # Passo 2: Busca as métricas de desempenho (sempre)
    all_host_ids = current_hosts_df['hostid'].tolist()
    if all_host_ids:
        metrics_df = metrics_fetcher.get_latest_metrics(all_host_ids)
        if not metrics_df.empty:
            current_hosts_df['hostid'] = current_hosts_df['hostid'].astype(str)
            metrics_df['hostid'] = metrics_df['hostid'].astype(str)
            current_hosts_df = pd.merge(current_hosts_df, metrics_df, on='hostid', how='left')

    # Passo 3: Geocodificação com cache (para economia)
    if cache_exists:
        cached_df = pd.read_excel(GEOCODED_FILENAME)
        cached_df = cached_df[['hostid', 'latitude', 'longitude', 'google_address']]
        
        current_hosts_df['hostid'] = current_hosts_df['hostid'].astype(str)
        cached_df['hostid'] = cached_df['hostid'].astype(str)
        current_hosts_df = pd.merge(current_hosts_df, cached_df, on='hostid', how='left')
    else:
        # Se o cache não existe, cria as colunas vazias para a lógica funcionar
        current_hosts_df['latitude'] = np.nan
        current_hosts_df['longitude'] = np.nan
        current_hosts_df['google_address'] = None
    
    # Geocodifica apenas os hosts novos
    needs_geocoding = current_hosts_df[current_hosts_df['latitude'].isna()]
    if not needs_geocoding.empty:
        st.info(f"Geocodificando {len(needs_geocoding)} hosts novos...")
        geocoded_subset = geocoder.apply_geocoding(needs_geocoding.copy(), address_column='treated_name')
        current_hosts_df.update(geocoded_subset)
    
    # Passo 4: Análise espacial
    hosts_dataframe = spatial_analyzer.apply_spatial_analysis(current_hosts_df)
    
    # Passo 5: Salva apenas o cache de geocodificação
    # Salva apenas as colunas necessárias para geocodificação futura
    geocache_df = current_hosts_df[['hostid', 'name', 'latitude', 'longitude', 'google_address']].copy()
    geocache_df.to_excel(GEOCODED_FILENAME, index=False)

    return hosts_dataframe