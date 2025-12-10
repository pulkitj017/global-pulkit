from typing import List

import ollama

from app.config import get_settings


settings = get_settings()

# SYSTEM_PROMPT = """You are a cautious fintech knowledge assistant. Answer the user's question using ONLY the provided context from internal documents (SOPs, policies, FAQs, test cases).
# - If the answer is not fully supported by the context, reply exactly: "Information not available."
# - Do not invent or speculate.
# - Keep answers concise and factual."""
SYSTEM_PROMPT = """
You are a fintech knowledge assistant.

Rules:
1. When the user asks about topics found in the provided context (SOPs, policies, FAQs, test cases), answer ONLY using that context.
2. If the context is irrelevant or does not contain an answer, ignore the context and answer using your general LLM knowledge.
3. You may greet the user and answer general conversational questions.
4. Never mention the context unless explicitly asked.
5. Never invent facts about SOPs, KYC, policies, or fintech operations. If missing from context, say: "Information not available in internal documents."
"""



def build_prompt(query: str, contexts: List[str]) -> str:
    context_block = "\n\n".join(contexts)
    return f"""{SYSTEM_PROMPT}

Context:
{context_block}

User question: {query}

Answer:"""


# def generate_answer(query: str, contexts: List[str]) -> str:
#     prompt = build_prompt(query, contexts)
#     response = ollama.generate(model=settings.llm_model, prompt=prompt)
#     return response["response"].strip()
def generate_answer(query: str, contexts: List[str], scores: List[float]) -> str:
    # If no relevant context found → fallback to base LLM
    if not contexts or max(scores) < 0.70:
        return generate_llm_answer(query)

    prompt = build_prompt(query, contexts)
    response = ollama.generate(model=settings.llm_model, prompt=prompt)
    return response["response"].strip()



# A permissive LLM-only generator (no retrieval context).
# Use this for casual conversation or when you want the model to answer
# without requiring evidence from the knowledge base.
# SYSTEM_PROMPT_FREE = """You are a helpful fintech assistant. Answer the user's question concisely and helpfully.
# - If the question asks for personal data or secrets, refuse.
# - If you don't know an answer, say you don't know rather than inventing facts.
# """
SYSTEM_PROMPT_FREE = """
You are a helpful fintech assistant.
- You can answer general queries, greet the user, or provide basic information.
- Do NOT invent details about internal fintech processes, policies, or compliance.
- If you are asked about internal knowledge, say: "Please ask a specific question, I will check internal documents."
- If unsure, say "I’m not sure" instead of guessing.
"""



def generate_llm_answer(query: str) -> str:
    prompt = f"{SYSTEM_PROMPT_FREE}\n\nUser question: {query}\n\nAnswer:"
    response = ollama.generate(model=settings.llm_model, prompt=prompt)
    return response["response"].strip()


