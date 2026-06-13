"""
Pipeline de busca RAG: recebe uma pergunta, busca chunks relevantes no ChromaDB
e monta o prompt final.
"""

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL, TOP_K
from prompt_builder import build_prompt


def retrieve_chunks(question: str, top_k: int = TOP_K) -> list[dict]:
    """Busca os `top_k` chunks mais similares à pergunta no ChromaDB."""
    model = SentenceTransformer(EMBEDDING_MODEL)
    question_embedding = model.encode(question).tolist()

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({"text": text, "metadata": metadata, "distance": distance})

    return chunks


def run_query(question: str) -> str:
    """Executa o pipeline completo de busca e retorna o prompt montado."""
    print(f"\nBuscando: '{question}'")
    chunks = retrieve_chunks(question)

    print(f"  {len(chunks)} chunk(s) recuperado(s):")
    for i, c in enumerate(chunks, 1):
        src = c["metadata"].get("document_name", "?")
        print(f"    [{i}] {src}  (distância: {c['distance']:.4f})")

    prompt = build_prompt(question, chunks)
    return prompt


if __name__ == "__main__":
    question = input("Pergunta: ").strip()
    if question:
        prompt = run_query(question)
        print("\n--- PROMPT GERADO ---")
        print(prompt)
