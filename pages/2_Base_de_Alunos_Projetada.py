import streamlit as st
from src.data import carregar_dados, carregar_lista_marca_polo, carregar_base_alunos, carregar_tickets, encontrar_ticket
from src.utils import obter_modelos_para_curso, oferta_resumida_por_curso, agrupar_oferta, formatar_df_precificacao_oferta, calcular_resumo_semestre, calcula_base_alunos_por_semestre, calcula_base_alunos_total, adiciona_linha_total,calcula_df_final, plotar_custo_total_pag2, plotar_ch_total_pag2, plot_custo_docente_pag2, plot_ch_docente_por_categoria_pag2, formatar_df_por_semestre, projetar_base_alunos, calcula_custo_aluno_para_todos_semestre,plot_custo_aluno_por_semestre_pag2, calcula_ticket_medio,  busca_base_de_alunos
from src.formatting import formatar_valor_brl
import pandas as pd
import numpy as np
import locale
import time
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def remover_calda_longa():
    with st.spinner('Removendo turmas com poucos alunos...'):
        time.sleep(1)
        for chave in list(st.session_state.cursos_selecionados.keys()):
                config = st.session_state.cursos_selecionados[chave]
                alunos_por_semestre = {semestre: alunos for semestre, alunos in config['alunos_por_semestre'].items() if alunos >= 25}
                if alunos_por_semestre:
                    st.session_state.cursos_selecionados[chave]['alunos_por_semestre'] = alunos_por_semestre
                else:
                    del st.session_state.cursos_selecionados[chave]
    st.success("A calda longa foi removida com sucesso!")

def limpar_todas_as_ofertas():
    with st.spinner('Limpando todas as ofertas...'):
        time.sleep(1)
        for chave in list(st.session_state.cursos_selecionados.keys()):
            del st.session_state.cursos_selecionados[chave]
    st.success("Todas as ofertas foram removidas!")

st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# Carrega todos os DataFrames no início
df_matrizes = carregar_dados("databases/matrizes.xlsx")
df_parametros = carregar_dados("databases/parametros_turma.xlsx")
df_dimensao_cursos = carregar_dados("databases/dimensao_curso_modelo.xlsx")
df_curso_marca_modalidade, df_curso_modalidade, df_modalidade = carregar_tickets()
df_base_alunos = carregar_base_alunos()


if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}

if 'confirmacao_calda_longa' not in st.session_state:
    st.session_state.confirmacao_calda_longa = False

if 'confirmacao_remover_todas' not in st.session_state:
    st.session_state.confirmacao_remover_todas = False

# --- Listas ---
LISTA_CURSOS_COMPLETA = sorted(df_dimensao_cursos['Curso'].unique().tolist())
df_marcas_polos = carregar_lista_marca_polo("databases/marcas_polos.csv")
LISTA_MARCAS = sorted(df_marcas_polos['MARCA'].unique().tolist())
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

# Filtra a lista de polos com base na marca selecionada
df_marcas_polos = df_marcas_polos[df_marcas_polos['MARCA'] == marca_para_adicionar]
LISTA_POLOS = df_marcas_polos['CAMPUS'].unique().tolist()
LISTA_POLOS.insert(0, "Novo Polo")

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

add_button_disabled = not all([marca_para_adicionar, polo_para_adicionar, curso_para_adicionar, modelo_para_adicionar])

col1, col2, col3 = st.columns([1,1,4])
with col1:
    checkbox_base_alunos = st.checkbox(
        label="Buscar a base de alunos em 2025/1 para essa oferta.",
        help="O sistema buscará a base de alunos histórica e preencherá automaticamente todas as 'séries' do curso. Se uma base não for encontrada, todos os semestres são preenchidos com 50 estudantes",
        value=False
    )
with col2:
    checkbox_calda_longa_oferta = st.checkbox(
        label="Remover turmas abaixo de 25 alunos nessa oferta.",
        value=False
    )
with col3:
    if st.button("Adicionar Oferta", type="primary", use_container_width=True, disabled=add_button_disabled):
        chave_oferta = f"{marca_para_adicionar} - {polo_para_adicionar} - {curso_para_adicionar} ({modelo_para_adicionar})"
        
        if chave_oferta not in st.session_state.cursos_selecionados:
            try:
                filtro = (df_dimensao_cursos['Curso'] == curso_para_adicionar) & (df_dimensao_cursos['Modelo'] == modelo_para_adicionar)
                dados_curso = df_dimensao_cursos[filtro].iloc[0]
                
                num_semestres = int(dados_curso['Qtde Semestres'])
                if checkbox_base_alunos:
                    alunos_por_semestre = busca_base_de_alunos(df_base_alunos, marca_para_adicionar, polo_para_adicionar, curso_para_adicionar, modelo_para_adicionar, num_semestres)
                else:
                    alunos_por_semestre = {}

                if checkbox_calda_longa_oferta:
                    alunos_por_semestre = {semestre: alunos for semestre, alunos in alunos_por_semestre.items() if alunos >= 25}

                st.session_state.cursos_selecionados[chave_oferta] = {
                    "marca": marca_para_adicionar,
                    "polo": polo_para_adicionar,
                    "curso": curso_para_adicionar,
                    "modelo": modelo_para_adicionar,
                    "ticket": encontrar_ticket(curso_para_adicionar, marca_para_adicionar, modelo_para_adicionar, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade),
                    "cluster": dados_curso['Cluster'],
                    "sinergia": dados_curso['Sinergia'],
                    "num_semestres": num_semestres,
                    "alunos_por_semestre": alunos_por_semestre
                }
            except (IndexError, TypeError):
                st.error(f"Não foi possível encontrar os dados para o curso '{curso_para_adicionar}' com o modelo '{modelo_para_adicionar}'.")
        else:
            st.warning(f"A oferta '{chave_oferta}' já foi adicionada.")
