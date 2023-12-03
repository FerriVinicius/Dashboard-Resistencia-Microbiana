import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def graph2():
    st.header("Sensibilidade aos Antibióticos por Microorganismo")

    col1, col2, col3 = st.columns([1, 1, 2])

    # Carregar os dados do CSV
    url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
    df = pd.read_csv(url)

    # Converter a coluna de datas
    df['dh_liberacao_exame'] = pd.to_datetime(df['dh_liberacao_exame'])

    # Botões para seleção de período
    periodo_opcao = col1.radio("Selecione o período:", ["30 dias", "90 dias", "6 meses", "1 ano", "Período completo"])

    # Calcular o período correspondente
    if periodo_opcao == "30 dias":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=30)
    elif periodo_opcao == "90 dias":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=90)
    elif periodo_opcao == "6 meses":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(months=6)
    elif periodo_opcao == "1 ano":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(years=1)
    else:  # Período completo
        data_inicial = df['dh_liberacao_exame'].min().date()
        data_maxima = df['dh_liberacao_exame'].max().date()

    # Adicionar filtro de período
    filtro_periodo = col1.date_input('Selecione o período:', [data_inicial, data_maxima])

    # Converter para numpy.datetime64
    filtro_periodo = [np.datetime64(date) for date in filtro_periodo]

    # Aplicar filtro de período
    df_filtrado = df[(df['dh_liberacao_exame'] >= filtro_periodo[0]) & (df['dh_liberacao_exame'] <= filtro_periodo[1])]

    # Adicionar filtros
    microorganismos_selecionados = col2.multiselect(
        'Selecione os microorganismos:',
        df_filtrado['cd_sigla_microorganismo'].unique(),
        key='microorganismos_multiselect'
    )

    # Verificar se há dados para os microorganismos selecionados
    if not df_filtrado[df_filtrado['cd_sigla_microorganismo'].isin(microorganismos_selecionados)].empty:
        # Criar gráfico para a sensibilidade aos antibióticos usando Altair
        chart = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('ds_antibiotico_microorganismo:N', title='Antibiótico'),
            y=alt.Y('count():Q', title='Contagem'),
            color=alt.Color('cd_interpretacao_antibiograma:N', title='Interpretação')
        ).properties(
            width=400,
            height=200
        )

        col3.altair_chart(chart, use_container_width=True)

        # Exibir resumo no DataFrame abaixo do gráfico
        resumo_antibioticos = df_filtrado.groupby(['ds_antibiotico_microorganismo', 'cd_interpretacao_antibiograma']).size().unstack(fill_value=0)
        resumo_antibioticos = resumo_antibioticos.reset_index()

        col3.dataframe(resumo_antibioticos, use_container_width=True, hide_index=True)

        # Adicionar informações sobre os microorganismos selecionados
        st.write(f"Microorganismos: {', '.join(microorganismos_selecionados) if microorganismos_selecionados else 'Todos'}")
        st.write(f"Período: {filtro_periodo[0]} a {filtro_periodo[1]}")
