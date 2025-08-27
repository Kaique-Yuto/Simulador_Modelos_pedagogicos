import streamlit as st
from src.data import carregar_dados
from src.utils import obter_modelos_para_curso, oferta_resumida_por_curso, agrupar_oferta, agrupar_oferta_v2, formatar_df_precificacao_oferta, calcular_resumo_semestre, calcula_base_alunos_por_semestre, calcula_base_alunos_total, adiciona_linha_total,calcula_df_final, plotar_custo_total_pag2, plotar_ch_total_pag2, plot_custo_docente_pag2, plot_ch_docente_por_categoria_pag2, calcula_eficiencia_para_todos_semestre, plot_eficiencia_por_semestre_pag2, formatar_df_por_semestre, projetar_base_alunos
from src.formatting import formatar_valor_brl
import pandas as pd
import numpy as np
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
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


st.markdown("Você selecionou a Simulação com Base de Alunos Projetada, isso significa que você poderá escolher uma base inicial de calouros para os cursos selecionados. Para cada um dos cursos você deverá preencher uma premissa de ingresso e evasão, o aplicativo irá simular o avanço e a formação de novas turmas automaticamente")


# --- Seção 1 (Adicionar Cursos) ---
st.header("1. Adicione as Ofertas de Curso para Simulação", divider='rainbow')

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    curso_para_adicionar = st.selectbox(
        "Escolha um curso", 
        options=LISTA_CURSOS_COMPLETA, 
        index=None, 
        placeholder="Selecione o curso..."
    )

modelos_disponiveis = []
if curso_para_adicionar:
    modelos_disponiveis = obter_modelos_para_curso(df_dimensao_cursos, curso_para_adicionar)

with col2:
    modelo_para_adicionar = st.selectbox(
        "Escolha o modelo de oferta", 
        options=modelos_disponiveis, 
        index=None, 
        placeholder="Selecione o modelo...",
        disabled=not curso_para_adicionar # Desabilita se nenhum curso for escolhido
    )

with col3:
    st.write(" ") 
    add_button_disabled = not (curso_para_adicionar and modelo_para_adicionar)
    
    if st.button("Adicionar Oferta", type="primary", use_container_width=True, disabled=add_button_disabled):
        chave_oferta = f"{curso_para_adicionar} ({modelo_para_adicionar})"
        if chave_oferta not in st.session_state.cursos_selecionados:
            try:
                # Busca o número de semestres filtrando por CURSO e MODELO
                filtro = (df_dimensao_cursos['Curso'] == curso_para_adicionar) & (df_dimensao_cursos['Modelo'] == modelo_para_adicionar)
                cluster = df_dimensao_cursos.loc[filtro, 'Cluster'].iloc[0]
                sinergia = df_dimensao_cursos.loc[filtro, 'Sinergia'].iloc[0]
                num_semestres = int(df_dimensao_cursos.loc[filtro, 'Qtde Semestres'].iloc[0])
                alunos_por_semestre = {f"Semestre {i}": 50 for i in range(1, num_semestres + 1)}

                st.session_state.cursos_selecionados[chave_oferta] = {
                    "curso": curso_para_adicionar,
                    "modelo": modelo_para_adicionar,
                    "cluster": cluster,
                    "sinergia": sinergia,
                    "num_semestres": num_semestres,
                    "alunos_por_semestre": alunos_por_semestre
                }
            except (IndexError, TypeError):
                st.error(f"Não foi possível encontrar a 'Qtde Semestres' para o curso '{curso_para_adicionar}' com o modelo '{modelo_para_adicionar}'.")
        else:
            st.warning(f"A oferta '{chave_oferta}' já foi adicionada.")

# --- Seção 2 (Configurar Cursos) ---
st.header("2. Configure os Parâmetros de Cada Oferta", divider='rainbow')
st.markdown("Aqui estão todas as ofertas que você adicionou para a simulação...") 

if not st.session_state.cursos_selecionados:
    st.info("Nenhuma oferta adicionada ainda. Comece selecionando um curso e um modelo acima.")
