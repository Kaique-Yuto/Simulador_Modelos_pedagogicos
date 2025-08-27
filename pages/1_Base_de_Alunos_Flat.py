import streamlit as st
import pandas as pd
import numpy as np
from src.utils import obter_modelos_para_curso, plotar_custo_total, plotar_ch_total, plot_custo_docente, plotar_indicador_eficiencia, plot_ch_docente_por_categoria, format_detalhe_precificacao_uc, plot_eficiencia_por_semestre
from src.formatting import colorir_semestres, formatar_valor_brl
from src.data import carregar_dados
from streamlit import column_config
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# --- Configuração da Página ---
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


st.markdown("Você selecionou a Simulação com Base de Alunos Flat, isso significa que a mesma quantidade de estudantes será aplicada em cada um dos semestres do curso. Por exemplo: Ao escolher 70 alunos para um curso de 8 Semestres, a simulação roda para um total de 560 alunos (70*8)")
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

# Isso permite que o data_editor recalcule a página a cada edição sem precisar clicar no botão novamente.
if st.session_state.get('simulacao_ativa', False) and dataframes_carregados:
    st.header("4. Analítico de Custos", divider='rainbow')

    for curso, config in st.session_state.cursos_selecionados.items():
        with st.expander(f"Análise do Curso de {curso}"):
        
            # Pega o nome técnico do modelo
            modelo_selecionado = config["modelo_oferta"]
            
            # --- Parte 1: Mostrar a Matriz Curricular (UCs) ---
            st.subheader(f"Matriz Curricular")
            if modelo_selecionado:
                df_matriz_curso = df_matrizes[df_matrizes['MODELO'] == modelo_selecionado]
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
                    st.warning(f"Matriz não encontrada para o modelo: '{modelo_selecionado}'")
            
            # --- Parte 2: Mostrar Tabela de Parâmetros Editáveis ---
            st.subheader(f"Parâmetros de Simulação")
            
            # Se os parâmetros para este curso ainda não foram salvos no estado da sessão,
            # filtramos os padrões do DF principal e os salvamos.
            if ('parametros_editaveis' not in config or len(config.get('parametros_editaveis'))==0) and modelo_selecionado:
                parametros_iniciais = df_parametros[df_parametros['Modelo'] == modelo_selecionado].copy()
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
                    st.warning(f"Sem parâmetros para o modelo {modelo_selecionado} no curso {curso}. Pulando.")
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
                    new_row['Modelo'] = modelo_selecionado
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
            st.subheader("Resumo")
            col1, col2 = st.columns(2, border=True)
            with col1:
                col3,col4,col5,col6 = st.columns([2,1,1,1])
                with col3:
                    st.metric(
                        label="Custo Total",
                        value=locale.currency(plotar_custo_total(df_precificacao_curso), grouping=True, symbol="R$")
                        ,width='stretch'
                    )
                with col4:
                    st.metric(label="CH Total", value=locale.format_string('%.1f', plotar_ch_total(df_precificacao_curso), grouping=True),width='content')
                    
                with col5:
                    st.metric(label="Base de Alunos", value=config.get("numero_alunos")*8,width='content')
                with col6:
                    eficiencia = np.round(config.get("numero_alunos")*8/plotar_ch_total(df_precificacao_curso),2)
                    st.metric(label="Eficiência", value = eficiencia,width='content')
                st.pyplot(plot_custo_docente(df_precificacao_curso), use_container_width=False)
                
            with col2:
                #st.pyplot(plotar_indicador_eficiencia(4610, config.get("numero_alunos")))
                st.pyplot(plot_ch_docente_por_categoria(df_precificacao_curso))
                st.pyplot(plot_eficiencia_por_semestre(df_precificacao_curso), use_container_width=False)

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
                                value=locale.format_string('%.1f', total_ch_semestre, grouping=True)
                            )
                        with col2:
                            st.metric(
                                label="Custo Total do Semestre", 
                                value=formatar_valor_brl(total_semestre_as)
                            )
                            st.metric(
                                label="Eficiência do Semestre",
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