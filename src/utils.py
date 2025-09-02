import pandas as pd
import numpy as np
import streamlit as st
from streamlit import column_config
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from .formatting import formatador_k
from .data import encontrar_ticket
import time
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

def plot_custo_docente(df_precificacao_curso):
    # Agregar os dados
    df_plot = df_precificacao_curso.groupby('Semestre').agg(func='sum')

    # Criar a figura
    fig, ax = plt.subplots(figsize=(6, 6))

    # Fundo e cores
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    bar_color = '#1f77b4'

    # Gráfico de barras
    bars = ax.bar(
        df_plot.index,
        df_plot['total_uc_as'],
        color=bar_color
    )

    # Aumenta o limite superior do eixo Y para dar espaço para as labels
    ax.set_ylim(top=df_plot['total_uc_as'].max() * 1.15)

    # Adicionar data labels formatados em moeda brasileira
    for i, bar in enumerate(bars):
        height = bar.get_height()
        if i % 2 == 0:
            y_position = height + (df_plot['total_uc_as'].max() * 0.05)
        else:
            y_position = height

        ax.text(
            bar.get_x() + bar.get_width()/2,
            y_position,
            f'R$ {height:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            ha='center',
            va='bottom',
            color='white',
            fontsize=8,
            fontweight='bold'
        )

    formatter = FuncFormatter(formatador_k)
    ax.yaxis.set_major_formatter(formatter)

    ax.tick_params(colors='white', axis='y', labelsize=8) # Aplica a cor branca apenas ao eixo y
    ax.tick_params(colors='white', axis='x', labelsize=8) # Aplica a cor branca apenas ao eixo x

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel("Custo Docente por Série", fontdict={"color": "white", "fontsize": 13})
    return fig

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

def plot_ch_docente_por_categoria(df_precificacao_curso: pd.DataFrame):
    """
    Plota a distribuição da CH Docente como um gráfico de rosca,
    utilizando uma legenda para identificar as categorias e porcentagens.
    """
    totais_categoria = {}

    for _, row in df_precificacao_curso.iterrows():
        df_precificacao = row["Precificacao"]
        soma_categoria = df_precificacao.groupby("Tipo de CH")["ch_ator_pedagogico"].sum()
        for cat, valor in soma_categoria.items():
            totais_categoria[cat] = totais_categoria.get(cat, 0) + valor

    df_plot = pd.Series(totais_categoria).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 2))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Paleta de cores
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_plot)))

    wedges, _ = ax.pie(
        df_plot,
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='#0E1117')
    )

    # Criar os rótulos para a legenda, combinando categoria e porcentagem
    total = df_plot.sum()
    legend_labels = [
        f'{label} ({value/total:.1%})'
        for label, value in df_plot.items()
    ]

    # Adicionar e estilizar a legenda
    ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1), # Posiciona a legenda à direita do gráfico
        fontsize=8,
        facecolor='#0E1117',
        edgecolor='white',
        labelcolor='white',
        title_fontsize='12'
    )

    # Título
    ax.set_title("Distribuição da CH Docente por Categoria", color='white', fontsize=12, fontweight='bold', pad=20)
    
    # Garante que o layout se ajuste para a legenda não ser cortada
    plt.tight_layout(rect=[0, 0, 0.85, 1])

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