else:
    for chave_oferta in list(st.session_state.cursos_selecionados.keys()):
        if chave_oferta in st.session_state.cursos_selecionados:
            config = st.session_state.cursos_selecionados[chave_oferta]
            
            with st.expander(f"Configurações para: **{chave_oferta}**", expanded=True):
                
                info_col1, info_col2 = st.columns([4, 1])
                
                with info_col1:
                    st.markdown(f"**Curso:** `{config['curso']}`")
                    st.markdown(f"**Modelo de Oferta:** `{config['modelo']}`")

                with info_col2:
                    st.write("")
                    if st.button("Remover", key=f"remover_{chave_oferta}", use_container_width=True):
                        del st.session_state.cursos_selecionados[chave_oferta]
                        st.rerun()
                
                st.markdown("---") 

                st.write("**Parâmetros para Simulação da Base de Alunos:**")

                sim_col1, sim_col2 = st.columns(2)

                with sim_col1:
                    alunos_iniciais = st.number_input(
                        "Alunos da turma inicial", 
                        min_value=0, 
                        step=5, 
                        value=100, 
                        key=f"sim_iniciais_{chave_oferta}"
                    )
                    media_ingressantes = st.number_input(
                        "Média de ingressantes por semestre", 
                        min_value=0, 
                        step=5, 
                        value=100, 
                        key=f"sim_media_{chave_oferta}"
                    )
                    taxa_evasao_inicial = st.slider(
                        "Taxa de Evasão Inicial (%)", 
                        min_value=0, 
                        max_value=100, 
                        value=30, 
                        key=f"sim_evasao_{chave_oferta}"
                    )

                with sim_col2:
                    n_semestres = st.slider(
                        "Número de semestres",
                        min_value=1,
                        max_value=config.get("num_semestres"),
                        value=config.get("num_semestres"),
                        step=1
                    )
                    
                    desvio_padrao_ingressantes = st.number_input(
                        "Desvio padrão dos ingressantes", 
                        min_value=0, 
                        step=1, 
                        value=0, 
                        key=f"sim_dp_{chave_oferta}"
                    )

                    decaimento_evasao = st.slider(
                        "Decaimento da Evasão a/s (%)", 
                        min_value=0, 
                        max_value=100, 
                        value=10, 
                        key=f"sim_decaimento_{chave_oferta}"
                    )
                if st.button("Simular Base de Alunos", key=f"simular_{chave_oferta}", use_container_width=True, type="primary"):                    
                    resultado_simulacao = projetar_base_alunos(
                        base_alunos_inicial=alunos_iniciais,
                        n_semestres_curso=n_semestres,
                        dist_ingresso=(media_ingressantes, desvio_padrao_ingressantes),
                        taxa_evasao_inicial=taxa_evasao_inicial / 100.0,
                        decaimento_evasao=decaimento_evasao / 100.0
                    )
                    
                    st.session_state.cursos_selecionados[chave_oferta]["alunos_por_semestre"] = resultado_simulacao["alunos_por_semestre"]
                    st.rerun()

                st.markdown("---")
                
                alunos_data = config.get("alunos_por_semestre", {})
                if not alunos_data:
                    st.info("Clique em 'Simular Base de Alunos' para gerar a projeção.")
                else:
                    st.subheader("**Base de Alunos projetada**")
                    num_semestres = config.get("num_semestres", 0)
                    
                    with st.expander("**Alunos por Período**"):
                        cols = st.columns(4)
                        alunos_acumulados = 0  # Inicializa a variável antes do loop principal
                        
                        for i in range(num_semestres):
                            semestre_key = f"Semestre {i + 1}"
                            col_index = i % 4
                            semestre_index = i % 2 + 1
                            ano_index = 2026 + i // 2
                            
                            alunos_acumulados += alunos_data.get(semestre_key, 0)
                            with cols[col_index]:
                                st.metric(
                                    label=f"Alunos em {ano_index}/{semestre_index}",
                                    value=alunos_acumulados
                                )
                    with st.expander("**Alunos por série**"):
                        cols = st.columns(4)
                        for i in range(num_semestres):
                            semestre_key = f"Semestre {i + 1}"
                            col_index = i % 4
                            with cols[col_index]:
                                st.metric(
                                    label=f"Alunos na Série {i+1}",
                                    value=alunos_data.get(semestre_key, 0)
                                )



# Filtrar apenas modelos selecionados para mostrar nos parâmetros
modelos_selecionados = set([])
for key, item in st.session_state.cursos_selecionados.items():
    modelos_selecionados.add(item.get('modelo')) 
df_parametros_editado = df_parametros[(df_parametros["Modelo"].isin(modelos_selecionados)) | (df_parametros["Tipo de UC"] == "AFP")]


# --- Seção 3: Executar Simulação ---
st.header("3. Executar Simulação", divider='rainbow')
with st.expander("Mostrar Parâmetros", expanded=True):
    st.subheader(f"Parâmetros de Simulação")

    ignorar_tcc = st.checkbox(
        label="Não considerar o TCC na análise"
    )
    if ignorar_tcc:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "TCC"]
        df_matrizes = df_matrizes[df_matrizes["Tipo de UC"] != "TCC"]


    ignorar_estagio = st.checkbox(
        label="Não considerar Estágio na análise"
    )
    if ignorar_estagio:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "ESTÁGIO"]

    ignorar_AFP = st.checkbox(
        label="Não considerar AFP na Análise"
    )
    if ignorar_AFP:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "AFP"]

    ignorar_extensao = st.checkbox(
        label="Não considerar Extensão na análise"
    )
    if ignorar_extensao:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "EXTENSÃO"]


    df_parametros_editado = st.data_editor(df_parametros_editado,
                                           hide_index=True,
                                            use_container_width=True,
                                            disabled=['Modelo', 'Tipo de UC', 'Parâmetro', 'Tipo de CH', 'Ator Pedagógico']
                                        )
