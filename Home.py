import streamlit as st
# --- Configuração da Página ---
st.set_page_config(
    page_title="Simulador de Precificação",
    page_icon="🎓",
    layout="wide"
)

# --- Título e Descrição ---
st.title("Simulação de Precificação para Polos 🎓")
st.markdown("Use esta ferramenta para simular um portfólio de oferta em diversos polos/sedes da Ânima, com uma visão também para expansão de polos/sedes, tudo de acordo com as premissas do novo marco regulatório")
st.markdown("Este simulador está apto para duas versões: Adaptação de projeção recebida direto da área demandante, e área demandante simular a partir de uma base zero, diretamente do simulador")
st.markdown("Você pode personalizar a oferta da maneira que desejar e obter uma estimativa de custo docente, receita, contratação de CH e muito mais! ")
st.markdown("Você pode dar início navegando à página 'Simulação' na aba lateral ao lado.")
st.markdown('''A página de simulação contém várias seções, entre elas: 
            
1. Ofertas de Curso --> Aqui é feita a inserção dos polos/sedes e seu portfólio de oferta, com a opção de buscar uma base de alunos existente na Ânima para iniciar a simulação.
                
2. Parâmetros da Projeção --> Aqui você encontra as configurações de regras de projeção de base de alunos, ferramentas de gerenciamento (remoção em lote, conversão de ofertas para o novo modelo...), e a lista de ofertas adicionadas para personalização individual.
                
3. Parâmetros de Precificação --> Aqui você pode escolher adotar/ignorar algumas premissas de oferta, como TCC, Estágio, AFP, etc. Você também pode alterar os parâmetros de máximo de alunos por turma, carga horária semanal, e remuneração por hora cada Ator Pedagógico em cada modelo de oferta.
                
4. Analítico de Custos --> Seção com todos os resultados da simulação, traduz todas as premissas adotadas em métricas financeiras para planejamento da oferta. Contém um seção geral, resumida por semestre, e depois uma seção para análise detalhada de semestres específicos.
            ''')
st.markdown('''
    ## Premissas de simulação: 

- O simulador conta com base de alunos para 13 cursos na USJT, que compõem cerca de 80% da oferta na USJT. São eles: 
ADMINISTRAÇÃO, ANÁLISE E DESENVOLVIMENTO DE SISTEMAS, CIÊNCIAS CONTÁBEIS, PEDAGOGIA, BIOMEDICINA, EDUCAÇÃO FÍSICA,
ENGENHARIA CIVIL, ENGENHARIA DE PRODUÇÃO, ENGENHARIA ELÉTRICA, ENGENHARIA MECÂNICA, FARMÁCIA, FISIOTERAPIA, NUTRIÇÃO
            
- Existem duas opções para simulação de base de alunos: A opção "Iniciar do Zero" admite X alunos em uma turma inicial, e acrescenta uma lógica de ingressantes por ano, com evasão por semestre. 
A opção "Continuar da Base Histórica" admite a base de ingressantes em 2025/1 como ingressantes em 2026/1 (turma inicial), e também adota uma lógica de ingressantes por ano, com evasão por semestre.

- A simulação sempre se inicia em 2026/1 e se extende por 10 semestres, até 2030/2. 
            
- A matriz curricular dos cursos é definida por um "Chassi", único para cada modelo de oferta. Cursos com o mesmo modelo de oferta compartilham a mesma matriz curricular (Chassi).
            
- A sinergia entre cursos é aplicada com base no percentual de CH "Ânima" + "Integrada", definido pelas novas matrizes radiais, para cada Área do Conhecimento, de acordo com o **BI Matrizes Radiais**
            
- Essa sinergia é aplicada nas UCs iniciais de cada curso, até que a CH sinérgina se aproxime do percentual da área de conhecimento, conforme o tempo de duração de curso, determinado pelo Chassi.
            
- O agrupamento de oferta é feito com base na Marca, Polo/Sede, Curso, Modelo de Oferta, Área do Conhecimento, UC, dessa maneira:
            
    - São agrupadas apenas UCs de mesma ordem em nosso Chassi. UC1 apenas com UC1, UC10 apenas com UC10 ...
        
    - CH presencial de UCs **sinérgicas** só podem ser agrupadas dentro da mesma Marca, Polo/Sede, Modelo de Oferta e Área do Conhecimento.
        
    - CH presencial de UCs **específicas** não são agrupadas
    
    - CHs Assíncronas, Síncronas Mediadas e Síncronas de UCs **sinérgicas** são agrupadas dentro da mesma Marca, Modelo de Oferta e Área do Conhecimento, independente do Polo/Sede.
        
    - CHs Assíncronas, Síncronas Mediadas e Síncronas de UCs **específicas** são agrupadas dentro da mesma Marca, Modelo de Oferta e Curso, independente do Polo/Sede.
            
    - A disciplina de **Academia de Futuros Profissionais (AFP)** é agrupada na mesma marca, mas isolando o presencial com os demais tipos de oferta.
            
- O ticket médio foi apurado por curso, modalidade, e marca, com base em 2025/1, de acordo com o BI de Performance Acadêmica 2025, fonte da Diretoria de Receitas
            
- Caso a combinação de curso, modalidade e marca não seja encontrada na base de tickets, admite-se a média Ânima do curso e modalidade. Caso a Ânima não oferte o curso na modalidade escolhida, é admitido o ticket médio da própria modalidade de oferta na Ânima (ignorando o curso).
            
- O ticket médio final (calculado e mostrado) é uma média ponderada pelo número de alunos em cada curso, e o respectivo ticket médio dos cursos adicionados.
            
- Um semestre letivo é composto por 20 semanas de aulas.
            
- O pagamento dos docentes inclui descansos remunerados, deixando um valor efetivo de 5,25 semanas por mês. Além disso, incluímos o adicional de 70% sobre o valor para pagamento de encargos (Custo Semestral = Custo semanal * 5,25 * 1,7 * 6)

- As premissas de ofertas do modelo atual (EAD Atual, Semi Presencial Atual e Presencial Atual) também estão admitindo as mesmas regras de enturmação e Chassi, diferindo do novo marco apenas pelos parâmetros na Seção 3.
            
- Seguindo a lógica do Chassi, o ator pedagógico "Professor Regente" é considerado o mesmo para:
    - **UCs sinérgicas**: Área do conhecimento, marca e modelo de oferta.
    - **UCs específicas**: Curso, marca e modelo de oferta.
            
- Quando simulado mais de um polo/sede, é feito rateio de custo e receita entre os polos/sedes de uma mesma marca, levando em consideração a proporção de alunos por polo/sede.
''', width='content')