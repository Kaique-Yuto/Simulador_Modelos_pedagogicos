import streamlit as st
from src.data import carregar_dados, carregar_lista_marca_polo, carregar_base_alunos, carregar_tickets, encontrar_ticket
from src.utils import obter_modelos_para_curso, oferta_resumida_por_curso, agrupar_oferta,calcular_df_precificacao_oferta, calcular_resumo_semestre, calcula_base_alunos_por_semestre, calcula_base_alunos_total, adiciona_linha_total,calcula_df_final, plotar_custo_total_pag2, plotar_ch_total_pag2, plot_custo_docente_pag2, plot_ch_docente_por_categoria_pag2, formatar_df_por_semestre, projetar_base_alunos, calcula_custo_aluno_para_todos_semestre,plot_custo_aluno_por_semestre_pag2, calcula_ticket_medio,  busca_base_de_alunos, adicionar_todas_ofertas_do_polo, remover_ofertas_por_marca, remover_ofertas_por_polo, trazer_ofertas_para_novo_modelo, adicionar_todas_ofertas_da_marca, cria_select_box_modelo, plotar_composicao_alunos_por_serie, plotar_evolucao_total_alunos, preparar_dados_para_dashboard_macro, plotar_margem_e_base_alunos, plotar_custos_vs_receita, ratear_custo_por_polo, calcula_total_alunos_por_polo, upload_arquivo, adiciona_linha_total_rateio, calcula_receita_por_polo_periodo, calcula_ticket_por_serie_no_semestre, calcula_df_resumo_semestre
from src.formatting import formatar_valor_brl, formatar_df_precificacao_oferta, formatar_df_rateio, formatar_df_rateio_polo, formatar_df_pivot_custo, formata_df_resumo_semestre
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
df_base_alunos = carregar_base_alunos("databases/base_alunos_curso_marca_v3.xlsx", version="v2")

if 'cursos_selecionados' not in st.session_state:
    st.session_state.cursos_selecionados = {}

