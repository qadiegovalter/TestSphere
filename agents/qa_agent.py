import os
from services.groq_client import get_groq_client
from google import genai
from openai import OpenAI

from prompts.impact_analysis import SYSTEM_PROMPT as prompt_impacto
from prompts.case_test import SYSTEM_PROMPT as prompt_casos
from prompts.bug_report import SYSTEM_PROMPT as prompt_bug

# Mapeamento do menu do Streamlit para o respectivo Prompt do Sistema[cite: 2]
MAPA_PROMPTS = {
    "Planejamento: Requisitos e Riscos 📝": prompt_impacto,
    "Design: Cenários e Casos de Teste 🧩": prompt_casos,
    "Relatórios: Bugs e Métricas de Qualidade 📊": prompt_bug
}

# =====================================================================
# FUNÇÕES AUXILIARES PARA CADA PROVEDOR DE IA
# =====================================================================

def tentar_groq(system_prompt, user_context):
    """Tentativa 1: Groq (Rápida e Gratuita/Barata)"""
    client = get_groq_client()[cite: 7]
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1
    )
    return response.choices[0].message.content[cite: 7]


def tentar_gemini(system_prompt, user_context):
    """Tentativa 2 (Fallback): Gemini Oficial"""
    # Inicializa usando a variável de ambiente GEMINI_API_KEY automaticamente
    client = genai.Client()
    
    # Unificamos os prompts pois o SDK do Gemini aceita a instrução do sistema na configuração
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_context,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1
        )
    )
    return response.text


def tentar_openrouter(system_prompt, user_context):
    """Tentativa 3 (Fallback Final): OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Chave da OpenRouter não configurada.")
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ],
        model="nvidia/nemotron-3-super", # Modelo OpenRouter
        temperature=0.1
    )
    return response.choices[0].message.content


# =====================================================================
# ORQUESTRADOR PRINCIPAL COM SUCESSÃO DE FALLBACK
# =====================================================================

def process_full_qa_flow(funcao, detalhes, linguagem=None, framework=None):
    # 1. Busca o prompt correto do dicionário[cite: 7]
    system_prompt = MAPA_PROMPTS.get(funcao, prompt_casos)
    
    # 2. Constrói o contexto dinâmico do usuário[cite: 7]
    contexto_usuario = f"""
    [CONTEXTO DA STACK DO PROJETO]
    Linguagem Principal: {linguagem}
    Framework/Biblioteca: {framework if framework else 'Não especificado'}

    [DEMANDA / REQUISITO ENVIADO]
    {detalhes}
    """
    
    # --- FILA DE EXECUÇÃO DO FALLBACK ---
    
    # Passo 1: Tenta o Provedor Principal (Groq)
    try:
        return tentar_groq(system_prompt, contexto_usuario)
    except Exception as e_groq:
        print(f"⚠️ Groq falhou: {e_groq}. Tentando rota de contingência (Gemini)...")
        
        # Passo 2: Se a Groq falhar, tenta o Gemini
        try:
            return tentar_gemini(system_prompt, contexto_usuario)
        except Exception as e_gemini:
            print(f"⚠️ Gemini falhou: {e_gemini}. Tentando rota final (OpenRouter)...")
            
            # Passo 3: Se o Gemini falhar, joga para o OpenRouter
            try:
                return tentar_openrouter(system_prompt, contexto_usuario)
            except Exception as e_openrouter:
                # Se tudo falhar, devolve um erro amigável na tela do seu Streamlit
                return f"❌ Erro Crítico: Todos os provedores de IA falharam.\n" \
                       f"Detalhes dos erros:\n" \
                       f"- Groq: {str(e_groq)}\n" \
                       f"- Gemini: {str(e_gemini)}\n" \
                       f"- OpenRouter: {str(e_openrouter)}"
