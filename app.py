import streamlit as st
from modules.host_fetcher import run_update_pipeline
import time
import plotly.express as px

st.set_page_config(page_title="Dashboard de Hosts Zabbix", layout="wide")

st.title("Dashboard de Análise de Hosts do Zabbix")

# --- Sidebar para Controles ---
st.sidebar.header("Controles")
if st.sidebar.button("Limpar Cache e Atualizar Dados"):
    run_update_pipeline.clear()
    # Limpa o estado dos filtros ao atualizar os dados
    if 'selected_category' in st.session_state:
        del st.session_state['selected_category']
    if 'selected_bairro' in st.session_state:
        del st.session_state['selected_bairro']
    st.success("Cache limpo. Os dados serão atualizados.")
    st.rerun()

# --- Carregamento dos Dados ---
df = run_update_pipeline()

# --- Inicialização do Estado da Sessão para Filtros ---
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = []
if 'selected_bairro' not in st.session_state:
    st.session_state.selected_bairro = []

if df is not None and not df.empty:
    # ... (código dos cards de estatísticas permanece o mesmo) ...
    st.header("Status da Rede")
    
    # Definir o status UP baseado em ping_status e memory_usage_percent
    # Host UP = ping respondendo (1) E memória não crítica (abaixo de 85%)
    if 'ping_status' in df.columns and 'memory_usage_percent' in df.columns:
        # CORRIGIDO: Usando .loc para evitar o warning
        df = df.copy()  # Garantir que temos uma cópia independente
        df.loc[:, 'status_up'] = (df['ping_status'] == 1) & (df['memory_usage_percent'] < 85)
        
        # Contagens para os cards
        total_hosts = len(df)
        up_hosts = df['status_up'].sum()
        down_hosts = total_hosts - up_hosts
        pct_up = (up_hosts / total_hosts * 100) if total_hosts > 0 else 0
        
        # Layout dos cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Hosts", f"{total_hosts}")
        col2.metric("Hosts UP", f"{up_hosts}", f"{pct_up:.1f}%")
        col3.metric("Hosts DOWN", f"{down_hosts}")
    else:
        st.warning("Dados de monitoramento não disponíveis. Verifique a conexão com a API do Zabbix.")

    # --- Filtros com Gerenciamento de Estado ---
    st.header("Filtros")
    col1, col2 = st.columns(2)
    
    # Filtro por Categoria
    col1.multiselect(
        "Filtrar por Categoria:",
        options=df['category'].unique(),
        key='selected_category' # Usa a chave para conectar ao session_state
    )
    
    # Filtro por Bairro
    col2.multiselect(
        "Filtrar por Bairro:",
        options=df['bairro'].sort_values().unique(),
        key='selected_bairro' # Usa a chave para conectar ao session_state
    )
    
    # Aplicação dos filtros lendo do session_state
    filtered_df = df.copy()
    if st.session_state.selected_category:
        filtered_df = filtered_df[filtered_df['category'].isin(st.session_state.selected_category)]
    if st.session_state.selected_bairro:
        filtered_df = filtered_df[filtered_df['bairro'].isin(st.session_state.selected_bairro)]
    
    # ... (o resto do seu código para exibir métricas e o mapa continua o mesmo) ...
    # NOVO: Visualização detalhada dos dados do Zabbix
    # NOVO: Visualização detalhada dos dados do Zabbix
    st.header("Métricas de Monitoramento")
    
    # Colunas de métricas a serem exibidas com nomes amigáveis
    metric_columns = {
        'ping_status': 'Status (Online/Offline)',
        'ping_latency_sec': 'Latência (seg)',
        'ping_loss_percent': 'Perda de Pacotes (%)',
        'memory_usage_percent': 'Uso de Memória (%)',
        'cpu_utilization': 'Utilização de CPU (%)'
    }
    
    # Verificar quais colunas de métricas existem no DataFrame
    available_metrics = [col for col in metric_columns.keys() if col in filtered_df.columns]
    
    if available_metrics:
        # Criar um DataFrame com as métricas disponíveis e informações básicas dos hosts
        metrics_view = filtered_df[['name', 'category', 'bairro'] + available_metrics].copy(deep=True)
        
        if 'ping_status' in metrics_view:
            # CORRIGIDO: Converte a coluna para 'object' antes de inserir strings para evitar o FutureWarning
            metrics_view['ping_status'] = metrics_view['ping_status'].astype(object)
            metrics_view.loc[:, 'ping_status'] = metrics_view['ping_status'].map({1: '✅ Online', 0: '❌ Offline'})
        
        # Renomear colunas para nomes mais amigáveis
        metrics_view = metrics_view.rename(columns={
            k: v for k, v in metric_columns.items() if k in metrics_view.columns
        })
        
        # Exibir a tabela de métricas
        st.dataframe(metrics_view)
        
        # NOVO: Gráficos de métricas
        st.subheader("Distribuição de Métricas")
        metric_to_plot = st.selectbox(
            "Selecione uma métrica para visualizar:", 
            options=[v for k, v in metric_columns.items() if k in available_metrics],
            index=0
        )
        
        # Mapear o nome amigável de volta para o nome da coluna
        original_col = next((k for k, v in metric_columns.items() if v == metric_to_plot), None)
        
        if original_col and original_col != 'ping_status':  # Ignorar ping_status pois é categórico
            fig = px.histogram(
                filtered_df, 
                x=original_col,
                title=f"Distribuição de {metric_to_plot}",
                nbins=20
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não foram encontradas métricas do Zabbix nos dados.")
    
    # Mapa
    st.header("Mapa de Localização dos Hosts")
    map_df = filtered_df.dropna(subset=['latitude', 'longitude']).copy()  # Garantir cópia independente
    
    # CORRIGIDO: Usando .loc para evitar o warning
    if 'status_up' in map_df.columns:
        map_df.loc[:, 'color'] = map_df['status_up'].map({True: [0, 255, 0, 100], False: [255, 0, 0, 100]})
        st.map(map_df, color='color')
    else:
        st.map(map_df)
    
else:
    st.warning("Nenhum dado para exibir. Tente forçar uma atualização.")