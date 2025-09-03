import streamlit as st
from src.data import carregar_dados, carregar_lista_marca_polo, carregar_base_alunos, carregar_tickets, encontrar_ticket
from src.utils import obter_modelos_para_curso, oferta_resumida_por_curso, agrupar_oferta,formatar_df_precificacao_oferta, calcular_resumo_semestre, calcula_base_alunos_por_semestre, calcula_base_alunos_total, adiciona_linha_total,calcula_df_final, plotar_custo_total_pag2, plotar_ch_total_pag2, plot_custo_docente_pag2, plot_ch_docente_por_categoria_pag2, formatar_df_por_semestre, projetar_base_alunos, calcula_custo_aluno_para_todos_semestre,plot_custo_aluno_por_semestre_pag2, calcula_ticket_medio,  busca_base_de_alunos, adicionar_todas_ofertas_do_polo, remover_ofertas_por_marca, remover_ofertas_por_polo, trazer_ofertas_para_novo_modelo, adicionar_todas_ofertas_da_marca, cria_select_box_modelo, plotar_composicao_alunos_por_serie, plotar_evolucao_total_alunos
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
df_base_alunos = carregar_base_alunos("databases/base_alunos_curso_marca_v2.xlsx", version="v2")


if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}

if 'parametros_globais' not in st.session_state:
    st.session_state.parametros_globais = {
        "alunos_iniciais": 60,
        "media_ingressantes": 100,
        "desvio_padrao_ingressantes": 10,
        "taxa_evasao_inicial": 30,
        "decaimento_evasao": 10,
    }
# --- Listas ---
LISTA_CURSOS_COMPLETA = sorted(df_dimensao_cursos['Curso'].unique().tolist())
df_marcas_polos = carregar_lista_marca_polo("databases/marcas_polos_v2.csv")
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


st.write("")
st.markdown("##### Preenchimento Automático")

add_brand_disabled = not marca_para_adicionar
if st.button("Adicionar Todas as Ofertas da MARCA Selecionada", disabled=add_brand_disabled, use_container_width=True, help="Busca e adiciona os cursos de TODOS os polos da marca selecionada."):
    adicionar_todas_ofertas_da_marca(
        marca=marca_para_adicionar,
        df_marcas_polos=df_marcas_polos,
        df_base_alunos=df_base_alunos,
        df_dimensao_cursos=df_dimensao_cursos,
        df_curso_marca_modalidade=df_curso_marca_modalidade,
        df_curso_modalidade=df_curso_modalidade,
        df_modalidade=df_modalidade
    )
    st.rerun()

add_all_disabled = not (marca_para_adicionar and polo_para_adicionar and polo_para_adicionar != "Novo Polo")
if st.button("Adicionar Todas as Ofertas do Polo (com base histórica)", type="primary", use_container_width=True, disabled=add_all_disabled, help="Busca e adiciona todos os cursos com base de alunos histórica para a marca e polo selecionados."):
    adicionar_todas_ofertas_do_polo(
        marca=marca_para_adicionar,
        polo=polo_para_adicionar,
        df_base_alunos=df_base_alunos,
        df_dimensao_cursos=df_dimensao_cursos,
        df_curso_marca_modalidade=df_curso_marca_modalidade,
        df_curso_modalidade=df_curso_modalidade,
        df_modalidade=df_modalidade
    )


