import streamlit as st
import pandas as pd
import numpy as np
from streamlit import column_config
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
import matplotlib.pyplot as plt
# --- Configuração da Página ---
st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# --- Carregamento dos Dados ---
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

# Carrega ambos os DataFrames no início
df_matrizes = carregar_dados("databases/matrizes.xlsx")
df_parametros = carregar_dados("databases/parametros_turma.xlsx")

def colorir_semestres(row: pd.Series):
    """Aplica uma cor de fundo diferente para linhas de semestres pares."""
    cor = "#2e2f31"
    if row['Semestre'] % 2 == 0:
        return [f'background-color: {cor}'] * len(row)
    return [''] * len(row)



def format_currency(value):
    return locale.currency(value, grouping=True, symbol=True)

def formatar_valor_brl(valor):
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    if isinstance(valor, (int, float)):
        return f'R$ {valor:_.2f}'.replace('.', ',').replace('_', '.')
    return valor

def plot_custo_docente(df_precificacao_curso):
    # Agregar os dados
    df_plot = df_precificacao_curso.groupby('Semestre').agg(func='sum')

    # Criar a figura (mais compacto)
    fig, ax = plt.subplots(figsize=(10,8.5))

    # Fundo azul escuro (igual tema dark do Streamlit)
    fig.patch.set_facecolor('#0E1117')  
    ax.set_facecolor('#0E1117')

    # Cor única (azul escuro para barras)
    bar_color = '#1f77b4'

    # Criar gráfico de barras
    bars = ax.bar(
        df_plot.index, 
        df_plot['total_uc_as'], 
        color=bar_color
    )

    # Adicionar data labels formatados em moeda brasileira
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2, 
            height, 
            f'R$ {height:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),  
            ha='center', 
            va='bottom', 
            color='white',
            fontsize=9,
            fontweight='bold'
        )

    # Títulos e labels
    ax.set_title("Custo Docente por Semestre", color='white', fontsize=20, fontweight='bold')

    # Ajustar ticks
    ax.tick_params(colors='white')

    # Tirar bordas superiores e direitas
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig

def plot_ch_docente_por_categoria(df_precificacao_curso: pd.DataFrame):
    # Dicionário para acumular totais por categoria
    totais_categoria = {}

    # Itera sobre cada linha do dataframe principal
    for _, row in df_precificacao_curso.iterrows():
        df_precificacao = row["Precificacao"]

        # Soma CH por categoria dentro do dataframe da linha
        soma_categoria = df_precificacao.groupby("Tipo de CH")["ch_ator_pedagogico"].sum()

        # Acumula no dicionário global
        for cat, valor in soma_categoria.items():
            totais_categoria[cat] = totais_categoria.get(cat, 0) + valor

    # Transforma em DataFrame para plotagem
    df_plot = pd.Series(totais_categoria).sort_values(ascending=False)

    # Criar figura
    fig, ax = plt.subplots(figsize=(4,4))

    # Fundo escuro
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Paleta monocromática azul
    colors = ['#1f77b4', '#2c82c9', '#3a9bdc', '#62b0e8', '#8cc7f0']

    # Criar gráfico de rosca
    wedges, texts, autotexts = ax.pie(
        df_plot,
        labels=df_plot.index,
        autopct=lambda p: f'{p:.1f}%',
        startangle=90,
        colors=colors[:len(df_plot)],
        wedgeprops=dict(width=0.4, edgecolor='#0E1117')
    )

    # Ajustar estilo dos textos
    for text in texts:
        text.set_color('white')
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')

    # Título
    ax.set_title("Distribuição da CH Docente por Categoria", color='white', fontsize=10, fontweight='bold')

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
# --- Título e Descrição ---
st.title("Simulação de Precificação para Polos 🎓")
st.markdown("Use esta ferramenta para montar um cenário de simulação para o seu polo, personalizando a oferta da maneira que lhe interessa.")

# --- Inicialização do Session State ---
if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}

# --- Listas e Opções ---
LISTA_CURSOS_COMPLETA = [
    "Administração", "Direito", "Enfermagem", "Engenharia Civil",
    "Psicologia", "Ciência da Computação", "Pedagogia", "Arquitetura"
]
MODELOS_OFERTA = ["EAD 10/10", "Semi 30/20"]
MAPEAMENTO_MODELOS = {
    "EAD 10/10": "10_10_bacharelado",
    "Semi 30/20": "30_20_semi_bacharelado" # Ajustado para corresponder à imagem
}

