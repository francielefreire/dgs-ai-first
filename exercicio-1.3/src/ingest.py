"""
Ingestão de documentos para o pipeline RAG da NovaTech.

Lê .md de pratica-1/, divide em chunks, gera embeddings e persiste no ChromaDB.
"""

import hashlib
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_PATH,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DOCS_ALLOWED,
    DOCS_DIR,
    EMBEDDING_MODEL,
)


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------

def load_markdown_files(docs_dir: Path) -> list[dict]:
    """Lê todos os .md do diretório e retorna lista de {filename, content}."""
    if not docs_dir.exists():
        raise FileNotFoundError(f"Pasta '{docs_dir}' não encontrada.")

    documents = []
    for path in sorted(docs_dir.glob("*.md")):
        if path.name not in DOCS_ALLOWED:
            print(f"  [ignorado] {path.name}")
            continue
        content = path.read_text(encoding="utf-8").strip()
        if content:
            documents.append({"filename": path.name, "content": content})
            print(f"  [ok] {path.name}  ({len(content):,} chars)")

    if not documents:
        raise ValueError(f"Nenhum .md encontrado em '{docs_dir}'.")

    return documents


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Divide texto em chunks de `size` caracteres com sobreposição."""
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start : start + size].strip()
        if chunk:
            chunks.append(chunk)
        start += size - overlap
    return chunks


def build_chunks(documents: list[dict]) -> list[dict]:
    """Gera chunks para todos os docs com IDs determinísticos."""
    result = []
    for doc in documents:
        for idx, text in enumerate(chunk_text(doc["content"], CHUNK_SIZE, CHUNK_OVERLAP)):
            chunk_id = hashlib.md5(f"{doc['filename']}::{idx}".encode()).hexdigest()
            result.append(
                {
                    "chunk_id": chunk_id,
                    "document_name": doc["filename"],
                    "chunk_index": idx,
                    "text": text,
                }
            )
    return result


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def embed_chunks(chunks: list[dict], model_name: str) -> list[list[float]]:
    """Gera embeddings para os textos dos chunks."""
    print(f"\n  Carregando modelo '{model_name}'...")
    model = SentenceTransformer(model_name)
    texts = [c["text"] for c in chunks]
    print(f"  Gerando embeddings para {len(texts)} chunks...")
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()


# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

def store_in_chroma(
    chunks: list[dict],
    embeddings: list[list[float]],
    chroma_path: str,
    collection_name: str,
) -> None:
    """Persiste chunks e metadados no ChromaDB (recria a coleção a cada run)."""
    client = chromadb.PersistentClient(path=chroma_path)

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(collection_name)
    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "document_name": c["document_name"],
                "chunk_id": c["chunk_id"],
                "chunk_index": c["chunk_index"],
            }
            for c in chunks
        ],
    )

    print(f"\n  Coleção '{collection_name}': {len(chunks)} chunks → {chroma_path}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run_ingestion() -> None:
    print("=" * 50)
    print("  Pipeline de Ingestão RAG — NovaTech")
    print("=" * 50)

    print(f"\n[1/4] Lendo documentos de '{DOCS_DIR}'...")
    documents = load_markdown_files(DOCS_DIR)
    print(f"  Total: {len(documents)} arquivo(s)")

    print(f"\n[2/4] Gerando chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = build_chunks(documents)
    print(f"  Total: {len(chunks)} chunk(s)")

    print("\n[3/4] Gerando embeddings...")
    embeddings = embed_chunks(chunks, EMBEDDING_MODEL)

    print("\n[4/4] Armazenando no ChromaDB...")
    store_in_chroma(chunks, embeddings, CHROMA_PATH, COLLECTION_NAME)

    print("\n[concluído] Ingestão finalizada com sucesso.")


if __name__ == "__main__":
    run_ingestion()
