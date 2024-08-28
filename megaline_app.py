import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind
from dotenv import load_dotenv
import os

# variáveis de ambiente do arquivo .env
load_dotenv()

# layout do dashboard
st.set_page_config(layout="wide", page_title="Analise dos clientes Megaline")

@st.cache_data
def carregar_dados():
    """Carrega os dados necessários para o dashboard."""
    data_path = os.getenv('DATA_PATH')  
    
    # verifica se a variável de ambiente está definida
    if not data_path:
        st.error("O caminho dos dados não está definido. Verifique o arquivo .env.")
        return None, None, None, None, None

    # Carrega os arquivos CSV
    users = pd.read_csv(os.path.join(data_path, 'megaline_users.csv'))
    calls = pd.read_csv(os.path.join(data_path, 'megaline_calls.csv'))
    messages = pd.read_csv(os.path.join(data_path, 'megaline_messages.csv'))
    internet = pd.read_csv(os.path.join(data_path, 'megaline_internet.csv'))
    plans = pd.read_csv(os.path.join(data_path, 'megaline_plans.csv'))
    
    # Converter a coluna de data para datetime
    if 'date' not in users.columns:
        users['date'] = pd.to_datetime('2018-01-01').normalize()
    else:
        users['date'] = pd.to_datetime(users['date'])

    return users, calls, messages, internet, plans

def calcular_receita(users, calls, messages, internet, plans):
    """Calcula a receita total por usuário com base em custos fixos e adicionais, tratando dados nulos."""
    plan_costs = plans.set_index('plan_name').to_dict('index')
    
    # Adiciona colunas de receita ao DataFrame de usuários
    users['monthly_revenue'] = users['plan'].map(lambda plan: plan_costs.get(plan, {}).get('usd_monthly_pay', 0))

    # Verificação e tratamento de dados nulos em chamadas
    calls = calls.merge(users[['user_id', 'plan']], on='user_id', how='left')
    calls['additional_call_cost'] = (
        (calls['duration'] - calls['plan'].map(lambda plan: plan_costs.get(plan, {}).get('minutes_included', 0)))
        .clip(lower=0) * calls['plan'].map(lambda plan: plan_costs.get(plan, {}).get('usd_per_minute', 0))
    )

    # Verificação e tratamento de dados nulos em mensagens
    messages = messages.merge(users[['user_id', 'plan']], on='user_id', how='left')
    messages_count = messages.groupby('user_id').size().reset_index(name='message_count')
    messages_count = messages_count.merge(users[['user_id', 'plan']], on='user_id', how='left')
    messages_count['additional_message_cost'] = (
        (messages_count['message_count'] - messages_count['plan'].map(lambda plan: plan_costs.get(plan, {}).get('messages_included', 0)))
        .clip(lower=0) * messages_count['plan'].map(lambda plan: plan_costs.get(plan, {}).get('usd_per_message', 0))
    )

    # Verificação e tratamento de dados nulos em uso de internet
    internet = internet.merge(users[['user_id', 'plan']], on='user_id', how='left')
    internet['additional_internet_cost'] = (
        (internet['mb_used'] - internet['plan'].map(lambda plan: plan_costs.get(plan, {}).get('mb_per_month_included', 0)))
        .clip(lower=0) / 1024 * internet['plan'].map(lambda plan: plan_costs.get(plan, {}).get('usd_per_gb', 0))
    )

    # Somar todas as receitas para cada usuário
    total_revenue_per_user = users[['user_id', 'plan', 'monthly_revenue', 'date']].copy()
    total_revenue_per_user = total_revenue_per_user.merge(calls.groupby('user_id')['additional_call_cost'].sum().reset_index(), on='user_id', how='left')
    total_revenue_per_user = total_revenue_per_user.merge(messages_count[['user_id', 'additional_message_cost']], on='user_id', how='left')
    total_revenue_per_user = total_revenue_per_user.merge(internet.groupby('user_id')['additional_internet_cost'].sum().reset_index(), on='user_id', how='left')

    # Substituindo NaNs por 0 (caso algum usuário não tenha registros de chamadas, mensagens ou internet)
    total_revenue_per_user = total_revenue_per_user.fillna(0)

    # Calcular receita total por usuário (fixa + adicional)
    total_revenue_per_user['total_revenue'] = (
        total_revenue_per_user['monthly_revenue'] +
        total_revenue_per_user['additional_call_cost'] +
        total_revenue_per_user['additional_message_cost'] +
        total_revenue_per_user['additional_internet_cost']
    )
    
    return total_revenue_per_user

