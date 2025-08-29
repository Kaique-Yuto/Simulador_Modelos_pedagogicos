import streamlit as st
import pandas as pd

@st.cache_data
def carregar_dados(caminho_arquivo: str):
    """Função genérica para carregar e retornar um DataFrame de um arquivo Excel."""
    try:
        df = pd.read_excel(caminho_arquivo)
        return df
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho_arquivo}' não encontrado. Verifique o caminho.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo '{caminho_arquivo}': {e}")
        return None

@st.cache_data    
def carregar_lista_marca_polo(caminho_arquivo: str):
    """Carrega a lista de marcas e polos de um arquivo CSV e retorna listas únicas."""
    try:
        lista = pd.read_csv(caminho_arquivo, sep=',')
        return lista
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho_arquivo}' não encontrado. Verifique o caminho.")
        return [], []
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo '{caminho_arquivo}': {e}")
        return [], []
    
@st.cache_data
def carregar_base_alunos(caminho_arquivo: str = "databases/base_alunos_curso_marca.csv"):
    df = pd.read_csv(caminho_arquivo,sep=",")
    df = df.rename(columns={"Max of Contagem de CPF": "ALUNOS", "NOME_CURSO": "CURSO"})
    df['ALUNOS'] = df['ALUNOS'].astype(int)
    df_pivot = df.pivot_table(index=['MARCA','CURSO'], columns='SERIE', values='ALUNOS', fill_value=0).reset_index()
    return df_pivot