def oferta_resumida_por_curso(df_matrizes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key,item in st.session_state.cursos_selecionados.items():
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

def agrupar_oferta(OFERTA_POR_CURSO: pd.DataFrame, df_matrizes: pd.DataFrame, df_parametros: pd.DataFrame) -> pd.DataFrame:
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
        curso_selecionado = st.session_state.cursos_selecionados.get(curso_key)
                    
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
                afp_acumulador[f"{marca_nome} ({flag_presencial})"] = afp_acumulador.get(f"{marca_nome} ({flag_presencial})",0) + num_alunos
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
                    sinergia_acumulador[chave_acumulador] = sinergia_acumulador.get(chave_acumulador, 0) + num_alunos
                        
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

    # --- Montagem Final (sem alterações, já está preparada para a chave mais longa) ---
    for (uc, tipo_uc, marca, cluster, modelo, semestre, tipo_ch, polo), total_alunos in sinergia_acumulador.items():
        oferta_rows.append({
            "UC": uc,
            "Tipo de UC": tipo_uc,
            "Chave": f"{marca} - {uc} - {cluster} - {modelo} - {semestre} - {tipo_ch} - {polo}",
            "Semestre": semestre,
            "Modelo": modelo,
            "Base de Alunos": total_alunos,
            "Marca": marca,
            "Polo": polo,
            "Tipo de CH": tipo_ch
        })

    # Adicionar AFP
    for key, alunos in afp_acumulador.items():
        tipo_ch = "Assíncrono" if key.split(" (")[1].replace(")","") == "EAD/Semi" else "Síncrono"
        modelo_nome = "Presencial 70.30" if key.split(" (")[1].replace(")","") == "Presencial" else "EAD 10.10"
        oferta_rows.append({
            "UC": "AFP", "Tipo de UC": "AFP", "Chave": f"AFP - {key} - Todos os polos - Todos os cursos",
            "Semestre": 1, "Modelo": f"{modelo_nome}", "Base de Alunos": alunos,
            "Marca": key.split(" (")[0], "Polo": "Todos (Agrupado)", "Tipo de CH":tipo_ch 
        })
            
    if not oferta_rows:
        return pd.DataFrame()

    OFERTA_POR_UC = pd.DataFrame(oferta_rows)
    
    OFERTA_POR_UC = OFERTA_POR_UC.sort_values(
        by=['Marca', 'Polo', 'Semestre', 'UC', 'Tipo de CH']
    ).reset_index(drop=True)
    
    return OFERTA_POR_UC

def formatar_df_precificacao_oferta(df: pd.DataFrame):
    """
    Formata e exibe um DataFrame de precificação no Streamlit,
    lidando de forma segura com colunas que podem não existir.
    """
    # Função interna para destacar a linha "Total Geral"
    # Adicionada verificação 'if "Chave" in row' para segurança
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

    df = df.drop(columns=["Eficiência da UC"]) if "Eficiência da UC" in df.columns else df

    # Ordenar e deixar o "x" por ultimo
    numeric_mask = pd.to_numeric(df['Semestre'], errors='coerce').notna()
    df_numeric = df[numeric_mask]
    df_text = df[~numeric_mask]
    df_numeric['Semestre'] = pd.to_numeric(df_numeric['Semestre'])
    df_numeric_sorted = df_numeric.sort_values(by='Semestre')
    df = pd.concat([df_numeric_sorted, df_text])

    # Aplica o estilo usando o dicionário de formatação seguro
    df_styled = df.style.apply(highlight_total, axis=1).format(formatadores_seguros)

    # Exibe o DataFrame usando o dicionário de configuração seguro
    df_formatado = st.dataframe(
        df_styled,
        use_container_width=True,
        column_config=configuracao_segura,
        hide_index=True
    )
    
    return df_formatado

def calcula_df_final(df_parametros_editado: pd.DataFrame, OFERTA_POR_UC: pd.DataFrame) -> pd.DataFrame:
    df_sinergicas = OFERTA_POR_UC[OFERTA_POR_UC['Tipo de CH']!="Todas"]
    df_especificas = OFERTA_POR_UC[OFERTA_POR_UC['Tipo de CH']=="Todas"].drop(columns=['Tipo de CH'])

    # Max de alunos
    filtro = (df_parametros_editado['Parâmetro']=='Máximo de Alunos por Turma')
    df_precificacao_oferta_especificas = df_especificas.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo'])
    df_precificacao_oferta_especificas = df_precificacao_oferta_especificas.drop(columns=["Parâmetro"]).rename(columns={"Valor": "Máximo de Alunos"})
    df_precificacao_oferta_sinergicas = df_sinergicas.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo', 'Tipo de CH'])
    df_precificacao_oferta_sinergicas = df_precificacao_oferta_sinergicas.drop(columns=["Parâmetro"]).rename(columns={"Valor": "Máximo de Alunos"})
    df_precificacao_oferta = pd.concat([df_precificacao_oferta_especificas, df_precificacao_oferta_sinergicas], ignore_index=True)
    # Remuneração
    filtro = (df_parametros_editado['Parâmetro']=='Remuneração por Hora')
    df_precificacao_oferta = df_precificacao_oferta.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo', 'Tipo de CH', 'Ator Pedagógico'])
    df_precificacao_oferta = df_precificacao_oferta.drop(columns=["Parâmetro"]).rename(columns={"Valor": "Remuneração por Hora"})
    
    # CH Semanal
    filtro = (df_parametros_editado['Parâmetro']=='CH Semanal')
    df_precificacao_oferta = df_precificacao_oferta.merge(right=df_parametros_editado[filtro], how='left',on=['Tipo de UC','Modelo', 'Tipo de CH', 'Ator Pedagógico'])
    df_precificacao_oferta = df_precificacao_oferta.drop(columns=["Parâmetro"]).rename(columns={"Valor": "CH Semanal"})
    #df_precificacao_oferta['CH Semanal'] = df_precificacao_oferta['CH Semanal'] + 1 if df_precificacao_oferta['Tipo de CH'] == "Assíncrona" else df_precificacao_oferta['CH Semanal']

    df_precificacao_oferta["Qtde Turmas"] = np.ceil(df_precificacao_oferta["Base de Alunos"]/df_precificacao_oferta["Máximo de Alunos"])
    df_precificacao_oferta["CH por Semestre"] = df_precificacao_oferta["CH Semanal"] * df_precificacao_oferta["Qtde Turmas"] * 20
    df_precificacao_oferta["Custo Docente por Semestre"] = df_precificacao_oferta["CH por Semestre"] * df_precificacao_oferta["Remuneração por Hora"] *5.25*1.7*6/20
    
    df_precificacao_oferta

    df_pivot = df_precificacao_oferta.pivot_table(
                                        index=["Chave","Semestre","Base de Alunos"],
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
    for _, item in session_state.cursos_selecionados.items():
        for semestre in range(0,10):    
            soma_alunos += item.get("alunos_por_semestre").get(f"Semestre {semestre+1}",0)
    return soma_alunos

def calcula_base_alunos_por_semestre(session_state: dict, semestre:int) -> int:
    soma_alunos = 0
    for _, item in session_state.cursos_selecionados.items():
        soma_alunos += item.get("alunos_por_semestre").get(f"Semestre {semestre}", 0)
    return soma_alunos

def adiciona_linha_total(df: pd.DataFrame, base_alunos):
    somas = df.sum(numeric_only=True)

    linha_total = somas.to_dict()

    linha_total['Chave'] = 'Total Geral'
    linha_total['Semestre'] = 'x'
    linha_total["Eficiência da UC"] = 'x'
    linha_total['Base de Alunos'] = base_alunos

    df_com_total = pd.concat([df, pd.DataFrame([linha_total])], ignore_index=True)
    return df_com_total

def plotar_custo_total_pag2(df: pd.DataFrame)-> float:
    return np.round(float(df['Custo Total'].sum()),2)

def plotar_ch_total_pag2(df: pd.DataFrame)-> float:
    return np.round(float(df['CH Total'].sum()),1)

def plot_custo_docente_pag2(df: pd.DataFrame):
    # Agregar os dados
    df_plot = df.groupby('Semestre').agg(func='sum')

    # Criar a figura
    fig, ax = plt.subplots(figsize=(6, 6))

    # Fundo e cores
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    bar_color = '#1f77b4'

    # Gráfico de barras
    bars = ax.bar(
        df_plot.index,
        df_plot['Custo Total'],
        color=bar_color,
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
            color='white',
            fontsize=8,
            fontweight='bold'
        )

    formatter = FuncFormatter(formatador_k)
    ax.yaxis.set_major_formatter(formatter)

    ax.tick_params(colors='white', axis='y', labelsize=8)
    ax.tick_params(colors='white', axis='x', labelsize=8)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xticks(df_plot.index)
    # Define os rótulos dos ticks como números inteiros
    ax.set_xticklabels(df_plot.index.astype(int))

    ax.set_xlabel("Custo Docente por Série", fontdict={"color": "white", "fontsize": 13})
    return fig

def plot_ch_docente_por_categoria_pag2(df: pd.DataFrame):
    """
    Plota a distribuição da CH Docente como um gráfico de rosca,
    utilizando uma legenda para identificar as categorias e porcentagens.
    """
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

    fig, ax = plt.subplots(figsize=(12, 2))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Paleta de cores
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_plot)))

    wedges, _ = ax.pie(
        df_plot,
        startangle=90,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor='#0E1117')
    )

    # Criar os rótulos para a legenda, combinando categoria e porcentagem
    total = df_plot.sum()
    legend_labels = [
        f'{label} ({value/total:.1%})'
        for label, value in df_plot.items()
    ]

    # Adicionar e estilizar a legenda
    ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1), # Posiciona a legenda à direita do gráfico
        fontsize=8,
        facecolor='#0E1117',
        edgecolor='white',
        labelcolor='white',
        title_fontsize='12'
    )

    # Título
    ax.set_title("Distribuição da CH Docente por Categoria", color='white', fontsize=12, fontweight='bold', pad=20)
    
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

