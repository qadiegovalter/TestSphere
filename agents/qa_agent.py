from services.groq_client import get_groq_client
from prompts.impact_analysis import SYSTEM_PROMPT as prompt_impacto
from prompts.case_test import SYSTEM_PROMPT as prompt_casos
from prompts.bug_report import SYSTEM_PROMPT as prompt_bug

# Mapeamento do menu do Streamlit para o respectivo Prompt do Sistema
MAPA_PROMPTS = {
    "Planejamento: Requisitos e Riscos 📝": prompt_impacto,
    "Design: Cenários e Casos de Teste 🧩": prompt_casos,
    "Relatórios: Bugs e Métricas de Qualidade 📊": prompt_bug
}

def process_full_qa_flow(funcao, detalhes, linguagem=None, framework=None):
    try:
        client = get_groq_client()
        
        # 1. Busca o prompt do dicionário com base na seleção do menu
        system_prompt = MAPA_PROMPTS.get(funcao, prompt_casos)
        
        # 2. Constrói o contexto dinâmico do usuário incluindo a stack técnica
        contexto_usuario = f"""
        [CONTEXTO DA STACK DO PROJETO]
        Linguagem Principal: {linguagem}
        Framework/Biblioteca: {framework if framework else 'Não especificado'}

        [DEMANDA / REQUISITO ENVIADO]
        {detalhes}
        """
        
        # 3. Faz uma única chamada rápida e assertiva
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contexto_usuario}
            ],
            model="llama-3.3-70b-versatile",  # Modelo rápido, inteligente e ideal para formatações estritas
            temperature=0.1  # Temperatura baixa mantém a IA rígida seguindo o template solicitado
        )
        
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erro ao processar o artefato de QA: {str(e)}"