if 'parametros_globais' not in st.session_state:
    st.session_state.parametros_globais = {
        "alunos_iniciais": 60,
        "media_ingressantes": 100,
        "desvio_padrao_ingressantes": 10,
        "taxa_evasao_inicial": 30,
        "decaimento_evasao": 50,
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

with st.expander("Adicionar Polo Novo a partir de arquivo"):
    with st.container(border=True):
        st.markdown("##### Carregar Base de Ingressantes para o Novo Polo")
        st.info("O arquivo Excel (.xlsx) deve conter as colunas 'Modalidade', 'Curso' e os semestres da projeção")
        
        uploaded_file = st.file_uploader(
            "Selecione o arquivo Excel com a projeção de ingressantes",
            type=['xlsx'],
            label_visibility="collapsed"
        )
        
        # Botão único com a lógica de processamento integrada
        if st.button("Processar Arquivo e Adicionar Ofertas", type="primary", disabled=not uploaded_file, use_container_width=True):
            with st.spinner("Processando arquivo e adicionando ofertas..."):
                upload_arquivo(
                    uploaded_file=uploaded_file,
                    df_dimensao_cursos=df_dimensao_cursos,
                    df_curso_marca_modalidade=df_curso_marca_modalidade,
                    df_curso_modalidade=df_curso_modalidade,
                    df_modalidade=df_modalidade
                )
            time.sleep(10)

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
            help="O sistema buscará a base de ingressantes histórica (em 2025/1) e admitirá o mesmo volume de ingressantes para 2026/1. Caso uma base não seja encontrada, 50 alunos são ingressados na primeira série do curso em 2026/1",
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
                        alunos_por_semestre = {"Semestre 1": 50}

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
            min_value=10, step=5, 
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
    
    st.markdown("---")
    st.markdown("##### Controle Global do Modo de Projeção")

    col_global1, col_global2 = st.columns([2, 1])

    with col_global1:
        modo_global = st.selectbox(
            label="Definir o modo de projeção para TODAS as ofertas adicionadas:",
            options=[
                "Manter configurações individuais",
                "Forçar 'Iniciar do Zero' para todas",
                "Forçar 'Continuar da Base Histórica' para todas"
            ],
            key="modo_projecao_global",
            help="Use esta opção para alterar rapidamente o modo de todas as ofertas. A alteração será refletida nos controles individuais de cada oferta."
        )

    with col_global2:
        st.write("") # Espaçamento para alinhar o botão
        if st.button("Aplicar Modo Global", use_container_width=True, disabled=(modo_global == "Manter configurações individuais")):
            
            # Define para qual modo converter com base na seleção
            if modo_global == "Forçar 'Iniciar do Zero' para todas":
                novo_modo = "Iniciar do Zero"
            elif modo_global == "Forçar 'Continuar da Base Histórica' para todas":
                novo_modo = "Continuar da Base Histórica"
            else:
                novo_modo = None

            if novo_modo:
                # Itera por todas as ofertas e atualiza o modo de projeção
                for config in st.session_state.cursos_selecionados.values():
                    config['modo_projecao'] = novo_modo
                
                st.toast(f"Modo '{novo_modo}' aplicado a todas as ofertas!", icon="✅")
                # st.rerun() # Descomente esta linha se quiser que a página recarregue para ver as alterações imediatamente
    
    if st.button("Simular TODAS as Bases de Alunos", type="primary", use_container_width=True, help="Roda a simulação de projeção para todas as ofertas adicionadas usando os parâmetros definidos em cada uma."):
        with st.spinner("Projetando base de alunos para todas as ofertas..."):
            for chave, config in st.session_state.cursos_selecionados.items():
                params = st.session_state[f"params_sim_{chave}"]
                
                
                base_para_simulacao = None # Começa com None por padrão
                
                # Pega o modo escolhido na UI. Se não houver, assume "Iniciar do Zero".
                modo_projecao = config.get('modo_projecao', 'Iniciar do Zero')

                # Caso especial: se o usuário escolher 'Continuar' mas não houver base, reverte para 'Iniciar do Zero'
                if modo_projecao == 'Continuar da Base Histórica' and ('alunos_por_semestre' not in config or not config['alunos_por_semestre']):
                    st.warning(f"Para a oferta '{chave}', não foi encontrada base histórica. A simulação iniciará do zero.")
                    modo_projecao = 'Iniciar do Zero'

                if modo_projecao == 'Iniciar do Zero':
                    base_para_simulacao = {'Semestre 1': params["alunos_iniciais"]}
                
                elif modo_projecao == 'Continuar da Base Histórica':
                    base_para_simulacao = config.get('alunos_por_semestre')
                    
                elif modo_projecao == 'Definir Base Personalizada':
                    base_para_simulacao = config.get('base_personalizada')
                
                ingressantes_para_simulacao = None
                modo_captacao = config.get('modo_captacao', 'Estatística (Média Anual)')
                if modo_captacao == 'Manual (Por Semestre)':
                    ingressantes_para_simulacao = config.get('ingressantes_personalizados')

                # Chama a função de projeção com a base correta
                projecao_temporal = projetar_base_alunos(
                    n_semestres_curso=config["num_semestres"],
                    dist_ingresso=(params["media_ingressantes"], params["desvio_padrao_ingressantes"]),
                    taxa_evasao_inicial=params["taxa_evasao_inicial"] / 100.0,
                    decaimento_evasao=params["decaimento_evasao"] / 100.0,
                    base_inicial=base_para_simulacao,
                    ingressantes_personalizados=ingressantes_para_simulacao
                )
                
                # Limpa chaves antigas de simulação antes de adicionar as novas
                for k in list(config.keys()):
                    if k.startswith("alunos_por_semestre_"):
                        del st.session_state.cursos_selecionados[chave][k]

                # Adiciona as novas chaves temporais ao config da oferta
                for chave_temporal, dados_semestre in projecao_temporal.items():
                    st.session_state.cursos_selecionados[chave][chave_temporal] = dados_semestre
        st.success("Projeção de base de alunos concluída para todas as ofertas!")
        st.rerun()

with st.expander("Ferramentas de Gerenciamento", expanded=True):
    # Lógica para os novos botões
    with st.container(border=True):
        col1, col2 = st.columns(2)
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

# --- Seção 3 (Configurar Cursos) ---
st.subheader("Configuração de Ofertas Adicionadas")
st.markdown("Aqui estão todas as ofertas que você adicionou para a simulação... você pode expandir cada uma para ajustar o número de alunos por semestre")
col1, col2, col3 = st.columns([1,1,3])
with col1:
    num_polos = len(set(config['polo'] for config in st.session_state.cursos_selecionados.values()))
    st.metric(
        label="Total de Polos",
        value=num_polos
    )
with col2:
    st.metric(
        label="Total de Ofertas",
        value=locale.format_string('%d', len(st.session_state.cursos_selecionados), grouping=True),
    )
if not st.session_state.cursos_selecionados:
    st.info("Nenhuma oferta adicionada ainda. Adicione as ofertas na Seção 1.") 
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
            st.markdown("---")


            with st.expander("Gerenciar Simulação de Base de Alunos"):
                st.markdown("---")
                st.markdown("##### Modo de Captação")

                # Salva a escolha do modo de captação no session_state da oferta
                opcoes_captacao = ["Estatística (Média Anual)", "Manual (Por Semestre)"]

                # Primeiro, lemos o valor que já está no session_state para definir qual item deve vir selecionado
                valor_atual = config.get('modo_captacao', opcoes_captacao[0])
                indice_padrao = opcoes_captacao.index(valor_atual)

                # Agora, o radio button usará o índice correto como padrão e salvará a nova escolha do usuário
                config['modo_captacao'] = st.radio(
                    label="Escolha como a captação de novos alunos será calculada:",
                    options=opcoes_captacao,
                    key=f"modo_captacao_{chave_oferta}",
                    horizontal=True,
                    index=indice_padrao, # <-- A CORREÇÃO PRINCIPAL ESTÁ AQUI
                    help="""
                    - **Estatística:** Usa a média de ingressantes e a sazonalidade 60/40 para projetar a captação.
                    - **Manual:** Permite definir um número exato de ingressantes para cada semestre futuro.
                    """
                )

                # Lógica para o modo "Manual (Por Semestre)"
                if config.get('modo_captacao') == "Manual (Por Semestre)":
                    st.markdown("###### Preencha o número de ingressantes para cada semestre da projeção:")
                    
                    # Cria o dicionário para guardar os dados se não existir
                    if 'ingressantes_personalizados' not in config:
                        config['ingressantes_personalizados'] = {}

                    # Usa o slider 'Número de semestres a simular' para definir quantos inputs mostrar
                    # Buscamos o valor do slider que já existe nos parâmetros da simulação
                    params_sim_oferta = st.session_state.get(f"params_sim_{chave_oferta}", {})
                    n_periodos_a_projetar = 10 # Default de 10 se não achar

                    cols = st.columns(5)
                    ano_inicial, semestre_inicial = 2026, 1

                    for i in range(n_periodos_a_projetar):
                        ano = ano_inicial + (i // 2)
                        semestre = semestre_inicial + (i % 2)
                        chave_periodo = f"{ano}_{semestre}"
                        label_periodo = f"{ano}/{semestre}"

                        # Usa o valor anterior como default, ou 0
                        default_value = config['ingressantes_personalizados'].get(chave_periodo, 0)
                        
                        # Distribui os inputs nas colunas
                        ingressantes_input = cols[i % 5].number_input(
                            label=f"Ingressantes {label_periodo}",
                            min_value=0,
                            step=10,
                            value=default_value,
                            key=f"ingressantes_pers_{chave_oferta}_{chave_periodo}"
                        )
                        # Atualiza o dicionário com o valor do input
                        config['ingressantes_personalizados'][chave_periodo] = ingressantes_input
                st.markdown("---")
                
                
               

                st.markdown("##### Modo de Projeção")
                # Opções do radio button
                opcoes_projecao = ["Continuar da Base Histórica", "Iniciar do Zero", "Definir Base Personalizada"]
                # Desabilita a opção 'Continuar' se não houver base histórica carregada
                desabilitar_continuar = 'alunos_por_semestre' not in config or not config['alunos_por_semestre']

                valor_atual = config.get('modo_projecao', opcoes_projecao[0])
                indice_padrao = opcoes_projecao.index(valor_atual)
                # Salva a escolha do usuário no session_state da oferta
                config['modo_projecao'] = st.radio(
                    label="Escolha como a projeção deve começar para esta oferta:",
                    options=opcoes_projecao,
                    key=f"modo_projecao_{chave_oferta}",
                    horizontal=True,
                    index=indice_padrao,
                    help="""
                    - **Iniciar do Zero:** Começa a simulação apenas com uma turma de calouros.
                    - **Continuar da Base Histórica:** Usa a base de 2025/1 como ponto de partida.
                    - **Definir Base Personalizada:** Permite inserir manualmente o nº de alunos em cada série.
                    """,
                    disabled=desabilitar_continuar,
                    # O argumento acima na verdade não funciona para desabilitar uma única opção no st.radio
                    # A lógica para lidar com isso será feita no backend.
                    # Se o usuário selecionar 'Continuar' sem base, vamos reverter para 'Iniciar do Zero'.
                )

                # Lógica para o modo "Definir Base Personalizada"
                if config['modo_projecao'] == "Definir Base Personalizada":
                    st.markdown("###### Preencha a base de alunos para iniciar a projeção (2026/1):")
                    
                    # Cria um dicionário para guardar a base personalizada se não existir
                    if 'base_personalizada' not in config:
                        config['base_personalizada'] = {}

                    # Layout em colunas para os inputs
                    num_semestres = config.get("num_semestres", 8)
                    cols = st.columns(4)
                    
                    for i in range(1, num_semestres + 1):
                        semestre_key = f"Série {i}"
                        # Usa o valor anterior como default, ou 0
                        default_value = config['base_personalizada'].get(semestre_key, 0)
                        
                        # Distribui os inputs nas colunas
                        aluno_input = cols[(i-1) % 4].number_input(
                            label=semestre_key,
                            min_value=0,
                            step=5,
                            value=default_value,
                            key=f"alunos_pers_{chave_oferta}_{i}"
                        )
                        # Atualiza o dicionário com o valor do input
                        config['base_personalizada'][semestre_key] = aluno_input
                
                st.markdown("---")
                
                if f"params_sim_{chave_oferta}" not in st.session_state:
                    st.session_state[f"params_sim_{chave_oferta}"] = {}
                
                sim_col1, sim_col2 = st.columns(2)
                with sim_col1:
                    alunos_iniciais = st.number_input(
                        "Alunos da turma inicial", 
                        min_value=4, step=5, 
                        value=st.session_state.parametros_globais["alunos_iniciais"], 
                        key=f"sim_iniciais_{chave_oferta}"
                    )
                    media_ingressantes = st.number_input(
                        "Média de ingressantes por Ano", 
                        min_value=10, step=5, 
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
st.divider()
# --- Seção 3: Executar Simulação ---
st.header("3. Defina os parâmetros de Precificação", divider='rainbow')

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

    ignorar_ppi = st.checkbox(
        label="Não considerar PPI na análise (influencia apenas licenciatura)",
        value=True
    )
    
    if ignorar_ppi:
        df_parametros_editado = df_parametros_editado[df_parametros_editado["Tipo de UC"] != "PPI"]
        df_matrizes_editado = df_matrizes_editado[df_matrizes_editado["Tipo de UC"] != "PPI"]


    df_para_visualizar = df_parametros_editado.pivot_table(
        index=['Modelo', 'Tipo de UC', 'Ator Pedagógico', 'Tipo de CH'],
        columns='Parâmetro',
        values='Valor'
    ).reset_index()
    df_para_visualizar.columns.name = None


    # Chamar o data_editor com a versão pivotada
    df_visualizado_editado = st.data_editor(
        df_para_visualizar,
        hide_index=True,
        use_container_width=True,
        disabled=['Modelo', 'Tipo de UC', 'Ator Pedagógico', 'Tipo de CH'],
        column_config={
        "Remuneração por Hora": st.column_config.NumberColumn(
            label="Remuneração por Hora",
            format="R$ %.2f"
        )
    }
    )

    # Despivotar de volta para o formato longo original
    df_parametros_editado = df_visualizado_editado.melt(
        id_vars=['Modelo', 'Tipo de UC', 'Ator Pedagógico', 'Tipo de CH'],
        var_name='Parâmetro',
        value_name='Valor'
    )
                                          
# Verifica se os dataframes essenciais foram carregados
dataframes_carregados = df_matrizes_editado is not None and df_parametros is not None and df_dimensao_cursos is not None

if st.button("Confirmar e Rodar Cálculos", type="primary", use_container_width=True, disabled=not dataframes_carregados):
    if not st.session_state.cursos_selecionados:
        st.warning("Adicione pelo menos um curso antes de rodar os cálculos.")
    elif dataframes_carregados:
        # Apenas um indicador de que o botão foi pressionado
        st.session_state['simulacao_ativa'] = True



@st.cache_data
def calcular_analise_completa(cursos_selecionados: dict, df_matrizes: pd.DataFrame, df_parametros: pd.DataFrame) -> dict:
    # 1. Identificar todos os períodos disponíveis na projeção
    todos_os_periodos = sorted(list(set(
        k.replace("alunos_por_semestre_", "").replace("_", "/")
        for config in cursos_selecionados.values()
        for k in config if k.startswith("alunos_por_semestre_")
    )))
    # 2. Preparar os dataframes base que são iguais para todos os períodos
    oferta_por_curso = oferta_resumida_por_curso(df_matrizes, cursos_selecionados)
    # 3. Inicializar o dicionário que guardará todos os resultados
    resultados_finais = {}

    # 4. Loop principal: iterar sobre cada período e calcular tudo para ele
    for periodo in todos_os_periodos:
        chave_sufixo_temporal = "_" + periodo.replace("/", "_")
        
        # Cria o snapshot de alunos para este período específico
        snapshot_cursos = {}
        for chave_oferta, config in cursos_selecionados.items():
            chave_temporal_especifica = f"alunos_por_semestre{chave_sufixo_temporal}"
            if chave_temporal_especifica in config:
                snapshot_config = config.copy()
                snapshot_config['alunos_por_semestre'] = config.get(chave_temporal_especifica, {})
                snapshot_cursos[chave_oferta] = snapshot_config
        
        dados_para_analise = {'cursos_selecionados': snapshot_cursos}
        base_alunos_total = calcula_base_alunos_total(dados_para_analise)
        # Se não houver alunos, pula para o próximo período
        if base_alunos_total == 0:
            continue

        # Lógica de cálculo principal (a mesma que você já tinha)
        oferta_por_uc = agrupar_oferta(oferta_por_curso, df_matrizes, df_parametros=df_parametros, session_state=dados_para_analise)
        oferta_por_uc = oferta_por_uc[(oferta_por_uc['Tipo de UC'].isin(df_parametros['Tipo de UC'].unique().tolist())) | (oferta_por_uc['Tipo de UC'] == 'AFP')]
        df_final = calcula_df_final(df_parametros, oferta_por_uc)
        df_final = df_final[df_final['Custo Total'] > 0]
        df_rateio = ratear_custo_por_polo(df_final=df_final, oferta_por_uc=oferta_por_uc)
        # 5. Calcular e armazenar todas as métricas e dataframes
        custo_total_periodo = plotar_custo_total_pag2(df_final)
        ticket_medio_periodo = calcula_ticket_medio(dados_para_analise, None)
        custo_por_aluno_periodo = custo_total_periodo / base_alunos_total
        margem_periodo = (ticket_medio_periodo*6 - custo_por_aluno_periodo) * base_alunos_total
        dados_para_plot_custo_docente = df_final
        dados_para_plot_ch_categoria = df_final
        dados_para_plot_custo_aluno_semestre = calcula_custo_aluno_para_todos_semestre(df_final, dados_para_analise)

 #-------------------------------
        rateio_por_polo = df_rateio.groupby('Polo')['Custo Rateado'].sum().sort_values(ascending=False)
        rateio_por_polo = rateio_por_polo.reset_index()
        rateio_por_polo["Base Alunos Total"] = base_alunos_total
        rateio_por_polo['Base Alunos no Polo'] = rateio_por_polo['Polo'].apply(
                                                    lambda polo: calcula_total_alunos_por_polo(
                                                        st.session_state.cursos_selecionados,
                                                        periodo, # Variável com o período (ex: "2026/1")
                                                        polo
                                                    )
                                                )
        rateio_por_polo["Custo Total"] = custo_total_periodo
        rateio_por_polo["% de Custo"] = rateio_por_polo["Custo Rateado"] / rateio_por_polo["Custo Total"]
        rateio_por_polo["% de Alunos"] = rateio_por_polo["Base Alunos no Polo"] / rateio_por_polo["Base Alunos Total"]




        # Armazena tudo em um dicionário para este período
        resultados_finais[periodo] = {
            "metricas_gerais": {
                "base_alunos": base_alunos_total,
                "custo_total": custo_total_periodo,
                "ch_total": plotar_ch_total_pag2(df_final),
                "ticket_medio": ticket_medio_periodo,
                "custo_por_aluno": custo_por_aluno_periodo,
                "margem": margem_periodo,
                "delta_margem": (margem_periodo/(ticket_medio_periodo*6*base_alunos_total) * 100) if ticket_medio_periodo > 0 else 0
            },
            "dataframes": {
                "df_final": df_final,
                "df_sinergia": oferta_por_curso,
                "df_oferta": calcular_df_precificacao_oferta(adiciona_linha_total(df_final, base_alunos_total)),
                "df_oferta_por_uc": oferta_por_uc,
                "df_rateio": df_rateio,
                "df_rateio_por_polo": rateio_por_polo,
                "df_oferta_por_curso": oferta_por_curso
            },
            "dados_para_plots": {
                "custo_docente": dados_para_plot_custo_docente,
                "ch_docente_categoria": dados_para_plot_ch_categoria,
                "custo_aluno_serie": dados_para_plot_custo_aluno_semestre
            },
            "detalhes_por_serie": {} # Vamos preencher isso em seguida
        }
        
        # Loop para calcular e armazenar os detalhes de cada série
        for i in range(df_final['Semestre'].max()):
            semestre_num = i + 1
            df_por_semestre = df_final[df_final['Semestre'] == semestre_num]
            base_alunos_semestre = calcula_base_alunos_por_semestre(dados_para_analise, semestre_num)

            if base_alunos_semestre > 0:
                ch_total_sem, custo_total_sem, custo_mensal_sem, _ = calcular_resumo_semestre(df_por_semestre, base_alunos_semestre)
                ticket_medio_sem = calcula_ticket_medio(dados_para_analise, semestre_num)
                margem_sem = ticket_medio_sem*base_alunos_semestre*6 - (custo_total_sem)

                resultados_finais[periodo]["detalhes_por_serie"][semestre_num] = {
                    "base_alunos": base_alunos_semestre,
                    "custo_mensal": custo_mensal_sem,
                    "ch_total": ch_total_sem,
                    "custo_total": custo_total_sem,
                    "custo_por_aluno": custo_total_sem / base_alunos_semestre,
                    "ticket_medio": ticket_medio_sem,
                    "margem": margem_sem,
                    "delta_margem": (margem_sem / ticket_medio_sem * 100) if ticket_medio_sem > 0 else 0
                }
    return resultados_finais


# ---------------- SEÇÃO 4: ANALÍTICO DE CUSTOS (NOVA ESTRUTURA) ------------------
if st.session_state.cursos_selecionados and st.session_state.get('simulacao_ativa', False):
    st.header("4. Analítico de Custos", divider='rainbow')

    try:
        todos_os_resultados = calcular_analise_completa(
            st.session_state.cursos_selecionados,
            df_matrizes_editado,
            df_parametros_editado
        )
    except Exception as e:
        st.warning("Tente clicar em Simular TODAS as Bases de Alunos novamente")
        st.markdown(str(e))
        todos_os_resultados = None

    if not todos_os_resultados:
        st.warning("A análise de custos não pôde ser gerada. Verifique se a projeção da base de alunos resultou em estudantes para os períodos futuros.")
    else:
        # ------------ INÍCIO: DASHBOARD MACRO -------------
        st.subheader("Dashboard de Visão Geral")
        df_macro = preparar_dados_para_dashboard_macro(todos_os_resultados)
        if not df_macro.empty:
            # 1. Calcular os totais da projeção a partir da última linha do DataFrame
            receita_total_projetada = df_macro['receita_acumulada'].iloc[-1]
            custo_total_projetado = df_macro['custo_acumulado'].iloc[-1]
            margem_total_projetada = df_macro['margem_acumulada'].iloc[-1]

            # 2. Calcular os indicadores médios
            # Evita divisão por zero caso não haja receita
            margem_media_percentual = (margem_total_projetada / receita_total_projetada * 100) if receita_total_projetada > 0 else 0
            
            # Soma a base de alunos de cada período para ter o total de "alunos-semestre"
            soma_alunos_periodos = df_macro['base_alunos'].sum()
            # Evita divisão por zero caso não haja alunos
            custo_medio_por_aluno = custo_total_projetado / soma_alunos_periodos if soma_alunos_periodos > 0 else 0
            
            # 3. Calcular o total de Carga Horária entregue
            ch_total_entregue = df_macro['ch_total'].sum()

            # 4. Exibir os KPIs em colunas
            st.markdown("##### Indicadores Consolidados da Projeção")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Receita Total Projetada",
                    value=locale.currency(receita_total_projetada, grouping=True, symbol="R$")
                )
                st.metric(
                    label="Custo Médio por Aluno",
                    value=locale.currency(custo_medio_por_aluno, grouping=True, symbol="R$")
                )
            with col2:
                st.metric(
                    label="Custo Total Projetado",
                    value=locale.currency(custo_total_projetado, grouping=True, symbol="R$")
                )
                st.metric(
                    label="CH Total Entregue",
                    value=f"{locale.format_string('%.0f', ch_total_entregue, grouping=True)} horas"
                )
            with col3:
                st.metric(
                    label="Margem Total Projetada",
                    value=locale.currency(margem_total_projetada, grouping=True, symbol="R$"),
                    delta=f"{margem_media_percentual:.2f}%"
                )
                st.metric(
                    label="Base Total de Alunos",
                    value=locale.format_string('%d',soma_alunos_periodos, grouping=True)
                )

            st.divider() 

        col1, col2 = st.columns(2)
        with col1:
            fig1 = plotar_custos_vs_receita(df_macro)
            st.pyplot(fig1)
        with col2:
            fig2 = plotar_margem_e_base_alunos(df_macro)
            st.pyplot(fig2)

        lista_dfs_rateio = []
        todos_os_periodos_analise = list(todos_os_resultados.keys())

        for periodo in todos_os_periodos_analise:
            df_por_periodo = todos_os_resultados.get(periodo, {}).get("dataframes", {}).get("df_rateio_por_polo")
            if df_por_periodo is not None and not df_por_periodo.empty:
                # Adiciona uma coluna para identificar o período de origem dos dados
                df_por_periodo['Periodo'] = periodo
                lista_dfs_rateio.append(df_por_periodo)

        if not lista_dfs_rateio:
            st.warning("Não há dados de rateio para exibir no resumo consolidado.")
        else:
            df_rateio_consolidado = pd.concat(lista_dfs_rateio, ignore_index=True)
            df_pivot_custo = df_rateio_consolidado.pivot_table(
                index='Polo',
                columns='Periodo',
                values='Custo Rateado',
                fill_value=0
            )
            
            df_resumo_semestre = calcula_df_resumo_semestre(todos_os_resultados)
            formata_df_resumo_semestre(df_resumo_semestre)
            
            # Tabela 2: Resumo consolidado com totais e percentuais
            st.markdown("##### Resumo Consolidado por Polo")
            df_resumo_polos = df_rateio_consolidado.groupby('Polo').agg(
                Custo_Rateado_Total=('Custo Rateado', 'sum'),
                Base_Alunos_Total_Polo=('Base Alunos no Polo', 'sum')
            ).reset_index()

            custo_geral_total = df_resumo_polos['Custo_Rateado_Total'].sum()
            alunos_geral_total = df_resumo_polos['Base_Alunos_Total_Polo'].sum()

            df_resumo_polos['Custo Total'] = custo_geral_total
            df_resumo_polos['Base Alunos Total'] = alunos_geral_total
            df_resumo_polos['% de Custo'] = df_resumo_polos['Custo_Rateado_Total'] / df_resumo_polos['Custo Total']
            df_resumo_polos['% de Alunos'] = df_resumo_polos['Base_Alunos_Total_Polo'] / df_resumo_polos['Base Alunos Total']
            
            # Renomeia as colunas para corresponder à função de formatação
            df_resumo_polos = df_resumo_polos.rename(columns={
                'Custo_Rateado_Total': 'Custo Rateado',
                'Base_Alunos_Total_Polo': 'Base Alunos no Polo'
            })

            receita_por_polo_periodo = calcula_receita_por_polo_periodo(config=st.session_state,todos_periodos=todos_os_periodos_analise)
            receita_por_polo = receita_por_polo_periodo.groupby("polo")['receita'].sum().reset_index().rename(columns={'receita': 'Receita do Polo'})
            df_resumo_polos = df_resumo_polos.merge(receita_por_polo, left_on='Polo', right_on='polo')
            # Utiliza a função que já criamos para formatar a tabela
            receita_geral = df_resumo_polos['Receita do Polo'].sum()
            df_resumo_polos['% Receita'] = (df_resumo_polos['Receita do Polo'] / receita_geral) 
            df_resumo_polos['Margem do Polo'] = (df_resumo_polos['Receita do Polo'] - df_resumo_polos['Custo Rateado']) / df_resumo_polos['Receita do Polo']
            
            df_resumo_polos = adiciona_linha_total_rateio(df_resumo_polos)
            formatar_df_rateio_polo(df_resumo_polos, True)

        # ---DASHBOARD MACRO---

        # ---ANÁLISE DETALHADA POR PERÍODO---
        st.subheader("Análise Detalhada por Semestre")
        # Tabela 1: Pivot com semestres nas colunas e custo rateado nos valores
        st.markdown("##### Custos Rateados por Semestre")
        df_pivot_custo = adiciona_linha_total_rateio(df_pivot_custo.reset_index())
        df_pivot_custo = formatar_df_pivot_custo(df_pivot_custo)

        
        default_index_analise = len(todos_os_periodos_analise) - 1

        periodo_selecionado_analise = st.selectbox(
            "**Selecione o período para detalhar os cálculos:**",
            options=todos_os_periodos_analise,
            index=default_index_analise,
            help="Escolha o semestre futuro para o qual deseja visualizar os custos e a rentabilidade."
        )

        resultados_do_periodo = todos_os_resultados.get(periodo_selecionado_analise)
        if resultados_do_periodo:
            # Extrai as métricas e dataframes para facilitar o acesso
            metricas = resultados_do_periodo['metricas_gerais']
            dfs = resultados_do_periodo['dataframes']
            dados_plots = resultados_do_periodo['dados_para_plots']
            detalhes_series = resultados_do_periodo['detalhes_por_serie']

            # Coluna com o resumo e o gráfico de composição de alunos
            col_detalhe1, col_detalhe2 = st.columns([1, 1])
            with col_detalhe1:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Base de Alunos no Período", value=locale.format_string('%d', metricas['base_alunos'], grouping=True))
                    st.metric(label="Custo Total no Período", value=locale.currency(metricas['custo_total'], grouping=True, symbol="R$"))
                    st.metric(label="Receita Total no Período", value=locale.currency(metricas['base_alunos'] * metricas['ticket_medio'] * 6, grouping=True, symbol="R$"))
                with col2:
                    st.metric(label="Margem no Período", value=locale.currency(metricas['margem'], grouping=True, symbol="R$"), delta=f"{np.round(metricas['delta_margem'], 2)}%")
                    st.metric(label="Custo por Aluno", value=locale.currency(metricas['custo_por_aluno'], grouping=True, symbol="R$"))
                    st.metric(label="Ticket Médio", value=locale.currency(metricas['ticket_medio'], grouping=True, symbol="R$"))

            with col_detalhe2:
                fig_composicao = plotar_composicao_alunos_por_serie(st.session_state.cursos_selecionados, periodo_selecionado_analise)
                st.pyplot(fig_composicao)
            col1, col2 = st.columns(2)
            with col1:
                fig_custo_docente = dados_plots.get("custo_docente")
                st.pyplot(plot_custo_docente_pag2(fig_custo_docente))
            with col2:
                fig_ch_docente_categoria = dados_plots.get("ch_docente_categoria")
                st.pyplot(plot_ch_docente_por_categoria_pag2(fig_ch_docente_categoria))

                fig_custo_aluno_serie = dados_plots.get("custo_aluno_serie")
                ticket_medio_por_serie = calcula_ticket_por_serie_no_semestre(st.session_state,periodo_selecionado_analise)
                st.pyplot(plot_custo_aluno_por_semestre_pag2(fig_custo_aluno_serie, ticket_medio_por_serie))
                
            with st.expander("Detalhamento da Sinergia", expanded=False):
                # ... (o seu código do dataframe de sinergia continua aqui)
                 df_sinergia = dfs['df_sinergia'].rename(columns={
                    "curso": "Curso", "modelo": "Modelo", "cluster": "Cluster",
                    "ch_sinergica": "CH Sinérgica", "per    centual_sinergico": "% Sinérgica",
                    "ucs_sinergicas": "UCs Sinérgicas", "ucs_especificas": "UCs Específicas"
                })
                 st.dataframe(df_sinergia)
                
            with st.expander("Rateio de Custos"):
                #df_rateio = df_rateio_filtrado_marca
                df_rateio = dfs["df_rateio"]
                formatar_df_rateio(df_rateio)
                formatar_df_rateio_polo(dfs['df_rateio_por_polo'], False)

            with st.expander("Agrupamento da Oferta", expanded=False):
                st.markdown("Todas as ofertas")
                df_oferta = dfs['df_oferta'].copy()
                df_rateio = dfs["df_rateio"].copy()
                # --------- Oferta -----------
                split_cols = df_oferta['Chave'].str.split(' - ', expand=True)
                if split_cols.shape[1] < 2:
                    st.error("Não foi possível extrair 'Marca' e 'UC' da coluna 'Chave'. Verifique se o separador ' - ' existe nos dados.")
                    st.stop()
                else:
                    df_oferta['Marca'] = split_cols[0]
                    df_oferta['UC'] = split_cols[1]

                df_oferta.dropna(subset=['Marca', 'UC'], inplace=True)
                df_oferta['UC'] = df_oferta['UC'].astype(str)
                # --------- Oferta -----------

                # --------- Rateio -----------
                split_cols2 = df_rateio['Chave'].str.split(' - ', expand=True)
                if split_cols2.shape[1] < 2:
                    st.error("Não foi possível extrair 'Marca' e 'UC' da coluna 'Chave'. Verifique se o separador ' - ' existe nos dados.")
                    st.stop()
                else:
                    df_rateio['Marca'] = split_cols2[0]
                    df_rateio['UC'] = split_cols2[1]

                df_rateio.dropna(subset=['Marca', 'UC'], inplace=True)
                df_rateio['UC'] = df_rateio['UC'].astype(str)
                # --------- Rateio -----------

                
                marcas_disponiveis = sorted(df_oferta['Marca'].unique())
                col1,col2, _ = st.columns([1,1,2])
                with col1:
                    marcas_selecionadas = st.multiselect(
                        "Filtro por Marca:",
                        options=marcas_disponiveis,
                        default=marcas_disponiveis
                    )

                    if marcas_selecionadas:
                        df_filtrado_marca = df_oferta[(df_oferta['Marca'].isin(marcas_selecionadas))]
                        df_rateio_filtrado_marca = df_rateio[(df_rateio['Marca'].isin(marcas_selecionadas))]
                    else:
                        df_filtrado_marca = df_oferta
                        df_rateio_filtrado_marca = df_rateio

                    ucs_disponiveis = sorted(df_filtrado_marca['UC'].unique())
                with col2: 
                    ucs_selecionadas = st.multiselect(
                        "Filtro por UC:",
                        options=ucs_disponiveis,
                        default=None
                    )

                    if ucs_selecionadas:
                        df_oferta = df_filtrado_marca[df_filtrado_marca['UC'].isin(ucs_selecionadas)]
                        df_rateio_filtrado_marca = df_rateio[(df_rateio['UC'].isin(ucs_selecionadas))]
                    else:
                        df_oferta = df_filtrado_marca
                        df_rateio_filtrado_marca = df_rateio

                if "CH por Semestre_Assíncrono" in df_oferta.columns:
                    with st.expander("CH Assíncrona"):
                        df_oferta_assin = df_oferta[df_oferta["CH por Semestre_Assíncrono"] > 0].copy()
                        df_oferta_assin = df_oferta_assin[["Chave", "Semestre", "Base de Alunos", "Qtde Turmas", "CH por Semestre_Assíncrono", "Custo Docente por Semestre_Assíncrono"]]
                        df_oferta_assin = adiciona_linha_total_rateio(df_oferta_assin)
                        formatar_df_precificacao_oferta(df_oferta_assin)

                if "CH por Semestre_Síncrono Mediado" in df_oferta.columns:
                    with st.expander("CH Síncrona Mediada"):
                        df_oferta_sinc_med = df_oferta[df_oferta["CH por Semestre_Síncrono Mediado"] > 0].copy()
                        df_oferta_sinc_med = df_oferta_sinc_med[["Chave", "Semestre", "Base de Alunos", "Qtde Turmas", "CH por Semestre_Síncrono Mediado", "Custo Docente por Semestre_Síncrono Mediado"]]
                        df_oferta_sinc_med = adiciona_linha_total_rateio(df_oferta_sinc_med)
                        formatar_df_precificacao_oferta(df_oferta_sinc_med)

                if "CH por Semestre_Presencial" in df_oferta.columns:
                    with st.expander("CH Presencial"):
                        df_oferta_pres = df_oferta[df_oferta["CH por Semestre_Presencial"] > 0].copy()
                        df_oferta_pres = df_oferta_pres[["Chave", "Semestre", "Base de Alunos", "Qtde Turmas", "CH por Semestre_Presencial", "Custo Docente por Semestre_Presencial"]]
                        df_oferta_pres = adiciona_linha_total_rateio(df_oferta_pres)
                        formatar_df_precificacao_oferta(df_oferta_pres)

                if "CH por Semestre_Síncrono" in df_oferta.columns:
                    with st.expander("CH Síncrona"):
                        df_oferta_sinc = df_oferta[df_oferta["CH por Semestre_Síncrono"] > 0].copy()
                        df_oferta_sinc = df_oferta_sinc[["Chave", "Semestre", "Base de Alunos", "Qtde Turmas", "CH por Semestre_Síncrono", "Custo Docente por Semestre_Síncrono"]]
                        df_oferta_sinc = adiciona_linha_total_rateio(df_oferta_sinc)
                        formatar_df_precificacao_oferta(df_oferta_sinc)

                #df_oferta_formatado = formatar_df_precificacao_oferta(df_oferta)

            # O restante dos expanders com os detalhes que você já tinha
            with st.expander("Detalhamento por Série", expanded=False):
                # ... (o seu código para o loop de detalhes por série continua aqui, sem alterações)
                for serie_num, dados_serie in detalhes_series.items():
                    with st.expander(f"{serie_num}º Série"):
                        # ... (todo o seu código de métricas por série)
                        st.markdown(f"Base de alunos: {dados_serie['base_alunos']}")
                        col1_serie, col2_serie, col3_serie = st.columns(3)
                        with col1_serie:
                            st.metric(label="Custo Mensal Aproximado", value=formatar_valor_brl(dados_serie['custo_mensal']))
                            st.metric(label="Carga Horária Total (horas)", value=locale.format_string('%.1f', dados_serie['ch_total'], grouping=True))
                        with col2_serie:
                            st.metric(label="Custo Total do Semestre", value=formatar_valor_brl(dados_serie['custo_total']))
                            st.metric(label="Custo por Aluno", value=formatar_valor_brl(dados_serie['custo_por_aluno']))
                        with col3_serie:
                            st.metric(label="Ticket Médio", value=formatar_valor_brl(dados_serie['ticket_medio']))
                            st.metric(
                                label="Lucro",
                                value=formatar_valor_brl(dados_serie['margem'])
                            )
                        df_oferta = dfs['df_oferta']
                        df_por_semestre = df_oferta[df_oferta['Semestre'] == serie_num]
                        df_por_semestre = adiciona_linha_total(df_por_semestre, dados_serie['base_alunos'])
                        formatar_df_por_semestre(df_por_semestre)
                        st.divider()


st.sidebar.title("Debug Info")
with st.sidebar.expander("Dados da Simulação (Session State)"):
    st.json(st.session_state)
    if "todos_os_resultados" in globals():
        if todos_os_resultados:
            st.json(todos_os_resultados)