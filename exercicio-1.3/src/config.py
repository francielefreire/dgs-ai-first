from pathlib import Path

# Pasta raiz do exercício (exercicio-1.3/)
BASE_DIR = Path(__file__).resolve().parent.parent

DOCS_DIR = BASE_DIR.parent / "pratica-1"
CHROMA_PATH = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "novatech_docs"

# Somente os documentos oficiais da NovaTech — exclui metaarquivos do exercício
DOCS_ALLOWED = {
    "FAQ-atendimento.md",
    "POL-001-politica-devolucao.md",
    "PROC-042-frete-especial-v1.md",
    "PROC-042-v2-frete-especial-revisado.md",
    "SLA-2024-tabela-sla-clientes.md",
}

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Número de chunks retornados na busca por similaridade
TOP_K = 3
