import pandas as pd
import numpy as np
import streamlit as st
from streamlit import column_config
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as mticker
from .formatting import formatador_k
from .data import encontrar_ticket
import time
from collections import defaultdict

def format_currency(x, pos):
    if x >= 1_000_000:
        return f'R$ {x/1_000_000:.1f}M'
    elif x >= 1_000:
        return f'R$ {x/1_000:.0f}K'
    return f'R$ {x:.0f}'

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

def plot_eficiencia_por_semestre(df_precificacao_curso, base_alunos=70):
    # Agregar os dados
    df_plot = df_precificacao_curso.groupby('Semestre').agg(func='sum')
    df_plot['Eficiencia'] = base_alunos / (df_plot['total_ch_uc'] * 20)
    
    # Criar a figura e os eixos
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Cores
    line_color = '#1f77b4'
    
    # Dados para o gráfico
    x = df_plot.index
    y = df_plot['Eficiencia']

    # Gráfico de linha padrão com marcadores
    ax.plot(x, y, color=line_color, linewidth=2.5, marker='o', markersize=8, label='Eficiência')

    # Encontrar e destacar o menor valor
    min_val = y.min()
    min_idx = y.idxmin()
    ax.plot(min_idx, min_val, marker='o', markersize=10, color='red', linestyle='None', label=f'Menor Valor ({min_val:,.2f})')

    # Adicionar data labels
    for xi, yi in zip(x, y):
        ax.text(
            xi,
            yi + yi * 0.05,  # Posição um pouco acima do ponto
            f'{yi:,.2f}'.replace('.', ','),
            ha='center',
            va='bottom',
            color='white',
            fontsize=10,
            fontweight='bold'
        )
    
    # Aumenta o limite superior do eixo Y para dar espaço para as labels
    ax.set_ylim(bottom=0, top=y.max() * 1.25)
    ax.set_xlim(x.min() - 0.5, x.max() + 0.5)

    # Formatação e estilo
    ax.tick_params(colors='white', axis='y', labelsize=8)
    ax.tick_params(colors='white', axis='x', labelsize=8)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    
    ax.set_xlabel("Eficiência por Semestre", fontdict={"color": "white", "fontsize": 12})
    
    
    # Adicionar legenda
    legend = ax.legend(facecolor='#0E1117', edgecolor='white', labelcolor='white')
    
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

def oferta_resumida_por_curso(df_matrizes: pd.DataFrame, session_state) -> pd.DataFrame:
    rows = []
    for key,item in session_state.items():
        new_row = {}
        new_row["marca"] = item.get("marca")
        new_row["polo"] = item.get("polo")
        new_row["curso"] = item.get("curso")
        new_row["modelo"] = item.get("modelo")
        new_row["cluster"] = item.get("cluster")
        matriz = df_matrizes[df_matrizes['MODELO'] == item.get("modelo")]
        ch_total = matriz['CH TOTAL'].sum()
        ch_sinergica_target = ch_total*item.get("sinergia")
        ch_sinergica = []
        ucs_sinergicas = []
        ucs_especificas = []
        for index, row in matriz.iterrows():
            if sum(ch_sinergica) < ch_sinergica_target and row["SINERGIA VALIDA"] == "SIM":
                ch_sinergica.append(row["CH TOTAL"])
                ucs_sinergicas.append(row["UC"])
            else:
                ucs_especificas.append(row["UC"])
        new_row["ch_sinergica"] = sum(ch_sinergica)
        new_row["percentual_sinergico"] = np.round(sum(ch_sinergica)/ch_total,2)
        new_row["ucs_sinergicas"] = ucs_sinergicas
        new_row["ucs_especificas"] = ucs_especificas
        
        rows.append(new_row)

    df = pd.DataFrame(rows)
    return df

def agrupar_oferta(OFERTA_POR_CURSO: pd.DataFrame, df_matrizes: pd.DataFrame, df_parametros: pd.DataFrame, session_state: dict) -> pd.DataFrame:
    # Dicionários para acumular a base de alunos.
    sinergia_acumulador = {}
    afp_acumulador = {}

    # Lista para armazenar as linhas do novo dataframe
    oferta_rows = []
    
    ch_remota_agrupavel = ["Assíncrono", "Síncrono", "Síncrono Mediado"]

    for _, row in OFERTA_POR_CURSO.iterrows():
        marca_nome = row['marca']
        polo_nome = row['polo']
        curso_nome = row['curso']
        modelo_nome = row['modelo']
        cluster_nome = row['cluster']
        flag_presencial = "Presencial" if modelo_nome in ["Presencial Atual", "Presencial 70.30"] else "EAD/Semi"

        curso_key = f"{marca_nome} - {polo_nome} - {curso_nome} ({modelo_nome})"
        curso_selecionado = session_state.get("cursos_selecionados").get(curso_key)
                    
        alunos_por_semestre = curso_selecionado.get("alunos_por_semestre", {})
        

        # --- Processamento das UCs Sinérgicas ---
        ucs_sinergicas = row['ucs_sinergicas']
        for uc in ucs_sinergicas:            
            matriz_uc = df_matrizes[(df_matrizes['MODELO'] == modelo_nome) & (df_matrizes['UC'] == uc)]

            semestre = matriz_uc['Semestre'].iloc[0]
            semestre_key = f"Semestre {semestre}"
            num_alunos = alunos_por_semestre.get(semestre_key, 0)
            tipo_uc = matriz_uc['Tipo de UC'].iloc[0]
            if uc == "AFP":
                key_afp = f"{marca_nome} ({flag_presencial})"
                # Pega a entrada atual ou cria uma nova com a estrutura correta
                entry = afp_acumulador.get(key_afp, {'total_alunos': 0, 'alunos_por_polo': {}})
                # Atualiza o total de alunos
                entry['total_alunos'] += num_alunos
                # Atualiza a contagem para o polo específico
                entry['alunos_por_polo'][polo_nome] = entry['alunos_por_polo'].get(polo_nome, 0) + num_alunos
                # Devolve a entrada atualizada para o acumulador
                afp_acumulador[key_afp] = entry
                continue

            #Busca todos os Tipos de CH para esta UC/Modelo em df_parametros
            parametros_filtrados = df_parametros[(df_parametros['Tipo de UC'] == tipo_uc) & (df_parametros['Modelo'] == modelo_nome)]
            tipos_ch_para_esta_uc = parametros_filtrados['Tipo de CH'].unique().tolist()
            
            # itera em cada Tipo de CH encontrado
            for tipo_ch_atual in tipos_ch_para_esta_uc:
                chave_acumulador = None
                
                if tipo_ch_atual == "Presencial":
                    # Para CH Presencial, o POLO faz parte da chave.
                    chave_acumulador = (uc, tipo_uc, marca_nome, cluster_nome, modelo_nome, semestre, tipo_ch_atual, polo_nome)
                
                elif tipo_ch_atual in ch_remota_agrupavel:
                    # Para CHs remotas, usamos um placeholder para o polo.
                    polo_agrupado_placeholder = "Polos Agrupados"
                    chave_acumulador = (uc, tipo_uc, marca_nome, cluster_nome, modelo_nome, semestre, tipo_ch_atual, polo_agrupado_placeholder)
                
                if chave_acumulador:
                    entry = sinergia_acumulador.get(chave_acumulador, {'total_alunos': 0, 'alunos_por_polo': {}})
                    entry['total_alunos'] += num_alunos
                    entry['alunos_por_polo'][polo_nome] = entry['alunos_por_polo'].get(polo_nome, 0) + num_alunos
                    sinergia_acumulador[chave_acumulador] = entry

            # --- Adição do Professor Regente ---
            oferta_rows.append({
                "UC": uc,
                "Tipo de UC": tipo_uc,
                "Chave": f"{marca_nome} - {uc} - {cluster_nome} - {modelo_nome} - Professor Regente",
                "Semestre": semestre,
                "Modelo": modelo_nome,
                "Base de Alunos": num_alunos,
                "Marca": marca_nome,
                "Polo": polo_nome,
                "Tipo de CH": "Assíncrono"
            })



        # --- Processamento das UCs Específicas ---
        ucs_especificas = row['ucs_especificas']

        for uc in ucs_especificas:
            if not uc: continue
            matriz_uc = df_matrizes[(df_matrizes['MODELO'] == modelo_nome) & (df_matrizes['UC'] == uc)]
            
            if not matriz_uc.empty:
                semestre = matriz_uc['Semestre'].iloc[0]
                semestre_key = f"Semestre {semestre}"
                num_alunos = alunos_por_semestre.get(semestre_key, 0)

                tipo_uc = matriz_uc['Tipo de UC'].iloc[0]

                oferta_rows.append({
                    "UC": uc,
                    "Tipo de UC": tipo_uc,
                    "Chave": f"{marca_nome} - {uc} - {curso_nome} - {modelo_nome} - {polo_nome}",
                    "Semestre": semestre,
                    "Modelo": modelo_nome,
                    "Base de Alunos": num_alunos,
                    "Marca": marca_nome,
                    "Polo": polo_nome,
                    "Tipo de CH": "Todas"
                    })
                # --- Adição do Professor Regente ---
                oferta_rows.append({
                    "UC": uc,
                    "Tipo de UC": tipo_uc,
                    "Chave": f"{marca_nome} - {uc} - {curso_nome} - {modelo_nome} - Professor Regente",
                    "Semestre": semestre,
                    "Modelo": modelo_nome,
                    "Base de Alunos": num_alunos,
                    "Marca": marca_nome,
                    "Polo": polo_nome,
                    "Tipo de CH": "Assíncrono"
                })
                


    # UCs Sinérgicas
    for chave_tuple, data_dict in sinergia_acumulador.items():
        # Desempacota a tupla da chave
        uc, tipo_uc, marca, cluster, modelo, semestre, tipo_ch, polo_placeholder = chave_tuple
        
        # Gera a chave de agrupamento que será a mesma para todos os polos da mesma oferta
        chave_de_agrupamento = f"{marca} - {uc} - {cluster} - {modelo} - {semestre} - {tipo_ch} - {polo_placeholder}"

        # Loop aninhado para "explodir" a linha para cada polo
        for polo_real, alunos_do_polo in data_dict['alunos_por_polo'].items():
            if alunos_do_polo > 0: # Adiciona a linha apenas se houver alunos
                oferta_rows.append({
                    "UC": uc,
                    "Tipo de UC": tipo_uc,
                    "Chave": chave_de_agrupamento, # Chave de Agrupamento
                    "Semestre": semestre,
                    "Modelo": modelo,
                    "Base de Alunos": alunos_do_polo, # Base específica do polo
                    "Marca": marca,
                    "Polo": polo_real, # Nome real do polo
                    "Tipo de CH": tipo_ch
                })

    # Adicionar AFP
    for key, data_dict in afp_acumulador.items():
        marca = key.split(" (")[0]
        flag_presencial = key.split(" (")[1].replace(")","")
        tipo_ch = "Assíncrono" if flag_presencial == "EAD/Semi" else "Síncrono"
        modelo_nome = "EAD 10.10" if flag_presencial == "EAD/Semi" else "Presencial 70.30"
        chave_de_agrupamento = f"AFP - {key} - Todos os polos - Todos os cursos"

        # Loop aninhado para "explodir" a linha para cada polo
        for polo_real, alunos_do_polo in data_dict['alunos_por_polo'].items():
            if alunos_do_polo > 0:
                oferta_rows.append({
                    "UC": "AFP", "Tipo de UC": "AFP", "Chave": chave_de_agrupamento,
                    "Semestre": 1, "Modelo": modelo_nome, "Base de Alunos": alunos_do_polo,
                    "Marca": marca, "Polo": polo_real, "Tipo de CH": tipo_ch 
                })
            
    if not oferta_rows:
        return pd.DataFrame()

    OFERTA_POR_UC = pd.DataFrame(oferta_rows)
    
    OFERTA_POR_UC = OFERTA_POR_UC.sort_values(
        by=['Marca', 'Polo', 'Semestre', 'UC', 'Tipo de CH']
    ).reset_index(drop=True)
    
    return OFERTA_POR_UC