# --- Seções 1 e 2 (Adicionar e Configurar Cursos) ---
st.header("1. Adicione os Cursos para Simulação", divider='rainbow')
col1, col2 = st.columns([3, 1])
with col1:
    curso_para_adicionar = st.selectbox(
        "Adicione um curso à sua oferta", options=LISTA_CURSOS_COMPLETA, index=None, placeholder="Escolha um curso..."
    )
with col2:
    add_button_disabled = not curso_para_adicionar
    if st.button("Adicionar Curso", type="primary", use_container_width=True, disabled=add_button_disabled):
        if curso_para_adicionar and curso_para_adicionar not in st.session_state.cursos_selecionados:
            st.session_state.cursos_selecionados[curso_para_adicionar] = {
                "modelo_oferta": MODELOS_OFERTA[0], "numero_alunos": 50
            }
            st.rerun()
        elif curso_para_adicionar:
            st.warning(f"O curso '{curso_para_adicionar}' já foi adicionado.")

st.header("2. Configure os Parâmetros de Cada Curso", divider='rainbow')
st.markdown("Aqui estão todos os cursos que adicionou para a simulação. Você precisa configurá-los manualmente. Selecione um modelo de oferta e entre uma base de alunos para cada um dos cursos. Utilize o botão acima 'Adicionar Curso' para complementar essa lista. Quando estiver satisfeito com a seleção, clique em 'Confirmar e Rodar Cálculos'")
if not st.session_state.cursos_selecionados:
    st.info("Nenhum curso adicionado ainda. Comece selecionando um curso acima.")
else:
    for curso, config in st.session_state.cursos_selecionados.items():
        with st.expander(f"Configurações para: **{curso}**", expanded=True):
            config_col1, config_col2, config_col3 = st.columns([2, 2, 1])
            with config_col1:
                modelo = st.selectbox("Modelo de Oferta", options=MODELOS_OFERTA, key=f"modelo_{curso}")
                st.session_state.cursos_selecionados[curso]["modelo_oferta"] = modelo
            with config_col2:
                alunos = st.number_input("Número de Alunos Projetado", min_value=0, step=5, key=f"alunos_{curso}")
                st.session_state.cursos_selecionados[curso]["numero_alunos"] = alunos
            with config_col3:
                if st.button("Remover", key=f"remover_{curso}", use_container_width=True):
                    del st.session_state.cursos_selecionados[curso]
                    st.rerun()

# --- Seção 3: Executar Simulação ---
st.header("3. Executar Simulação", divider='rainbow')

# Verifica se os dataframes essenciais foram carregados
dataframes_carregados = df_matrizes is not None and df_parametros is not None

if st.button("Confirmar e Rodar Cálculos", type="primary", use_container_width=True, disabled=not dataframes_carregados):
    if not st.session_state.cursos_selecionados:
        st.warning("Adicione pelo menos um curso antes de rodar os cálculos.")
    elif dataframes_carregados:
        # Apenas um indicador de que o botão foi pressionado
        st.session_state['simulacao_ativa'] = True

