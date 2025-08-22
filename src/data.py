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