def calcular_df_precificacao_oferta(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formata e exibe um DataFrame de precificação no Streamlit,
    lidando de forma segura com colunas que podem não existir.
    """
    df = df.drop(columns=["Eficiência da UC"]) if "Eficiência da UC" in df.columns else df

    # Ordenar e deixar o "x" por ultimo
    numeric_mask = pd.to_numeric(df['Semestre'], errors='coerce').notna()
    df_numeric = df[numeric_mask]
    df_text = df[~numeric_mask]
    df_numeric['Semestre'] = pd.to_numeric(df_numeric['Semestre'])
    df_numeric_sorted = df_numeric.sort_values(by='Semestre')
    df = pd.concat([df_numeric_sorted, df_text])
    
    return df

def calcula_df_final(df_parametros_editado: pd.DataFrame, OFERTA_POR_UC: pd.DataFrame) -> pd.DataFrame:
    colunas_de_agrupamento = ['Chave', 'UC', 'Tipo de UC', 'Semestre', 'Modelo', 'Marca', 'Tipo de CH']
    OFERTA_POR_UC = OFERTA_POR_UC.groupby(colunas_de_agrupamento, as_index=False).agg(
        Base_Alunos_Grupo=('Base de Alunos', 'sum')
    )
    OFERTA_POR_UC = OFERTA_POR_UC.rename(columns={"Base_Alunos_Grupo": "Base de Alunos"})

    df_sinergicas = OFERTA_POR_UC[OFERTA_POR_UC['Tipo de CH']!="Todas"]
    df_especificas = OFERTA_POR_UC[OFERTA_POR_UC['Tipo de CH']=="Todas"].drop(columns=['Tipo de CH'])
    #primeira_uc_especifica = df_especificas["Chave"].str.split(" - ").str[1].str.replace("UC", "").astype(int).min()

    # Max de alunos
    filtro = (df_parametros_editado['Parâmetro']=='Máximo de Alunos por Turma')
    df_precificacao_oferta_especificas = df_especificas.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo'])
    df_precificacao_oferta_especificas = df_precificacao_oferta_especificas.drop(columns=["Parâmetro"]).rename(columns={"Valor": "Máximo de Alunos"})
    df_precificacao_oferta_sinergicas = df_sinergicas.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo', 'Tipo de CH'])
    df_precificacao_oferta_sinergicas = df_precificacao_oferta_sinergicas.drop(columns=["Parâmetro"]).rename(columns={"Valor": "Máximo de Alunos"})
    
    # ------------UCS ESPECÍFICAS AINDA SÃO SINÉRGICAS NO CURSO ---------
    df_precificacao_oferta_especificas_presencial = df_precificacao_oferta_especificas[df_precificacao_oferta_especificas["Tipo de CH"] == "Presencial"]
    
    df_precificacao_oferta_especificas_agrupavel = df_precificacao_oferta_especificas[df_precificacao_oferta_especificas["Tipo de CH"] != "Presencial"]
    df_precificacao_oferta_especificas_agrupavel = df_precificacao_oferta_especificas_agrupavel[~df_precificacao_oferta_especificas_agrupavel["Chave"].str.endswith("Professor Regente", na=False)]
    df_precificacao_oferta_especificas_agrupavel["Chave"] = (df_precificacao_oferta_especificas_agrupavel["Chave"].str.split(" - ").str[:-1].str.join(" - "))
    colunas_de_agrupamento_2 = ['Chave', 'UC', 'Tipo de UC', 'Semestre', 'Modelo', 'Marca', 'Tipo de CH', 'Ator Pedagógico', 'Máximo de Alunos']
    df_precificacao_oferta_especificas_agrupavel = df_precificacao_oferta_especificas_agrupavel.groupby(colunas_de_agrupamento_2, as_index=False).agg(
                                                                                                    Base_Alunos_Grupo=('Base de Alunos', 'sum')
                                                                                                )
    df_precificacao_oferta_especificas_agrupavel= df_precificacao_oferta_especificas_agrupavel.rename(columns={"Base_Alunos_Grupo": "Base de Alunos"})
    #df_precificacao_oferta_especificas_agrupavel.to_csv("df_precificacao_oferta_especificas_agrupavel.csv")
    df_precificacao_oferta_especificas = pd.concat([df_precificacao_oferta_especificas_presencial, df_precificacao_oferta_especificas_agrupavel])
    # ------------UCS ESPECÍFICAS AINDA SÃO SINÉRGICAS NO CURSO ---------
        
    df_precificacao_oferta = pd.concat([df_precificacao_oferta_especificas, df_precificacao_oferta_sinergicas], ignore_index=True)
    #df_precificacao_oferta.to_csv("df_precificacao_oferta.csv")
    # Remuneração
    filtro = (df_parametros_editado['Parâmetro']=='Remuneração por Hora')
    df_precificacao_oferta = df_precificacao_oferta.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo', 'Tipo de CH', 'Ator Pedagógico'])
    df_precificacao_oferta = df_precificacao_oferta.drop(columns=["Parâmetro"]).rename(columns={"Valor": "Remuneração por Hora"})
    
    # CH Semanal
    filtro = (df_parametros_editado['Parâmetro']=='CH Semanal')
    df_precificacao_oferta = df_precificacao_oferta.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo', 'Tipo de CH', 'Ator Pedagógico'])
    df_precificacao_oferta = df_precificacao_oferta.drop(columns=["Parâmetro"]).rename(columns={"Valor": "CH Semanal"})
    #df_precificacao_oferta['CH Semanal'] = df_precificacao_oferta['CH Semanal'] + 1 if df_precificacao_oferta['Tipo de CH'] == "Assíncrona" else df_precificacao_oferta['CH Semanal']
    
    # ------------PROFESSOR REGENTE ------------------

    df_prof_regente = df_precificacao_oferta[df_precificacao_oferta["Chave"].str.endswith("Professor Regente", na=False)]
    df_prof_regente = df_prof_regente[df_prof_regente["Ator Pedagógico"] == "Professor Regente"]
    df_prof_regente.groupby(colunas_de_agrupamento, as_index=False).agg(
                            Base_Alunos_Grupo=('Base de Alunos', 'sum')
                        )
    df_prof_regente = df_prof_regente.rename(columns={"Base_Alunos_Grupo": "Base de Alunos"})

    df_precificacao_oferta = df_precificacao_oferta[~df_precificacao_oferta["Chave"].str.endswith("Professor Regente", na=False)]
    df_precificacao_oferta = df_precificacao_oferta[df_precificacao_oferta["Ator Pedagógico"] != "Professor Regente"]
    
    df_precificacao_oferta = pd.concat([df_precificacao_oferta, df_prof_regente])
    # ------------PROFESSOR REGENTE ------------------

    df_precificacao_oferta["Qtde Turmas"] = np.ceil(df_precificacao_oferta["Base de Alunos"]/df_precificacao_oferta["Máximo de Alunos"])
    df_precificacao_oferta["CH por Semestre"] = df_precificacao_oferta["CH Semanal"] * df_precificacao_oferta["Qtde Turmas"] * 20
    df_precificacao_oferta["Custo Docente por Semestre"] = df_precificacao_oferta["CH por Semestre"] * df_precificacao_oferta["Remuneração por Hora"] *5.25*1.7*6/20
    
    df_precificacao_oferta

    df_pivot = df_precificacao_oferta.pivot_table(
                                        index=["Chave","Semestre","Base de Alunos", "Qtde Turmas"],
                                        columns="Tipo de CH",
                                        values=["CH por Semestre","Custo Docente por Semestre"],
                                        aggfunc='sum'    
                                    )
    df_pivot['CH Total'] = df_pivot['CH por Semestre'].sum(axis=1)
    df_pivot['Custo Total'] = df_pivot['Custo Docente por Semestre'].sum(axis=1)
    df_final = df_pivot.reset_index()
    df_final.columns = ['_'.join(map(str, col)).strip() if isinstance(col, tuple) and col[1] else col[0] if isinstance(col, tuple) else col for col in df_final.columns]
    df_final["Eficiência da UC"] = np.round(df_final["Base de Alunos"]/df_final["CH Total"],2)
    return df_final

def calcular_resumo_semestre(df_por_semestre: pd.DataFrame, base_alunos):
    ch_total_semestre = 0
    custo_total_semestre = 0

    colunas_ch = [
        "CH por Semestre_Assíncrono",
        "CH por Semestre_Presencial",
        "CH por Semestre_Síncrono",
        "CH por Semestre_Síncrono Mediado"
    ]

    colunas_custo = [
        "Custo Docente por Semestre_Assíncrono",
        "Custo Docente por Semestre_Presencial",
        "Custo Docente por Semestre_Síncrono",
        "Custo Docente por Semestre_Síncrono Mediado"
    ]

    for coluna in colunas_ch:
        if coluna in df_por_semestre.columns:
            ch_total_semestre += df_por_semestre[coluna].sum()

    for coluna in colunas_custo:
        if coluna in df_por_semestre.columns:
            custo_total_semestre += df_por_semestre[coluna].sum()


    custo_mensal = custo_total_semestre / 6

    if ch_total_semestre > 0:
        eficiencia = base_alunos / ch_total_semestre
    else:
        eficiencia = 0 

    return ch_total_semestre, custo_total_semestre, custo_mensal, eficiencia

def calcula_base_alunos_total(session_state:dict) -> int:
    soma_alunos = 0
    for _, item in session_state.get("cursos_selecionados").items():
        for semestre in range(0,10):    
            soma_alunos += item.get("alunos_por_semestre").get(f"Semestre {semestre+1}",0)
    return soma_alunos

def calcula_base_alunos_por_semestre(session_state: dict, semestre:int) -> int:
    soma_alunos = 0
    for _, item in session_state.get("cursos_selecionados").items():
        soma_alunos += item.get("alunos_por_semestre").get(f"Semestre {semestre}", 0)
    return soma_alunos

def adiciona_linha_total(df: pd.DataFrame, base_alunos: int) -> pd.DataFrame:
    somas = df.sum(numeric_only=True)

    linha_total = somas.to_dict()

    linha_total['Chave'] = 'Total Geral'
    linha_total['Semestre'] = 'x'
    linha_total["Eficiência da UC"] = 'x'
    linha_total['Base de Alunos'] = base_alunos

    df_com_total = pd.concat([df, pd.DataFrame([linha_total])], ignore_index=True)
    return df_com_total

def adiciona_linha_total_rateio(df: pd.DataFrame) -> pd.DataFrame:
    df_com_total = df.copy()
    linha_total = df.sum(numeric_only=True)
    linha_total[df.columns[0]] = 'Total Geral'
    df_com_total.loc[len(df_com_total)] = linha_total
    return df_com_total


def plotar_custo_total_pag2(df: pd.DataFrame)-> float:
    return np.round(float(df['Custo Total'].sum()),2)

def plotar_ch_total_pag2(df: pd.DataFrame)-> float:
    return np.round(float(df['CH Total'].sum()),1)

def plot_custo_docente_pag2(df: pd.DataFrame):
    # Agregar os dados
    df_plot = df.groupby('Semestre').agg(func='sum')

    # Criar a figura
    fig, ax = plt.subplots(figsize=(6, 3))

    # Gráfico de barras
    bars = ax.bar(
        df_plot.index,
        df_plot['Custo Total'],
        align='center'
    )

    # Aumenta o limite superior do eixo Y para dar espaço para as labels
    ax.set_ylim(top=df_plot['Custo Total'].max() * 1.15)

    # Adicionar data labels formatados em moeda brasileira
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if i % 2 == 0:
            y_position = height + (df_plot['Custo Total'].max() * 0.05)
        else:
            y_position = height

        ax.text(
            bar.get_x() + bar.get_width()/2,
            y_position,
            f'R$ {height:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            ha='center',
            va='bottom',
            fontsize=4.5,
            fontweight='bold'
        )

    formatter = FuncFormatter(formatador_k)
    ax.yaxis.set_major_formatter(formatter)

    ax.tick_params(axis='y', labelsize=6)
    ax.tick_params(axis='x', labelsize=6)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xticks(df_plot.index)
    # Define os rótulos dos ticks como números inteiros
    ax.set_xticklabels(df_plot.index.astype(int))

    ax.set_xlabel("Série", fontsize=6)
    ax.set_title("Custo Docente por Série", fontsize=10)
    return fig

def plot_ch_docente_por_categoria_pag2(df: pd.DataFrame):
    totais_categoria = {}
    colunas_ch = [
        "CH por Semestre_Assíncrono",
        "CH por Semestre_Presencial",
        "CH por Semestre_Síncrono",
        "CH por Semestre_Síncrono Mediado"
    ]
    for coluna in colunas_ch:
        ch_total=0
        if coluna in df.columns:
            ch_total += df[coluna].sum()
            totais_categoria[coluna] = ch_total

    df_plot = pd.Series(totais_categoria).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 1.5))

    # Gráfico de rosca
    wedges, _ = ax.pie(
        df_plot,
        startangle=90,
        wedgeprops=dict(width=0.4) # A cor da borda foi removida
    )

    # Criar os rótulos para a legenda
    total = df_plot.sum()
    legend_labels = [
        f'{label} ({value/total:.1%})'
        for label, value in df_plot.items()
    ]

    # Adicionar a legenda sem estilização de cor
    ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=8,
        title_fontsize='12'
    )

    # Título
    ax.set_title("Distribuição da CH Docente por Categoria", fontsize=10, pad=20)
    
    # Garante que o layout se ajuste para a legenda não ser cortada
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    return fig

def calcula_eficiencia_para_todos_semestre(df:pd.DataFrame, session_state:dict) -> dict:
    dict_semestres = {}
    for i in range(df["Semestre"].max()):
        df_por_semestre = df[df['Semestre'] == (i+1)]
        base_alunos_semestre = calcula_base_alunos_por_semestre(session_state, i+1)
        _, _, _, eficiencia = calcular_resumo_semestre(df_por_semestre, base_alunos_semestre)
        dict_semestres[i] = eficiencia
    return dict_semestres

def calcula_custo_aluno_para_todos_semestre(df:pd.DataFrame, session_state:dict) -> dict:
    dict_semestres = {}
    for i in range(df["Semestre"].max()):
        df_por_semestre = df[df['Semestre'] == (i+1)]
        base_alunos_semestre = calcula_base_alunos_por_semestre(session_state, i+1)
        _, custo_total_semestre, _, _ = calcular_resumo_semestre(df_por_semestre, base_alunos_semestre)
        dict_semestres[i] = custo_total_semestre/base_alunos_semestre if base_alunos_semestre > 0 else 0
    return dict_semestres


def plot_eficiencia_por_semestre_pag2(dict_semestres: dict):
    if not dict_semestres:
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#0E1117')
        ax.text(0.5, 0.5, 'Dados insuficientes para gerar o gráfico.', 
                color='white', ha='center', va='center')
        return fig

    df = pd.DataFrame.from_dict(dict_semestres, orient='index', columns=["eficiencia"])

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Cores
    line_color = '#1f77b4'
    
    # Dados para o gráfico
    x = df.index
    x = x+1
    y = df['eficiencia']

    # Gráfico de linha padrão com marcadores
    ax.plot(x, y, color=line_color, linewidth=2.5, marker='o', markersize=8, label='Eficiência')

    # Encontrar e destacar o menor valor
    min_val = y.min()
    min_idx = y.idxmin()+1
    ax.plot(min_idx, min_val, marker='o', markersize=10, color='red', linestyle='None', label=f'Menor Valor ({min_val:,.2f})'.replace('.',','))

    # Adicionar data labels
    for xi, yi in zip(x, y):
        ax.text(
            xi,
            yi + yi * 0.05,  # Posição um pouco acima do ponto
            f'{yi:,.2f}'.replace('.', ','),
            ha='center',
            va='bottom',
            color='white',
            fontsize=10,
            fontweight='bold'
        )
    
    # Aumenta o limite superior do eixo Y para dar espaço para as labels
    ax.set_ylim(bottom=0, top=y.max() * 1.25)
    ax.set_xlim(x.min() - 0.5, x.max() + 0.5)

    # Formatação e estilo
    ax.tick_params(colors='white', axis='y', labelsize=8)
    ax.tick_params(colors='white', axis='x', labelsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(x.astype(int))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    
    ax.set_xlabel("Semestre", fontdict={"color": "white", "fontsize": 12})
    
    legend = ax.legend(facecolor='#0E1117', edgecolor='white', labelcolor='white')
    

    return fig

def plot_custo_aluno_por_semestre_pag2(dict_semestres: dict, df_ticket: pd.DataFrame):
    if not dict_semestres:
        fig, ax = plt.subplots(figsize=(12, 1.5))
        ax.text(0.5, 0.5, 'Dados de custo insuficientes para gerar o gráfico.',
                ha='center', va='center')
        ax.set_axis_off()
        return fig

    df_custo = pd.DataFrame.from_dict(dict_semestres, orient='index', columns=["eficiencia"])
    df_custo.index = df_custo.index.astype(int) + 1
    
    df_ticket_proc = df_ticket.copy()
    df_ticket_proc["TicketMedio"] = df_ticket_proc["TicketMedio"]*6
    # Verifica se 'Semestre' é uma coluna. Se não, assume que está no índice.
    if 'Semestre' in df_ticket_proc.columns:
        df_ticket_proc['Série'] = df_ticket_proc['Semestre'].str.extract('(\d+)').astype(int)
    else:
        # Se não for uma coluna, extrai do índice do DataFrame.
        # Isso previne o KeyError.
        df_ticket_proc['Série'] = df_ticket_proc.index.to_series().str.extract('(\d+)').astype(int)
    
    df_ticket_proc = df_ticket_proc.set_index('Série').sort_index()

    df_plot = df_custo.join(df_ticket_proc['TicketMedio'])

    fig, ax = plt.subplots(figsize=(6, 2))
    
    x_values = df_plot.index
    y_custo = df_plot['eficiencia']
    y_ticket = df_plot['TicketMedio']

    ax.plot(x_values, y_custo, linewidth=2.5, marker='o', markersize=4.5, label='Custo por Aluno')
    
    if not y_ticket.isnull().all():
        ax.plot(x_values, y_ticket, linestyle=':', color='gray', label='Ticket Médio')
        for serie, row in df_plot.iterrows():
            if pd.notna(row['TicketMedio']) and row['eficiencia'] > row['TicketMedio']:
                ax.plot(serie, row['eficiencia'], marker='o', markersize=4.5, color='red', linestyle='None')

    max_val_custo = y_custo.max()
    max_idx_custo = y_custo.idxmax()
    ax.plot(max_idx_custo, max_val_custo, marker='o', markersize=4.5, linestyle='None', 
            label=f'Maior Custo/Aluno (R$ {max_val_custo:,.0f})')
    
    for xi, yi in y_custo.items():
        ax.text(xi, yi + yi * 0.05, f'R$ {int(yi):,}', ha='center',
                va='bottom', fontsize=4.5, fontweight='bold')
    
    all_y_values = pd.concat([y_custo, y_ticket]).dropna()
    max_val_y_axis = all_y_values.max() if not all_y_values.empty else y_custo.max()
    
    x_min = min(x_values) - 0.5 if not x_values.empty else 0
    x_max = max(x_values) + 0.5 if not x_values.empty else 5
    
    ax.set_ylim(bottom=0, top=max_val_y_axis * 1.25)
    ax.set_xlim(x_min, x_max)

    ax.tick_params(axis='y', labelsize=8)
    ax.tick_params(axis='x', labelsize=8)
    
    if not x_values.empty:
        unique_ticks = sorted(list(x_values))
        ax.set_xticks(unique_ticks)
        ax.set_xticklabels([str(int(x)) for x in unique_ticks])
    
    ax.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {int(x):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel("Série", fontsize=6)
    
    ax.legend(fontsize=6, borderpad=0.4, labelspacing=0.5, loc='best')
    
    return fig



def formatar_df_por_semestre(df: pd.DataFrame):
    
    def highlight_total(row):
        if "Chave" in row and row["Chave"] == "Total Geral":
            return (len(row)-2)*['background-color: #282c34'] + ['font-weight: bold; background-color: #273333'] * 2
        return [''] * len(row)

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
        "Qtde Turmas": column_config.NumberColumn(format="%d")
    }

    formatadores_seguros = {col: func for col, func in formatador_mestre.items() if col in df.columns}
    configuracao_segura = {col: cfg for col, cfg in column_config_mestre.items() if col in df.columns}
    df = df.drop(columns='Eficiência da UC', errors='ignore')
    df = df.rename(columns={"Semestre": "Série"})
    df_styled = df.style.apply(highlight_total, axis=1).format(formatadores_seguros)

    df_formatado = st.dataframe(
        df_styled,
        use_container_width=True,
        column_config=configuracao_segura,
        hide_index=True
    )
    
    return df_formatado

def projetar_base_alunos(
    n_semestres_curso: int,
    dist_ingresso: tuple,
    taxa_evasao_inicial: float,
    decaimento_evasao: float,
    n_periodos_a_projetar: int = 10,
    base_inicial: dict = None,
    ingressantes_personalizados: dict = None
) -> dict:
    """
    Projeta a evolução da base de alunos ao longo de vários semestres.
    [VERSÃO FINAL] Corrige a lógica para que a captação manual do primeiro período
    seja aplicada corretamente.
    """
    # 1. SETUP INICIAL
    fator_decaimento = 1.0 - decaimento_evasao
    taxas_evasao = np.array([taxa_evasao_inicial * (fator_decaimento ** i) for i in range(n_semestres_curso)])
    taxas_permanencia = 1 - taxas_evasao

    projecao_temporal = {}
    ano_inicial, semestre_inicial = 2026, 1

    turmas_atuais = np.zeros(n_semestres_curso, dtype=int)
    if base_inicial:
        for semestre_str, num_alunos in base_inicial.items():
            try:
                semestre_idx = int(semestre_str.split(" ")[1]) - 1
                if 0 <= semestre_idx < n_semestres_curso:
                    turmas_atuais[semestre_idx] = int(num_alunos)
            except (ValueError, IndexError):
                pass
    
    # 2. AJUSTE DO PRIMEIRO PERÍODO COM CAPTAÇÃO MANUAL
    # Se a captação manual estiver ativa, ela tem prioridade para definir
    # o número de alunos no Semestre 1 do período inicial (T=0).
    if ingressantes_personalizados:
        chave_primeiro_periodo_lookup = f"{ano_inicial}_{semestre_inicial}" # "2026_1"
        ingressantes_t0 = ingressantes_personalizados.get(chave_primeiro_periodo_lookup)

        if ingressantes_t0 is not None:
            # Sobrepõe o valor do Semestre 1 com o valor da captação manual
            turmas_atuais[0] = int(ingressantes_t0)


    # 3. TRATAMENTO DO PRIMEIRO PERÍODO (2026/1)
    # Salva o estado como o resultado final para o primeiro período.
    chave_primeiro_periodo = f"alunos_por_semestre_{ano_inicial}_{semestre_inicial}"
    projecao_temporal[chave_primeiro_periodo] = {f"Semestre {k + 1}": int(num_alunos) for k, num_alunos in enumerate(turmas_atuais)}
    
    # 4. LOOP DE SIMULAÇÃO PARA OS PERÍODOS SEGUINTES
    for i in range(1, n_periodos_a_projetar):
        turmas_seguinte = np.zeros(n_semestres_curso, dtype=int)

        # A. LÓGICA DE PROMOÇÃO
        for j in range(n_semestres_curso - 1, 0, -1):
            alunos_para_avancar = turmas_atuais[j-1]
            taxa_de_permanencia = taxas_permanencia[j-1]
            if alunos_para_avancar > 0:
                sobreviventes = np.random.binomial(n=alunos_para_avancar, p=taxa_de_permanencia)
            else:
                sobreviventes = 0
            turmas_seguinte[j] = int(max(0, sobreviventes))

        # B. LÓGICA DE CAPTAÇÃO CONDICIONAL
        ano_atual = ano_inicial + (i // 2)
        semestre_atual = semestre_inicial + (i % 2)
        chave_periodo_lookup = f"{ano_atual}_{semestre_atual}"

        novos_ingressantes = 0
        if ingressantes_personalizados:
            novos_ingressantes = ingressantes_personalizados.get(chave_periodo_lookup, 0)
        else:
            media_anual, dp_anual = dist_ingresso
            fator_sazonal = 0.6 if semestre_atual == 1 else 0.4
            media_semestral = media_anual * fator_sazonal
            dp_semestral = dp_anual * fator_sazonal
            novos_ingressantes = np.round(np.random.normal(media_semestral, dp_semestral))
        
        turmas_seguinte[0] = int(max(4, novos_ingressantes))

        # C. ARMAZENAMENTO E ATUALIZAÇÃO DE ESTADO
        chave_temporal = f"alunos_por_semestre_{ano_atual}_{semestre_atual}"
        alunos_por_semestre_dict = {f"Semestre {k + 1}": int(num_alunos) for k, num_alunos in enumerate(turmas_seguinte)}
        projecao_temporal[chave_temporal] = alunos_por_semestre_dict

        turmas_atuais = turmas_seguinte.copy()
        
    return projecao_temporal


def calcula_ticket_medio(config: dict, serie: int) -> float:
    cursos = config.get("cursos_selecionados", {})

    alunos_total = 0
    ticket_total = 0
    for _, dados_chave in cursos.items():
        ticket_curso = dados_chave.get("ticket", 0)
        alunos_curso = 0
        if serie:
            alunos_curso = dados_chave.get("alunos_por_semestre", {}).get(f"Semestre {serie}", 0)
            alunos_total += alunos_curso
        else:
            for _, num in dados_chave.get("alunos_por_semestre", {}).items():
                alunos_curso += num
                alunos_total += num
        ticket_total += ticket_curso * alunos_curso

    ticket_medio = ticket_total / alunos_total 
    return ticket_medio

def busca_base_de_alunos(df: pd.DataFrame, marca: str, campus: str, curso: str, modalidade: str, num_semestres: int):    
    filtro = (
        (df['MARCA'] == marca) &
        (df['CAMPUS'] == campus) &
        (df['CURSO'] == curso) &
        (df['MODALIDADE_OFERTA'] == modalidade)
    )
    df_filtrado = df.loc[filtro]
    if not df_filtrado.empty:
        dados_aluno = df_filtrado.iloc[0]
        alunos_por_semestre = {
            f"Semestre {i}": int(dados_aluno.get(i, 0))
            for i in range(1, num_semestres + 1)
        }
    else:
        alunos_por_semestre = {f"Semestre 1": 50 }
    return alunos_por_semestre

def adicionar_todas_ofertas_do_polo(marca, polo, df_base_alunos, df_dimensao_cursos, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade):
    time.sleep(0.5)
    with st.spinner(f"Buscando todas as ofertas para {marca} - {polo}..."):
        ofertas_polo = df_base_alunos[(df_base_alunos['MARCA'] == marca) & (df_base_alunos['CAMPUS'] == polo)]
        cursos_modelos_unicos = ofertas_polo[['CURSO', 'MODALIDADE_OFERTA']].drop_duplicates().to_numpy()

        if len(cursos_modelos_unicos) == 0:
            st.warning(f"Nenhuma oferta com base de alunos histórica foi encontrada para a marca '{marca}' e polo '{polo}'.")
            return

        cursos_adicionados = 0
        cursos_ignorados = 0

        for curso, modelo in cursos_modelos_unicos:
            chave_oferta = f"{marca} - {polo} - {curso} ({modelo})"

            if chave_oferta in st.session_state.cursos_selecionados:
                cursos_ignorados += 1
                continue

            try:
                filtro = (df_dimensao_cursos['Curso'] == curso) & (df_dimensao_cursos['Modelo'] == modelo)
                dados_curso = df_dimensao_cursos[filtro].iloc[0]
                
                num_semestres = int(dados_curso['Qtde Semestres'])
                
                alunos_por_semestre = busca_base_de_alunos(df_base_alunos, marca, polo, curso, modelo, num_semestres)

                # Se a busca não retornar nenhum aluno, ignora a oferta para não adicionar cursos vazios
                if not alunos_por_semestre or sum(alunos_por_semestre.values()) == 0:
                    cursos_ignorados += 1
                    continue

                st.session_state.cursos_selecionados[chave_oferta] = {
                    "marca": marca,
                    "polo": polo,
                    "curso": curso,
                    "modelo": modelo,
                    "ticket": encontrar_ticket(curso, marca, modelo, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade),
                    "cluster": dados_curso['Cluster'],
                    "sinergia": dados_curso['Sinergia'],
                    "num_semestres": num_semestres,
                    "alunos_por_semestre": alunos_por_semestre
                }
                cursos_adicionados += 1
            except (IndexError, TypeError):
                # Ocorre se o curso/modelo da base de alunos não for encontrado no df_dimensao_cursos
                cursos_ignorados += 1
                continue
    
    st.success(f"{cursos_adicionados} novas ofertas foram adicionadas com sucesso para o polo {polo}!")
    if cursos_ignorados > 0:
        st.info(f"{cursos_ignorados} ofertas foram ignoradas (já existentes na simulação, sem alunos na base ou sem dados de dimensionamento).")

def remover_ofertas_por_marca(marca_a_remover):
    with st.spinner(f'Removendo todas as ofertas da marca {marca_a_remover}...'):
        time.sleep(1)
        chaves_para_remover = [
            chave for chave, config in st.session_state.cursos_selecionados.items()
            if config['marca'] == marca_a_remover
        ]
        for chave in chaves_para_remover:
            del st.session_state.cursos_selecionados[chave]
    st.success(f"Todas as ofertas da marca '{marca_a_remover}' foram removidas!")

def remover_ofertas_por_polo(polo_a_remover):
    with st.spinner(f'Removendo todas as ofertas do polo {polo_a_remover}...'):
        time.sleep(1)
        chaves_para_remover = [
            chave for chave, config in st.session_state.cursos_selecionados.items()
            if config['polo'] == polo_a_remover
        ]
        for chave in chaves_para_remover:
            del st.session_state.cursos_selecionados[chave]
    st.success(f"Todas as ofertas do polo '{polo_a_remover}' foram removidas!")

def trazer_ofertas_para_novo_modelo(df_dimensao_cursos, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade):
    mapper_modelos = {
        "EAD Atual": ["EAD 10.10", "Semi Presencial 30.20 Bacharelado", "Semi Presencial 30.20 Licenciatura", "Semi Presencial 40.20 Bacharelado", "Presencial 70.30"],
        "Semi Presencial Atual": ["Semi Presencial 40.20 Bacharelado", "Semi Presencial 30.20 Bacharelado", "Semi Presencial 30.20 Licenciatura"],
        "Presencial Atual": ["Presencial 70.30", "Semi Presencial 40.20 Bacharelado"]
    }
    
    with st.spinner("Migrando ofertas para os novos modelos..."):
        novos_cursos_selecionados = {}
        migrados_sucesso = 0
        migrados_falha = 0
        falhas = []

        for chave_antiga, config in st.session_state.cursos_selecionados.items():
            modelo_antigo = config['modelo']
            curso = config['curso']

            # Verifica se o modelo antigo tem um mapeamento para migração
            if modelo_antigo in mapper_modelos:
                lista_modelos_novos = mapper_modelos[modelo_antigo]
                migracao_bem_sucedida = False

                # Tenta cada novo modelo na ordem da lista
                for modelo_novo_tentativa in lista_modelos_novos:
                    # Remove espaços em branco extras que podem causar falhas
                    modelo_novo_tentativa = modelo_novo_tentativa.strip()

                    # Verifica se o novo modelo é válido para o curso
                    filtro = (df_dimensao_cursos['Curso'] == curso) & (df_dimensao_cursos['Modelo'] == modelo_novo_tentativa)
                    
                    # Se o filtro NÃO estiver vazio, a combinação é válida
                    if not df_dimensao_cursos[filtro].empty:
                        # --- SUCESSO: Encontramos um modelo válido ---
                        dados_curso_novo = df_dimensao_cursos[filtro].iloc[0]
                        
                        # Cria uma cópia da configuração para evitar modificar a original no meio do loop
                        nova_config = config.copy()
                        
                        nova_config['modelo'] = modelo_novo_tentativa
                        nova_config['ticket'] = encontrar_ticket(nova_config['curso'], nova_config['marca'], modelo_novo_tentativa, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade)
                        nova_config['cluster'] = dados_curso_novo['Cluster']
                        nova_config['sinergia'] = dados_curso_novo['Sinergia']
                        nova_config['num_semestres'] = dados_curso_novo['Qtde Semestres']
                        chave_nova = f"{nova_config['marca']} - {nova_config['polo']} - {nova_config['curso']} ({modelo_novo_tentativa})"
                        novos_cursos_selecionados[chave_nova] = nova_config
                        
                        migrados_sucesso += 1
                        migracao_bem_sucedida = True
                        
                        # Interrompe o loop interno, pois já encontramos um modelo válido
                        break 
                
                # Se, após testar todos os modelos da lista, nenhum funcionou
                if not migracao_bem_sucedida:
                    migrados_falha += 1
                    # A mensagem de falha agora informa todas as tentativas
                    falhas.append(f"'{curso}' (tentativas: {', '.join(lista_modelos_novos)})")
                    # Mantém a oferta original se a migração falhar
                    novos_cursos_selecionados[chave_antiga] = config
            
            else:
                # Se não está no mapper, apenas mantém a oferta como está
                novos_cursos_selecionados[chave_antiga] = config
        
        # Atualiza o estado da sessão com as novas ofertas
        st.session_state.cursos_selecionados = novos_cursos_selecionados

    st.success(f"{migrados_sucesso} ofertas foram migradas para o novo modelo com sucesso!")
    if migrados_falha > 0:
        st.warning(f"{migrados_falha} ofertas não puderam ser migradas, pois nenhuma combinação válida foi encontrada para: {', '.join(falhas)}.")

    

def adicionar_todas_ofertas_da_marca(marca, df_marcas_polos, df_base_alunos, df_dimensao_cursos, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade):
    st.info(f"Iniciando busca em massa para a marca '{marca}'. Esta ação pode levar alguns minutos...")
    
    # 1. Encontrar todos os polos para a marca selecionada
    polos_da_marca = sorted(df_marcas_polos[df_marcas_polos['MARCA'] == marca]['CAMPUS'].unique().tolist())

    if not polos_da_marca:
        st.warning(f"Nenhum polo encontrado para a marca '{marca}' na base de dados.")
        return

    # 2. Iterar por cada polo e chamar a função existente
    # Usamos uma barra de progresso para melhor feedback ao usuário
    progress_bar = st.progress(0, text=f"Buscando ofertas em {len(polos_da_marca)} polos...")
    
    for i, polo in enumerate(polos_da_marca):
        # A função interna já exibe suas próprias mensagens de sucesso/aviso para cada polo
        adicionar_todas_ofertas_do_polo(
            marca=marca,
            polo=polo,
            df_base_alunos=df_base_alunos,
            df_dimensao_cursos=df_dimensao_cursos,
            df_curso_marca_modalidade=df_curso_marca_modalidade,
            df_curso_modalidade=df_curso_modalidade,
            df_modalidade=df_modalidade
        )
        progress_bar.progress((i + 1) / len(polos_da_marca), text=f"Processando polo: {polo} ({i+1}/{len(polos_da_marca)})")
    
    progress_bar.empty() # Limpa a barra de progresso ao final
    st.success(f"Busca em massa para a marca '{marca}' foi concluída!")
    st.balloons()

def cria_select_box_modelo(df_dimensao_cursos, config, chave_oferta, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade):
    modelos_disponiveis = obter_modelos_para_curso(df_dimensao_cursos, config['curso'])
    try:
        index_atual = modelos_disponiveis.index(config['modelo'])
    except ValueError:
        index_atual = 0
    novo_modelo_selecionado = st.selectbox(
        "Modelo",
        options=modelos_disponiveis,
        index=index_atual,
        key=f"modelo_select_{chave_oferta}"
    )
    if novo_modelo_selecionado != config['modelo']:
        nova_chave = f"{config['marca']} - {config['polo']} - {config['curso']} ({novo_modelo_selecionado})"
        if nova_chave in st.session_state.cursos_selecionados:
            st.warning(f"A oferta '{nova_chave}' já existe na simulação. Não é possível fazer a troca.")
        else:
            filtro = (df_dimensao_cursos['Curso'] == config['curso']) & (df_dimensao_cursos['Modelo'] == novo_modelo_selecionado)
            dados_curso_novo = df_dimensao_cursos[filtro].iloc[0]
            nova_config = {
                "marca": config['marca'],
                "polo": config['polo'],
                "curso": config['curso'],
                "modelo": novo_modelo_selecionado,
                "ticket": encontrar_ticket(config['curso'], config['marca'], novo_modelo_selecionado, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade),
                "cluster": dados_curso_novo['Cluster'],
                "sinergia": dados_curso_novo['Sinergia'],
                "num_semestres": config['num_semestres'], # Mantém o mesmo
                "alunos_por_semestre": config['alunos_por_semestre'] # Mantém os mesmos alunos
            }
            st.session_state.cursos_selecionados[nova_chave] = nova_config
            del st.session_state.cursos_selecionados[chave_oferta]
            st.rerun()

def plotar_evolucao_total_alunos(cursos_selecionados):
    """
    Agrega o total de alunos de todas as ofertas ao longo do tempo e gera um gráfico de linha.
    """
    # Dicionário para armazenar o total de alunos por período
    evolucao_total = {}

    for config in cursos_selecionados.values():
        # Encontra todas as chaves de projeção de alunos para a oferta atual
        chaves_projecao = sorted([k for k in config if k.startswith("alunos_por_semestre_")])
        
        for chave in chaves_projecao:
            periodo = chave.replace("alunos_por_semestre_", "").replace("_", "/")
            total_alunos_no_periodo = sum(config[chave].values())
            
            # Adiciona (ou soma) o total de alunos ao período correspondente
            if periodo in evolucao_total:
                evolucao_total[periodo] += total_alunos_no_periodo
            else:
                evolucao_total[periodo] = total_alunos_no_periodo

    if not evolucao_total:
        return None

    # Cria um DataFrame para facilitar a plotagem
    df_evolucao = pd.DataFrame(list(evolucao_total.items()), columns=['Período', 'Total de Alunos']).set_index('Período')
    
    # Gera o gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_evolucao.index, df_evolucao['Total de Alunos'], marker='o', linestyle='-')
    ax.set_title('Evolução do Total de Alunos (Agregado)')
    ax.set_ylabel('Número Total de Alunos')
    ax.set_xlabel('Período da Simulação')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def plotar_composicao_alunos_por_serie(cursos_selecionados, periodo_selecionado):
    """
    Agrega a composição de alunos por série para um dado período e gera um gráfico de barras.
    """
    composicao_total = {}
    chave_projecao = f"alunos_por_semestre_{periodo_selecionado.replace('/', '_')}"

    for config in cursos_selecionados.values():
        if chave_projecao in config:
            dados_do_periodo = config[chave_projecao]
            for serie, n_alunos in dados_do_periodo.items():
                if serie in composicao_total:
                    composicao_total[serie] += n_alunos
                else:
                    composicao_total[serie] = n_alunos
    
    if not composicao_total:
        return None

    # Ordena as séries corretamente (ex: Semestre 1, Semestre 2, ...)
    sorted_series = sorted(composicao_total.keys(), key=lambda x: int(x.split(' ')[1]))
    sorted_values = [composicao_total[k] for k in sorted_series]

    df_composicao = pd.DataFrame({
        'Série': sorted_series,
        'Número de Alunos': sorted_values
    })

    # Gera o gráfico
    fig, ax = plt.subplots(figsize=(12, 4))
    x = df_composicao['Série'].str.replace("Semestre", "Série")
    bars = ax.bar(x, df_composicao['Número de Alunos'])
    ax.set_title(f'Composição Agregada de Alunos por Série em {periodo_selecionado}', fontsize=20)
    ax.set_ylabel('Número de Alunos')
    ax.set_xlabel('Série do Curso', fontsize=12)
    plt.xticks(rotation=45)

    # Adiciona os data labels em cima de cada barra
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center')

    plt.tight_layout()

    return fig


def preparar_dados_para_dashboard_macro(todos_os_resultados: dict) -> pd.DataFrame:
    """
    Consolida os resultados de todos os períodos em um único DataFrame
    para a criação do dashboard macro de séries temporais.
    """
    lista_de_metricas = []
    # Ordena os períodos cronologicamente para garantir que os cálculos acumulados fiquem corretos
    periodos_ordenados = sorted(todos_os_resultados.keys())

    for periodo in periodos_ordenados:
        metricas = todos_os_resultados[periodo]['metricas_gerais']
        metricas['periodo'] = periodo
        lista_de_metricas.append(metricas)

    if not lista_de_metricas:
        return pd.DataFrame()

    df_macro = pd.DataFrame(lista_de_metricas)
    df_macro.set_index('periodo', inplace=True)

    # Calcular novas colunas necessárias para os gráficos
    df_macro['receita_total'] = df_macro['base_alunos'] * df_macro['ticket_medio'] * 6
    
    # Cálculos acumulados
    df_macro['custo_acumulado'] = df_macro['custo_total'].cumsum()
    df_macro['receita_acumulada'] = df_macro['receita_total'].cumsum()
    df_macro['margem_acumulada'] = df_macro['receita_acumulada'] - df_macro['custo_acumulado']

    return df_macro

def plotar_custos_vs_receita(df_macro: pd.DataFrame):
    """
    Plota um gráfico de barras para Custo e Receita por semestre, 
    com linhas para os valores acumulados.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bar_width = 0.35
    index = np.arange(len(df_macro.index))

    # Barras para valores por semestre
    bars1 = ax.bar(index - bar_width/2, df_macro['custo_total'], bar_width, label='Custo por Semestre', color='orangered', alpha=0.7)
    bars2 = ax.bar(index + bar_width/2, df_macro['receita_total'], bar_width, label='Receita por Semestre', color='royalblue', alpha=0.7)

    # Eixo Y secundário para valores acumulados
    ax2 = ax.twinx()
    line1, = ax2.plot(index, df_macro['custo_acumulado'], color='darkred', linestyle='--', marker='o', label='Custo Acumulado')
    line2, = ax2.plot(index, df_macro['receita_acumulada'], color='darkblue', linestyle='--', marker='o', label='Receita Acumulada')

    ax.set_xlabel('Período')
    ax.set_ylabel('Valor por Semestre (R$)')
    ax2.set_ylabel('Valor Acumulado (R$)')
    ax.set_title('Custos vs. Receita: Visão Semestral e Acumulada', fontsize=16)
    ax.set_xticks(index)
    ax.set_xticklabels(df_macro.index, rotation=45, ha="right")
    
    # Formatação do eixo Y para moeda
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    
    # Legendas combinadas
    lines = [bars1, bars2, line1, line2]
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left')

    fig.tight_layout()
    return fig

def plotar_margem_e_base_alunos(df_macro: pd.DataFrame):
    """
    Plota a Margem por Semestre e a Base de Alunos, com cores condicionais
    nas barras e nos rótulos do eixo Y.
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    index = df_macro.index
    
    colors = ['lightcoral' if val < 0 else 'seagreen' for val in df_macro['margem']]
    
    ax1.bar(index, df_macro['margem'], color=colors, alpha=0.7, label='Lucro')
    ax1.set_xlabel('Período')
    ax1.set_ylabel('Margem (R$)', color='black')
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(format_currency))
    ax1.axhline(0, color='gray', linewidth=0.8, linestyle='--')

    max_margem = df_macro['margem'].max()
    ymax = max(50, max_margem) * 1.1
    
    min_margem = df_macro['margem'].min()
    ymin = min_margem * 1.1 if min_margem < 0 else 0
    
    ax1.set_ylim(bottom=ymin, top=ymax)

    # Define a cor padrão para todos os rótulos
    ax1.tick_params(axis='y', labelcolor='seagreen')

    # Forçamos o desenho do gráfico para que os rótulos (ticks) sejam criados
    fig.canvas.draw()

    # Agora, iteramos pelos rótulos e mudamos a cor dos negativos
    for label in ax1.get_yticklabels():
        try:
            # Pega o valor numérico a partir da posição do rótulo
            if float(label.get_position()[1]) < 0:
                label.set_color('red')
        except (ValueError, IndexError):
            # Ignora qualquer erro de conversão ou rótulos vazios
            continue

    ax2 = ax1.twinx()
    color_alunos = 'goldenrod'
    ax2.plot(index, df_macro['base_alunos'], color=color_alunos, marker='o', linestyle='-', label='Base de Alunos Total')
    ax2.set_ylabel('Nº de Alunos', color=color_alunos)
    ax2.tick_params(axis='y', labelcolor=color_alunos)
    
    ax1.set_title('Margem/Aluno por Semestre e Evolução da Base de Alunos', fontsize=16)
    ax1.set_xticklabels([str(i) for i in index], rotation=45, ha="right")

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    fig.tight_layout()
    return fig

def ratear_custo_por_polo(oferta_por_uc: pd.DataFrame, df_final: pd.DataFrame) -> pd.DataFrame:
    # Transformar chaves da oferta por UC
    oferta_por_uc_nao_todas = oferta_por_uc.copy()
    oferta_por_uc_todas = oferta_por_uc[oferta_por_uc["Tipo de CH"]== "Todas"]
    oferta_por_uc_todas["Chave"] = (oferta_por_uc_todas["Chave"].str.split(" - ").str[:-1].str.join(" - "))
    oferta_por_uc_todas = oferta_por_uc_todas.drop_duplicates()
    oferta_por_uc = pd.concat([oferta_por_uc_nao_todas, oferta_por_uc_todas])
    oferta_por_uc.drop(columns=["Tipo de CH"], inplace=True)

    colunas_ch = {
    'CH por Semestre_Assíncrono': 'Assíncrono',
    'CH por Semestre_Presencial': 'Presencial',
    'CH por Semestre_Síncrono Mediado': 'Síncrono Mediado',
    'CH por Semestre_Síncrono': 'Síncrono'
    }
    conditions = []
    choices = []

    for coluna, tipo in colunas_ch.items():
        if coluna in df_final.columns:
            conditions.append(df_final[coluna].notna())
            choices.append(tipo)

    df_final['Tipo de CH'] = np.select(conditions, choices, default=None)
    df_custos_para_merge = df_final[['Chave', 'Custo Total', 'Tipo de CH']].copy()
    
    # 2. Junta o Custo Total ao DataFrame detalhado, usando a 'Chave' como elo
    df_merged = pd.merge(oferta_por_uc, df_custos_para_merge, on='Chave', how='left')
    df_merged['Custo Total'].fillna(0, inplace=True)
    
    # 3. Calcula a base total de alunos para cada grupo (identificado pela 'Chave')
    df_merged['Base_Total_Grupo'] = df_merged.groupby('Chave')['Base de Alunos'].transform('sum')

    # 4. Calcula a porcentagem de participação de cada polo no seu grupo
    df_merged['Percentual_Rateio'] = 0
    df_merged.loc[df_merged['Base_Total_Grupo'] > 0, 'Percentual_Rateio'] = \
        df_merged['Base de Alunos'] / df_merged['Base_Total_Grupo']

    # 5. Calcula o Custo Rateado para cada polo
    df_merged['Custo Rateado'] = df_merged['Custo Total'] * df_merged['Percentual_Rateio']
    
    # 6. Remove as colunas auxiliares
    df_merged = df_merged.drop(columns=['Base_Total_Grupo', 'Percentual_Rateio'])

    return df_merged

def calcula_total_alunos_por_polo(cursos_selecionados, periodo_selecionado, nome_polo):
    total_alunos_polo = 0
    chave_projecao = f"alunos_por_semestre_{periodo_selecionado.replace('/', '_')}"

    for config in cursos_selecionados.values():
        # Filtra as configurações para o polo em questão e verifica se há dados para o período
        if config.get('polo') == nome_polo and chave_projecao in config:
            dados_do_periodo = config[chave_projecao]
            total_alunos_polo += sum(dados_do_periodo.values())
            
    return total_alunos_polo

def upload_arquivo(
    uploaded_file, 
    df_dimensao_cursos: pd.DataFrame,
    df_curso_marca_modalidade: pd.DataFrame, 
    df_curso_modalidade: pd.DataFrame, 
    df_modalidade: pd.DataFrame
) -> None:
    """
    Lê um arquivo Excel com projeção de ingressantes e adiciona as ofertas correspondentes
    """
    try:
        df_ingressantes = pd.read_excel(uploaded_file, sheet_name="Ofertas")
        df_ingressantes.dropna(axis=0, how="any", inplace=True)
        df_ingressantes.drop_duplicates(inplace=True)
        cursos_adicionados = 0
        
        for _, row in df_ingressantes.iterrows():
            marca_nome = row['Marca']
            polo_nome = row['Polo/Sede']
            curso_nome = row['Curso']
            modelo_nome = row['Modalidade']
            
            filtro = (df_dimensao_cursos['Curso'] == curso_nome) & (df_dimensao_cursos['Modelo'] == modelo_nome)
            dados_curso = df_dimensao_cursos[filtro]

            if dados_curso.empty:
                st.warning(f"O curso '{curso_nome}' com modelo '{modelo_nome}' não foi encontrado na base de dados e será ignorado.")
                continue

            dados_curso = dados_curso.iloc[0]
            chave_oferta = f"{marca_nome} - {polo_nome} - {curso_nome} ({modelo_nome})"

            if chave_oferta in st.session_state.cursos_selecionados:
                st.warning(f"A oferta '{chave_oferta}' já existe e foi ignorada do arquivo.")
                continue
                
            # 2. Monta o dicionário de ingressantes personalizados
            ingressantes_personalizados = {}
            for col in df_ingressantes.columns:
                if '/' in str(col) and str(col).split('/')[0].isdigit(): # Heurística para achar colunas de período
                    chave_periodo = str(col).replace('/', '_')
                    ingressantes_personalizados[chave_periodo] = int(row[col])

            # 3. Monta o objeto completo da oferta
            st.session_state.cursos_selecionados[chave_oferta] = {
                "marca": marca_nome,
                "polo": polo_nome,
                "curso": curso_nome,
                "modelo": modelo_nome,
                "ticket": encontrar_ticket(curso_nome, marca_nome, modelo_nome, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade),
                "cluster": dados_curso['Cluster'],
                "sinergia": dados_curso['Sinergia'],
                "num_semestres": int(dados_curso['Qtde Semestres']),
                "alunos_por_semestre": {}, # Base histórica vazia, pois é um polo novo
                "modo_captacao": "Manual (Por Semestre)", # Define o modo de captação
                "ingressantes_personalizados": ingressantes_personalizados # Adiciona os dados do arquivo
            }
            cursos_adicionados += 1
        
        st.success(f"{cursos_adicionados} ofertas de curso foram adicionadas com sucesso a partir do arquivo!")
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
        st.error("Verifique se as colunas 'Curso' e 'Modalidade' existem e se o arquivo não está corrompido.")

def calcula_receita_por_polo_periodo(config: dict, todos_periodos: list) -> pd.DataFrame:
    cursos = config.get("cursos_selecionados", {})
    dados_agregados = {}

    for periodo in todos_periodos:
        chave_sufixo_temporal = "_" + periodo.replace("/", "_")
        for _, dados_curso in cursos.items():
            polo = dados_curso.get("polo")
            if not polo:
                continue

            # Chave única para agregação
            chave_agregacao = (polo, periodo)

            # Inicializa a chave no dicionário se for a primeira vez
            if chave_agregacao not in dados_agregados:
                dados_agregados[chave_agregacao] = {"receita": 0, "alunos": 0}

            ticket_curso = dados_curso.get("ticket", 0)
            alunos_no_periodo_curso = 0
            
            alunos_por_semestre = dados_curso.get(f"alunos_por_semestre{chave_sufixo_temporal}", {})
            for _, num_alunos in alunos_por_semestre.items():
                alunos_no_periodo_curso += num_alunos
            
            # Acumula os valores para a chave (polo, periodo)
            dados_agregados[chave_agregacao]["alunos"] += alunos_no_periodo_curso
            dados_agregados[chave_agregacao]["receita"] += alunos_no_periodo_curso * ticket_curso

    # Monta a lista de resultados a partir dos dados agregados
    lista_final = []
    for (polo, periodo), totais in dados_agregados.items():
        receita = totais["receita"]
        alunos = totais["alunos"]
        
        lista_final.append({
            "polo": polo,
            "semestre": periodo,
            "receita": receita,
            "alunos": alunos,
            "ticket_medio": receita / alunos if alunos > 0 else 0
        })
    
    return pd.DataFrame(lista_final)


def calcula_ticket_por_serie_no_semestre(config: dict, periodo: str) -> pd.DataFrame:
    """
    Calcula o ticket médio por série (semestre) para um dado período,
    agregando dados de múltiplos cursos.
    """
    cursos = config.get("cursos_selecionados", {})
    
    # Estruturas para acumular os totais de todos os cursos.
    receita_total_por_semestre = defaultdict(float)
    alunos_total_por_semestre = defaultdict(int)

    chave_sufixo_temporal = "_" + periodo.replace("/", "_")
    
    for _, dados_curso in cursos.items():
        if not dados_curso.get("polo"):
            continue

        ticket_curso = dados_curso.get("ticket", 0)
        alunos_por_semestre = dados_curso.get(f"alunos_por_semestre{chave_sufixo_temporal}", {})
        
        # Acumula a receita e o número de alunos para cada semestre.
        for semestre, num_alunos in alunos_por_semestre.items():
            receita_total_por_semestre[semestre] += num_alunos * ticket_curso
            alunos_total_por_semestre[semestre] += num_alunos

    # Calcula o ticket médio para cada semestre com base nos totais acumulados.
    ticket_medio_por_semestre = {}
    for semestre, total_alunos in alunos_total_por_semestre.items():
        if total_alunos > 0:
            receita_total = receita_total_por_semestre[semestre]
            ticket_medio_por_semestre[semestre] = receita_total / total_alunos
        else:
            ticket_medio_por_semestre[semestre] = 0
            
    # Converte o dicionário final para um DataFrame, conforme a assinatura da função.
    if not ticket_medio_por_semestre:
        return pd.DataFrame(columns=['TicketMedio'])

    df_resultado = pd.DataFrame.from_dict(
        ticket_medio_por_semestre, 
        orient='index', 
        columns=['TicketMedio']
    )
    df_resultado.index.name = 'Semestre'
    df_resultado = df_resultado.sort_index()

    return df_resultado