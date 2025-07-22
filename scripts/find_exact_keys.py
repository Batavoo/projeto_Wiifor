# Este script busca as chaves exatas para um conjunto de métricas de interesse.

import os
import sys
import pandas as pd

# Adiciona o diretório raiz do projeto ao caminho do Python
script_dir = os.path.dirname(__file__)
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from modules import zabbix_connector

def find_exact_keys():
    """
    Busca todas as variações de um conjunto de chaves e exibe as versões únicas.
    """
    print("Iniciando o buscador de chaves exatas...")
    
    api = zabbix_connector.connect_to_zabbix()
    if not api:
        return

    # Padrões das métricas que estamos procurando
    metric_patterns = [
        "icmpping",
        "vm.memory.util",
        "system.cpu.util",
    ]

    try:
        print(f"Buscando itens que correspondam aos padrões: {metric_patterns}...")
        items = api.item.get(
            output=["key_"],
            search={"key_": metric_patterns},
            searchByAny=True
        )
        
        if not items:
            print("Nenhum item correspondente encontrado.")
            return

        keys_df = pd.DataFrame(items)
        
        # Filtra para garantir que a chave realmente começa com um dos nossos padrões
        # e depois encontra as chaves únicas.
        pattern_filter = "|".join(metric_patterns)
        filtered_keys = keys_df[keys_df['key_'].str.contains(pattern_filter)]
        unique_keys = filtered_keys['key_'].unique()

        print("\n--- Chaves Exatas Encontradas ---")
        print("Copie estas chaves e cole no 'metric_keys' e 'key_map' do seu 'metrics_fetcher.py'")
        for key in sorted(unique_keys):
            print(f"'{key}',")

    except Exception as e:
        print(f"\nOcorreu um erro: {e}")
    finally:
        if api:
            api.logout()
            print("\nLogout da API realizado.")

if __name__ == "__main__":
    find_exact_keys()