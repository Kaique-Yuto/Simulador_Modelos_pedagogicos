import pandas as pd

df = pd.read_csv("databases/base_alunos_curso_marca.csv",sep=",")
df = df.rename(columns={"Max of Contagem de CPF": "ALUNOS", "NOME_CURSO": "CURSO"})
df['ALUNOS'] = df['ALUNOS'].astype(int)
# Transforma valores da coluna SERIE em colunas
df_pivot = df.pivot_table(index=['MARCA','CURSO'], columns='SERIE', values='ALUNOS', fill_value=0).reset_index()
print(df_pivot.head())