def criar_graficos_desempenho(total_users, total_calls, total_messages, total_internet_usage_mb, total_revenue, users, calls, messages, internet):
    """Cria gráficos de desempenho para o dashboard com mais interatividade."""
    col1, col2, col3, col4, col5 = st.columns(5)

    # Gráfico gauge para total de usuários
    with col1:
        st.markdown("#### Total de Usuários")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_users,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, users['user_id'].nunique()], 'tickwidth': 1, 'tickcolor': "darkred"},
                'bar': {'color': "darkred"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, users['user_id'].nunique() * 0.5], 'color': 'lightgray'},
                    {'range': [users['user_id'].nunique() * 0.5, users['user_id'].nunique()], 'color': 'gray'}
                ],
            },
            title={'text': "Usuários Totais"}
        ))
        st.plotly_chart(fig, use_container_width=True)

    # Gauge para total de ligações
    with col2:
        st.markdown("#### Total de Chamadas")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_calls,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, calls['id'].count()], 'tickwidth': 1, 'tickcolor': "red"},
                'bar': {'color': "red"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, calls['id'].count() * 0.5], 'color': 'lightgray'},
                    {'range': [calls['id'].count() * 0.5, calls['id'].count()], 'color': 'gray'}
                ],
            },
            title={'text': "Chamadas Totais"}
        ))
        st.plotly_chart(fig, use_container_width=True)

    # Gauge para total de mensagens
    with col3:
        st.markdown("#### Total de Mensagens")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_messages,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, messages['id'].count()], 'tickwidth': 1, 'tickcolor': "orangered"},
                'bar': {'color': "orangered"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, messages['id'].count() * 0.5], 'color': 'lightgray'},
                    {'range': [messages['id'].count() * 0.5, messages['id'].count()], 'color': 'gray'}
                ],
            },
            title={'text': "Mensagens Totais"}
        ))
        st.plotly_chart(fig, use_container_width=True)

    # Converter uso total de internet de MB para GB
    total_internet_usage_gb = total_internet_usage_mb / 1024

    # Gauge para total do uso de internet
    with col4:
        st.markdown("#### Uso Total de Internet (GB)")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_internet_usage_gb,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, max(total_internet_usage_gb, 35000)],'tickwidth':1, 'tickcolor': "darkred"},
                'bar': {'color': "darkred"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, total_internet_usage_gb * 0.5], 'color': 'lightgray'},
                    {'range': [total_internet_usage_gb * 0.5, max(total_internet_usage_gb, 35000)], 'color': 'gray'}
                ],
            },
            title={'text': "Internet (GB) Totais"}
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Gauge para receita total
    with col5:
        st.markdown("#### Receita Total (USD)")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_revenue,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, max(total_revenue, 15000)], 'tickwidth': 1, 'tickcolor': "darkred"},
                'bar': {'color': "darkred"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, total_revenue * 0.5], 'color': 'lightgray'},
                    {'range': [total_revenue * 0.5, max(total_revenue, 15000)], 'color': 'gray'}
                ],
            },
            title={'text': "Receita Total (USD)"}
        ))
        st.plotly_chart(fig, use_container_width=True)

def criar_histograma_idade_por_plano(users):
    """Cria um histograma para comparar as idades dos assinantes de cada plano."""
    st.markdown("### Comparação de Idade dos Assinantes por Plano")
    
    # Verifica se a coluna 'age' está presente no DataFrame
    if 'age' not in users.columns or 'plan' not in users.columns:
        st.error("Erro: As colunas 'age' ou 'plan' não estão presentes no DataFrame.")
        return
    
    # Histograma com Plotly usando uma paleta de cores vermelha mais escura
    hist_fig = px.histogram(
        users, 
        x='age', 
        color='plan',
        barmode='overlay',
        title="Distribuição de Idade dos Assinantes por Plano",
        labels={'age': 'Idade', 'plan': 'Plano'},
        template='plotly_white',
        color_discrete_sequence=['#660000', '#800000']
    )
    st.plotly_chart(hist_fig, use_container_width=True)

