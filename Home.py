import streamlit as st
# --- Configuração da Página ---
st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# --- Título e Descrição ---
st.title("Simulação de Precificação para Polos 🎓")
st.markdown("Use esta ferramenta para montar um cenário de simulação para o seu polo, personalizando a oferta da maneira que lhe interessa.")
st.markdown("Você vai encontrar 2 opções de simulação na barra lateral, cada página segue uma premissa para base de alunos a ser simulada")
st.markdown("Opção 1: Base de Alunos específica - Permite inserir a quantidade de alunos para cada um dos semestres dos cursos escolhidos.")
st.markdown("Opção 2: Base de Alunos projetada - Admite uma base inicial de calouros e simula ingresso e evasão nos cursos")