def plot_custo_aluno_por_semestre_pag2(dict_semestres: dict, ticket: float):
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
    ticket_line_color = '#d62728'
    
    # Dados para o gráfico
    x = df.index
    x = x.astype(int) + 1
    y = df['eficiencia']

    # Gráfico de linha padrão com marcadores
    ax.plot(x, y, color=line_color, linewidth=2.5, marker='o', markersize=8, label='Custo por Aluno')

    # Encontrar e destacar o maior valor
    max_val = y.max()
    max_idx = y.idxmax() + 1
    # Formata o texto do maior valor para não ter casas decimais e adicionar "R$"
    ax.plot(max_idx, max_val, marker='o', markersize=10, color='red', linestyle='None', label=f'Maior Custo/Aluno (R$ {int(max_val):,})')
    
    # Adicionar a linha constante para o valor do ticket
    ax.axhline(y=ticket, color=ticket_line_color, linestyle='--', linewidth=2, label=f'Ticket R$ {int(ticket):,}')

    # Adicionar data labels com formatação em reais e sem centavos
    for xi, yi in zip(x, y):
        ax.text(
            xi,
            yi + yi * 0.05,  # Posição um pouco acima do ponto
            f'R$ {int(yi):,}',
            ha='center',
            va='bottom',
            color='white',
            fontsize=10,
            fontweight='bold'
        )
    
    # Aumenta o limite superior do eixo Y para dar espaço para as labels e a linha do ticket
    ax.set_ylim(bottom=0, top=max(y.max() * 1.25, ticket * 1.25))
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
    
    ax.set_xlabel("Série", fontdict={"color": "white", "fontsize": 12})
    
    legend = ax.legend(facecolor='#0E1117', edgecolor='white', labelcolor='white')
    
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

