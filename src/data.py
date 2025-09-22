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
        lista["CAMPUS"] = lista["CAMPUS"].astype(str).apply(lambda x: x.replace("-", ":"))
        return lista
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho_arquivo}' não encontrado. Verifique o caminho.")
        return [], []
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo '{caminho_arquivo}': {e}")
        return [], []
    
@st.cache_data
def carregar_base_alunos(caminho_arquivo: str = "databases/base_alunos_curso_marca.csv", version: str="v1"):
    if version == "v1":
        df = pd.read_csv(caminho_arquivo,sep=",")
        df = df.rename(columns={"Max of Contagem de CPF": "ALUNOS", "NOME_CURSO": "CURSO"})
        df['ALUNOS'] = df['ALUNOS'].astype(int)
        df["CAMPUS"] = df["CAMPUS"].astype(str).apply(lambda x: x.replace("-", ":"))
        df_pivot = df.pivot_table(index=['MARCA','CAMPUS','CURSO','MODALIDADE_OFERTA'], columns='SERIE', values='ALUNOS', fill_value=0).reset_index()
        return df_pivot
    elif version == "v2":
        df = pd.read_excel(caminho_arquivo, sheet_name="Export")
        df = df.rename(columns={"Max of Contagem de CPF": "ALUNOS", "NOME_CURSO": "CURSO"})
        
        df['ALUNOS'] = df['ALUNOS'].astype(int)
        df["CAMPUS"] = df["CAMPUS"].astype(str).apply(lambda x: x.replace("-", ":"))
        df_pivot = df.pivot_table(index=['MARCA','CAMPUS','CURSO','MODALIDADE_OFERTA'], columns='SERIE', values='ALUNOS', fill_value=0).reset_index()
        return df_pivot

@st.cache_data
def carregar_tickets(caminho_arquivo: str = "databases/ticket.xlsx"):
    df_curso_marca_modalidade = pd.read_excel(caminho_arquivo, sheet_name="CURSO_MARCA_MODALIDADE").dropna()
    df_curso_modalidade = pd.read_excel(caminho_arquivo, sheet_name="CURSO_MODALIDADE").dropna()
    df_modalidade = pd.read_excel(caminho_arquivo, sheet_name="MODALIDADE").dropna()
    return df_curso_marca_modalidade, df_curso_modalidade, df_modalidade

def encontrar_ticket(curso: str, marca: str, modalidade: str,
                               df_curso_marca_modalidade: pd.DataFrame,
                               df_curso_modalidade: pd.DataFrame,
                               df_modalidade: pd.DataFrame) -> float: # Alterado para float, pois ticket é um valor numérico

    mapper = {
        "EAD 10.10": "LIVE",
        "EAD Atual": "LIVE",
        "Semi Presencial 30.20 Bacharelado": "SEMIPRESENCIAL",
        "Semi Presencial 30.20 Licenciatura": "SEMIPRESENCIAL",
        "Semi Presencial 40.20 Bacharelado": "SEMIPRESENCIAL",
        "Semi Presencial Atual": "SEMIPRESENCIAL",
        "Presencial 70.30": "PRESENCIAL",
        "Presencial Atual": "PRESENCIAL"
    }
    modalidade = mapper.get(modalidade, modalidade)
    
    df_filtrado1 = df_curso_marca_modalidade[
        (df_curso_marca_modalidade["CURSO"] == curso) &
        (df_curso_marca_modalidade["IES"] == marca) &
        (df_curso_marca_modalidade["MODALIDADE"] == modalidade)
    ]
    if not df_filtrado1.empty:
        return df_filtrado1.iloc[0]["Average of Ticket Médio"]

    df_filtrado2 = df_curso_modalidade[
        (df_curso_modalidade["CURSO"] == curso) &
        (df_curso_modalidade["MODALIDADE"] == modalidade)
    ]
    if not df_filtrado2.empty:
        return df_filtrado2.iloc[0]["Average of Ticket Médio"]

    df_filtrado3 = df_modalidade[df_modalidade["MODALIDADE"] == modalidade]
    if not df_filtrado3.empty:
        return df_filtrado3.iloc[0]["Average of Ticket Médio"]

    return 685.0
    