st.divider()
# --- Seção 2 (Configurar Cursos) ---
st.header("2. Configure os Parâmetros de Cada Oferta", divider='rainbow')

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        label="Total de Alunos",
        value=locale.format_string('%d', sum(sum(config['alunos_por_semestre'].values()) for config in st.session_state.cursos_selecionados.values()), grouping=True),
    )
with col2:
    num_polos = len(set(config['polo'] for config in st.session_state.cursos_selecionados.values()))
    st.metric(
        label="Total de Polos",
        value=num_polos
    )
with col3:
    st.metric(
        label="Total de Ofertas",
        value=locale.format_string('%d', len(st.session_state.cursos_selecionados), grouping=True),
    )
with col4:
    if st.button("Remover calda longa", help="Remove todas as turmas com menos de 25 alunos.", type="primary"):
        st.session_state.confirmacao_calda_longa = True

    if st.session_state.confirmacao_calda_longa:
        st.warning("**Atenção:** Você tem certeza que deseja remover a calda longa? Esta ação não pode ser desfeita.")
        
        col_sim, col_nao = st.columns(2)
        with col_sim:
            if st.button("Sim, tenho certeza", key='confirma_calda'):
                remover_calda_longa()
                st.session_state.confirmacao_calda_longa = False
                st.rerun()
        with col_nao:
            if st.button("Cancelar", key='cancela_calda'):
                st.session_state.confirmacao_calda_longa = False
                st.rerun()
with col5:
    if st.button("Limpar todas as ofertas", help="Limpa todas as ofertas para começar do zero.", type="primary", use_container_width=True):
        st.session_state.confirmacao_remover_todas = True
    
    if st.session_state.confirmacao_remover_todas:
        st.error("Esta ação é irreversível e limpará TODAS as ofertas adicionadas. Deseja continuar?")
        
        col_sim2, col_nao2 = st.columns(2)
        with col_sim2:
            if st.button("Sim, quero limpar tudo", key='confirma_limpar', type="primary"):
                limpar_todas_as_ofertas()
                st.session_state.confirmacao_remover_todas = False
                st.rerun()
        with col_nao2:
            if st.button("Cancelar", key='cancela_limpar'):
                st.session_state.confirmacao_remover_todas = False
                st.rerun()

st.markdown("Aqui estão todas as ofertas que você adicionou para a simulação...")
if not st.session_state.cursos_selecionados:
    st.info("Nenhuma oferta adicionada ainda. Comece selecionando todos os campos acima.")
else:
    ofertas_ordenadas = sorted(
        st.session_state.cursos_selecionados.items(),
        key=lambda item: (item[1]['marca'], item[1]['polo'], item[1]['curso'], item[1]['modelo'])
    )

    # Itera sobre a lista JÁ ORDENADA
    for chave_oferta, config in ofertas_ordenadas:
        with st.expander(f"**{chave_oferta}**", expanded=True):
            info_col1, info_col2 = st.columns([4, 1])
            
            with info_col1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Marca:** `{config['marca']}`")
                    st.markdown(f"**Curso:** `{config['curso']}`")
                with col2:
                    st.markdown(f"**Polo:** `{config['polo']}`")
                    st.markdown(f"**Modelo:** `{config['modelo']}`")
                with col3:
                    st.markdown(f"**Cluster:** `{config['cluster']}`")
                    st.markdown(f"**Ticket Médio:** {formatar_valor_brl(config['ticket'])}")

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
                resultado_simulacao, historico = projetar_base_alunos(
                    base_alunos_inicial=alunos_iniciais,
                    n_semestres_curso=n_semestres,
                    dist_ingresso=(media_ingressantes, desvio_padrao_ingressantes),
                    taxa_evasao_inicial=taxa_evasao_inicial / 100.0,
                    decaimento_evasao=decaimento_evasao / 100.0
                )
                
                st.session_state.cursos_selecionados[chave_oferta]["alunos_por_semestre"] = resultado_simulacao["alunos_por_semestre"]
                st.session_state.cursos_selecionados[chave_oferta]["historico_simulacao"] = historico
                st.rerun()

            st.markdown("---")
            
            alunos_data = config.get("alunos_por_semestre", {})
            historico_data = config.get("historico_simulacao", [])
            if not alunos_data:
                st.info("Clique em 'Simular Base de Alunos' para gerar a projeção.")
            else:
                st.subheader("**Base de Alunos projetada**")
                num_semestres_config = config.get("num_semestres", 0)
                
                with st.expander("**Alunos por Período**", expanded=True): # Adicionei expanded=True para começar aberto
                    cols = st.columns(4)
                    
                    # Itera diretamente sobre o histórico da simulação
                    for i, alunos_data_semestre in enumerate(historico_data):
                        # Calcula o total de alunos NAQUELE semestre da simulação
                        total_alunos_no_periodo = sum(alunos_data_semestre.values())
                        
                        # Lógica para determinar o rótulo do período (ano/semestre)
                        col_index = i % 4
                        semestre_index = i % 2 + 1
                        ano_index = 2026 + i // 2
                        
                        with cols[col_index]:
                            st.metric(
                                label=f"Total em {ano_index}/{semestre_index}",
                                value=int(total_alunos_no_periodo)
                            )

                # A segunda parte, "Alunos por série", permanece inalterada
                with st.expander("**Alunos por série**"):
                    num_semestres_config = len(alunos_data)
                    cols_serie = st.columns(4)
                    for i in range(num_semestres_config):
                        semestre_key = f"Semestre {i + 1}"
                        col_index = i % 4
                        with cols_serie[col_index]:
                            st.metric(
                                label=f"Alunos na Série {i+1}",
                                value=int(alunos_data.get(semestre_key, 0))
                            )
