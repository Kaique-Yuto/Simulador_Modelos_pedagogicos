import pandas as pd

def carregar_base_alunos(caminho_arquivo: str = "databases/base_alunos_curso_marca.csv"):
    df = pd.read_csv(caminho_arquivo,sep=",")
    df = df.rename(columns={"Max of Contagem de CPF": "ALUNOS", "NOME_CURSO": "CURSO"})
    df['ALUNOS'] = df['ALUNOS'].astype(int)
    df_pivot = df.pivot_table(index=['MARCA','CAMPUS','CURSO','MODALIDADE_OFERTA'], columns='SERIE', values='ALUNOS', fill_value=0).reset_index()
    return df_pivot

df = carregar_base_alunos()
print(df.head())