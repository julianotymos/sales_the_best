import streamlit as st
from read_sales_report import read_sales_report
from datetime import datetime, timedelta
import altair as alt

def tab_sales_total(start_date, end_date):
    """
    Exibe o conteúdo da aba "Resumo Geral" do dashboard de vendas,
    incluindo as métricas e análises do 99food.
    """
    st.header("Metricas Totais - Resumo Geral")

    daily_sales_df, total_sales_df = read_sales_report(start_date, end_date)
    
    if not total_sales_df.empty:
        total_row = total_sales_df.iloc[0]
        
        # O NÚMERO DE COLUNAS FOI AUMENTADO DE 9 PARA 12
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns(12)
        
        with col1:
            st.metric("Total Geral", f"{total_row['Total Geral']:.2f}")
        with col2:
            # O CÁLCULO DE QTD. TOTAL DE VENDAS FOI ATUALIZADO PARA INCLUIR O 99FOOD
            st.metric("Qtd. Total de Vendas", int(total_row['Qtd. Vendas Loja'] + total_row['Qtd. Vendas iFood'] + total_row['Qtd. Vendas 99food']))
        with col3:
            st.metric("Ticket Medio Total", f"{total_row['ticket_medio_total']:.2f}")
        with col4:
            st.metric("Total Loja", f"{total_row['Total Loja']:.2f}")
        with col5:
            st.metric("Qtd. Vendas Loja", int(total_row['Qtd. Vendas Loja']))
        with col6:
            st.metric("Ticket Médio Loja", f"{total_row['Ticket Médio Loja']:.2f}")
        with col7:
            st.metric("Total iFood", f"{total_row['Total iFood']:.2f}")
        with col8:
            st.metric("Qtd. Vendas iFood", int(total_row['Qtd. Vendas iFood']))
        with col9:
            st.metric("Ticket Médio iFood", f"{total_row['Ticket Médio iFood']:.2f}")
        with col10:
            # NOVAS MÉTRICAS DO 99FOOD ADICIONADAS
            st.metric("Total 99food", f"{total_row['Total 99food']:.2f}")
        with col11:
            st.metric("Qtd. Vendas 99food", int(total_row['Qtd. Vendas 99food']))
        with col12:
            st.metric("Ticket Médio 99food", f"{total_row['Ticket Médio 99food']:.2f}")
        
        st.markdown("---")
        
        st.header("Análise Diária de Vendas")
        st.subheader("Gráfico de Vendas por Canal")
        
        # O DATAFRAME `df_long` FOI ATUALIZADO PARA INCLUIR O NOVO CANAL
        df_long = daily_sales_df.melt(
            id_vars=['Data da Venda'],
            # 'Total 99food' foi adicionado à lista de variáveis
            value_vars=['Total Loja', 'Total iFood', 'Total 99food', 'Total Geral'],
            var_name='Categoria',
            value_name='Valor'
        )

        # Criação do gráfico Altair
        chart = alt.Chart(df_long).mark_line(point=True).encode(
            x=alt.X('Data da Venda:T', title=None),
            y=alt.Y(
                'Valor:Q',
                title=None,
                axis=alt.Axis(format='.0f')  # Remove separador de milhar
            ),
            color=alt.Color('Categoria:N', title='Categoria', legend=alt.Legend(
                orient="bottom", 
                direction="horizontal",
                columns=2
            )),
            tooltip=[
                alt.Tooltip('Data da Venda:T', title='Data da Venda'),
                alt.Tooltip('Categoria:N', title='Categoria'),
                alt.Tooltip('Valor:Q', title='Valor (R$)', format=".2f")
            ]
        ).properties(
            width=700,
            height=400
        )

        st.altair_chart(chart, use_container_width=True)
        
        st.subheader("Tabela de Dados Detalhada")
        st.dataframe(daily_sales_df.set_index('Data da Venda'))
    else:
        st.warning("⚠️ Não há dados de vendas para o período selecionado. Por favor, ajuste o filtro de datas.")
