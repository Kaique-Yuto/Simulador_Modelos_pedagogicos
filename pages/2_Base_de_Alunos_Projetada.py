import streamlit as st
from src.data import carregar_dados, carregar_lista_marca_polo
from src.utils import obter_modelos_para_curso, oferta_resumida_por_curso, agrupar_oferta, agrupar_oferta_v2, formatar_df_precificacao_oferta, calcular_resumo_semestre, calcula_base_alunos_por_semestre, calcula_base_alunos_total, adiciona_linha_total,calcula_df_final, plotar_custo_total_pag2, plotar_ch_total_pag2, plot_custo_docente_pag2, plot_ch_docente_por_categoria_pag2, calcula_eficiencia_para_todos_semestre, plot_eficiencia_por_semestre_pag2, formatar_df_por_semestre, projetar_base_alunos, calcula_custo_aluno_para_todos_semestre,plot_custo_aluno_por_semestre_pag2, calcula_ticket_medio
from src.formatting import formatar_valor_brl
import pandas as pd
import numpy as np
import locale
st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# Carrega todos os DataFrames no início
df_matrizes = carregar_dados("databases/matrizes.xlsx")
df_parametros = carregar_dados("databases/parametros_turma.xlsx")
df_dimensao_cursos = carregar_dados("databases/dimensao_curso_modelo.xlsx")

# --- Inicialização do Session State ---
if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}

# --- Listas ---
# Simulação de dados para df_dimensao_cursos se estiver vazio
if df_dimensao_cursos.empty:
    import pandas as pd
    df_dimensao_cursos = pd.DataFrame({
        'Curso': ['Curso Alpha', 'Curso Beta'],
        'Modelo': ['Modelo 1', 'Modelo 2'],
        'Qtde Semestres': [8, 10],
        'Ticket': [500, 600],
        'Cluster': ['C1', 'C2'],
        'Sinergia': [0.1, 0.2]
    })

LISTA_CURSOS_COMPLETA = sorted(df_dimensao_cursos['Curso'].unique().tolist())
LISTA_MARCAS, LISTA_POLOS = carregar_lista_marca_polo("databases/marcas_polos.csv")

st.markdown("Você selecionou a Simulação com Base de Alunos Projetada, isso significa que você poderá escolher uma base inicial de calouros para os cursos selecionados. Para cada um dos cursos você deverá preencher uma premissa de ingresso e evasão, o aplicativo irá simular o avanço e a formação de novas turmas automaticamente")

# --- Seção 1 (Adicionar Cursos) ---
st.header("1. Adicione as Ofertas de Curso para Simulação", divider='rainbow')

# Layout com 4 colunas para os 4 seletores
col1, col2, col3, col4 = st.columns(4)

with col1:
    marca_para_adicionar = st.selectbox(
        "Escolha uma marca",
        options=LISTA_MARCAS,
        index=None,
        placeholder="Selecione a marca..."
    )

with col2:
    polo_para_adicionar = st.selectbox(
        "Escolha um polo",
        options=LISTA_POLOS,
        index=None,
        placeholder="Selecione o polo...",
        disabled=not marca_para_adicionar
    )

with col3:
    curso_para_adicionar = st.selectbox(
        "Escolha um curso",
        options=LISTA_CURSOS_COMPLETA,
        index=None,
        placeholder="Selecione o curso...",
        disabled=not polo_para_adicionar
    )

modelos_disponiveis = []
if curso_para_adicionar:
    modelos_disponiveis = obter_modelos_para_curso(df_dimensao_cursos, curso_para_adicionar)

with col4:
    modelo_para_adicionar = st.selectbox(
        "Escolha o modelo",
        options=modelos_disponiveis,
        index=None,
        placeholder="Selecione o modelo...",
        disabled=not curso_para_adicionar
    )

st.write("") # Adiciona um espaço antes do botão

# O botão de adicionar agora depende dos 4 campos
add_button_disabled = not all([marca_para_adicionar, polo_para_adicionar, curso_para_adicionar, modelo_para_adicionar])

