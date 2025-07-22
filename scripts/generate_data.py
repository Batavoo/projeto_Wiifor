# generate_data.py
import pandas as pd
import os
import sys

# Adiciona o diretório raiz do projeto ao caminho do Python
# para que ele possa encontrar a pasta 'modules'.
script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from modules import host_fetcher, geocoder, spatial_analyzer, metrics_fetcher 

def main():
    """
    Executa a pipeline de dados completa e salva o resultado em um arquivo Excel.
    Usa 'print' para feedback em vez de elementos do Streamlit.
    """
    GEOCODED_FILENAME = "zabbix_hosts_geocoded.xlsx"
    
    # Verifica se o usuário quer forçar uma atualização completa
    force_refresh = '--refresh' in sys.argv
    cache_exists = os.path.exists(GEOCODED_FILENAME)

    if not force_refresh and cache_exists:
        print(f"Arquivo '{GEOCODED_FILENAME}' já existe. Para forçar a atualização, use --refresh.")
        return

    print("Iniciando a pipeline de atualização de dados...")

    # A lógica abaixo é uma cópia da de host_fetcher, mas adaptada para o terminal
    
    # Passo 1: Busca, trata e categoriza os hosts
    print("Buscando e tratando hosts...")
    current_hosts_df = host_fetcher.fetch_treat_and_categorize_hosts()
    if current_hosts_df is None:
        print("ERRO: Falha ao buscar hosts do Zabbix. Abortando.")
        return

    # Passo 2: Busca as métricas de desempenho
    all_host_ids = current_hosts_df['hostid'].tolist()
    if all_host_ids:
        print(f"Buscando métricas de desempenho para {len(all_host_ids)} hosts...")
        metrics_df = metrics_fetcher.get_latest_metrics(all_host_ids)
        if not metrics_df.empty:
            # Garante que a chave de merge seja do mesmo tipo (string)
            current_hosts_df['hostid'] = current_hosts_df['hostid'].astype(str)
            metrics_df['hostid'] = metrics_df['hostid'].astype(str)
            
            # Junta os dados das métricas ao DataFrame principal
            current_hosts_df = pd.merge(current_hosts_df, metrics_df, on='hostid', how='left')
            print("Métricas de desempenho adicionadas.")

    # Passo 3: Geocodificação com cache inteligente
    if cache_exists:
        print("Carregando cache para geocodificação...")
        cached_df = pd.read_excel(GEOCODED_FILENAME)
        cached_df = cached_df[['hostid', 'latitude', 'longitude', 'google_address']]
        current_hosts_df['hostid'] = current_hosts_df['hostid'].astype(str)
        cached_df['hostid'] = cached_df['hostid'].astype(str)
        current_hosts_df = pd.merge(current_hosts_df, cached_df, on='hostid', how='left')
    
    needs_geocoding = current_hosts_df[current_hosts_df['latitude'].isna()]
    if not needs_geocoding.empty:
        print(f"{len(needs_geocoding)} hosts precisam de geocodificação.")
        geocoded_subset = geocoder.apply_geocoding(needs_geocoding.copy(), address_column='treated_name')
        current_hosts_df.update(geocoded_subset)
    else:
        print("Nenhum host novo para geocodificar.")

    # Passo 4: Análise Espacial
    print("Aplicando análise espacial...")
    final_df = spatial_analyzer.apply_spatial_analysis(current_hosts_df)

    # Passo 5: Salvar o arquivo
    try:
        final_df.to_excel(GEOCODED_FILENAME, index=False)
        print(f"\nSUCESSO: Pipeline concluída. Dados salvos em '{GEOCODED_FILENAME}'.")
    except Exception as e:
        print(f"\nERRO: Falha ao salvar o arquivo Excel: {e}")

if __name__ == "__main__":
    main()