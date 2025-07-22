# modules/zabbix_connector.py
from zabbix_utils import ZabbixAPI
from . import config

def connect_to_zabbix():
    """
    Cria e autentica uma conexão com a API do Zabbix (GIGA).
    """
    try:
        print("Conectando à API do Zabbix (GIGA)...")
        # CORRIGIDO: Usando as variáveis específicas da GIGA
        api = ZabbixAPI(url=config.GIGA_ZABBIX_URL)
        api.login(token=config.GIGA_ZABBIX_API_TOKEN)
        print("Conexão bem-sucedida.")
        return api
    except Exception as e:
        print(f"Falha ao conectar à API do Zabbix: {e}")
        return None