# Verifica se os dataframes essenciais foram carregados
dataframes_carregados = df_matrizes is not None and df_parametros is not None and df_dimensao_cursos is not None

if st.button("Confirmar e Rodar Cálculos", type="primary", use_container_width=True, disabled=not dataframes_carregados):
    if not st.session_state.cursos_selecionados:
        st.warning("Adicione pelo menos um curso antes de rodar os cálculos.")
    elif dataframes_carregados:
        # Apenas um indicador de que o botão foi pressionado
        st.session_state['simulacao_ativa'] = True

if st.session_state.cursos_selecionados:
    st.header("4. Analítico de Custos", divider='rainbow')
    OFERTA_POR_CURSO = oferta_resumida_por_curso(df_matrizes)

    OFERTA_POR_UC = agrupar_oferta(OFERTA_POR_CURSO, df_matrizes)

    df_final = calcula_df_final(df_parametros_editado, OFERTA_POR_UC)

    base_alunos = calcula_base_alunos_total(st.session_state)

    df_com_total = adiciona_linha_total(df_final, base_alunos)


    st.subheader("Resumo")
    col1, col2 = st.columns(2, border=True)
    with col1:
        col3,col4 = st.columns([2,1])
        with col3:
            st.metric(
                label="Custo Total",
                value=locale.currency(plotar_custo_total_pag2(df_final), grouping=True, symbol="R$")
                ,width='stretch'
            )
            st.metric(label="Base de Alunos", value=locale.format_string('%d',base_alunos, grouping=True),width='content')
            st.metric(label="Custo por Aluno", value=locale.currency(plotar_custo_total_pag2(df_final)/base_alunos, grouping=True, symbol="R$"))
        with col4:
            st.metric(label="CH Total", value=locale.format_string('%.1f', plotar_ch_total_pag2(df_final), grouping=True),width='content')
            eficiencia = np.round(base_alunos/plotar_ch_total_pag2(df_final),2)
            st.metric(label="Eficiência", value = eficiencia,width='content')
        st.pyplot(plot_custo_docente_pag2(df_final), use_container_width=False)
        
    with col2:
        st.pyplot(plot_ch_docente_por_categoria_pag2(df_final))
        dict_semestres = calcula_eficiencia_para_todos_semestre(df_final, st.session_state)
        st.pyplot(plot_eficiencia_por_semestre_pag2(dict_semestres), use_container_width=False)

        
    with st.expander("Detalhamento por Semestre"):
        for i in range(df_final['Semestre'].max()):
            df_por_semestre = df_final[df_final['Semestre'] == (i+1)]
            base_alunos_semestre = calcula_base_alunos_por_semestre(st.session_state, i+1)
            ch_total_semestre, custo_total_semestre, custo_mensal, eficiencia = calcular_resumo_semestre(df_por_semestre, base_alunos_semestre)          
            df_por_semestre = adiciona_linha_total(df_por_semestre, base_alunos_semestre)
            with st.expander(f"{i+1}º Semestre"):
                st.markdown(f"Base de alunos: {base_alunos_semestre}")
                col1, col2 = st.columns(2)
                with col1: 
                    st.metric(
                        label = "Custo Mensal Aproximado",
                        value = formatar_valor_brl(custo_mensal)
                    )
                    st.metric(
                        label = "Carga Horária Total (horas)",
                        value = locale.format_string('%.1f', ch_total_semestre, grouping=True)
                    )
                with col2:
                    st.metric(
                        label="Custo Total do Semestre", 
                        value=formatar_valor_brl(custo_total_semestre)
                    )
                    try:
                        st.metric(
                        label="Eficiência do Semestre",
                        value=f"{eficiencia:.2f}"
                    )
                    except:
                        pass
                st.divider()
                df_por_semestre_format = formatar_df_por_semestre(df_por_semestre)
    with st.expander("Oferta resumida por curso"):
        OFERTA_POR_CURSO

    with st.expander("Oferta resumida por UC"):
        OFERTA_POR_UC
        
    with st.expander("Detalhamento da Oferta", expanded=True):
        df_precificacao_oferta_formatado = formatar_df_precificacao_oferta(df_com_total)
    
# --- Debug na Barra Lateral ---
st.sidebar.title("Debug Info")
with st.sidebar.expander("Dados da Simulação (Session State)"):
    st.json(st.session_state)