if st.button("Adicionar Oferta", type="primary", use_container_width=True, disabled=add_button_disabled):
    chave_oferta = f"{marca_para_adicionar} - {polo_para_adicionar} - {curso_para_adicionar} ({modelo_para_adicionar})"
    
    if chave_oferta not in st.session_state.cursos_selecionados:
        try:
            filtro = (df_dimensao_cursos['Curso'] == curso_para_adicionar) & (df_dimensao_cursos['Modelo'] == modelo_para_adicionar)
            dados_curso = df_dimensao_cursos[filtro].iloc[0]
            
            num_semestres = int(dados_curso['Qtde Semestres'])

            st.session_state.cursos_selecionados[chave_oferta] = {
                "marca": marca_para_adicionar,
                "polo": polo_para_adicionar,
                "curso": curso_para_adicionar,
                "modelo": modelo_para_adicionar,
                "ticket": dados_curso['Ticket'],
                "cluster": dados_curso['Cluster'],
                "sinergia": dados_curso['Sinergia'],
                "num_semestres": num_semestres,
                "alunos_por_semestre": {} # Inicia vazio, será preenchido pela simulação
            }

        except (IndexError, TypeError):
            st.error(f"Não foi possível encontrar os dados para o curso '{curso_para_adicionar}' com o modelo '{modelo_para_adicionar}'.")
    else:
        st.warning(f"A oferta '{chave_oferta}' já foi adicionada.")

# --- Seção 2 (Configurar Cursos) ---
st.header("2. Configure os Parâmetros de Cada Oferta", divider='rainbow')
st.markdown("Aqui estão todas as ofertas que você adicionou para a simulação...")

if not st.session_state.cursos_selecionados:
    st.info("Nenhuma oferta adicionada ainda. Comece selecionando todos os campos acima.")
else:
    # ORDENA as ofertas para exibição consistente
    ofertas_ordenadas = sorted(
        st.session_state.cursos_selecionados.items(),
        key=lambda item: (item[1]['marca'], item[1]['polo'], item[1]['curso'], item[1]['modelo'])
    )

    # Itera sobre a lista JÁ ORDENADA
    for chave_oferta, config in ofertas_ordenadas:
        if chave_oferta in st.session_state.cursos_selecionados:
            
            # Expander com título melhorado
            with st.expander(f"**{chave_oferta}**", expanded=True):
                
                # --- Linha 1: Informações e Botão de Remover (Melhorado) ---
                info_col1, info_col2 = st.columns([4, 1])
                
                with info_col1:
                    # Mostra as novas informações de Marca e Polo
                    st.markdown(f"**Marca:** `{config['marca']}` | **Polo:** `{config['polo']}`")
                    st.markdown(f"**Curso:** `{config['curso']}` | **Modelo:** `{config['modelo']}`")

                with info_col2:
                    st.write("")
                    if st.button("Remover", key=f"remover_{chave_oferta}", use_container_width=True):
                        del st.session_state.cursos_selecionados[chave_oferta]
                        st.rerun()
                
                st.markdown("---")

                # --- LÓGICA DA PÁGINA 2 (SIMULAÇÃO) MANTIDA INTEGRALMENTE ---
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
                        step=1,
                        key = f"sim_n_semestres_{chave_oferta}"
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
                
                # Exibição dos resultados da simulação (mantido)
                alunos_data = config.get("alunos_por_semestre", {})
                if not alunos_data:
                    st.info("Clique em 'Simular Base de Alunos' para gerar a projeção.")
                else:
                    st.subheader("**Base de Alunos projetada**")
                    num_semestres_config = config.get("num_semestres", 0)
                    
                    with st.expander("**Alunos por Período**"):
                        cols = st.columns(4)
                        alunos_acumulados = 0
                        
                        for i in range(num_semestres_config):
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
                        for i in range(num_semestres_config):
                            semestre_key = f"Semestre {i + 1}"
                            col_index = i % 4
                            with cols[col_index]:
                                st.metric(
                                    label=f"Alunos na Série {i+1}",
                                    value=int(alunos_data.get(semestre_key, 0))
                                )

# --- Seção 3: Executar Simulação ---
# Esta seção já estava idêntica à da página 1, então não precisa de grandes alterações.
st.header("3. Executar Simulação", divider='rainbow')

