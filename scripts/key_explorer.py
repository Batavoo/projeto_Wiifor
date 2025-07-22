# Este script se conecta à API do Zabbix para explorar as chaves de métricas (items) mais comuns.

import os
import sys
import pandas as pd
import re

# Adiciona o diretório raiz do projeto ao caminho do Python
script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from modules import zabbix_connector

def normalize_key(key):
    """
    Normaliza uma chave Zabbix, removendo os parâmetros específicos dentro de colchetes.
    Exemplo: 'net.if.in[ifInDiscards.241]' se torna 'net.if.in.discards[]'.
    """
    # Usa uma expressão regular para substituir o conteúdo dentro dos colchetes por nada.
    return re.sub(r'\[.*\]', '[]', key)

def explore_common_keys():
    """
    Busca as chaves de métricas, normaliza-as e exibe as mais comuns.
    """
    print("Iniciando o explorador de chaves Zabbix...")
    
    api = zabbix_connector.connect_to_zabbix()
    if not api:
        print("Não foi possível conectar ao Zabbix.")
        return

    try:
        print("Buscando todas as chaves de métricas da API... Isso pode levar um momento.")
        all_items = api.item.get(output=["key_"])
        
        if not all_items:
            print("Nenhum item (métrica) foi encontrado.")
            return

        keys_df = pd.DataFrame(all_items)
        
        # 1. CRIA UMA NOVA COLUNA COM AS CHAVES NORMALIZADAS
        keys_df['normalized_key'] = keys_df['key_'].apply(normalize_key)
        
        # 2. CONTA A OCORRÊNCIA DAS CHAVES NORMALIZADAS
        common_keys = keys_df['normalized_key'].value_counts().reset_index()
        common_keys.columns = ['key_pattern', 'item_count']

        print("\n--- Padrões de Chaves Mais Comuns (Top 50) ---")
        print(f"Um total de {len(keys_df)} items foram analisados.")
        print("As chaves abaixo representam os padrões mais frequentes.\n")
        
        # 3. EXIBE APENAS AS 50 MAIS COMUNS PARA NÃO SOBRECARREGAR O TERMINAL
        print(common_keys.head(50).to_string())

    except Exception as e:
        print(f"\nOcorreu um erro durante a busca na API: {e}")
    finally:
        if api:
            api.logout()
            print("\nLogout da API realizado.")

if __name__ == "__main__":
    explore_common_keys()