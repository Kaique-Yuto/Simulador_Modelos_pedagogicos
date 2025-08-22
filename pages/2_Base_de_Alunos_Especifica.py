import streamlit as st
from src.data import carregar_dados
from src.utils import obter_modelos_para_curso


st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# Carrega ambos os DataFrames no início
df_matrizes = carregar_dados("databases/matrizes.xlsx")
df_parametros = carregar_dados("databases/parametros_turma.xlsx")
df_dimensao_cursos = carregar_dados("databases/dimensao_curso_modelo.xlsx")

# --- Inicialização do Session State ---
if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}

# --- Listas ---
LISTA_CURSOS_COMPLETA = sorted(df_dimensao_cursos['Curso'].unique().tolist())


st.markdown("Você selecionou a Simulação com Base de Alunos Específica, isso significa que você deve preencher manualmente um quantitativo de alunos em todos os semestres dos cursos selecionados.")
# --- Seções 1 e 2 (Adicionar e Configurar Cursos) ---
st.header("1. Adicione os Cursos para Simulação", divider='rainbow')
col1, col2 = st.columns([3, 1])
with col1:
    curso_para_adicionar = st.selectbox(
        "Adicione um curso à sua oferta", options=LISTA_CURSOS_COMPLETA, index=None, placeholder="Escolha um curso..."
    )
with col2:
    st.write(" ") # Para alinhar o botão
    add_button_disabled = not curso_para_adicionar
    if st.button("Adicionar Curso", type="primary", use_container_width=True, disabled=add_button_disabled):
        if curso_para_adicionar and curso_para_adicionar not in st.session_state.cursos_selecionados:
            # <<< LÓGICA MELHORADA AO ADICIONAR >>>
            # 1. Busca os modelos disponíveis para o curso selecionado
            modelos_disponiveis = obter_modelos_para_curso(df_dimensao_cursos, curso_para_adicionar)
            
            # 2. Verifica se existem modelos antes de adicionar
            if modelos_disponiveis:
                st.session_state.cursos_selecionados[curso_para_adicionar] = {
                    # Define o PRIMEIRO modelo disponível como padrão
                    "modelo_oferta": modelos_disponiveis[0], 
                    "numero_alunos": 50
                }
                st.rerun()
            else:
                # Informa ao usuário que o curso não pode ser adicionado
                st.error(f"O curso '{curso_para_adicionar}' não possui modelos de oferta cadastrados e não pode ser adicionado.")

        elif curso_para_adicionar:
            st.warning(f"O curso '{curso_para_adicionar}' já foi adicionado.")

st.header("2. Configure os Parâmetros de Cada Curso", divider='rainbow')
st.markdown("Aqui estão todos os cursos que adicionou para a simulação...") # Texto original omitido por brevidade

if not st.session_state.cursos_selecionados:
    st.info("Nenhum curso adicionado ainda. Comece selecionando um curso acima.")
else:
    # Copia das chaves para iterar, permitindo a remoção segura de itens
    for curso in list(st.session_state.cursos_selecionados.keys()):
        # Verifica se o curso ainda existe no estado da sessão (pode ter sido removido)
        if curso in st.session_state.cursos_selecionados:
            config = st.session_state.cursos_selecionados[curso]
            with st.expander(f"Configurações para: **{curso}**", expanded=True):
                config_col1, config_col2, config_col3 = st.columns([2, 2, 1])
                
                with config_col1:
                    opcoes_modelo_para_este_curso = obter_modelos_para_curso(df_dimensao_cursos, curso)
                    try:
                        index_atual = opcoes_modelo_para_este_curso.index(config["modelo_oferta"])
                    except ValueError:
                        index_atual = 0

                    modelo = st.selectbox(
                        "Modelo de Oferta", 
                        options=opcoes_modelo_para_este_curso,
                        index=index_atual,
                        key=f"modelo_{curso}"
                    )
                    st.session_state.cursos_selecionados[curso]["modelo_oferta"] = modelo

                with config_col2:
                    alunos = st.number_input(
                        "Número de Alunos Projetado", 
                        min_value=0, 
                        step=5, 
                        key=f"alunos_{curso}",
                        value=config.get("numero_alunos", 50)
                    )
                    st.session_state.cursos_selecionados[curso]["numero_alunos"] = alunos

                with config_col3:
                    st.write(" ") # Para alinhar o botão
                    if st.button("Remover", key=f"remover_{curso}", use_container_width=True):
                        del st.session_state.cursos_selecionados[curso]
                        st.rerun()