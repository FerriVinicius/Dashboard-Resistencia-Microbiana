##importa bibliotecas e funções úteis para o programa
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from Authenticate import check_password

##muda o título da página na aba do navegador
st.set_page_config(
    page_title="Dashboard - Einstein PMRM",
    page_icon="📊",
    layout="wide",
    )

##esconde a barra de acesso lateral durante o login do usuário
hide_bar= """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        visibility:hidden;
        width: 0px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        visibility:hidden;
    }
    </style>
"""

if check_password() == True:
    # Carregar os dados do CSV
    url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
    df = pd.read_csv(url)
    
    # Converter as colunas de data para o formato apropriado
    df['dh_admissao_paciente'] = pd.to_datetime(df['dh_admissao_paciente'])
    df['dh_alta_paciente'] = pd.to_datetime(df['dh_alta_paciente'])
    
    # Adicionar filtros interativos
    filtro_periodo = st.date_input('Selecione o período:', [df['dh_admissao_paciente'].min().date(), df['dh_alta_paciente'].max().date()])
    # Converter para numpy.datetime64
    filtro_periodo = [np.datetime64(date) for date in filtro_periodo]
    
    microorganismos_selecionados = st.multiselect('Selecione os microorganismos:', df['cd_sigla_microorganismo'].unique())
    
    # Adicionar botão para análise de todo o período para o microorganismo selecionado
    analise_periodo_completo = st.button('Analisar Todo o Período para o Microorganismo Selecionado')
    
    # Aplicar os filtros
    df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_alta_paciente'] <= filtro_periodo[1])]
    if microorganismos_selecionados:
        df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    # Calcular o tempo de internação em dias
    df_filtrado['tempo_internacao_dias'] = (df_filtrado['dh_alta_paciente'] - df_filtrado['dh_admissao_paciente']).dt.days
    
    # Agrupar por microorganismo, calculando a média e o total de admissões para cada grupo
    resumo_microorganismo = df_filtrado.groupby('cd_sigla_microorganismo').agg(
        media_tempo_internacao=pd.NamedAgg(column='tempo_internacao_dias', aggfunc='mean'),
        total_admissoes=pd.NamedAgg(column='tempo_internacao_dias', aggfunc='count')
    ).reset_index()
    
    # Criar o aplicativo Streamlit
    st.write('Tempo de Internação por Microorganismo')
    
    # Verificar se há dados para o período selecionado
    if not df_filtrado.empty:
        # Verificar se o botão foi clicado
        if analise_periodo_completo:
            df_analise_completa = df[df['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
            # Calcular o tempo de internação em dias para o período completo
            df_analise_completa['tempo_internacao_dias'] = (df_analise_completa['dh_alta_paciente'] - df_analise_completa['dh_admissao_paciente']).dt.days
    
            # Agrupar por microorganismo, calculando a média e o total de admissões para cada grupo
            resumo_microorganismo_completo = df_analise_completa.groupby('cd_sigla_microorganismo').agg(
                media_tempo_internacao=pd.NamedAgg(column='tempo_internacao_dias', aggfunc='mean'),
                total_admissoes=pd.NamedAgg(column='tempo_internacao_dias', aggfunc='count')
            ).reset_index()
    
            # Exibir resumo no DataFrame abaixo do gráfico
            st.dataframe(resumo_microorganismo_completo, use_container_width=True)
    
            # Criar gráfico para o período completo usando Altair
            chart_completo = alt.Chart(df_analise_completa).mark_line().encode(
                x='dh_admissao_paciente:T',
                y='tempo_internacao_dias:Q',
                color='cd_sigla_microorganismo:N'
            ).properties(
                width=800,
                height=400
            )
    
            st.altair_chart(chart_completo, use_container_width=True)
        else:
            # Criar gráfico para o período selecionado usando Altair
            chart = alt.Chart(df_filtrado).mark_line().encode(
                x='dh_admissao_paciente:T',
                y='tempo_internacao_dias:Q',
                color='cd_sigla_microorganismo:N'
            ).properties(
                width=800,
                height=400
            )
    
            st.altair_chart(chart, use_container_width=True)
    
            # Exibir resumo no DataFrame abaixo do gráfico
            st.dataframe(resumo_microorganismo, use_container_width=True)
    
            # Adicionar informações sobre os filtros selecionados
            st.write(f"Filtrado por período de {filtro_periodo[0]} a {filtro_periodo[1]}")
            st.write(f"Microorganismos selecionados: {', '.join(microorganismos_selecionados) if microorganismos_selecionados else 'Todos'}")
    else:
        st.write("Nenhum dado disponível para o período selecionado e os microorganismos escolhidos.")
else:
    st.stop()
