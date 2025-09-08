import streamlit as st
from read_sales_by_payment_type_report import read_sales_by_payment_type_report
from generate_chart import generate_stacked_bar_chart, generate_pie_chart
from babel.numbers import format_currency

def tab_sales_by_payment(start_date, end_date):
    """
    Exibe o conteúdo da aba "Vendas por Pagamento" do dashboard de vendas.
    """
    st.header("Métricas Totais - Vendas por Pagamento Loja")

    df_detailed, df_by_payment, df_total_summary = read_sales_by_payment_type_report(start_date, end_date)
    
    if not df_total_summary.empty:
        total_row = df_total_summary.iloc[0]
        
        col1, col2, col3, col4, col5 ,col6 , col7  = st.columns(7)
        with col1:
            st.metric("Faturamento Total", format_currency(total_row['faturamento'], 'BRL', locale='pt_BR'))
        with col2:
            st.metric("Total de Vendas", int(total_row['total_vendas']))
        with col3:
            st.metric("Faturamento com NFC", format_currency(total_row['faturamento_com_nfc'], 'BRL', locale='pt_BR'))
        with col4:
            st.metric("Qtd. de NFC", int(total_row['quantidade_de_nfc']))
        with col5:
            st.metric("Fat. sem NFC", format_currency(total_row['faturamento'] - total_row['faturamento_com_nfc'] , 'BRL', locale='pt_BR'))
        with col6:
            st.metric("Fat. com NFC Sorvete", format_currency(total_row['nfc_sorvete'], 'BRL', locale='pt_BR'))
        with col7:
            st.metric("Qtd. de NFC Sorvete", int(total_row['quantidade_de_nfc_sorvete']))

        st.markdown("---")
        
        st.header("Análise Detalhada")
        
        st.subheader("Faturamento por Tipo de Pagamento")
        chart_by_payment = generate_pie_chart(df_by_payment)
        st.altair_chart(chart_by_payment, use_container_width=True)

        st.markdown("---")
        
        st.subheader("Faturamento com e sem NFC por Tipo de Pagamento")
        colunas_para_formatar = ['faturamento', 'faturamento_com_nfc', 'nfc_sorvete']
    
        final_chart_stacked_bars = generate_stacked_bar_chart(df_by_payment)
        st.altair_chart(final_chart_stacked_bars, use_container_width=True)

        st.markdown("---")
        
        #st.subheader("Faturamento Diário Total")
        
        #st.dataframe(total_row.set_index('faturamento'))

        st.subheader("Tabela de Dados Detalhada por periodo")
        #colunas_para_formatar = ['faturamento', 'faturamento_com_nfc', 'nfc_sem_venda']
        st.dataframe(df_by_payment.set_index('tipo_de_pagamento'))

       
        st.subheader("Tabela de Dados Detalhada por dia")

        st.dataframe(df_detailed.set_index('data'))

    else:
        st.warning("⚠️ Não há dados de vendas para o período selecionado. Por favor, ajuste o filtro de datas.")
