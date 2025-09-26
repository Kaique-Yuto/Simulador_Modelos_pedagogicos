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
            return (len(row)-2)*['background-color: #282c34 ; color:yellow'] + ['font-weight: bold; background-color: #273333; color: yellow'] * 2
        return [''] * len(row)
    
    df.drop(columns=["CH por Semestre_Assíncrono", "CH por Semestre_Presencial",
                     "CH por Semestre_Síncrono","CH por Semestre_Síncrono Mediado"], inplace=True, errors='ignore')
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
        "CH Semanal": column_config.NumberColumn("CH Semanal", format="%d"),
        "Custo Docente por Semestre_Assíncrono": column_config.NumberColumn("Custo CH Assíncrona"),
        "Custo Docente por Semestre_Presencial": column_config.NumberColumn("Custo CH Presencial"),
        "Custo Docente por Semestre_Síncrono": column_config.NumberColumn("Custo CH Síncrona"),
        "Custo Docente por Semestre_Síncrono Mediado": column_config.NumberColumn("Custo CH Síncrona Mediada"),
        "CH Total": column_config.NumberColumn("CH Total", format="%d"),
        "Eficiência da UC": column_config.NumberColumn("Eficiência da UC", format="%2f"),
        "Qtde Turmas": column_config.NumberColumn("Qtde Turmas", format="%d"),
        "Base de Alunos": column_config.NumberColumn("Base de Alunos", format="%d"),
        "Semestre": column_config.TextColumn("Semestre")
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
    df = df[df["Custo Total"] >0]
    df = df.style.format(formatador_mestre)
    df = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    return df


def formatar_df_pivot_custo(df:pd.DataFrame):
    def highlight_total(row):
        if "Polo" in row and row["Polo"] == "Total Geral":
            return (len(row)-2)*['background-color: #282c34; color:yellow'] + ['font-weight: bold; background-color: #273333; color: yellow'] * 2
        return [''] * len(row)
    colunas_numericas = df.select_dtypes(include='number').columns

    # Cria o dicionário de formatação apenas para essas colunas
    formatador = {
        col: lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.') 
        for col in colunas_numericas
    }

    return st.dataframe(
        df.style.apply(highlight_total, axis=1).format(formatador),
        use_container_width=True
    )


def formatar_df_rateio_polo(df:pd.DataFrame, receita:bool):
    def highlight_total(row):
        if "Polo" in row and row["Polo"] == "Total Geral":
            return (len(row)-2)*['background-color: #282c34; color:yellow'] + ['font-weight: bold; background-color: #273333; color: yellow'] * 2
        return [''] * len(row)
    # Garante que a ordem das colunas está correta
    colunas_ordenadas = ["Polo", "Base Alunos no Polo", "% de Alunos", "Custo Rateado", "% de Custo"]
    if receita:
        colunas_ordenadas.insert(3, "Receita do Polo")
        colunas_ordenadas.insert(4, "% Receita")
        colunas_ordenadas.insert(7, "Margem do Polo")
    df = df[colunas_ordenadas]
    df = df[df["Custo Rateado"]>0]
    formatador_mestre = {
        "Custo Rateado": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        #"Custo Total": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "% de Custo": lambda val: f'{val:.2%}'.replace('.', ','),
        "% de Alunos": lambda val: f'{val:.2%}'.replace('.', ',')
    }
    if receita:
        formatador_mestre["Receita do Polo"] = lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.')
        formatador_mestre["% Receita"] = lambda val: f'{val:.2%}'.replace('.', ',')
        formatador_mestre["Margem do Polo"] = lambda val: f'{val:.2%}'.replace('.', ',')
        df.loc[df["Polo"] == "Total Geral", "Margem do Polo"] = None

        
    df_estilizado = df.style.apply(highlight_total, axis=1).format(formatador_mestre)
    
    return st.dataframe(
        df_estilizado,
        column_config={"Base Alunos no Polo": column_config.NumberColumn(format="%d")},
        use_container_width=True,
        hide_index=True
    )


def formata_df_resumo_semestre(df_resumo_semestre: pd.DataFrame):
    def highlight_total(row):
        if "Chave" in row and row["Chave"] == "Total Geral":
            return (len(row)-2)*['background-color: #282c34 ; color:yellow'] + ['font-weight: bold; background-color: #273333; color: yellow'] * 2
        return [''] * len(row)

    formatador_mestre = {
        "Receita Total": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo/Aluno": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Custo Total": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.'),
        "Lucro": lambda val: f'R$ {val:_.2f}'.replace('.', ',').replace('_', '.')
    }

    column_config_mestre = {
        "Base de Alunos": column_config.NumberColumn("Base de Alunos", format="%d"),
        "CH Semanal": column_config.NumberColumn("CH Semanal", format="%d"),
        "Margem": column_config.NumberColumn("Margem", format='percent'),
        "Eficiência": column_config.NumberColumn("Eficiência", format="%2f"),
        "Semestre": column_config.TextColumn("Semestre")
    }

    formatadores_seguros = {col: func for col, func in formatador_mestre.items() if col in df_resumo_semestre.columns}
    configuracao_segura = {col: cfg for col, cfg in column_config_mestre.items() if col in df_resumo_semestre.columns}

    df_resumo_semestre = df_resumo_semestre.style.apply(highlight_total, axis=1).format(formatadores_seguros)
    df_resumo_semestre = st.dataframe(
        df_resumo_semestre,
        use_container_width=True,
        column_config=configuracao_segura,
        hide_index=True
    )
    return df_resumo_semestre