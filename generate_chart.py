import altair as alt
import numpy as np
import pandas as pd

def generate_stacked_bar_chart(df_by_payment):
    """
    Gera um gráfico de barras empilhadas que compara o faturamento total com o faturamento com e sem NFC.

    Args:
        df_by_payment (pd.DataFrame): DataFrame contendo os dados de faturamento por tipo de pagamento.

    Returns:
        alt.Chart: O objeto do gráfico Altair completo.
    """
    # Cria uma nova coluna para o faturamento sem NFC para o gráfico empilhado
    df_by_payment['faturamento_sem_nfc'] = df_by_payment['faturamento'] - df_by_payment['faturamento_com_nfc']

    # O DataFrame precisa ser 'tidy' para o Altair, então vamos derreter os dados
    df_stacked = df_by_payment.melt(
        id_vars=['tipo_de_pagamento'],
        value_vars=['faturamento_com_nfc', 'faturamento_sem_nfc'],
        var_name='Tipo de Faturamento',
        value_name='Valor'
    )
    
    # Corrige o erro: relabeling os dados para a legenda e tooltip.
    df_stacked['Tipo de Faturamento'] = df_stacked['Tipo de Faturamento'].apply(
        lambda x: 'Com NFC' if x == 'faturamento_com_nfc' else 'Sem NFC'
    )

    # Gráfico de barras empilhadas
    chart_stacked_bars = alt.Chart(df_stacked).mark_bar().encode(
        x=alt.X('Valor', title='Faturamento (R$)', axis=alt.Axis(format=".0f") ),
        y=alt.Y('tipo_de_pagamento', title='Tipo de Pagamento'),
        color=alt.Color('Tipo de Faturamento', title='Faturamento'),
        tooltip=[
            alt.Tooltip('tipo_de_pagamento', title='Tipo de Pagamento'),
            alt.Tooltip('Tipo de Faturamento', title='Tipo de Faturamento'),
            alt.Tooltip('Valor', title='Valor (R$)', format=".2f")
        ]
    ).properties(
        title='Faturamento Total (Com e Sem NFC)'
    )

    # Camada de texto para o valor total de cada barra
    # Calculamos o total para cada tipo de pagamento
    df_total_text = df_by_payment.groupby('tipo_de_pagamento')['faturamento'].sum().reset_index()

    text_layer = alt.Chart(df_total_text).mark_text(
        align='left',
        baseline='middle',
        dx=5 # desloca o texto para a direita da barra
    ).encode(
        x=alt.X('faturamento', title='Faturamento (R$)' , axis=alt.Axis(format=".0f")  ),
        y=alt.Y('tipo_de_pagamento', title='Tipo de Pagamento'),
        text=alt.Text('faturamento', format=".2f")
    )

    # Combinamos o gráfico de barras e a camada de texto
    final_chart_stacked_bars = chart_stacked_bars + text_layer
    
    return final_chart_stacked_bars


def generate_pie_chart(df_by_payment):
    # Calcula percentual
    df_by_payment['percentual'] = df_by_payment['faturamento'] / df_by_payment['faturamento'].sum()

    base = alt.Chart(df_by_payment).encode(
        theta=alt.Theta("faturamento", stack=True),
        color=alt.Color("tipo_de_pagamento", title="Tipo de Pagamento")
    ).properties(
        title='Total de Faturamento por Tipo de Pagamento',
        width='container'
    )

    # Camada de pizza
    pie = base.mark_arc(outerRadius=80).encode(
        tooltip=[
            "tipo_de_pagamento",
            alt.Tooltip("faturamento", format=".2f", title="Faturamento"),
            alt.Tooltip("percentual", format=".1%", title="Percentual")
        ]
    )

    # Texto sempre visível
    text = base.mark_text(
        radius=100,                # distância do centro
        fontWeight="bold",         # negrito para destaque
        fontSize=14,               # tamanho do texto
        color="black"              # cor fixa para legibilidade
    ).encode(
        text=alt.Text("percentual", format=".1%")
    )

    # Combina pizza e texto
    chart_by_payment = pie + text
    return chart_by_payment