def criar_grafico_heatmap(filtered_users):
    """Cria um heatmap para mostrar a distribuição de usuários por plano e cidade."""
    st.markdown("### Distribuição de Usuários por Plano e Cidade")
    
    # Verificar se os dados estão disponíveis
    if filtered_users.empty:
        st.warning("Nenhum dado disponível para gerar o heatmap.")
        return
    
    # Contagem de usuários por cidade e plano
    city_plan_counts = filtered_users.groupby(['city', 'plan']).size().reset_index(name='user_count')
    heatmap_data = city_plan_counts.pivot(index="plan", columns="city", values="user_count").fillna(0)

    # Criar o gráfico de heatmap usando Plotly
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Reds'
    ))

    heatmap_fig.update_layout(
        title='Distribuição de Usuários por Plano e Cidade',
        xaxis_nticks=36,
        font=dict(color='black')
    )

    # Exibe o gráfico de heatmap no Streamlit
    st.plotly_chart(heatmap_fig, use_container_width=True)

def criar_graficos_segunda_pagina(users, calls, messages, internet, plans):
    """Cria os gráficos interativos para a segunda página usando uma paleta de cores vermelha mais escura."""
    
    # Preparo dos dados
    calls['call_date'] = pd.to_datetime(calls['call_date'])
    internet['session_date'] = pd.to_datetime(internet['session_date'])
    messages['message_date'] = pd.to_datetime(messages['message_date'])

    calls_merged = calls.merge(users[['user_id', 'plan']], on='user_id', how='left')
    internet_merged = internet.merge(users[['user_id', 'plan']], on='user_id', how='left')
    messages_merged = messages.merge(users[['user_id', 'plan']], on='user_id', how='left')

    calls_merged['month'] = calls_merged['call_date'].dt.to_period('M').astype(str)
    internet_merged['month'] = internet_merged['session_date'].dt.to_period('M').astype(str)
    messages_merged['month'] = messages_merged['message_date'].dt.to_period('M').astype(str)

    calls_avg = calls_merged.groupby(['month', 'plan']).agg({'duration': 'mean'}).reset_index()
    internet_avg = internet_merged.groupby(['month', 'plan']).agg({'mb_used': 'mean'}).reset_index()
    messages_avg = messages_merged.groupby(['month', 'plan']).agg({'id': 'count'}).reset_index()
    messages_avg.rename(columns={'id': 'messages_count'}, inplace=True)

    # Usando uma paleta de cores mais escura para os gráficos
    dark_red_colors = ['#7F0000', '#660000', '#4C0000']

    # Gráfico de linha interativo - Uso médio de minutos, mensagens e dados
    fig_line_calls = px.line(
        calls_avg, 
        x='month', 
        y='duration', 
        color='plan', 
        title='Uso Médio de Minutos por Mês e por Plano',
        labels={'duration': 'Minutos Médios', 'month': 'Mês', 'plan': 'Plano'},
        markers=True,
        color_discrete_sequence=dark_red_colors  # Paleta de cores mais escura
    )
    st.plotly_chart(fig_line_calls, use_container_width=True)

    fig_line_data = px.line(
        internet_avg, 
        x='month', 
        y='mb_used', 
        color='plan', 
        title='Uso Médio de Dados por Mês e por Plano',
        labels={'mb_used': 'Dados Médios (MB)', 'month': 'Mês', 'plan': 'Plano'},
        markers=True,
        color_discrete_sequence=dark_red_colors  # Paleta de cores mais escura
    )
    st.plotly_chart(fig_line_data, use_container_width=True)

    fig_line_messages = px.line(
        messages_avg, 
        x='month', 
        y='messages_count', 
        color='plan', 
        title='Uso Médio de Mensagens por Mês e por Plano',
        labels={'messages_count': 'Mensagens Médias', 'month': 'Mês', 'plan': 'Plano'},
        markers=True,
        color_discrete_sequence=dark_red_colors  # Paleta de cores mais escura
    )
    st.plotly_chart(fig_line_messages, use_container_width=True)

    # Boxplot interativo - Receita média por plano
    total_revenue_per_user = calcular_receita(users, calls, messages, internet, plans)
    fig_box = px.box(
        total_revenue_per_user, 
        x='plan', 
        y='total_revenue', 
        title='Receita Média por Plano',
        labels={'total_revenue': 'Receita (USD)', 'plan': 'Plano'},
        color_discrete_sequence=dark_red_colors  # Paleta de cores mais escura
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Mapa de calor interativo - Correlação entre uso de serviços e receita
    usage_summary = total_revenue_per_user.copy()
    usage_summary = usage_summary.merge(calls_merged.groupby('user_id')['duration'].sum().reset_index(name='total_minutes'), on='user_id', how='left')
    usage_summary = usage_summary.merge(internet_merged.groupby('user_id')['mb_used'].sum().reset_index(name='total_data'), on='user_id', how='left')

    messages_count = messages_merged.groupby('user_id').size().reset_index(name='total_messages')
    usage_summary = usage_summary.merge(messages_count, on='user_id', how='left')

    correlation_matrix = usage_summary[['total_revenue', 'total_minutes', 'total_data', 'total_messages']].corr()
    fig_heatmap = px.imshow(
        correlation_matrix, 
        text_auto=True, 
        title='Correlação entre o Uso de Serviços e a Receita Gerada',
        labels=dict(x="Variável", y="Variável", color="Correlação"),
        color_continuous_scale=['#4C0000', '#660000', '#7F0000']  # Escala de cores mais escura para o heatmap
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

def main():
    """Função principal para execução do dashboard."""
    
    # Carregar dados
    users, calls, messages, internet, plans = carregar_dados()
    
    # Calcular receitas
    total_revenue_per_user = calcular_receita(users, calls, messages, internet, plans)
    
    # Sidebar para navegação entre páginas
    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Ir para", [
        "Página 1: Métricas Gerais",
        "Página 2: Análise Avançada"
    ])

    if page == "Página 1: Métricas Gerais":
        st.title("Análise de Dados de Clientes da Megaline")

        # Descrição geral do dashboard
        st.markdown("""
            Este dashboard fornece uma análise interativa dos dados dos clientes da Megaline. 
            Utilize os seletores abaixo para visualizar métricas e gráficos específicos para cada plano de assinatura.
        """)

        # Seletor de múltiplos planos (nenhum selecionado por padrão)
        selected_plans = st.multiselect("Escolha os Planos", users['plan'].unique(), default=[])

        # Filtrar dados de acordo com os planos selecionados
        filtered_users = users[users['plan'].isin(selected_plans)] if selected_plans else users
        filtered_calls = calls[calls['user_id'].isin(filtered_users['user_id'])]
        filtered_messages = messages[messages['user_id'].isin(filtered_users['user_id'])]
        filtered_internet = internet[internet['user_id'].isin(filtered_users['user_id'])]
        filtered_revenue = total_revenue_per_user[total_revenue_per_user['user_id'].isin(filtered_users['user_id'])]

        # Calculando métricas principais baseadas nos planos selecionados
        total_users = filtered_users['user_id'].nunique()
        total_calls = filtered_calls['id'].count()
        total_messages = filtered_messages['id'].count()
        total_internet_usage_mb = filtered_internet['mb_used'].sum()
        total_revenue = filtered_revenue['total_revenue'].sum()

        st.markdown("### Métricas Principais")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total de Usuários", total_users)
        col2.metric("Total de Chamadas", total_calls)
        col3.metric("Total de Mensagens", total_messages)
        col4.metric("Uso Total de Internet (GB)", f"{total_internet_usage_mb / 1024:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col5.metric("Receita Total (USD)", f"${total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Criar gráficos de desempenho se houver planos selecionados
        if selected_plans:
            st.markdown("### Índices de Desempenho")
            criar_graficos_desempenho(total_users, total_calls, total_messages, total_internet_usage_mb, total_revenue, users, calls, messages, internet)

            # Criar histograma de idades dos assinantes por plano
            criar_histograma_idade_por_plano(filtered_users)
        else:
            st.warning("Por favor, selecione pelo menos um plano para visualizar os gráficos.")

        # Criar gráfico de heatmap
        criar_grafico_heatmap(filtered_users)

    elif page == "Página 2: Análise Avançada":
        st.title("Análise Avançada de Uso e Receita dos Clientes")

        st.markdown("""
            Esta página oferece uma análise mais detalhada do uso de serviços e da receita gerada pelos clientes da Megaline.
            Explore os gráficos abaixo para insights avançados.
        """)

        criar_graficos_segunda_pagina(users, calls, messages, internet, plans)

if __name__ == "__main__":
    main()
