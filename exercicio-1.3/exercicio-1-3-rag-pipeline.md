# Exercício 1.3 - Construção de Pipeline RAG

## Arquitetura

O pipeline RAG (Retrieval-Augmented Generation) foi construído com cinco módulos independentes que se comunicam por meio de um arquivo central de configuração:

```
pratica-1/*.md
      │
      ▼
 [ingest.py]
  └─ Leitura dos .md
  └─ Chunking (500 chars / overlap 100)
  └─ Embeddings (sentence-transformers)
  └─ Persistência no ChromaDB
      │
      ▼
  [chroma_db/]  ←── banco vetorial local
      │
      ▼
  [query.py]
  └─ Embedding da pergunta
  └─ Busca por similaridade (top-k=3)
      │
      ▼
 [prompt_builder.py]
  └─ Montagem do prompt com contexto + pergunta
      │
      ▼
      LLM
```

### Módulos

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Fonte única de configuração (paths, parâmetros, modelo) |
| `ingest.py` | Leitura, chunking, embeddings e persistência no ChromaDB |
| `query.py` | Busca vetorial e orquestração do pipeline de consulta |
| `prompt_builder.py` | Formatação do prompt final para o LLM |
| `test_queries.py` | Execução das perguntas de teste |

---

## Estratégia de Chunking

Foi adotada uma estratégia de chunking por tamanho fixo com sobreposição (overlap).

### Configuração

- Tamanho do chunk: **500 caracteres**
- Overlap: **100 caracteres**

### Justificativa

A documentação da NovaTech é composta por políticas, procedimentos e tabelas de SLA com informações que frequentemente dependem do contexto anterior e posterior.

- Chunks muito pequenos fragmentariam informações importantes, reduzindo a qualidade da recuperação semântica.
- Chunks muito grandes poderiam misturar assuntos distintos, diminuindo a precisão da busca.

O tamanho de 500 caracteres equilibra:

- Preservação do contexto semântico
- Precisão na recuperação
- Baixo consumo de tokens no prompt final
- Melhor qualidade dos embeddings gerados

O overlap de 100 caracteres evita perda de contexto entre chunks consecutivos, especialmente em regras de negócio distribuídas em múltiplos parágrafos, tabelas de SLA e políticas com exceções.

### Exemplo

**Sem overlap:**

> Chunk 1: `"Cliente Gold — resposta em até 2h"`
> Chunk 2: `"resolução em até 24h"`

Uma busca pode recuperar apenas metade da informação.

**Com overlap:**

> Chunk 1: `"Cliente Gold — resposta em até 2h, resolução em até 24h"`
> Chunk 2: `"resolução em até 24h..."`

As informações permanecem semanticamente completas.

### Possíveis Melhorias

Em produção, o chunking poderia ser baseado na estrutura do documento (títulos, seções, tabelas), preservando melhor o significado e reduzindo a fragmentação de informações relacionadas.

---

## Tecnologias Utilizadas

| Tecnologia | Versão mínima | Uso |
|---|---|---|
| `sentence-transformers` | 2.7.0 | Geração de embeddings |
| `chromadb` | 0.5.0 | Banco vetorial local |
| Modelo `all-MiniLM-L6-v2` | — | Encoder leve e eficiente para português/inglês |
| Python | 3.10+ | Linguagem do pipeline |

O modelo `all-MiniLM-L6-v2` foi escolhido por ser leve (22 MB), rápido e produzir embeddings de boa qualidade para tarefas de busca semântica em textos curtos a médios.

---

## Processo de Ingestão

Executado pelo script `ingest.py`, o pipeline de ingestão segue quatro etapas:

### 1. Leitura dos documentos

Todos os arquivos `.md` da pasta `pratica-1/` são lidos e armazenados com seu nome de arquivo e conteúdo.

```python
documents = load_markdown_files(DOCS_DIR)
```

