import streamlit as st
from streamlit import column_config
from src.formatting import colorir_semestres, formatar_valor_brl, format_detalhe_precificacao_uc

st.set_page_config(
    page_title="Resultados da Simulação",
    page_icon="📊",
    layout="wide"
)

st.header("4. Analítico de Custos", divider='rainbow')

if not st.session_state.get('simulacao_ativa', False):
    st.info("Nenhuma simulação foi executada ainda. Volte para a página principal para configurar e rodar os cálculos.")
    st.stop()

for curso, config in st.session_state.get('cursos_selecionados', {}).items():
    df_matriz_curso = config.get('df_matriz_curso')
    df_precificacao_curso = config.get('df_precificacao_curso')
    edited_df = config.get('parametros_editaveis')

    if df_precificacao_curso is None or df_precificacao_curso.empty:
        st.warning(f"Não há resultados de precificação para o curso de {curso}. Verifique as configurações na página principal.")
        continue

    with st.expander(f"Análise do Curso de {curso}", expanded=True):
        
        # --- Parte 1: Mostrar a Matriz Curricular (UCs) ---
        st.subheader(f"Matriz Curricular")
        if df_matriz_curso is not None and not df_matriz_curso.empty:
            df_display = df_matriz_curso[['Semestre', 'UC', 'CH TOTAL', 'PRESENCIALIDADE', 'ASSÍNCRONA', 'SÍNCRONA MED']]
            df_display = df_display.style.apply(colorir_semestres, axis=1)
            with st.expander("Expandir matriz"):
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Semestre": column_config.NumberColumn("SEMESTRE", format="%d"),
                        "PRESENCIALIDADE": "PRESENCIALIDADE (hr)",
                        "ASSÍNCRONA": "ASSÍNCRONA (hr)",
                        "SÍNCRONA MED": "SÍNCRONA MED (hr)"
                    }
                )
        else:
            st.warning(f"Matriz curricular não encontrada para o curso: '{curso}'")
        
        # --- Parte 2: Mostrar Tabela de Parâmetros Editáveis ---
        st.subheader(f"Parâmetros de Simulação Utilizados")
        if edited_df is not None and not edited_df.empty:
            with st.expander("Expandir parâmetros"):
                # A edição é feita na página principal, aqui apenas exibimos
                st.data_editor(
                    edited_df,
                    hide_index=True,
                    use_container_width=True,
                    disabled=['modelo', 'parametro', 'categoria', 'ator_pedagogico', 'valor'],
                    key=f"viewer_{curso}"
                )
        else:
            st.warning(f"Parâmetros não encontrados para o curso: '{curso}'")

        # --- Parte 3: Detalhamento da Precificação ---
        st.subheader("Detalhamento da Precificação por Semestre")
        with st.expander("Expandir detalhamento", expanded=True):
            semestres_unicos = sorted(df_precificacao_curso["Semestre"].dropna().unique())
            for semestre in semestres_unicos:
                with st.expander(f"{semestre}º Semestre"):
                    df_do_semestre = df_precificacao_curso[df_precificacao_curso["Semestre"] == semestre]

                    total_semestre_am = df_do_semestre['total_uc_am'].sum()
                    total_semestre_as = df_do_semestre['total_uc_as'].sum()
                    total_ch_semestre = df_do_semestre['total_ch_uc'].sum()
                    taxa_eficiencia = config.get("numero_alunos") / total_ch_semestre if total_ch_semestre > 0 else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            label="Custo Mensal Aproximado", 
                            value=formatar_valor_brl(total_semestre_am)
                        )
                        st.metric(
                            label="Carga Horária Total",
                            value=f"{int(total_ch_semestre)} h"
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

                    for _, row in df_do_semestre.iterrows():
                        st.markdown(f"**UC:** {row['UC']}")
                        format_detalhe_precificacao_uc(row)