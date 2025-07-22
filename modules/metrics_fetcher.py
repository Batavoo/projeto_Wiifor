import pandas as pd
from . import zabbix_connector

def get_latest_metrics(host_ids):
    """
    Busca os valores mais recentes de um conjunto de métricas para uma lista de hosts,
    usando chaves exatas para precisão e agregando os resultados.
    """
    api = zabbix_connector.connect_to_zabbix()
    if not api:
        print("Não foi possível conectar ao Zabbix para buscar métricas.")
        return pd.DataFrame()

    # 1. Lista de chaves exatas que encontramos.
    metric_keys = [
        'icmpping',
        'icmppingloss',
        'icmppingsec',
        'icmppingsecjitter',
        'system.cpu.util[hrProcessorLoad.1]',
        'system.cpu.util[hrProcessorLoad.2]',
        'system.cpu.util[hrProcessorLoad.3]',
        'system.cpu.util[hrProcessorLoad.4]',
        'vm.memory.util[memoryUsedPercentage.Memory]',
        'vm.memory.util[memoryUsedPercentage]',
    ]

    print(f"Buscando métricas com chaves exatas para {len(host_ids)} hosts...")
    try:
        # 2. Usamos 'filter' para uma busca exata e eficiente.
        items = api.item.get(
            hostids=host_ids,
            output=["hostid", "key_", "lastvalue"],
            filter={"key_": metric_keys}
        )
    except Exception as e:
        print(f"Erro ao buscar métricas da API: {e}")
        return pd.DataFrame()

    if not items:
        print("Nenhuma das métricas desejadas foi encontrada para os hosts.")
        return pd.DataFrame()

    # 3. Mapeamento de todas as chaves encontradas para nomes de colunas limpos.
    key_map = {
        'icmpping': 'ping_status',
        'icmppingloss': 'ping_loss_percent',
        'icmppingsec': 'ping_latency_sec',
        'icmppingsecjitter': 'ping_jitter_sec',
        'system.cpu.util[hrProcessorLoad.1]': 'cpu_utilization',
        'system.cpu.util[hrProcessorLoad.2]': 'cpu_utilization',
        'system.cpu.util[hrProcessorLoad.3]': 'cpu_utilization',
        'system.cpu.util[hrProcessorLoad.4]': 'cpu_utilization',
        'vm.memory.util[memoryUsedPercentage.Memory]': 'memory_usage_percent',
        'vm.memory.util[memoryUsedPercentage]': 'memory_usage_percent',
    }

    processed_data = []
    for item in items:
        metric_name = key_map.get(item['key_'])
        if metric_name:
            processed_data.append({
                "hostid": item['hostid'],
                "metric": metric_name,
                "value": item['lastvalue']
            })

    if not processed_data:
        return pd.DataFrame(columns=['hostid'])

    metrics_df = pd.DataFrame(processed_data)
    metrics_df['value'] = pd.to_numeric(metrics_df['value'], errors='coerce')
    metrics_df.dropna(subset=['value'], inplace=True)

    # 4. Agrupamento explícito para evitar o bug do 'pivot_table'.
    # Agrupamos por host e métrica, e calculamos a média.
    # Para CPU, isso nos dará a média dos núcleos. Para os outros, nos dará o valor único.
    final_df = metrics_df.groupby(['hostid', 'metric'])['value'].mean().unstack('metric').reset_index()
    
    final_df.columns.name = None

    print("Busca de métricas concluída.")
    return final_df