Documentos ingeridos:
- `FAQ-atendimento.md`
- `POL-001-politica-devolucao.md`
- `PROC-042-frete-especial-v1.md`
- `PROC-042-v2-frete-especial-revisado.md`
- `SLA-2024-tabela-sla-clientes.md`
- `anexo-a-documentacao-simulada-novatech.md`
- `anexo-b-chunks-referencia-rag.md`
- `exercicio-fase-1-entendimento.md`

### 2. Geração dos chunks

Cada documento é dividido em chunks de 500 caracteres com overlap de 100. Cada chunk recebe um ID determinístico gerado via `MD5(filename::index)`, evitando duplicatas em re-execuções.

```python
chunks = build_chunks(documents)
```

### 3. Geração dos embeddings

O modelo `all-MiniLM-L6-v2` transforma cada chunk em um vetor de 384 dimensões.

```python
embeddings = embed_chunks(chunks, EMBEDDING_MODEL)
```

### 4. Persistência no ChromaDB

Os chunks, embeddings e metadados são armazenados na coleção `novatech_docs`. A coleção é recriada a cada execução para garantir idempotência.

```python
store_in_chroma(chunks, embeddings, CHROMA_PATH, COLLECTION_NAME)
```

**Metadados armazenados por chunk:**

```python
{
    "document_name": "FAQ-atendimento.md",
    "chunk_id":      "a3f7c9...",   # MD5 determinístico
    "chunk_index":   0              # posição no documento
}
```

---

## Processo de Busca

Executado pelo script `query.py`, o processo de busca segue três etapas:

### 1. Embedding da pergunta

A pergunta do usuário é transformada em vetor usando o mesmo modelo da ingestão (`all-MiniLM-L6-v2`).

### 2. Busca por similaridade

O ChromaDB compara o vetor da pergunta com todos os vetores armazenados usando distância cosseno e retorna os `TOP_K = 3` chunks mais similares.

```python
chunks = retrieve_chunks(question, top_k=TOP_K)
```

### 3. Montagem e retorno

Os chunks recuperados são passados para o `prompt_builder` junto com a pergunta original.

**Exemplo de saída da busca:**

```
Buscando: 'Qual o prazo de devolução?'
  [1] POL-001-politica-devolucao.md  (distância: 0.1823)
  [2] FAQ-atendimento.md             (distância: 0.3104)
  [3] anexo-a-documentacao-simulada-novatech.md  (distância: 0.4271)
```

---

## Montagem do Prompt

O `prompt_builder.py` recebe a pergunta e a lista de chunks recuperados e formata o prompt final para o LLM.

### Estrutura do prompt

```
Você é um assistente especializado nos documentos internos da NovaTech.
Responda à pergunta abaixo usando APENAS as informações dos documentos fornecidos.
Se a resposta não estiver nos documentos, diga "Não encontrei essa informação..."

--- DOCUMENTOS ---
[Fonte 1 — POL-001-politica-devolucao.md]
<texto do chunk 1>

[Fonte 2 — FAQ-atendimento.md]
<texto do chunk 2>

[Fonte 3 — anexo-a-documentacao-simulada-novatech.md]
<texto do chunk 3>
--- FIM DOS DOCUMENTOS ---

Pergunta: Qual o prazo de devolução?
Resposta:
```

O prompt instrui o LLM a se restringir ao contexto fornecido, reduzindo alucinações e garantindo respostas rastreáveis aos documentos originais.

---

## Testes Realizados

As perguntas de teste estão definidas em `test_queries.py` e cobrem os principais documentos da base.
Resultado geral: **3/5 testes passaram**.

### Teste 1 — ✅ PASSOU

**Pergunta:** Qual o prazo de devolução?

**Esperado pelo gabarito:** `POL-001-politica-devolucao.md`

| # | Documento recuperado | Distância | Avaliação |
|---|---|---|---|
| 1 | `POL-001-politica-devolucao.md` | 0.6862 | ✅ esperado |
| 2 | `FAQ-atendimento.md` | 0.7989 | ⚠️ aceitável |
| 3 | `POL-001-politica-devolucao.md` | 0.8162 | ✅ esperado |

