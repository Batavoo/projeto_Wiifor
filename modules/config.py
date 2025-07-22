import os
import sys

# Função para verificar se estamos em uma sessão do Streamlit
def is_running_in_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except ImportError:
        return False

# Lógica principal de configuração
if is_running_in_streamlit():
    # Carrega do Streamlit secrets (para a aplicação web)
    import streamlit as st
    print("Configuração carregada a partir dos segredos do Streamlit.")
    GIGA_ZABBIX_URL = st.secrets["giga_zabbix"]["url"]
    GIGA_ZABBIX_API_TOKEN = st.secrets["giga_zabbix"]["token"]
    TEXTNET_ZABBIX_URL = st.secrets["textnet_zabbix"]["url"]
    TEXTNET_ZABBIX_API_TOKEN = st.secrets["textnet_zabbix"]["token"]
    GOOGLE_MAPS_API_KEY = st.secrets["google_maps"]["api_key"]
else:
    # Carrega do arquivo .env (para execução de script local)
    from dotenv import load_dotenv
    print("Configuração carregada a partir do arquivo .env.")
    load_dotenv()
    GIGA_ZABBIX_URL = os.getenv("GIGA_ZABBIX_URL")
    GIGA_ZABBIX_API_TOKEN = os.getenv("GIGA_ZABBIX_API_TOKEN")
    TEXTNET_ZABBIX_URL = os.getenv("TEXTNET_ZABBIX_URL")
    TEXTNET_ZABBIX_API_TOKEN = os.getenv("TEXTNET_ZABBIX_API_TOKEN")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Verificação final para garantir que a chave do Google Maps não é nula
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("A chave da API do Google Maps não foi encontrada. Verifique seu arquivo .env ou secrets.toml.")