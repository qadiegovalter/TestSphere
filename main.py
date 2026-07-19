import streamlit as st
from services.groq_client import get_groq_client
from agents.qa_agent import process_full_qa_flow

# 1. Configuração da Página
st.set_page_config(
    page_title="QA Auto Artifacts",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Barra Lateral (Configurações)
with st.sidebar:
    st.title("🧪 QA Auto Artifacts")
    st.markdown("Gere artefatos profissionais de testes com o poder da IA.")
    st.markdown("---")
    
    # Menu focado nas funções mapeadas
    qa_tools = st.selectbox(
        "O que vamos construir hoje?",
        [
            "Design: Cenários e Casos de Teste 🧩",
            "Planejamento: Requisitos e Riscos 📝",
            "Relatórios: Bugs e Métricas de Qualidade 📊"
        ]
    )
    
    st.markdown("### 🛠️ Stack Técnica")
    linguagem = st.selectbox(
        "Linguagem Principal:", 
        ["Python 🐍", "JavaScript ✨", "TypeScript 🟦", "Java ☕", "C# 🎵", "Outra/Não aplicável"]
    )
    
    framework = st.text_input(
        "Framework / Biblioteca:", 
        placeholder="Ex: Playwright, Cypress, RestAssured..."
    )

    st.markdown("---")
    st.caption("🚀 Dica: Copie e cole os requisitos da sua User Story ou a descrição do bug direto no chat.")

# 3. Interface Principal (Chat)
st.title("Assistente para QA")
st.info(f"**Modo Ativo:** {qa_tools} | **Stack:** {linguagem} + {framework if framework else 'Nenhum'}")

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Execução do Cliente Groq para garantir que a chave API está configurada
try:
    _ = get_groq_client()
except Exception as e:
    st.sidebar.error(f"Erro de configuração: {e}")
    st.stop()

# Captura o Input do Usuário
if prompt := st.chat_input("Insira as informações/requisitos aqui..."):
    
    # Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Processamento Direto e Rápido
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        status_placeholder.info("⏳ Processando e estruturando artefato...")
        
        # Chama a função unificada
        ai_resposta = process_full_qa_flow(
            funcao=qa_tools,
            detalhes=prompt,
            linguagem=linguagem,
            framework=framework
        )
        
        status_placeholder.empty()
        st.markdown(ai_resposta)
        
        # Salva a resposta no histórico
        st.session_state.messages.append({"role": "assistant", "content": ai_resposta})
