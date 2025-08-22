import pandas as pd
import numpy as np
import streamlit as st
from streamlit import column_config
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from .formatting import formatador_k

def obter_modelos_para_curso(df: pd.DataFrame, nome_curso: str) -> list:
    """
    Garante a árvore de escolhas para a configuração de cursos
    
    Args:
        df (pd.DataFrame): O dataframe com a dimensão de cursos e modelos.
        nome_curso (str): O nome do curso a ser filtrado.
        
    Returns:
        list: Uma lista com os nomes dos modelos disponíveis.
    """
    try:
        modelos_disponiveis = df[df['Curso'] == nome_curso]['Modelo'].unique().tolist()
        return modelos_disponiveis
    except (KeyError, Exception):
        # Retorna lista vazia se o curso não for encontrado ou ocorrer outro erro
        return []

def plot_custo_docente(df_precificacao_curso):
    # Agregar os dados
    df_plot = df_precificacao_curso.groupby('Semestre').agg(func='sum')

    # Criar a figura
    fig, ax = plt.subplots(figsize=(10, 8.5))

    # Fundo e cores
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    bar_color = '#1f77b4'

    # Gráfico de barras
    bars = ax.bar(
        df_plot.index,
        df_plot['total_uc_as'],
        color=bar_color
    )

    # Aumenta o limite superior do eixo Y para dar espaço para as labels
    ax.set_ylim(top=df_plot['total_uc_as'].max() * 1.15)

    # Adicionar data labels formatados em moeda brasileira
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if i % 2 == 0:
            y_position = height + (df_plot['total_uc_as'].max() * 0.05)
        else:
            y_position = height

        ax.text(
            bar.get_x() + bar.get_width()/2,
            y_position,
            f'R$ {height:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            ha='center',
            va='bottom',
            color='white',
            fontsize=12,
            fontweight='bold'
        )

    formatter = FuncFormatter(formatador_k)
    ax.yaxis.set_major_formatter(formatter)

    ax.tick_params(colors='white', axis='y') # Aplica a cor branca apenas ao eixo y
    ax.tick_params(colors='white', axis='x') # Aplica a cor branca apenas ao eixo x

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel("Custo Docente por Semestre", fontdict={"color": "white", "fontsize": 20})
    return fig

def plot_ch_docente_por_categoria(df_precificacao_curso: pd.DataFrame):
    # Dicionário para acumular totais por categoria
    totais_categoria = {}

    # Itera sobre cada linha do dataframe principal
    for _, row in df_precificacao_curso.iterrows():
        df_precificacao = row["Precificacao"]

        # Soma CH por categoria dentro do dataframe da linha
        soma_categoria = df_precificacao.groupby("Tipo de CH")["ch_ator_pedagogico"].sum()

        # Acumula no dicionário global
        for cat, valor in soma_categoria.items():
            totais_categoria[cat] = totais_categoria.get(cat, 0) + valor

    # Transforma em DataFrame para plotagem
    df_plot = pd.Series(totais_categoria).sort_values(ascending=False)

    # Criar figura
    fig, ax = plt.subplots(figsize=(4,4))

    # Fundo escuro
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Paleta monocromática azul
    colors = ['#1f77b4', '#2c82c9', '#3a9bdc', '#62b0e8', '#8cc7f0']

    # Criar gráfico de rosca
    wedges, texts, autotexts = ax.pie(
        df_plot,
        labels=df_plot.index,
        autopct=lambda p: f'{p:.1f}%',
        startangle=90,
        colors=colors[:len(df_plot)],
        wedgeprops=dict(width=0.4, edgecolor='#0E1117')
    )

    # Ajustar estilo dos textos
    for text in texts:
        text.set_color('white')
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')

    # Título
    ax.set_title("Distribuição da CH Docente por Categoria", color='white', fontsize=10, fontweight='bold')

    return fig

def plotar_indicador_eficiencia(total_ch: float, numero_alunos: int):
    
    eficiencia = np.round(numero_alunos/total_ch,2)
    # Criar figura larga e baixa
    fig, ax = plt.subplots(figsize=(8,1.2))
    # Fundo escuro
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Barra de fundo (0 a 10)
    ax.barh(0, 10, color="#2c2f38", height=0.5)

    # Barra de progresso até a eficiência
    ax.barh(0, eficiencia, color="#1f77b4", height=0.5)

    # Texto com valor no centro
    ax.text(
        5, 0, f"{eficiencia:.2f} / 10",
        ha="center", va="center",
        color="white", fontsize=12, fontweight="bold"
    )

    # Remover eixos e bordas
    ax.set_xlim(0, 10)
    ax.axis("off")
    ax.set_title("Eficiência",{'color': 'white', 'fontweight': 'bold', 'fontsize':16})
    return fig

def plotar_custo_total(df_precificacao_curso: pd.DataFrame)-> float:
    return np.round(float(df_precificacao_curso['total_uc_as'].sum()),2)

def plotar_ch_total(df_precificacao_curso: pd.DataFrame)-> float:
    return np.round(float(df_precificacao_curso['total_ch_uc'].sum()*20),1)

def format_detalhe_precificacao_uc(row: pd.Series) -> st.dataframe:
    df = row["Precificacao"].drop(columns=['Remuneração por Hora', 'CH Semanal'])

    total_am = df["custo_docente_am"].sum()
    total_as = df["custo_docente_as"].sum()

    total_row = {
        "curso": "TOTAL",
        "Modelo": "",
        "Tipo de CH": "",
        "Ator Pedagógico": "",
        "qtde_turmas": "",
        "ch_ator_pedagogico": "",
        "custo_docente_am": total_am,
        "custo_docente_as": total_as,
    }

    df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    # Função para destacar a linha "TOTAL"
    def highlight_total(row):
        if row["curso"] == "TOTAL":
            # Estiliza 8 colunas com fundo e 2 com negrito + fundo
            return 7*['background-color: #282c34'] + ['font-weight: bold; background-color: #273333'] * 2
        return [''] * len(row)
    

    df_styled = df_total.style.apply(highlight_total, axis=1).format({
        # O formato 'R$ {:_.2f}' usa '_' como separador de milhar e ',' como decimal.
        # A função .replace() troca os marcadores para o padrão brasileiro.
        "custo_docente_am": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "custo_docente_as": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.')
    })

    df_format = st.dataframe(
        df_styled, 
        column_config={
            "curso": "Curso",
            "qtde_turmas": column_config.NumberColumn("Turmas",format="%d"),
            "ch_ator_pedagogico": column_config.NumberColumn("CH Semanal",format="%.1f"),
            "custo_docente_am": column_config.NumberColumn("Custo por mês"),
            "custo_docente_as": column_config.NumberColumn("Custo por Semestre"),
        },
        use_container_width=True,
        hide_index=True
    )
    return df_format