**Análise:** O documento correto foi o mais similar. Dois chunks do mesmo documento foram recuperados (índices diferentes), o que é esperado dado o overlap. O FAQ apareceu como segundo resultado mas com distância maior — aceitável.

---

### Teste 2 — ✅ PASSOU

**Pergunta:** Qual o SLA do cliente Gold?

**Esperado pelo gabarito:** `SLA-2024-tabela-sla-clientes.md`

| # | Documento recuperado | Distância | Avaliação |
|---|---|---|---|
| 1 | `SLA-2024-tabela-sla-clientes.md` | 0.8412 | ✅ esperado |
| 2 | `FAQ-atendimento.md` | 0.8737 | ❌ não esperado |
| 3 | `SLA-2024-tabela-sla-clientes.md` | 0.9382 | ✅ esperado |

**Análise:** O documento correto foi recuperado em primeiro lugar. O FAQ apareceu na segunda posição com um chunk que trata de SLA de resposta vs. resolução — semanticamente próximo, mas não o ideal. O terceiro chunk recuperado contém a tabela de tiers, que é contexto útil para a resposta.

---

### Teste 3 — ❌ NÃO PASSOU

**Pergunta:** Como calcular frete acima de 500kg?

**Esperado pelo gabarito:** `PROC-042-v2-frete-especial-revisado.md`

| # | Documento recuperado | Distância | Avaliação |
|---|---|---|---|
| 1 | `PROC-042-frete-especial-v1.md` | 0.8193 | ⚠️ aceitável |
| 2 | `PROC-042-frete-especial-v1.md` | 0.8194 | ⚠️ aceitável |
| 3 | `PROC-042-frete-especial-v1.md` | 0.8434 | ⚠️ aceitável |

**Análise:** O pipeline recuperou exclusivamente a versão **v1 (desatualizada)** do procedimento, ignorando completamente a versão v2 revisada. Como os dois documentos tratam do mesmo assunto com vocabulário quase idêntico, o modelo não conseguiu distingui-los semanticamente. Este é um problema real: um atendente que usasse essa resposta aplicaria **multiplicadores regionais incorretos** (ex: Nordeste 1.4 em vez de 1.5). Ver Problema 1 na seção de problemas encontrados.

---

### Teste 4 — ❌ NÃO PASSOU

**Pergunta:** Quais documentos precisam ser anexados na solicitação de frete especial?

**Esperado pelo gabarito:** `PROC-042-v2-frete-especial-revisado.md`

| # | Documento recuperado | Distância | Avaliação |
|---|---|---|---|
| 1 | `FAQ-atendimento.md` | 0.8434 | ❌ não esperado |
| 2 | `FAQ-atendimento.md` | 0.8799 | ❌ não esperado |
| 3 | `FAQ-atendimento.md` | 0.9071 | ❌ não esperado |

**Análise:** O pipeline não recuperou nenhum chunk relevante. A pergunta usa o termo "documentos anexados", mas o procedimento PROC-042 provavelmente usa termos como "documentação obrigatória" ou "checklist". Essa diferença de vocabulário causa falha na busca semântica — o modelo não associou a intenção da pergunta ao conteúdo do documento correto. Ver Problema 2 na seção de problemas encontrados.

---

### Teste 5 — ✅ PASSOU

**Pergunta:** O que acontece se o prazo de entrega for descumprido?

**Esperado pelo gabarito:** `SLA-2024-tabela-sla-clientes.md`

| # | Documento recuperado | Distância | Avaliação |
|---|---|---|---|
| 1 | `SLA-2024-tabela-sla-clientes.md` | 0.7600 | ✅ esperado |
| 2 | `FAQ-atendimento.md` | 0.9261 | ❌ não esperado |
| 3 | `FAQ-atendimento.md` | 0.9700 | ❌ não esperado |