st.write("")
st.markdown("##### Adicionar Oferta Manualmente")
with st.container(border=True):
    col3, col4 = st.columns(2)
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

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        checkbox_base_alunos = st.checkbox(
            label="Buscar base de alunos (2025/1)",
            help="O sistema buscará a base de alunos histórica e preencherá automaticamente todas as 'séries' do curso. Se uma base não for encontrada, todos os semestres são preenchidos com 50 estudantes",
            value=False
        )
    with col2:
        checkbox_calda_longa_oferta = st.checkbox(
            label="Remover turmas < 25 alunos",
            help="Ao adicionar, já remove as turmas com menos de 25 alunos para esta oferta específica.",
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
                        alunos_por_semestre = {f"Semestre {i}": 50 for i in range(1, num_semestres + 1)}

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

# -- Seção 2. Parâmetros de simulação de base de alunos ---
st.header("2. Defina os Parâmetros da Projeção", divider='rainbow')

with st.container(border=True):
    st.markdown("##### Parâmetros Globais (Padrão para todas as ofertas)")
    st.info("Estes valores servirão como padrão para todas as ofertas. Você poderá ajustar individualmente cada uma na seção abaixo.")

    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.session_state.parametros_globais["alunos_iniciais"] = st.number_input(
            "Alunos da turma inicial", 
            min_value=0, step=5, 
            value=st.session_state.parametros_globais["alunos_iniciais"], 
            key="global_iniciais"
        )
        st.session_state.parametros_globais["media_ingressantes"] = st.number_input(
            "Média de ingressantes por Ano", 
            min_value=0, step=5, 
            value=st.session_state.parametros_globais["media_ingressantes"],
            key="global_media"
        )
        st.session_state.parametros_globais["taxa_evasao_inicial"] = st.slider(
            "Taxa de Evasão Inicial (%)", 
            min_value=0, max_value=100, 
            value=st.session_state.parametros_globais["taxa_evasao_inicial"],
            key="global_evasao"
        )

    with pcol2:
        # Nota: O número de semestres da simulação continuará sendo individual por curso.
        # Não faz sentido ter um n_semestres global, pois cada curso tem sua duração.
        st.session_state.parametros_globais["desvio_padrao_ingressantes"] = st.number_input(
            "Desvio padrão dos ingressantes", 
            min_value=0, step=1, 
            value=st.session_state.parametros_globais["desvio_padrao_ingressantes"],
            key="global_dp"
        )
        st.session_state.parametros_globais["decaimento_evasao"] = st.slider(
            "Decaimento da Evasão a/s (%)", 
            min_value=0, max_value=100, 
            value=st.session_state.parametros_globais["decaimento_evasao"],
            key="global_decaimento"
        )
    
    st.write("") # Espaçamento
    
    if st.button("Simular TODAS as Bases de Alunos", type="primary", use_container_width=True, help="Roda a simulação de projeção para todas as ofertas adicionadas usando os parâmetros definidos em cada uma."):
        with st.spinner("Projetando base de alunos para todas as ofertas..."):
            for chave, config in st.session_state.cursos_selecionados.items():
                # Pega os parâmetros individuais de cada curso (que estarão com o default global)
                params = st.session_state[f"params_sim_{chave}"]
                
                # Chama a nova função que retorna o dicionário temporal
                projecao_temporal = projetar_base_alunos(
                    base_alunos_inicial=params["alunos_iniciais"],
                    n_semestres_curso=params["n_semestres"],
                    dist_ingresso=(params["media_ingressantes"], params["desvio_padrao_ingressantes"]),
                    taxa_evasao_inicial=params["taxa_evasao_inicial"] / 100.0,
                    decaimento_evasao=params["decaimento_evasao"] / 100.0
                )
                
                # Limpa chaves antigas de simulação antes de adicionar as novas
                for k in list(config.keys()):
                    if k.startswith("alunos_por_semestre"):
                        del st.session_state.cursos_selecionados[chave][k]

                # Adiciona as novas chaves temporais ao config da oferta
                for chave_temporal, dados_semestre in projecao_temporal.items():
                    st.session_state.cursos_selecionados[chave][chave_temporal] = dados_semestre
        st.success("Projeção de base de alunos concluída para todas as ofertas!")
        st.rerun()
st.divider()


st.write("")


st.divider()
# --- Seção 3 (Configurar Cursos) ---
st.subheader("Configuração de Ofertas Adicionadas")
st.markdown("Aqui estão todas as ofertas que você adicionou para a simulação... você pode expandir cada uma para ajustar o número de alunos por semestre")
st.markdown("##### Ferramentas de Gerenciamento")
# Lógica para os novos botões
with st.container(border=True):
    col1, col2 = st.columns(2)
    
    # Coluna para remoção por Marca e Polo
    with col1:
        st.markdown("**Remoção em Lote**")
        # Remover por marca
        marcas_selecionadas = sorted(list(set(config['marca'] for config in st.session_state.cursos_selecionados.values())))
        marca_para_remover = st.selectbox(
            "Selecione uma marca para remover",
            options=marcas_selecionadas,
            index=None,
            placeholder="Escolha uma marca...",
            label_visibility="collapsed"
        )
        if st.button("Remover todas as ofertas da MARCA", disabled=not marca_para_remover, use_container_width=True):
            remover_ofertas_por_marca(marca_para_remover)
            st.rerun()

        # Remover por polo
        polos_selecionados = sorted(list(set(config['polo'] for config in st.session_state.cursos_selecionados.values())))
        polo_para_remover = st.selectbox(
            "Selecione um polo para remover",
            options=polos_selecionados,
            index=None,
            placeholder="Escolha um polo...",
            label_visibility="collapsed"
        )
        if st.button("Remover todas as ofertas do POLO", disabled=not polo_para_remover, use_container_width=True):
            remover_ofertas_por_polo(polo_para_remover)
            st.rerun()

    # Coluna para ações globais
    with col2:
        st.markdown("**Ações Globais**")
        if st.button("Remover calda longa (< 25 alunos)", help="Remove todas as turmas com menos de 25 alunos.", use_container_width=True):
            remover_calda_longa()

        if st.button("Trazer ofertas para o novo modelo", help="Altera os modelos 'Atuais' para a nova nomenclatura (Ex: EAD Atual -> EAD 10.10)", use_container_width=True):
            trazer_ofertas_para_novo_modelo(df_dimensao_cursos, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade)
            time.sleep(5)

        if st.button("Limpar TODAS as ofertas", help="Limpa todas as ofertas para começar do zero.", type="primary", use_container_width=True):
            limpar_todas_as_ofertas()

col1, col2, col3 = st.columns(3)

""" with col1:
    st.metric(
        label="Total de Alunos",
        value=locale.format_string('%d', sum(sum(config['alunos_por_semestre'].values()) for config in st.session_state.cursos_selecionados.values()), grouping=True),
    ) """
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
if not st.session_state.cursos_selecionados:
    st.info("Nenhuma oferta adicionada ainda. Comece selecionando todos os campos acima.")
else:
    ofertas_ordenadas = sorted(
        st.session_state.cursos_selecionados.items(),
        key=lambda item: (item[1]['marca'], item[1]['polo'], item[1]['curso'], item[1]['modelo'])
    )

    # Itera sobre a lista JÁ ORDENADA
    for chave_oferta, config in ofertas_ordenadas:
        with st.expander(f"**{chave_oferta}**", expanded=False):
            info_col1, info_col2 = st.columns([4, 1])
            
            with info_col1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Marca:** `{config['marca']}`")
                    st.markdown(f"**Curso:** `{config['curso']}`")
                with col2:
                    st.markdown(f"**Polo:** `{config['polo']}`")
                    st.markdown(f"**Cluster:** `{config['cluster']}`")
                    st.markdown(f"**Ticket Médio:** `{formatar_valor_brl(config['ticket'])}`")
                with col3:
                    cria_select_box_modelo(df_dimensao_cursos, config, chave_oferta, df_curso_marca_modalidade, df_curso_modalidade, df_modalidade)

            with info_col2:
                st.write("")
                if st.button("Remover", key=f"remover_{chave_oferta}", use_container_width=True):
                    del st.session_state.cursos_selecionados[chave_oferta]
                    st.rerun()
            
            st.markdown("---")

            st.write("**Parâmetros para Simulação da Base de Alunos:**")

            if f"params_sim_{chave_oferta}" not in st.session_state:
                st.session_state[f"params_sim_{chave_oferta}"] = {}
            
            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                # O 'value' agora busca o default dos parâmetros GLOBAIS
                alunos_iniciais = st.number_input(
                    "Alunos da turma inicial", 
                    min_value=0, step=5, 
                    value=st.session_state.parametros_globais["alunos_iniciais"], 
                    key=f"sim_iniciais_{chave_oferta}"
                )
                media_ingressantes = st.number_input(
                    "Média de ingressantes por Ano", 
                    min_value=0, step=5, 
                    value=st.session_state.parametros_globais["media_ingressantes"], 
                    key=f"sim_media_{chave_oferta}"
                )
                taxa_evasao_inicial = st.slider(
                    "Taxa de Evasão Inicial (%)", 
                    min_value=0, max_value=100, 
                    value=st.session_state.parametros_globais["taxa_evasao_inicial"], 
                    key=f"sim_evasao_{chave_oferta}"
                )

            with sim_col2:
                n_semestres = st.slider(
                    "Número de semestres a simular",
                    min_value=1,
                    max_value=config.get("num_semestres"),
                    value=config.get("num_semestres"),
                    step=1,
                    key=f"sim_n_semestres_{chave_oferta}"
                )
                desvio_padrao_ingressantes = st.number_input(
                    "Desvio padrão dos ingressantes", 
                    min_value=0, step=1, 
                    value=st.session_state.parametros_globais["desvio_padrao_ingressantes"], 
                    key=f"sim_dp_{chave_oferta}"
                )
                decaimento_evasao = st.slider(
                    "Decaimento da Evasão a/s (%)", 
                    min_value=0, max_value=100, 
                    value=st.session_state.parametros_globais["decaimento_evasao"], 
                    key=f"sim_decaimento_{chave_oferta}"
                )
            # Atualiza o dicionário de parâmetros na sessão
                st.session_state[f"params_sim_{chave_oferta}"] = {
                "alunos_iniciais": alunos_iniciais,
                "media_ingressantes": media_ingressantes,
                "taxa_evasao_inicial": taxa_evasao_inicial,
                "n_semestres": n_semestres,
                "desvio_padrao_ingressantes": desvio_padrao_ingressantes,
                "decaimento_evasao": decaimento_evasao
            }


            alunos_data = config.get("alunos_por_semestre", {})
            historico_data = config.get("historico_simulacao", [])
            if not alunos_data:
                st.info("Clique em 'Simular Base de Alunos' para gerar a projeção.")
            else:
                st.subheader("**Base de Alunos projetada**")
                num_semestres_config = config.get("num_semestres", 0)

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

st.header("Análise Agregada da Projeção", divider='rainbow')

# Verifica se já existem projeções no session_state
houve_projecao = any(k.startswith("alunos_por_semestre_") for config in st.session_state.cursos_selecionados.values() for k in config)

if not houve_projecao:
    st.info("Clique em 'Simular TODAS as Bases de Alunos' na seção de parâmetros para gerar a projeção e visualizar a análise agregada.")
else:
    # 1. Gráfico de Evolução (Visão Macro)
    fig_evolucao = plotar_evolucao_total_alunos(st.session_state.cursos_selecionados)
    if fig_evolucao:
        st.pyplot(fig_evolucao)

    st.markdown("---")

    # 2. Análise Detalhada (Visão Micro)
    st.subheader("Análise Detalhada por Período")

    # Obtém a lista de períodos simulados para popular o selectbox
    todos_os_periodos = sorted(list(set(
        k.replace("alunos_por_semestre_", "").replace("_", "/")
        for config in st.session_state.cursos_selecionados.values()
        for k in config if k.startswith("alunos_por_semestre_")
    )))
    
    # Verifica se a lista de períodos não está vazia antes de prosseguir
    if todos_os_periodos:
        # Define o índice do último período da lista como o padrão para o selectbox
        default_index = len(todos_os_periodos) - 1

        periodo_selecionado = st.selectbox(
            "Selecione o período para detalhar a composição por série:",
            options=todos_os_periodos,
            index=default_index  # Define o valor padrão aqui
        )
        
        # Com o valor padrão garantido, podemos gerar o gráfico com segurança
        if periodo_selecionado:
            fig_composicao = plotar_composicao_alunos_por_serie(st.session_state.cursos_selecionados, periodo_selecionado)
            if fig_composicao:
                st.pyplot(fig_composicao)


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

# --- Seção 4: Analítico de Custos (MODIFICADA) ---
# Adicionado um verificador para garantir que a projeção foi executada.
houve_projecao = any(k.startswith("alunos_por_semestre_") for config in st.session_state.cursos_selecionados.values() for k in config)

# A análise só deve rodar se o botão foi pressionado E se existem dados de projeção.
st.divider()

if st.session_state.cursos_selecionados:
    st.header("4. Analítico de Custos", divider='rainbow')

    # Criar o selectbox
    todos_os_periodos_analise = sorted(list(set(
        k.replace("alunos_por_semestre_", "").replace("_", "/")
        for config in st.session_state.cursos_selecionados.values()
        for k in config if k.startswith("alunos_por_semestre_")
    )))

    # Define o índice do último período da lista como o padrão
    default_index_analise = len(todos_os_periodos_analise) - 1
    periodo_selecionado_analise = st.selectbox(
        "**Selecione o período para a Análise de Custos:**",
        options=todos_os_periodos_analise,
        index=default_index_analise,
        help="Escolha o semestre futuro para o qual deseja calcular os custos e a rentabilidade."
    )

    if periodo_selecionado_analise:
        # Preparar o Snapshot de dados
        if st.session_state.get('simulacao_ativa', False) and houve_projecao:
            st.session_state['simulacao_ativa'] = False  # Reseta o gatilho do botão
            # Converte o formato '2026/2' de volta para o formato da chave '_2026_2'
            chave_sufixo_temporal = "_" + periodo_selecionado_analise.replace("/", "_")
            
            snapshot_cursos = {}
            for chave_oferta, config in st.session_state.cursos_selecionados.items():
                chave_temporal_especifica = f"alunos_por_semestre{chave_sufixo_temporal}"
                
                # Se a oferta tem dados para aquele período, cria a entrada no snapshot
                if chave_temporal_especifica in config:
                    snapshot_config = config.copy() 
                    snapshot_config['alunos_por_semestre'] = config.get(chave_temporal_especifica, {})
                    snapshot_cursos[chave_oferta] = snapshot_config

            # Chamar as funções de cálculo
            dados_para_analise = {'cursos_selecionados': snapshot_cursos}
            OFERTA_POR_CURSO = oferta_resumida_por_curso(df_matrizes_editado)
            OFERTA_POR_UC = agrupar_oferta(OFERTA_POR_CURSO, df_matrizes_editado, df_parametros=df_parametros_editado, session_state=dados_para_analise)
            OFERTA_POR_UC = OFERTA_POR_UC[(OFERTA_POR_UC['Tipo de UC'].isin(df_parametros_editado['Tipo de UC'].unique().tolist())) | (OFERTA_POR_UC['Tipo de UC'] == 'AFP')]
            df_final = calcula_df_final(df_parametros_editado, OFERTA_POR_UC)
            df_final = df_final[df_final['Custo Total'] > 0]

            # As funções agora usam o 'dados_para_analise' com o snapshot do período selecionado
            base_alunos = calcula_base_alunos_total(dados_para_analise)

            # Adiciona uma verificação para evitar divisão por zero se não houver alunos no período
            if base_alunos == 0:
                st.warning(f"Não há alunos projetados para o período de {periodo_selecionado_analise}. A análise de custos não pode ser gerada.")
            else:
                df_com_total = adiciona_linha_total(df_final, base_alunos)
                
                # O restante do seu código de exibição permanece praticamente o mesmo
                st.subheader(f"Resumo para o Período: {periodo_selecionado_analise}")
                col1, col2 = st.columns(2) # Removido o border=True que gerava erro
                with col1:
                    # ... (resto do seu código de métricas e plots)
                    col3,col4 = st.columns([2,1])
                    with col3:
                        st.metric(
                            label="Custo Total",
                            value=locale.currency(plotar_custo_total_pag2(df_final), grouping=True, symbol="R$")
                        )
                        st.metric(label="Base de Alunos", value=locale.format_string('%d',base_alunos, grouping=True))
                        
                        ticket = calcula_ticket_medio(dados_para_analise, None)
                        st.metric(label="Ticket Médio", value=locale.currency(ticket, grouping=True, symbol="R$"))
                    with col4:
                        st.metric(label="CH Total", value=locale.format_string('%.1f', plotar_ch_total_pag2(df_final), grouping=True))
                        custo_por_aluno = plotar_custo_total_pag2(df_final)/base_alunos
                        delta = np.round((ticket-custo_por_aluno)/ticket*100,2) if ticket > 0 else 0
                        st.metric(label="Custo por Aluno", value=locale.currency(custo_por_aluno, grouping=True, symbol="R$"))
                        st.metric(label="Margem", value=locale.currency(ticket-custo_por_aluno, grouping=True, symbol="R$"), delta=f"{delta}%")
                    st.pyplot(plot_custo_docente_pag2(df_final), use_container_width=True)

                with col2:
                    st.pyplot(plot_ch_docente_por_categoria_pag2(df_final))
                    dict_semestres = calcula_custo_aluno_para_todos_semestre(df_final, dados_para_analise)
                    st.pyplot(plot_custo_aluno_por_semestre_pag2(dict_semestres, ticket), use_container_width=True)
                
                with st.expander("Detalhamento por Série", expanded=True):
                    for i in range(df_final['Semestre'].max()):
                        df_por_semestre = df_final[df_final['Semestre'] == (i+1)]
                        # Passa 'dados_para_analise' para a função
                        base_alunos_semestre = calcula_base_alunos_por_semestre(dados_para_analise, i+1)
                        if base_alunos_semestre > 0:
                            ch_total_semestre, custo_total_semestre, custo_mensal, eficiencia = calcular_resumo_semestre(df_por_semestre, base_alunos_semestre)          
                            df_por_semestre = adiciona_linha_total(df_por_semestre, base_alunos_semestre)
                            with st.expander(f"{i+1}º Série"):
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
                                    st.metric(
                                    label="Custo por Aluno",
                                    value=formatar_valor_brl(custo_total_semestre/base_alunos_semestre)
                                    )
                                with col3:
                                    ticket_medio = calcula_ticket_medio(dados_para_analise, i+1)
                                    st.metric(
                                        label="Ticket Médio",
                                        value=formatar_valor_brl(ticket_medio)
                                    )
                                    if ticket_medio > 0:
                                        margem = ticket_medio - (custo_total_semestre/base_alunos_semestre)
                                        st.metric(
                                            label="Margem",
                                            value=formatar_valor_brl(margem),
                                            delta=f"{np.round(margem/ticket_medio*100,2)}%"
                                        )
                                st.divider()
                                df_por_semestre_format = formatar_df_por_semestre(df_por_semestre)

                with st.expander("Detalhamento da Sinergia"):
                    OFERTA_POR_CURSO = OFERTA_POR_CURSO.rename(columns={
                    "curso": "Curso", "modelo": "Modelo", "cluster": "Cluster",
                    "ch_sinergica": "CH Sinérgica", "percentual_sinergico": "% Sinérgica",
                    "ucs_sinergicas": "UCs Sinérgicas", "ucs_especificas": "UCs Específicas"
                    })
                    st.dataframe(OFERTA_POR_CURSO)
                    
                with st.expander("Detalhamento da Oferta", expanded=False):
                    df_precificacao_oferta_formatado = formatar_df_precificacao_oferta(df_com_total)
        
        # --- Debug na Barra Lateral ---
        st.sidebar.title("Debug Info")
        with st.sidebar.expander("Dados da Simulação (Session State)"):
            st.json(st.session_state)

# Adiciona uma mensagem caso o botão seja pressionado mas nenhuma projeção tenha sido feita
elif st.session_state.get('simulacao_ativa', False) and not houve_projecao:
    st.warning("Nenhuma projeção de base de alunos foi encontrada. Por favor, clique em 'Simular TODAS as Bases de Alunos' na seção 2 antes de executar a análise de custos.")
    st.session_state['simulacao_ativa'] = False # Reseta o gatilho