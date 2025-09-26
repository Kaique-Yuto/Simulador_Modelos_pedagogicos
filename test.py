import pandas as pd

from src.data import carregar_base_alunos

dados_cursos = [
    ['Semi Presencial 30.20 Bacharelado', 'ADMINISTRAÇÃO'],
    ['Semi Presencial 30.20 Bacharelado', 'ANÁLISE E DESENVOLVIMENTO DE SISTEMAS'],
    ['Semi Presencial 40.20 Bacharelado', 'BIOMEDICINA'],
    ['Semi Presencial 30.20 Bacharelado', 'CIÊNCIA DA COMPUTAÇÃO'],
    ['Semi Presencial 30.20 Bacharelado', 'DESIGN DE INTERIORES'],
    ['Semi Presencial 30.20 Bacharelado', 'DESIGN GRÁFICO'],
    ['Semi Presencial 40.20 Bacharelado', 'EDUCAÇÃO FÍSICA'],
    ['Semi Presencial 40.20 Bacharelado', 'ENGENHARIA CIVIL'],
    ['Semi Presencial 40.20 Bacharelado', 'FARMÁCIA'],
    ['Semi Presencial 40.20 Bacharelado', 'FISIOTERAPIA'],
    ['Semi Presencial 30.20 Licenciatura', 'LETRAS - PORTUGUÊS'],
    ['Semi Presencial 40.20 Bacharelado', 'NUTRIÇÃO'],
    ['Semi Presencial 30.20 Licenciatura', 'PEDAGOGIA'],
    ['Semi Presencial 30.20 Bacharelado', 'CIÊNCIAS CONTÁBEIS']
]

cursos_modelos = pd.DataFrame(data=dados_cursos, columns=["Modelo", "Curso"])

def main():
    base_alunos = carregar_base_alunos("databases/base_alunos_curso_marca_v3.xlsx", version="v2")
    df_marcas_campus = base_alunos[['MARCA','CAMPUS']].drop_duplicates()
    df_marcas_campus['key'] = 1
    cursos_modelos['key'] = 1
    new_df = pd.merge(df_marcas_campus, cursos_modelos, on='key').drop('key', axis=1)
    new_df.to_excel("Base_oferta.xlsx", sheet_name="Sheet1")

if __name__ == "__main__":
    main()