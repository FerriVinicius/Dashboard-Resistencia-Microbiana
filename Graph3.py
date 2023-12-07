import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

def graph3():
    st.header("Quantidade Total de Casos e Ranking de Alas por Infecções")

    col1, col2, col3 = st.columns([1, 1, 2])

    # Carregar os dados do CSV
    url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
    df = pd.read_csv(url)

    # Converter a coluna de datas
    df['dh_recebimento_exame'] = pd.to_datetime(df['dh_recebimento_exame'])

    # Botões para seleção de período
    periodo_opcao = col1.radio("3- Selecione o período:", ["30 dias", "90 dias", "6 meses", "1 ano", "Período completo"])

    # Calcular o período correspondente
    if periodo_opcao == "30 dias":
        data_maxima = df['dh_recebimento_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=30)
    elif periodo_opcao == "90 dias":
        data_maxima = df['dh_recebimento_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=90)
    elif periodo_opcao == "6 meses":
        data_maxima = df['dh_recebimento_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(months=6)
    elif periodo_opcao == "1 ano":
        data_maxima = df['dh_recebimento_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(years=1)
    else:  # Período completo
        data_inicial = df['dh_recebimento_exame'].min().date()
        data_maxima = df['dh_recebimento_exame'].max().date()

    # Adicionar filtro de período
    filtro_periodo = col1.date_input('3- Selecione o período:', [data_inicial, data_maxima])

    # Converter para numpy.datetime64
    filtro_periodo = [np.datetime64(date) for date in filtro_periodo]

    # Aplicar filtro de período
    df_filtrado = df[(df['dh_recebimento_exame'] >= filtro_periodo[0]) & (df['dh_recebimento_exame'] <= filtro_periodo[1])]

    # Contabilizar a quantidade total de casos
    total_casos = len(df_filtrado)

    # Ranquear as alas por maior número de infecções
    ranking_alas = df_filtrado['ds_ala_coleta'].value_counts().reset_index()
    ranking_alas.columns = ['Ala', 'Número de Infecções']
    ranking_alas = ranking_alas.sort_values(by='Número de Infecções', ascending=False)

    # Ranquear os microorganismos mais encontrados
    ranking_microorganismos = df_filtrado['cd_sigla_microorganismo'].value_counts().reset_index()
    ranking_microorganismos.columns = ['Microorganismo', 'Número de Casos']
    ranking_microorganismos = ranking_microorganismos.sort_values(by='Número de Casos', ascending=False)

    # Exibir resultados
    col2.write(f"Quantidade Total de Casos: {total_casos}")
    col3.dataframe(ranking_alas, use_container_width=True, hide_index=True)
    col2.write("Ranking de Microorganismos mais Encontrados:")
    col2.dataframe(ranking_microorganismos, use_container_width=True, hide_index=True)
