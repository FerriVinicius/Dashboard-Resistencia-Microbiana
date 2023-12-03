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
    
    # Calcular o período dos últimos 30 dias a partir da data máxima em 'dh_admissao_paciente'
    data_maxima = df['dh_admissao_paciente'].max().date()
    data_inicial = data_maxima - pd.DateOffset(days=30)
    
    # Adicionar filtros
    filtro_periodo = col1.date_input('Selecione o período:', [data_inicial, data_maxima])
    
    # Converter para numpy.datetime64
    filtro_periodo = [np.datetime64(date) for date in filtro_periodo]
    
    microorganismos_selecionados = col2.multiselect('Selecione os microorganismos:', df['cd_sigla_microorganismo'].unique())
    
    # Calcular o tempo de internação em dias
    df['tempo_internacao_dias'] = (df['dh_alta_paciente'] - df['dh_admissao_paciente']).dt.days
    
    # Aplicar os filtros
    df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_admissao_paciente'] <= filtro_periodo[1])]
    if microorganismos_selecionados:
        df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    # Adicionar botões para análise dos últimos 30 dias, últimos 90 dias, últimos 6 meses e último ano
    if col1.button('30 Dias'):
        filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(days=30)), filtro_periodo[1]]
        df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_admissao_paciente'] <= filtro_periodo[1])]
        if microorganismos_selecionados:
            df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    if col1.button('90 Dias'):
        filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(days=90)), filtro_periodo[1]]
        df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_admissao_paciente'] <= filtro_periodo[1])]
        if microorganismos_selecionados:
            df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    if col1.button('6 Meses'):
        filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(months=6)), filtro_periodo[1]]
        df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_admissao_paciente'] <= filtro_periodo[1])]
        if microorganismos_selecionados:
            df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    if col1.button('1 Ano'):
        filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(years=1)), filtro_periodo[1]]
        df_filtrado = df[(df['dh_admissao_paciente'] >= filtro_periodo[0]) & (df['dh_admissao_paciente'] <= filtro_periodo[1])]
        if microorganismos_selecionados:
            df_filtrado = df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)]
    
    # Adicionar botão para análise de todo o período para o microorganismo selecionado
    analise_periodo_completo = col1.button('Período Completo')
    if analise_periodo_completo:
        df_filtrado = df[(df['dh_admissao_paciente'] >= df['dh_admissao_paciente'].min()) & (df['dh_admissao_paciente'] <= df['dh_admissao_paciente'].max())]
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
        st.write(f"Período: {filtro_periodo[0]} a {filtro_periodo[1]}")
        st.write(f"Microorganismos: {', '.join(microorganismos_selecionados) if microorganismos_selecionados else 'Todos'}")