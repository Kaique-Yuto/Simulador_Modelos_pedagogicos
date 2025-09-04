import streamlit as st
import pandas as pd
import locale
from streamlit import column_config

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def colorir_semestres(row: pd.Series):
    """Aplica uma cor de fundo diferente para linhas de semestres pares."""
    cor = "#2e2f31"
    if row['Semestre'] % 2 == 0:
        return [f'background-color: {cor}'] * len(row)
    return [''] * len(row)

def formatador_k(valor, pos):
    """
    Recebe um valor e o formata para o padrão 'R$ Xk'.
    Ex: 10000 -> R$ 10k
    """
    return f'R$ {int(valor / 1000)}k'

def format_currency(value):
    return locale.currency(value, grouping=True, symbol=True)

def formatar_valor_brl(valor):
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    if isinstance(valor, (int, float)):
        return f'R$ {valor:_.2f}'.replace('.', ',').replace('_', '.')
    return valor

def formatar_df_precificacao_oferta(df:pd.DataFrame):
    def highlight_total(row):
        if "Chave" in row and row["Chave"] == "Total Geral":
            return (len(row)-2)*['background-color: #282c34'] + ['font-weight: bold; background-color: #273333'] * 2
        return [''] * len(row)
        # --- Dicionários Mestre com TODAS as configurações possíveis ---

    # 1. Dicionário para a formatação de valores (st.style.format)
    formatador_mestre = {
        "Custo Total": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Docente por Semestre_Assíncrono": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Docente por Semestre_Presencial": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Docente por Semestre_Síncrono": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Docente por Semestre_Síncrono Mediado": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
    }

    # 2. Dicionário para a configuração de colunas (st.dataframe)
    column_config_mestre = {
        "CH por Semestre_Assíncrono": column_config.NumberColumn("CH Assíncrona", format="%d"),
        "CH por Semestre_Presencial": column_config.NumberColumn("CH Presencial", format="%d"),
        "CH por Semestre_Síncrono": column_config.NumberColumn("CH Síncrona", format="%d"),
        "CH por Semestre_Síncrono Mediado": column_config.NumberColumn("CH Síncrona Mediada", format="%d"),
        "Custo Docente por Semestre_Assíncrono": column_config.NumberColumn("Custo CH Assíncrona"),
        "Custo Docente por Semestre_Presencial": column_config.NumberColumn("Custo CH Presencial"),
        "Custo Docente por Semestre_Síncrono": column_config.NumberColumn("Custo CH Síncrona"),
        "Custo Docente por Semestre_Síncrono Mediado": column_config.NumberColumn("Custo CH Síncrona Mediada"),
        "CH Total": column_config.NumberColumn("CH Total", format="%d"),
        "Eficiência da UC": column_config.NumberColumn("Eficiência da UC", format="%2f"),
    }

    # --- Criação dos Dicionários Seguros ---

    # Filtra os dicionários para conter apenas as colunas que REALMENTE existem no DataFrame
    formatadores_seguros = {col: func for col, func in formatador_mestre.items() if col in df.columns}
    configuracao_segura = {col: cfg for col, cfg in column_config_mestre.items() if col in df.columns}

    df = df.style.apply(highlight_total, axis=1).format(formatadores_seguros)
    df = st.dataframe(
        df,
        use_container_width=True,
        column_config=configuracao_segura,
        hide_index=True
    )
    return df

def formatar_df_rateio(df: pd.DataFrame):
    formatador_mestre = {
        "Custo Total": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Rateado": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.')
    }
    df = df.style.format(formatador_mestre)
    df = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    return df

def formatar_df_rateio_polo(df):
    # Garante que a ordem das colunas está correta
    colunas_ordenadas = ["Polo", "Base Alunos no Polo", "Base Alunos Total", "% de Alunos", "Custo Rateado", "Custo Total", "% de Custo"]
    df = df[colunas_ordenadas]

    formatador_mestre = {
        "Custo Rateado": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Total": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "% de Custo": lambda val: f'{val:.2%}'.replace('.', ','),
        "% de Alunos": lambda val: f'{val:.2%}'.replace('.', ',')
    }
    
    df_estilizado = df.style.format(formatador_mestre)
    
    return st.dataframe(
        df_estilizado,
        use_container_width=True,
        hide_index=True
    )