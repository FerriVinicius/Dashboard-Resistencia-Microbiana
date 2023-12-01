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
st.header("Programa de Monitoramento de Resistência Microbiana")

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
    tab1, tab2, tab3 = st.tabs(["Internações", "Microorganismos", "Alas"])
    with tab1:
        st.header("Tempo Médio de Internação por Microorganismo")
        
        
        col1, col2, col3 = st.columns([1, 1, 2])
               
  
        # Carregar os dados do CSV
        url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
        df = pd.read_csv(url)
        
        df['dh_admissao_paciente'] = pd.to_datetime(df['dh_admissao_paciente'])
        df['dh_alta_paciente'] = pd.to_datetime(df['dh_alta_paciente'])
        
        # Calcular o período dos últimos 30 dias a partir da data máxima em 'dh_alta_paciente'
        data_maxima = df['dh_alta_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=30)
        
        # Adicionar filtros
        filtro_periodo = col1.date_input('Selecione o período:', [data_inicial, data_maxima])
        
        # Converter para numpy.datetime64
        filtro_periodo = [np.datetime64(date) for date in filtro_periodo]
        
        microorganismos_selecionados = col2.multiselect('Selecione os microorganismos:', df['cd_sigla_microorganismo'].unique())
        # Adicionar botões para análise dos últimos 30 dias, últimos 90 dias, últimos 6 meses e último ano
        if col1.button('30 Dias'):
            filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(days=30)), filtro_periodo[1]]
        
        if col1.button('90 Dias'):
            filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(days=90)), filtro_periodo[1]]
        
        if col1.button('6 Meses'):
            filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(months=6)), filtro_periodo[1]]
        
        if col1.button('1 Ano'):
            filtro_periodo = [np.datetime64(filtro_periodo[1] - pd.DateOffset(years=1)), filtro_periodo[1]]
        
        # Adicionar botão para análise de todo o período para o microorganismo selecionado
        analise_periodo_completo = col1.button('Período Completo')
        
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
        
        resumo_microorganismo = resumo_microorganismo.rename(columns={
        'cd_sigla_microorganismo': 'Microorganismo',
        'media_tempo_internacao': 'Média Tempo Internação',
        'total_admissoes': 'Admissões'
        })
        resumo_microorganismo = resumo_microorganismo.set_index('Microorganismo')
        
        
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
                chart_completo = col1.alt.Chart(df_analise_completa).mark_line().encode(
                    x=alt.X('dh_admissao_paciente:T', title='Data de Admissão'),
                    y=alt.Y('tempo_internacao_dias:Q', title='Média Tempo de Internação'),
                    color=alt.Color('cd_sigla_microorganismo:N', title='Microorganismo')
                ).properties(
                    width=400,
                    height=200
                )
                st.altair_chart(chart_completo, use_container_width=True)
            
            else:
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
                col3.dataframe(resumo_microorganismo, use_container_width=True)
        
                # Adicionar informações sobre os filtros selecionados
                st.write(f"Período: {filtro_periodo[0]} a {filtro_periodo[1]}")
                st.write(f"Microorganismos: {', '.join(microorganismos_selecionados) if microorganismos_selecionados else 'Todos'}")
        else:
            st.write("Nenhum dado disponível para o período e/ou microorganismos escolhidos.")
else:
    st.stop()