# Filtrar apenas modelos selecionados para mostrar nos parâmetros
modelos_selecionados = set([])
for key, item in st.session_state.cursos_selecionados.items():
    modelos_selecionados.add(item.get('modelo')) 
df_parametros_editado = df_parametros[(df_parametros["Modelo"].isin(modelos_selecionados)) | (df_parametros["Tipo de UC"] == "AFP")]

with st.expander("Mostrar Parâmetros", expanded=True):
    st.subheader(f"Parâmetros de Simulação")

    ignorar_tcc = st.checkbox(
        label="Não considerar o TCC na análise",
        value=True
    )
    if ignorar_tcc:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "TCC"]
        df_matrizes = df_matrizes[df_matrizes["Tipo de UC"] != "TCC"]

    ignorar_estagio = st.checkbox(
        label="Não considerar Estágio na análise",
        value=True
    )
    if ignorar_estagio:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "ESTÁGIO"]
        df_matrizes = df_matrizes[df_matrizes["Tipo de UC"] != "ESTÁGIO"]


    ignorar_AFP = st.checkbox(
        label="Não considerar AFP na análise",
        value=True
    )
    if ignorar_AFP:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "AFP"]

    ignorar_extensao = st.checkbox(
        label="Não considerar Extensão na análise",
        value=True
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

    OFERTA_POR_UC = agrupar_oferta(OFERTA_POR_CURSO, df_matrizes, df_parametros=df_parametros_editado)
    OFERTA_POR_UC = OFERTA_POR_UC[OFERTA_POR_UC['Tipo de UC'].isin(df_parametros_editado['Tipo de UC'].unique().tolist())]
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
            ticket = calcula_ticket_medio(st.session_state)
            st.metric(label="Ticket Médio", value=locale.currency(ticket, grouping=True, symbol="R$"),width='content')
        with col4:
            st.metric(label="CH Total", value=locale.format_string('%.1f', plotar_ch_total_pag2(df_final), grouping=True),width='content')
            #eficiencia = np.round(base_alunos/plotar_ch_total_pag2(df_final),2)
            #st.metric(label="Eficiência", value = eficiencia,width='content')
            custo_por_aluno = plotar_custo_total_pag2(df_final)/base_alunos
            delta = np.round((ticket-custo_por_aluno)/ticket*100,2)
            st.metric(label="Custo por Aluno", value=locale.currency(custo_por_aluno, grouping=True, symbol="R$"))
            st.metric(label="Margem", value=locale.currency(ticket-custo_por_aluno, grouping=True, symbol="R$"), delta=f"{delta}%")
        st.pyplot(plot_custo_docente_pag2(df_final), use_container_width=False)
        
    with col2:
        st.pyplot(plot_ch_docente_por_categoria_pag2(df_final))
        dict_semestres = calcula_custo_aluno_para_todos_semestre(df_final, st.session_state)
        st.pyplot(plot_custo_aluno_por_semestre_pag2(dict_semestres, ticket), use_container_width=False)
    
    with st.expander("Detalhamento por Semestre", expanded=True):
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
                        label="Custo por Aluno",
                        value=formatar_valor_brl(custo_total_semestre/base_alunos_semestre)
                    )
                    except:
                        pass
                st.divider()
                df_por_semestre_format = formatar_df_por_semestre(df_por_semestre)
    with st.expander("Detalhamento da Sinergia"):
        OFERTA_POR_CURSO = OFERTA_POR_CURSO.rename(columns={
        "curso": "Curso",
        "modelo": "Modelo",
        "cluster": "Cluster",
        "ch_sinergica": "CH Sinérgica",
        "percentual_sinergico": "% Sinérgica",
        "ucs_sinergicas": "UCs Sinérgicas",
        "ucs_especificas": "UCs Específicas"
    })
        OFERTA_POR_CURSO
        
    with st.expander("Detalhamento da Oferta", expanded=False):
        df_precificacao_oferta_formatado = formatar_df_precificacao_oferta(df_com_total)
    
# --- Debug na Barra Lateral ---
st.sidebar.title("Debug Info")
with st.sidebar.expander("Dados da Simulação (Session State)"):
    st.json(st.session_state)