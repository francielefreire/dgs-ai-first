"""
Executa as 5 perguntas de teste, exibe chunks recuperados com scores
e compara com o gabarito do Anexo B.
"""

from query import retrieve_chunks

# ---------------------------------------------------------------------------
# Gabarito do Anexo B (mapa de cobertura)
# ---------------------------------------------------------------------------

GABARITO = {
    "Qual o prazo de devolução?": {
        "esperados": ["POL-001-politica-devolucao.md"],
        "aceitaveis": ["FAQ-atendimento.md"],
    },
    "Qual o SLA do cliente Gold?": {
        "esperados": ["SLA-2024-tabela-sla-clientes.md"],
        "aceitaveis": ["SLA-2024-tabela-sla-clientes.md"],
    },
    "Como calcular frete acima de 500kg?": {
        "esperados": ["PROC-042-v2-frete-especial-revisado.md"],
        "aceitaveis": ["PROC-042-frete-especial-v1.md", "FAQ-atendimento.md"],
    },
    "Quais documentos precisam ser anexados na solicitação de frete especial?": {
        "esperados": ["PROC-042-v2-frete-especial-revisado.md"],
        "aceitaveis": ["PROC-042-frete-especial-v1.md"],
    },
    "O que acontece se o prazo de entrega for descumprido?": {
        "esperados": ["SLA-2024-tabela-sla-clientes.md"],
        "aceitaveis": [],
    },
}


def avaliar_chunk(doc_name: str, gabarito: dict) -> str:
    if doc_name in gabarito["esperados"]:
        return "✅ esperado"
    if doc_name in gabarito["aceitaveis"]:
        return "⚠️  aceitável"
    return "❌ não esperado"


def run_all_tests() -> None:
    print("=" * 65)
    print("  Testes do Pipeline RAG — NovaTech")
    print("=" * 65)

    for i, (pergunta, gabarito) in enumerate(GABARITO.items(), start=1):
        print(f"\n{'─' * 65}")
        print(f"TESTE {i}: {pergunta}")
        print(f"  Esperado pelo gabarito: {', '.join(gabarito['esperados'])}")

        chunks = retrieve_chunks(pergunta)

        print(f"\n  Chunks recuperados:")
        acertou = False
        for j, chunk in enumerate(chunks, 1):
            doc = chunk["metadata"].get("document_name", "?")
            dist = chunk["distance"]
            avaliacao = avaliar_chunk(doc, gabarito)
            print(f"    [{j}] {doc}")
            print(f"         distância: {dist:.4f}  |  {avaliacao}")
            print(f"         trecho: \"{chunk['text'][:120].strip()}...\"")
            if doc in gabarito["esperados"]:
                acertou = True

        resultado = "✅ PASSOU" if acertou else "❌ NÃO RECUPEROU O DOCUMENTO ESPERADO"
        print(f"\n  Resultado: {resultado}")

    print(f"\n{'=' * 65}")
    print("  Testes concluídos. Cole os resultados no exercicio-1-3-rag-pipeline.md")


if __name__ == "__main__":
    run_all_tests()
