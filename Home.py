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
st.markdown('''
    Premissas:
           
            - A matriz curricular dos cursos é definida por um "Chassi", único para cada modelo de oferta. Cursos com o mesmo modelo de oferta compartilham a mesma matriz curricular.
            
            - A sinergia entre cursos é aplicada com base no percentual definido pelas novas matrizes radiais, para cada Área do Conhecimento.
            
            - Essa sinergia é aplicada nas UCs iniciais de cada curso, conforme o modelo de oferta.
            
            - O agrupamento de oferta considera apenas UCs sinérgicas, e é feito com base na Marca, Polo, Curso, Modelo de Oferta, Área do Conhecimento, UC, dessa maneira:
                . CH presencial de UCs sinérgicas só podem ser agrupadas dentro da mesma Marca, Polo, Modelo de Oferta e Área do Conhecimento.
                . CHs Assíncronas, Síncronas Mediadas e Síncronas são agrupadas dentro da mesma Marca, Modelo de Oferta e Área do Conhecimento, independente do Polo.
                . A disciplina de Academia de Futuros Profissionais (AFP) é sempre agrupada em todos os níveis, inclusive entre marcas.
            
            - O ticket médio foi retirado por curso, com base em 2025/1, de acordo com o BI de Performance Acadêmica 2025.
            
            - O ticket médio calculado e mostrado é uma média ponderada pelo número de alunos em cada curso, e o respectivo ticket médio.
            
            - Um semestre letivo é composto por 20 semanas de aulas.
            
            - O pagamento dos docentes inclui descansos remunerados, deixando um valor efetivo de 5,25 semanas por mês. Além disso, incluímos 170% sobre o valor para pagamento de encargos (Custo mensal = Custo semanal * 5,25 * 1,7)
''')