import streamlit as st
import pandas as pd
import datetime
from typing import List , Tuple

# Importe a função de conexão do seu arquivo real
from get_conection import get_connection

def read_sales_by_payment_type_report(start_date, end_date) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Busca no banco de dados e retorna DataFrames com dados de vendas
    detalhados, agrupados por tipo de pagamento e um resumo total.

    Args:
        start_date (datetime.date): A data de início para a consulta.
        end_date (datetime.date): A data final para a consulta.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Uma tupla contendo três DataFrames:
            - df_detailed: O DataFrame com os dados detalhados da consulta original.
            - df_by_payment: O DataFrame com os valores totais agrupados por tipo de pagamento.
            - df_total_summary: O DataFrame com a soma de todos os campos numéricos.
                             Retorna DataFrames vazios se a consulta não encontrar dados.
    """
    query = """
    SELECT
        date(created_at) AS Data,
        CASE
            WHEN TYPE = 0 THEN 'Loja'
            WHEN TYPE = 1 THEN 'iFood'
            ELSE 'Outro'
        END AS tipo_de_venda,
        CASE
            WHEN PAYMENT_TYPE = 1 THEN 'Cartão de Crédito'
            WHEN PAYMENT_TYPE = 2 THEN 'Cartão de Débito'
            WHEN PAYMENT_TYPE = 6 THEN 'Pagamento PIX'
            WHEN PAYMENT_TYPE = 0 THEN 'Dinheiro'
            WHEN PAYMENT_TYPE = 4 THEN 'Pagamento Online'
            WHEN PAYMENT_TYPE = 3 THEN 'Ticket'
            ELSE 'Outro'
        END AS tipo_de_pagamento,
        SUM(CASE WHEN abstract_sale = false THEN (amount - CHANGE_AMOUNT) ELSE 0 END) AS faturamento,

        SUM(CASE WHEN abstract_sale = false THEN 1 ELSE 0 END) AS total_vendas,
        SUM(CASE WHEN nfc_url IS NOT NULL AND abstract_sale = false THEN (amount - CHANGE_AMOUNT) ELSE 0 END) AS faturamento_com_nfc,
        SUM(CASE WHEN nfc_url IS NOT NULL AND abstract_sale = false THEN 1 ELSE 0 END) AS quantidade_de_nfc,
        SUM(CASE WHEN nfc_url IS NOT NULL AND product_code_changed = TRUE THEN (amount - CHANGE_AMOUNT) ELSE 0 END) AS nfc_sorvete,
        SUM(CASE WHEN nfc_url IS NOT NULL AND product_code_changed = TRUE THEN 1 ELSE 0 END) AS quantidade_de_nfc_sorvete
    FROM
        sales
    WHERE 1=1
        AND abstract_sale = false
        AND TYPE = 0
        AND date(created_at) >= %s
        AND date(created_at) <= %s
    GROUP BY
        Data,
        tipo_de_venda,
        tipo_de_pagamento
    ORDER BY
        Data Desc,
        tipo_de_venda,
        tipo_de_pagamento
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (start_date, end_date))
                data = cursor.fetchall()

                if data:
                    # Cria o DataFrame detalhado usando os dados e os nomes das colunas
                    column_names = [desc[0] for desc in cursor.description]
                    df_detailed = pd.DataFrame(data, columns=column_names)
                    
                    # Converte colunas numéricas para o tipo correto, incluindo as novas colunas
                    numeric_cols = [
                        'faturamento',
                        'total_vendas',
                        'faturamento_com_nfc',
                        'quantidade_de_nfc',
                        'nfc_sorvete',
                        'quantidade_de_nfc_sorvete'
                    ]
                    for col in numeric_cols:
                        df_detailed[col] = pd.to_numeric(df_detailed[col], errors='coerce')

                    # --- Cria o DataFrame agrupado por tipo de pagamento ---
                    cols_to_sum = numeric_cols
                    df_by_payment = df_detailed.groupby('tipo_de_pagamento')[cols_to_sum].sum().reset_index()

                    # --- Cria o DataFrame com o resumo total ---
                    df_total_summary = df_detailed[cols_to_sum].sum().to_frame().T
                    df_total_summary.insert(0, 'tipo_de_pagamento', 'Total Geral')
                    
                    return df_detailed, df_by_payment, df_total_summary
                else:
                    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar os dados do relatório: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

#start_date = datetime.date(2025, 8, 1) # Primeiro dia de agosto de 2025
#end_date = datetime.date(2025, 8, 10)   # Nono dia de agosto de 2025
#data , df_by_payment ,df_total = read_sales_by_payment_type_report(end_date=end_date , start_date=start_date )
#print(data)
#print(df_by_payment)
#print(df_total)
