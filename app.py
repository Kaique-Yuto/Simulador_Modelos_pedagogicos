import streamlit as st
import pandas as pd
from src.data import carregar_dados
from src.utils import calcular_precificacao_curso

# --- Configuração da Página ---
st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# --- Carregamento dos Dados ---
df_matrizes = carregar_dados("databases/matrizes.xlsx")
df_parametros = carregar_dados("databases/parametros_turma.xlsx")

# --- Título e Descrição ---
st.title("Simulação de Precificação para Polos 🎓")
st.markdown("Use esta ferramenta para montar um cenário de simulação para o seu polo, personalizando a oferta da maneira que lhe interessa.")

# --- Inicialização do Session State ---
if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}
if 'simulacao_ativa' not in st.session_state:
    st.session_state['simulacao_ativa'] = False

# --- Listas e Opções ---
LISTA_CURSOS_COMPLETA = [
    "Administração", "Direito", "Enfermagem", "Engenharia Civil",
    "Psicologia", "Ciência da Computação", "Pedagogia", "Arquitetura"
]
MODELOS_OFERTA = ["EAD 10/10", "Semi 30/20"]
MAPEAMENTO_MODELOS = {
    "EAD 10/10": "10_10_bacharelado",
    "Semi 30/20": "30_20_semi_bacharelado"
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

dataframes_carregados = df_matrizes is not None and df_parametros is not None

if st.button("Confirmar e Rodar Cálculos", type="primary", use_container_width=True, disabled=not dataframes_carregados):
    if not st.session_state.cursos_selecionados:
        st.warning("Adicione pelo menos um curso antes de rodar os cálculos.")
    elif dataframes_carregados:
        with st.spinner("Processando simulação..."):
            for curso, config in st.session_state.cursos_selecionados.items():
                modelo_selecionado = config["modelo_oferta"]
                modelo_no_df = MAPEAMENTO_MODELOS.get(modelo_selecionado)
                numero_alunos = config["numero_alunos"]

                df_matriz_curso = df_matrizes[df_matrizes['MODELO'] == modelo_no_df]
                
                if 'parametros_editaveis' not in config or len(config.get('parametros_editaveis', [])) == 0:
                    parametros_iniciais = df_parametros[df_parametros['modelo'] == modelo_no_df].copy()
                    st.session_state.cursos_selecionados[curso]['parametros_editaveis'] = parametros_iniciais
                
                edited_df = st.session_state.cursos_selecionados[curso]['parametros_editaveis']

                df_precificacao_curso = calcular_precificacao_curso(
                    curso=curso,
                    modelo_no_df=modelo_no_df,
                    numero_alunos=numero_alunos,
                    df_matriz_curso=df_matriz_curso,
                    edited_df=edited_df
                )
                
                st.session_state.cursos_selecionados[curso]['df_matriz_curso'] = df_matriz_curso
                st.session_state.cursos_selecionados[curso]['df_precificacao_curso'] = df_precificacao_curso
        
        st.session_state['simulacao_ativa'] = True
        st.success("Cálculos concluídos! Navegue para a página 'Resultados da Simulação' na barra lateral para ver a análise.")


# --- Debug na Barra Lateral ---
st.sidebar.title("Debug Info")
with st.sidebar.expander("Dados da Simulação (Session State)"):
    st.json(st.session_state)