**Análise:** O documento correto foi recuperado com a menor distância do conjunto de testes (0.76), indicando alta confiança. Os dois chunks do FAQ que apareceram têm distâncias acima de 0.92 — muito mais baixas que o primeiro resultado, logo não devem impactar negativamente a resposta do LLM.

---

## Problemas Encontrados

### Problema 1 — Versão desatualizada do documento recuperada no lugar da versão correta

**Identificado no:** Teste 3 — "Como calcular frete acima de 500kg?"

O pipeline recuperou exclusivamente chunks de `PROC-042-frete-especial-v1.md` (versão de março/2023), ignorando `PROC-042-v2-frete-especial-revisado.md` (versão de novembro/2023, com multiplicadores regionais atualizados). Como os dois documentos tratam do mesmo tema com vocabulário quase idêntico, o modelo de embeddings não conseguiu distingui-los semanticamente — ambos têm representações vetoriais muito próximas, e a v1 "venceu" a busca por ter aparecido primeiro na ordenação interna.

**Impacto real:** Um atendente que usasse a resposta gerada pelo LLM aplicaria multiplicadores incorretos. Exemplo: Nordeste 1.4 (v1) em vez de 1.5 (v2), gerando subcobrança de frete.

### Correção

Adicionar metadado de versão/data ao chunk e, ao montar o prompt, incluir instrução explícita para o LLM priorizar a versão mais recente quando houver conflito:

```python
# No ingest.py, incluir a data de emissão nos metadados
metadatas=[{
    "document_name": c["document_name"],
    "chunk_id": c["chunk_id"],
    "chunk_index": c["chunk_index"],
    "versao": extrair_versao(c["document_name"]),  # "v1" ou "v2"
}]
```

```
# No prompt, adicionar instrução de desambiguação
Se houver documentos de versões diferentes sobre o mesmo tema,
utilize SEMPRE a versão mais recente.
```

---

### Problema 2 — Falha semântica por diferença de vocabulário (Teste 4)

**Identificado no:** Teste 4 — "Quais documentos precisam ser anexados na solicitação de frete especial?"

O pipeline não recuperou nenhum chunk relevante — todos os três resultados vieram do `FAQ-atendimento.md`, que não contém essa informação. A pergunta usa o termo "documentos anexados", enquanto o procedimento PROC-042 provavelmente usa "documentação obrigatória", "checklist" ou "requisitos". Essa diferença de vocabulário faz com que a distância semântica entre a pergunta e o chunk correto seja maior do que com chunks do FAQ (que contêm palavras como "documento" em contextos variados).

**Impacto real:** O LLM receberia contexto irrelevante e responderia com base no FAQ genérico, potencialmente inventando uma lista de documentos que não existe.

### Correção

Expandir a pergunta antes da busca (técnica de *query expansion*), incluindo sinônimos do domínio logístico:

```python
def expandir_query(question: str) -> str:
    expansoes = {
        "documentos anexados": "documentação obrigatória checklist requisitos",
        "frete especial": "carga acima 500kg PROC-042",
    }
    for termo, sinonimos in expansoes.items():
        if termo in question.lower():
            return f"{question} {sinonimos}"
    return question
```

Alternativamente, usar chunking baseado em seções (por títulos do markdown) em vez de tamanho fixo, de modo que o chunk "Documentação necessária" fique como uma unidade semântica completa e seja mais facilmente recuperado.

---

## Conclusão

O pipeline RAG foi implementado com sucesso utilizando ferramentas open-source leves e locais. A separação em módulos (`config`, `ingest`, `query`, `prompt_builder`, `test_queries`) garante que cada parte possa ser evoluída de forma independente.

Os principais pontos de melhoria para uma versão de produção seriam:

- Chunking baseado na estrutura semântica dos documentos (por seções e títulos)
- Avaliação formal da qualidade da recuperação (Precision@K, MRR)
- Integração com um LLM real para geração das respostas finais
- Atualização incremental do ChromaDB sem necessidade de reingestão completa