def projetar_base_alunos(base_alunos_inicial: int, n_semestres_curso: int, dist_ingresso: tuple, taxa_evasao_inicial: float, decaimento_evasao: float):

    taxas_evasao = np.array([taxa_evasao_inicial * (decaimento_evasao ** i) for i in range(n_semestres_curso)])
    taxas_permanencia = 1 - taxas_evasao

    turmas = np.zeros(n_semestres_curso, dtype=int)
    turmas[0] = base_alunos_inicial

    historico_completo = []
    
    # Armazena o estado inicial
    alunos_por_semestre_dict = {f"Semestre {i + 1}": int(num_alunos) for i, num_alunos in enumerate(turmas)}
    historico_completo.append(alunos_por_semestre_dict)

    for semestre_da_simulacao in range(1, n_semestres_curso):

        turmas_seguinte = np.zeros(n_semestres_curso, dtype=int)

        for i in range(n_semestres_curso - 1, 0, -1):
            alunos_para_avancar = turmas[i-1]
            taxa_de_permanencia = taxas_permanencia[i-1]

            if alunos_para_avancar > 0:
                sobreviventes = np.random.binomial(n=alunos_para_avancar, p=taxa_de_permanencia)
            else:
                sobreviventes = 0

            turmas_seguinte[i] = int(max(0, sobreviventes))

        media_ingressantes, desvio_padrao_ingressantes = dist_ingresso
        # Divide a media_ingressantes em 60%/40% para semestres ímpares e pares
        if semestre_da_simulacao % 2 == 0:
            media_ingressantes *= 0.4
            desvio_padrao_ingressantes *= 0.4
        else:
            media_ingressantes *= 0.6
            desvio_padrao_ingressantes *= 0.6
        
        novos_ingressantes = np.round(np.random.normal(media_ingressantes, desvio_padrao_ingressantes))
        turmas_seguinte[0] = int(max(0, novos_ingressantes))

        turmas = turmas_seguinte.copy()

        # Armazena o estado atual no histórico
        alunos_por_semestre_dict = {f"Semestre {i + 1}": int(num_alunos) for i, num_alunos in enumerate(turmas)}
        historico_completo.append(alunos_por_semestre_dict)
    
    # Prepara o objeto de resultado final
    resultado_final = {
        "alunos_por_semestre": {f"Semestre {i + 1}": int(num_alunos) for i, num_alunos in enumerate(turmas)}
    }

    return resultado_final, historico_completo


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
        alunos_por_semestre = {f"Semestre {i}": 50 for i in range(1, num_semestres + 1)}
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
        "EAD Atual": "EAD 10.10",
        "Semi Presencial Atual": "Semi Presencial 40.20 Bacharelado",
        "Presencial Atual": "Presencial 70.30"
    }
    
    with st.spinner("Migrando ofertas para os novos modelos..."):
        novos_cursos_selecionados = {}
        migrados_sucesso = 0
        migrados_falha = 0
        falhas = []

        # Usamos list() para criar uma cópia e poder modificar o dicionário original
        for chave_antiga, config in list(st.session_state.cursos_selecionados.items()):
            modelo_antigo = config['modelo']

            if modelo_antigo in mapper_modelos:
                modelo_novo = mapper_modelos[modelo_antigo]
                curso = config['curso']

                # Verifica se o novo modelo é válido para o curso
                filtro = (df_dimensao_cursos['Curso'] == curso) & (df_dimensao_cursos['Modelo'] == modelo_novo)
                if df_dimensao_cursos[filtro].empty:
                    migrados_falha += 1
                    falhas.append(f"'{curso} ({modelo_novo})'")
                    # Mantém a oferta original se a migração falhar
                    novos_cursos_selecionados[chave_antiga] = config
                    continue

                # Se for válido, atualiza a configuração
                dados_curso_novo = df_dimensao_cursos[filtro].iloc[0]
                
                config['modelo'] = modelo_novo
                config['ticket'] = encontrar_ticket(config['curso'], config['marca'], modelo_novo, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade)
                config['cluster'] = dados_curso_novo['Cluster']
                config['sinergia'] = dados_curso_novo['Sinergia']
                # Mantém o num_semestres e alunos_por_semestre
                
                chave_nova = f"{config['marca']} - {config['polo']} - {config['curso']} ({modelo_novo})"
                novos_cursos_selecionados[chave_nova] = config
                migrados_sucesso += 1
            else:
                # Se não está no mapper, apenas mantém a oferta como está
                novos_cursos_selecionados[chave_antiga] = config
        
        st.session_state.cursos_selecionados = novos_cursos_selecionados

    st.success(f"{migrados_sucesso} ofertas foram migradas para o novo modelo com sucesso!")
    if migrados_falha > 0:
        st.warning(f"{migrados_falha} ofertas não puderam ser migradas, pois o novo modelo não foi encontrado para os seguintes cursos: {', '.join(falhas)}.")
    

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