st.divider()
# --- Seção 3: Executar Simulação ---
st.header("3. Executar Simulação", divider='rainbow')

# Filtrar apenas modelos selecionados para mostrar nos parâmetros
modelos_selecionados = set([])
for key, item in st.session_state.cursos_selecionados.items():
    modelos_selecionados.add(item.get('modelo')) 
df_parametros_editado = df_parametros[(df_parametros["Modelo"].isin(modelos_selecionados)) | ((df_parametros["Tipo de UC"] == "AFP") & (df_parametros["Modelo"].isin(modelos_selecionados)))]


df_matrizes_editado = df_matrizes
with st.expander("Mostrar Parâmetros", expanded=True):
    st.subheader(f"Parâmetros de Simulação")

    ignorar_tcc = st.checkbox(
        label="Não considerar o TCC na análise",
        value=True
    )
    
    if ignorar_tcc:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "TCC"]
        df_matrizes_editado = df_matrizes_editado[df_matrizes_editado["Tipo de UC"] != "TCC"]

    ignorar_estagio = st.checkbox(
        label="Não considerar Estágio na análise",
        value=True
    )
    
    if ignorar_estagio:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "ESTÁGIO"]
        df_matrizes_editado = df_matrizes_editado[df_matrizes_editado["Tipo de UC"] != "ESTÁGIO"]

    ignorar_AFP = st.checkbox(
        label="Não considerar AFP na análise",
        value=True
    )
    
    if ignorar_AFP:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "AFP"]
        df_matrizes_editado = df_matrizes_editado[df_matrizes_editado["Tipo de UC"] != "AFP"]

    ignorar_extensao = st.checkbox(
        label="Não considerar Extensão na análise",
        value=True
    )
    
    if ignorar_extensao:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "EXTENSÃO"]
        df_matrizes_editado = df_matrizes_editado[df_matrizes_editado["Tipo de UC"] != "EXTENSÃO"]
    df_parametros_editado = st.data_editor(df_parametros_editado,
                                           hide_index=True,
                                           use_container_width=True,
                                           disabled=['Modelo', 'Tipo de UC', 'Parâmetro', 'Tipo de CH', 'Ator Pedagógico']
                                          )
                                          
# Verifica se os dataframes essenciais foram carregados
dataframes_carregados = df_matrizes_editado is not None and df_parametros is not None and df_dimensao_cursos is not None

if st.button("Confirmar e Rodar Cálculos", type="primary", use_container_width=True, disabled=not dataframes_carregados):
    if not st.session_state.cursos_selecionados:
        st.warning("Adicione pelo menos um curso antes de rodar os cálculos.")
    elif dataframes_carregados:
        # Apenas um indicador de que o botão foi pressionado
        st.session_state['simulacao_ativa'] = True

st.divider()
if st.session_state.cursos_selecionados:
    st.header("4. Analítico de Custos", divider='rainbow')
    OFERTA_POR_CURSO = oferta_resumida_por_curso(df_matrizes_editado)

    OFERTA_POR_UC = agrupar_oferta(OFERTA_POR_CURSO, df_matrizes_editado, df_parametros=df_parametros_editado)
    OFERTA_POR_UC = OFERTA_POR_UC[(OFERTA_POR_UC['Tipo de UC'].isin(df_parametros_editado['Tipo de UC'].unique().tolist())) | (OFERTA_POR_UC['Tipo de UC'] == 'AFP')]
    
    df_final = calcula_df_final(df_parametros_editado, OFERTA_POR_UC)
    df_final = df_final[df_final['Custo Total']>0]

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
                col1, col2, col3 = st.columns(3)
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
                with col3:
                    try:
                        st.metric(
                            label="Ticket Médio",
                            value=formatar_valor_brl(calcula_ticket_medio(st.session_state))
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