# A lógica de exibição agora fica fora do botão, mas depende de um estado.
# Isso permite que o data_editor recalcule a página a cada edição sem precisar clicar no botão novamente.
if st.session_state.get('simulacao_ativa', False) and dataframes_carregados:
    st.header("4. Analítico de Custos", divider='rainbow')

    for curso, config in st.session_state.cursos_selecionados.items():
        with st.expander(f"Análise do Curso de {curso}"):
        
            # Pega o nome técnico do modelo
            modelo_selecionado = config["modelo_oferta"]
            modelo_no_df = MAPEAMENTO_MODELOS.get(modelo_selecionado)
            
            # --- Parte 1: Mostrar a Matriz Curricular (UCs) ---
            
            st.subheader(f"Matriz Curricular")
            if modelo_no_df:
                df_matriz_curso = df_matrizes[df_matrizes['MODELO'] == modelo_no_df]
                if not df_matriz_curso.empty:
                    df_display = df_matriz_curso[['Semestre', 'UC', 'CH TOTAL', 'PRESENCIALIDADE', 'ASSÍNCRONA', 'SÍNCRONA MED']]
                    df_display = df_display.style.apply(colorir_semestres, axis=1)
                    with st.expander("Expandir matriz"):
                        st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Semestre": column_config.NumberColumn("SEMESTRE", format="%d"),  # inteiro
                            "PRESENCIALIDADE": "PRESENCIALIDADE (hr)",
                            "ASSÍNCRONA": "ASSÍNCRONA (hr)",
                            "SÍNCRONA MED": "SÍNCRONA MED (hr)"
                        }
                    )
                else:
                    st.warning(f"Matriz não encontrada para o modelo: '{modelo_no_df}'")
            
            # --- Parte 2: Mostrar Tabela de Parâmetros Editáveis ---
            st.subheader(f"Parâmetros de Simulação")
            
            # Se os parâmetros para este curso ainda não foram salvos no estado da sessão,
            # filtramos os padrões do DF principal e os salvamos.
            if ('parametros_editaveis' not in config or len(config.get('parametros_editaveis'))==0) and modelo_no_df:
                parametros_iniciais = df_parametros[df_parametros['Modelo'] == modelo_no_df].copy()
                st.session_state.cursos_selecionados[curso]['parametros_editaveis'] = parametros_iniciais

            # Exibe a tabela editável usando os dados salvos no estado da sessão
            if 'parametros_editaveis' in config:
                df_para_editar = config['parametros_editaveis']
                
                # st.data_editor é o componente chave aqui.
                with st.expander("Expandir parâmetros"):
                    edited_df = st.data_editor(
                        df_para_editar,
                        hide_index=True,
                        use_container_width=True,
                        disabled=['Modelo', 'Tipo de UC', 'Parâmetro', 'Tipo de CH', 'Ator Pedagógico'],
                        key=f"editor_{curso}"
                    )
                if edited_df.empty or not (edited_df["Parâmetro"] == "Máximo de Alunos por Turma").any():
                    st.warning(f"Sem parâmetros para o modelo {modelo_no_df} no curso {curso}. Pulando.")
                    continue
                # Salva o dataframe editado de volta no estado da sessão.
                # É isso que garante a persistência das alterações do usuário.
                st.session_state.cursos_selecionados[curso]['parametros_editaveis'] = edited_df
            
            # Começo da precificação
            uc_rows = []
            for _, row in df_matriz_curso.iterrows():
                new_uc_row = {}
                new_uc_row['UC'] = row['UC']
                new_uc_row['Semestre'] = row['Semestre']
                new_uc_row['Tipo de UC'] = row['Tipo de UC']

                rows = []
                for _, row in edited_df[(edited_df['Parâmetro']=='Máximo de Alunos por Turma') & (edited_df['Tipo de UC'] == new_uc_row.get("Tipo de UC"))].iterrows():
                    new_row = {}
                    new_row['curso'] = curso
                    new_row['Modelo'] = modelo_no_df
                    new_row['Tipo de UC'] = row['Tipo de UC']
                    new_row['Tipo de CH'] = row['Tipo de CH']
                    new_row['Ator Pedagógico'] = row['Ator Pedagógico']
                    new_row['qtde_turmas'] = np.ceil(st.session_state.cursos_selecionados[curso]['numero_alunos'] / row['Valor'])
                    rows.append(new_row)
                df_precificacao_uc = pd.DataFrame(rows, columns=["curso","Modelo",'Tipo de UC',"Tipo de CH","Ator Pedagógico","qtde_turmas"])

                # Fazendo join para trazer ch
                df_ch_semanal = edited_df[edited_df['Parâmetro'] == 'CH Semanal'].copy().drop(columns=['Modelo', 'Parâmetro']).rename(mapper={"Valor": "CH Semanal"}, axis=1)
                df_precificacao_uc = df_precificacao_uc.merge(right=df_ch_semanal, how='left',on=['Tipo de CH', 'Ator Pedagógico', 'Tipo de UC'])
                df_precificacao_uc['ch_ator_pedagogico'] = df_precificacao_uc['qtde_turmas'] * df_precificacao_uc['CH Semanal']
                
                # Fazendo join para trazer remuneração
                df_ch_remuneracao = edited_df[edited_df['Parâmetro'] == 'Remuneração por Hora'].copy().drop(columns=['Modelo', 'Parâmetro']).rename(mapper={"Valor": "Remuneração por Hora"}, axis=1)
                df_precificacao_uc = df_precificacao_uc.merge(right=df_ch_remuneracao, how='left',on=['Tipo de CH', 'Ator Pedagógico','Tipo de UC'])
                df_precificacao_uc['custo_docente_am'] = df_precificacao_uc['ch_ator_pedagogico'] *5.25*1.7*df_precificacao_uc['Remuneração por Hora']
                df_precificacao_uc['custo_docente_as'] = df_precificacao_uc['custo_docente_am']*6 
                
                new_uc_row['Precificacao'] = df_precificacao_uc
                uc_rows.append(new_uc_row)
            df_precificacao_curso = pd.DataFrame(uc_rows)
            try:
                df_precificacao_curso['total_uc_am'] = df_precificacao_curso['Precificacao'].apply(lambda df: df['custo_docente_am'].sum())
                df_precificacao_curso['total_uc_as'] = df_precificacao_curso['Precificacao'].apply(lambda df: df['custo_docente_as'].sum())
                df_precificacao_curso['total_ch_uc'] = df_precificacao_curso['Precificacao'].apply(lambda df: pd.to_numeric(df['ch_ator_pedagogico'], errors='coerce').sum())       
            except (TypeError, KeyError) as e:
                st.error(f"Não foi possível calcular os totais por UC. Verifique se a coluna 'Precificacao' e suas colunas internas estão corretas. Erro: {e}")
                st.stop()

            col1, col2 = st.columns(2)
            with col1:
                col3,col4 = st.columns(2)
                with col3:
                    st.metric(
                        label="Custo Total",
                        value=locale.currency(plotar_custo_total(df_precificacao_curso), grouping=True, symbol="R$")
                    )
                with col4:
                    st.metric(label="CH Total", value=plotar_ch_total(df_precificacao_curso))
                st.pyplot(plot_custo_docente(df_precificacao_curso), use_container_width=False)
            with col2:
                st.pyplot(plotar_indicador_eficiencia(70, config.get("numero_alunos")))
                st.pyplot(plot_ch_docente_por_categoria(df_precificacao_curso))
            # O expander principal que conterá todos os semestres
            st.subheader("Detalhamento")
            with st.expander("Expandir detalhamento por semestre"):
                semestres_unicos = sorted(df_precificacao_curso["Semestre"].dropna().unique())
                for semestre in semestres_unicos:
                    with st.expander(f"{semestre}º Semestre"):
                        df_do_semestre = df_precificacao_curso[df_precificacao_curso["Semestre"] == semestre]

                        total_semestre_am = df_do_semestre['total_uc_am'].sum()
                        total_semestre_as = df_do_semestre['total_uc_as'].sum()
                        total_ch_semestre = df_do_semestre['total_ch_uc'].sum()*20
                        taxa_eficiencia = config.get("numero_alunos")/total_ch_semestre
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                label="Custo Mensal Aproximado", 
                                value=formatar_valor_brl(total_semestre_am)
                            )
                            st.metric(
                                label="Carga Horária Total",
                                value=f"{np.round(total_ch_semestre,1)} h"
                            )
                        with col2:
                            st.metric(
                                label="Custo Total do Semestre", 
                                value=formatar_valor_brl(total_semestre_as)
                            )
                            st.metric(
                                label="Eficiência da UC",
                                value=f"{taxa_eficiencia:.2f}"
                            )
                        st.divider()

                        # Loop para exibir o detalhe de cada UC
                        for _, row in df_do_semestre.iterrows():
                            st.markdown(f"**UC:** {row['UC']}")
                            format_detalhe_precificacao_uc(row)


            st.subheader("Mais informações aqui")
            with st.expander("Clique para ver mais"):
                st.write("Aqui vão outras informações detalhadas...")
        

# --- Debug na Barra Lateral ---
st.sidebar.title("Debug Info")
with st.sidebar.expander("Dados da Simulação (Session State)"):
    st.json(st.session_state)