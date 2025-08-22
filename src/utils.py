import pandas as pd
import numpy as np
import streamlit as st

def calcular_precificacao_curso(curso, modelo_no_df, numero_alunos, df_matriz_curso, edited_df):
    """
    Calcula a precificação para um curso específico com base nos parâmetros fornecidos.
    """
    uc_rows = []
    if df_matriz_curso.empty or edited_df.empty:
        return pd.DataFrame()

    for _, row_matriz in df_matriz_curso.iterrows():
        new_uc_row = {}
        new_uc_row['UC'] = row_matriz['UC']
        new_uc_row['Semestre'] = row_matriz['Semestre']

        rows = []
        for _, row_param in edited_df[edited_df['parametro']=='max_alunos_turma'].iterrows():
            new_row = {}
            new_row['curso'] = curso
            new_row['modelo'] = modelo_no_df
            new_row['categoria'] = row_param['categoria']
            new_row['ator_pedagogico'] = row_param['ator_pedagogico']
            new_row['qtde_turmas'] = np.ceil(numero_alunos / row_param['valor'])
            rows.append(new_row)
        df_precificacao_uc = pd.DataFrame(rows, columns=["curso","modelo","categoria","ator_pedagogico","qtde_turmas"])

        # Fazendo join para trazer ch
        df_ch_semanal = edited_df[edited_df['parametro'] == 'ch_semanal'].copy().drop(columns=['modelo', 'ator_pedagogico','parametro']).rename(mapper={"valor": "ch_semanal"}, axis=1)
        df_precificacao_uc = df_precificacao_uc.merge(right=df_ch_semanal, how='left',on='categoria')
        df_precificacao_uc['ch_ator_pedagogico'] = df_precificacao_uc['qtde_turmas'] * df_precificacao_uc['ch_semanal']
        
        # Fazendo join para trazer remuneração
        df_ch_remuneracao = edited_df[edited_df['parametro'] == 'remuneracao_hora'].copy().drop(columns=['modelo', 'ator_pedagogico','parametro']).rename(mapper={"valor": "remuneracao_hora"}, axis=1)
        df_precificacao_uc = df_precificacao_uc.merge(right=df_ch_remuneracao, how='left',on='categoria')
        df_precificacao_uc['custo_docente_am'] = df_precificacao_uc['ch_ator_pedagogico'] * 5.25 * 1.7 * df_precificacao_uc['remuneracao_hora']
        df_precificacao_uc['custo_docente_as'] = df_precificacao_uc['custo_docente_am'] * 6 
        
        new_uc_row['Precificacao'] = df_precificacao_uc
        uc_rows.append(new_uc_row)
    
    df_precificacao_curso = pd.DataFrame(uc_rows)
    
    try:
        df_precificacao_curso['total_uc_am'] = df_precificacao_curso['Precificacao'].apply(lambda df: df['custo_docente_am'].sum())
        df_precificacao_curso['total_uc_as'] = df_precificacao_curso['Precificacao'].apply(lambda df: df['custo_docente_as'].sum())
        df_precificacao_curso['total_ch_uc'] = df_precificacao_curso['Precificacao'].apply(lambda df: pd.to_numeric(df['ch_ator_pedagogico'], errors='coerce').sum())
    except (TypeError, KeyError) as e:
        st.error(f"Não foi possível calcular os totais por UC. Erro: {e}")
        return pd.DataFrame()

    return df_precificacao_curso