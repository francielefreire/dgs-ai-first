"""
Monta o prompt final enviado ao LLM combinando contexto recuperado e pergunta.
"""


def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Recebe a pergunta do usuário e os chunks recuperados do ChromaDB.
    Retorna o prompt formatado para o LLM.
    """
    context_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get("metadata", {}).get("document_name", "desconhecido")
        text = chunk.get("text", "")
        context_blocks.append(f"[Fonte {i} — {source}]\n{text}")

    context = "\n\n".join(context_blocks)

    return f"""Você é um assistente especializado nos documentos internos da NovaTech.
Responda à pergunta abaixo usando APENAS as informações dos documentos fornecidos.
Se a resposta não estiver nos documentos, diga "Não encontrei essa informação nos documentos disponíveis."

--- DOCUMENTOS ---
{context}
--- FIM DOS DOCUMENTOS ---

Pergunta: {question}
Resposta:"""
