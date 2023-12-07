import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

def graph1():
    st.header("Tempo Médio de Internação por Microorganismo")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    # Carregar os dados do CSV
    url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
    df = pd.read_csv(url)
    
    df['dh_admissao_paciente'] = pd.to_datetime(df['dh_admissao_paciente'])
    df['dh_alta_paciente'] = pd.to_datetime(df['dh_alta_paciente'])
    
    # Botões para seleção de período
    periodo_opcao = col1.radio("4- Selecione o período:", ["30 dias", "90 dias", "6 meses", "1 ano", "Período completo"])
    
    # Calcular o período correspondente
    if periodo_opcao == "30 dias":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=30)
    elif periodo_opcao == "90 dias":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=90)
    elif periodo_opcao == "6 meses":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(months=6)
    elif periodo_opcao == "1 ano":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(years=1)
    else:  # Período completo
        data_inicial = df['dh_admissao_paciente'].min().date()
        data_maxima = df['dh_admissao_paciente'].max().date()
    
    # Adicionar filtro de período
    filtro_periodo = col1.date_input('4- Selecione o período:', [data_inicial, data_maxima])
    
    # Converter para numpy.datetime64
    filtro_periodo = [np.datetime64(date) for date in filtro_periodo]
    
    microorganismos_selecionados = col2.multiselect('4- Selecione os microorganismos:', df['cd_sigla_microorganismo'].unique())
    
    # Calcular o tempo de internação em dias
    df['tempo_internacao_dias'] = (df['dh_alta_paciente'] - df['dh_admissao_paciente']).dt.days
    
    # Aplicar os filtros
    df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_admissao_paciente'] <= filtro_periodo[1])]
    if microorganismos_selecionados:
        df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    # Verificar se há dados para o período selecionado
    if not df_filtrado.empty:
        # Criar gráfico para o período selecionado usando Altair
        chart = alt.Chart(df_filtrado).mark_line().encode(
            x=alt.X('dh_admissao_paciente:T', title='Data de Admissão'),
            y=alt.Y('tempo_internacao_dias:Q', title='Média Tempo de Internação'),
            color=alt.Color('cd_sigla_microorganismo:N', title='Microorganismo')
        ).properties(
            width=400,
            height=200
        )
    
        col3.altair_chart(chart, use_container_width=True)
    
        # Exibir resumo no DataFrame abaixo do gráfico
        resumo_microorganismo = df_filtrado.groupby('cd_sigla_microorganismo').agg(
            media_tempo_internacao=pd.NamedAgg(column='tempo_internacao_dias', aggfunc='mean'),
            total_admissoes=pd.NamedAgg(column='tempo_internacao_dias', aggfunc='count')
        ).reset_index()
    
        resumo_microorganismo = resumo_microorganismo.rename(columns={
            'cd_sigla_microorganismo': 'Microorganismo',
            'media_tempo_internacao': 'Média Tempo Internação',
            'total_admissoes': 'Admissões'
        })
    
        col3.dataframe(resumo_microorganismo, use_container_width=True, hide_index=True)
    
        # Adicionar informações sobre os filtros selecionados
        st.write(f"Microorganismos: {', '.join(microorganismos_selecionados) if microorganismos_selecionados else 'Todos'}")
        st.write(f"Período: {filtro_periodo[0]} a {filtro_periodo[1]}")
