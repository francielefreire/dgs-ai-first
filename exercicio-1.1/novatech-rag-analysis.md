# Assistente Corporativo com RAG — Análise de Viabilidade Técnica
### NovaTech · Documento Técnico · Junho 2026

---

## Índice

1. [Resumo Executivo](#1-resumo-executivo)
2. [Contexto e Objetivos](#2-contexto-e-objetivos)
3. [Análise de Viabilidade Técnica](#3-análise-de-viabilidade-técnica)
4. [Gerenciamento de Contexto em LLMs e RAG](#4-gerenciamento-de-contexto-em-llms-e-rag)
5. [Análise por Tipo de Fonte Documental](#5-análise-por-tipo-de-fonte-documental)
6. [Arquitetura Proposta](#6-arquitetura-proposta)
7. [Estratégias de Ingestão, Chunking e Retrieval](#7-estratégias-de-ingestão-chunking-e-retrieval)
8. [Estimativas de Volume, Esforço e Custos](#8-estimativas-de-volume-esforço-e-custos)
9. [Riscos Técnicos e Estratégias de Mitigação](#9-riscos-técnicos-e-estratégias-de-mitigação)
10. [Recomendação Técnica Final](#10-recomendação-técnica-final)
11. [Glossário](#11-glossário)

---

## 1. Resumo Executivo

A NovaTech possui aproximadamente **1.200 funcionários** e um volume expressivo de documentação interna distribuída entre SharePoint (PDFs), Confluence (wiki corporativa) e planilhas de negócio. O tempo gasto por colaboradores na busca de informações representa uma perda operacional direta e mensurável.

Este documento apresenta a análise técnica completa para a implementação de um **assistente corporativo baseado em RAG (Retrieval-Augmented Generation)** — uma arquitetura que combina busca semântica em documentos indexados com geração de respostas por um Large Language Model (LLM).

### Veredicto

| Dimensão | Avaliação |
|---|---|
| Viabilidade técnica | ✅ Viável |
| Adequação da arquitetura RAG | ✅ Alta aderência ao cenário |
| Complexidade de implementação | ⚠️ Média-Alta (concentrada no pipeline de ingestão) |
| Risco principal | ⚠️ Qualidade e organização da base documental de entrada |
| Recomendação | ✅ Implementação faseada com MVP em 3 meses |

A solução é **tecnicamente viável e estrategicamente recomendada**. O maior risco não está no modelo de linguagem — está na qualidade dos documentos de entrada e na engenharia do pipeline de ingestão. Uma implementação faseada reduz risco, entrega valor incremental e permite validar a qualidade antes de escalar.

---

## 2. Contexto e Objetivos

### 2.1 Perfil da Organização

- **Tamanho:** ~1.200 funcionários
- **Fontes documentais:**
  - PDFs hospedados no SharePoint (incluindo documentos com tabelas complexas, fluxogramas e documentos escaneados)
  - Wiki corporativa no Confluence (com links internos e macros customizadas)
  - Planilhas de negócio (com fórmulas e dependências entre abas)
- **Problema central:** informação distribuída e de difícil acesso, gerando retrabalho e dependência de pessoas-chave como repositórios informais de conhecimento

### 2.2 Objetivos do Projeto

1. Reduzir o tempo médio de busca de informação por colaborador
2. Padronizar respostas sobre políticas, processos e procedimentos internos
3. Disponibilizar um ponto único de acesso ao conhecimento corporativo
4. Garantir rastreabilidade — respostas com citação de fonte
5. Manter controle sobre o escopo: o assistente responde **apenas** com base no conteúdo corporativo indexado

### 2.3 Restrições e Requisitos Não Funcionais

| Requisito | Expectativa |
|---|---|
| Segurança | Controle de acesso por área/perfil (RBAC) |
| Escalabilidade | Suportar crescimento da base documental sem refatoração |
| Custo | Operação viável em escala corporativa (~1.200 usuários) |
| Qualidade | Respostas precisas com indicação de fonte e confiança |
| Atualização | Base de conhecimento sincronizada com fontes originais |

---

## 3. Análise de Viabilidade Técnica

### 3.1 Por que RAG é a Abordagem Correta

RAG (Retrieval-Augmented Generation) é a arquitetura de referência para assistentes corporativos baseados em documentação proprietária. Ela resolve a limitação fundamental dos LLMs: o conhecimento treinado é estático e não inclui informações internas da empresa.

| Critério | RAG | Fine-tuning | LLM base sem customização |
|---|---|---|---|
| Conhecimento proprietário | ✅ Injetado em tempo real | ✅ Incorporado no modelo | ❌ Não possui |
| Atualização da base | ✅ Re-indexação incremental | ❌ Re-treinamento necessário | — |
| Custo de implementação | ✅ Baixo-Médio | ❌ Alto | ✅ Baixo |
| Rastreabilidade da fonte | ✅ Nativa | ❌ Limitada | ❌ Inexistente |
| Controle de escopo | ✅ Total | ⚠️ Parcial | ❌ Nenhum |
| Risco de alucinação | ⚠️ Mitigado (mas existe) | ⚠️ Reduzido | ❌ Alto |

### 3.2 Adequação ao Cenário NovaTech

O cenário da NovaTech apresenta as condições ideais para RAG:

- **Volume documental** suficiente para justificar o investimento em indexação
- **Diversidade de fontes** que inviabiliza soluções de busca tradicional (keyword only)
- **Base de usuários** (1.200 funcionários) que garante ROI mensurável
- **Necessidade de rastreabilidade** — usuários corporativos precisam saber de onde vem a informação

### 3.3 Limitações Inerentes à Arquitetura RAG

Antes de prosseguir, é fundamental declarar o que RAG **não resolve**:

- Não executa cálculos dinâmicos em planilhas (requer arquitetura híbrida com Code Interpreter)
- Não entende imagens/fluxogramas sem pipeline multimodal adicional
- Não garante 100% de precisão — qualidade depende diretamente da qualidade dos documentos indexados
- Não substitui sistemas transacionais (ERP, CRM) — não consulta dados em tempo real

---

## 4. Gerenciamento de Contexto em LLMs e RAG

Esta é a dimensão mais crítica e frequentemente subestimada em implementações RAG. A qualidade da resposta não depende apenas do que está no índice — depende de **o que chega ao modelo, em qual ordem e quanto espaço ocupa na janela de contexto**.

### 4.1 O Conceito de Janela de Contexto

Todo LLM processa uma quantidade finita de tokens por requisição. Esse espaço é compartilhado por todos os elementos do prompt:

```
Janela de contexto (Claude Sonnet 4.6 = 128k tokens)

┌──────────────────────────────────────────────────────────┐
│ System prompt + persona + restrições de comportamento    │
│                                              ~1.500 tok  │
│ ─────────────────────────────────────────────────────── │
│ Histórico da conversa (últimas N interações)             │
│                                              ~3.000 tok  │
│ ─────────────────────────────────────────────────────── │
│ Pergunta atual do usuário                      ~500 tok  │
│ ─────────────────────────────────────────────────────── │
│ Contexto recuperado via RAG (chunks indexados)           │
│                                            ~123.000 tok  │
│                                                          │
│  Chunk de texto médio:          ~300 tok                 │
│  Chunk de tabela complexa:      ~800 tok                 │
│  Descrição de fluxograma:     ~1.200 tok                 │
│  Capacidade efetiva: ~400 chunks (nunca usar todos)      │
└──────────────────────────────────────────────────────────┘
```

### 4.2 Orçamento de Atenção (Attention Budget)

Enviar 400 chunks ao modelo não é viável nem recomendado. Pesquisas sobre o comportamento dos LLMs demonstram que:

1. **A atenção não é uniforme** — o modelo presta mais atenção ao início e ao fim do contexto
2. **Informações no meio são esquecidas** — o efeito *lost-in-the-middle* degrada significativamente respostas quando chunks relevantes estão no centro do contexto
3. **Mais contexto ≠ melhor resposta** — chunks irrelevantes competem com chunks relevantes pela atenção do modelo

**Número ótimo de chunks para queries corporativas típicas: 5 a 15**, selecionados por relevância e posicionados estrategicamente no prompt.

### 4.3 Efeito Lost-in-the-Middle

```
Posição do chunk no contexto vs. probabilidade de ser usado na resposta

Alta  ████████░░░░░░░░░░░░░░░░░░░░░░░░████████
      │        ↑ Início                Fim ↑  │
      │          do contexto        do contexto│
Baixa │              meio do contexto         │
      └────────────────────────────────────────
       Início                              Fim
```

**Estratégia de mitigação:** re-ranker neural que prioriza chunks de alta relevância para as posições de destaque (início e fim do contexto RAG), relegando chunks de suporte para o meio.

### 4.4 Competição por Atenção — Exemplo Real

**Sem Context Engineering (resultado ruim):**

```
[System Prompt longo com regras]    ← 3.000 tokens
[Histórico completo da conversa]    ← 5.000 tokens
[Chunk de wiki sobre frete]         ← 300 tokens
[Chunk de tabela sem cabeçalho]     ← 400 tokens  ← PROBLEMA
[Chunk de outra página de wiki]     ← 300 tokens
[Chunk de tabela sem cabeçalho]     ← 400 tokens  ← PROBLEMA
[Pergunta do usuário]               ← 50 tokens

Resultado: LLM alucina valores numéricos por não ter
           cabeçalho das colunas nos chunks de tabela
```

**Com Context Engineering (resultado correto):**

```
[System Prompt conciso]                        ← 800 tokens
[Tabela completa serializada com cabeçalhos]   ← 900 tokens
[Texto de política relacionada]                ← 300 tokens
[Pergunta do usuário]                          ← 50 tokens

Resultado: resposta precisa com os valores corretos
           e citação da fonte
```

### 4.5 Impacto por Tipo de Conteúdo

| Tipo de Conteúdo | Posição Ótima no Contexto | Risco Lost-in-Middle | Estratégia de Posicionamento |
|---|---|---|---|
| Tabelas com dados numéricos | Início | Crítico | Re-ranker posiciona no topo |
| Texto de políticas/processos | Qualquer | Moderado | Resumo hierárquico precede o chunk |
| Descrições de fluxograma | Início | Alto | Máximo 1 fluxograma por query |
| Dados de planilha (JSON) | Início | Crítico | JSON com cabeçalhos sempre presentes |
| Texto de wiki | Qualquer | Baixo | Posicionamento padrão |

---

## 5. Análise por Tipo de Fonte Documental

### 5.1 PDFs com Tabelas Complexas

| Dimensão | Detalhe |
|---|---|
| **Desafio técnico** | Extratores padrão serializam tabelas linha a linha, destruindo a semântica colunar. Tabelas com 15+ colunas perdem o cabeçalho ao serem fragmentadas em chunks. |
| **Impacto na qualidade** | O LLM recebe texto linearizado sem estrutura bidimensional. Perguntas que exigem cruzar duas dimensões da tabela resultam em respostas plausíveis, mas imprecisas. Alto risco de alucinação numérica. |
| **Riscos de indexação incorreta** | Chunks com parte de uma linha sem cabeçalho → valores numéricos idênticos em colunas distintas (ex: CEP, peso, preço) são indistinguíveis. |
| **Estratégia de extração** | Camelot ou pdfplumber com detecção de bordas. Azure Document Intelligence para tabelas complexas. Serialização como Markdown ou JSON com cabeçalhos explícitos repetidos. |
| **Estratégia de chunking** | Table-aware chunking: cada linha da tabela prefixada com o cabeçalho completo. Tabelas grandes: JSON estruturado como documento único com metadados de dimensões. |
| **Complexidade** | **Alta** |
| **Risco residual** | **Médio** — tabelas muito grandes ainda dependem de múltiplos chunks recuperados corretamente |

### 5.2 PDFs Escaneados (OCR)

| Dimensão | Detalhe |
|---|---|
| **Desafio técnico** | Documentos escaneados são imagens — sem camada de texto. Pipeline exige OCR antes de qualquer extração. Qualidade varia com resolução, rotação e ruído. |
| **Impacto na qualidade** | Erros de OCR em valores numéricos (ex: "l" vs "1", "O" vs "0") produzem dados corrompidos indexados como verdade. O erro é silencioso — o modelo responde com confiança sobre informações erradas. |
| **Riscos de indexação incorreta** | Taxa de erro de 5% em 500 campos numéricos = 25 erros indexados. Documentos com baixa qualidade geram embeddings semanticamente imprecisos — o retrieval não recupera o documento correto. |
| **Estratégia de extração** | Pré-processamento (deskew, denoising); OCR com Azure AI Document Intelligence ou Google Document AI; pós-processamento com regex para validar formatos esperados; score de confiança do OCR como metadado. |
| **Estratégia de chunking** | Chunking padrão somente após validação. Metadado `ocr_confidence_score` por chunk — chunks com confiança abaixo do threshold recebem penalidade no re-ranking. |
| **Complexidade** | **Alta** |
| **Risco residual** | **Alto** — documentos de baixa qualidade podem ser irrecuperáveis sem revisão humana |

### 5.3 Fluxogramas Embutidos como Imagens

| Dimensão | Detalhe |
|---|---|
| **Desafio técnico** | Fluxogramas são conteúdo semântico denso codificado como pixels — invisíveis para pipelines de RAG baseados em texto. |
| **Impacto na qualidade** | O assistente responde perguntas sobre processos sem acesso ao fluxograma, usando apenas texto circundante. Respostas incompletas sobre processos críticos. |
| **Riscos de indexação incorreta** | Não se trata de indexação incorreta, mas de não-indexação: o conteúdo simplesmente não existe no índice. O usuário recebe "não encontrei informação" quando ela existe em formato visual. |
| **Estratégia de extração** | Pipeline multimodal: modelo vision (Claude Sonnet 4.6, GPT-4o) gera descrição textual estruturada — nós, arestas, condições e decisões. Combinar com contexto textual circundante (legenda, parágrafo adjacente). |
| **Estratégia de chunking** | Cada fluxograma = 1 chunk semântico unitário (descrição gerada + contexto). Não fragmentar — processo parcial é mais perigoso que ausência de resposta. |
| **Complexidade** | **Alta** |
| **Risco residual** | **Médio** — fluxogramas com notação avançada podem ser descritos de forma imprecisa; validação humana recomendada para processos críticos |

### 5.4 Wiki Confluence com Links Internos e Macros

| Dimensão | Detalhe |
|---|---|
| **Desafio técnico** | Links internos criam dependências entre páginas que se perdem na indexação isolada. Macros como `{include}`, `{excerpt}` e `{jira-issues}` renderizam conteúdo dinâmico que aparece como texto literal ou é omitido na exportação. |
| **Impacto na qualidade** | Chunks de páginas dependentes chegam ao LLM incompletos. Macros `{include}` ignoradas criam lacunas de informação — o modelo vê onde havia conteúdo, mas não o conteúdo em si. |
| **Riscos de indexação incorreta** | Referências a "veja a página XYZ" sem que XYZ esteja no contexto → resposta aparentemente completa, mas fundamentalmente incompleta. |
| **Estratégia de extração** | Confluence REST API (não exportação HTML/PDF) para resolução server-side de macros. Resolução recursiva de macros `{include}` e `{excerpt}` na ingestão. Construção de grafo de dependências entre páginas. |
| **Estratégia de chunking** | Graph-aware chunking: páginas fortemente acopladas agrupadas em documento lógico antes do chunking. Hierarquia (Space > Page > Child Page) como metadados. Chunking por seção (H2/H3). |
| **Complexidade** | **Alta** |
| **Risco residual** | **Médio** — macros com integrações externas permanecem irresolvíveis; conteúdo dinâmico exige re-indexação frequente |

### 5.5 Planilhas com Fórmulas Interdependentes

| Dimensão | Detalhe |
|---|---|
| **Desafio técnico** | Planilhas são modelos computacionais, não documentos de texto. Fórmulas dependem de outras abas e de contexto de execução. Valores calculados são estados que mudam com dados de entrada. |
| **Impacto na qualidade** | O modelo não executa fórmulas — responde com valores estáticos capturados no momento da indexação. Queries computacionais ("qual o custo se o volume for X?") são impossíveis via RAG puro. |
| **Riscos de indexação incorreta** | Fórmula indexada como texto → LLM retorna a fórmula como resposta. Valores de abas dependentes sem contexto da aba fonte → números sem semântica. Dados desatualizados indexados como verdade absoluta. |
| **Estratégia de extração** | openpyxl para extrair valores calculados (não fórmulas). Para análises dinâmicas: Code Interpreter como tool do LLM. Documentar modelo de dados (colunas, unidades, fonte) como metadados enriquecidos. |
| **Estratégia de chunking** | Schema-first chunking: (a) dicionário de dados separado, (b) dados tabulares por aba, (c) metadados de dependências entre abas. Para tabelas de referência críticas: expor via API de consulta direta em vez de RAG. |
| **Complexidade** | **Alta** |
| **Risco residual** | **Alto** (RAG puro) → **Médio** (arquitetura híbrida com Code Interpreter/API) |

### 5.6 Matriz Consolidada por Fonte

| Fonte | Complexidade | Risco Pré-Mitigação | Risco Residual | Viabilidade RAG Puro |
|---|---|---|---|---|
| PDFs com texto simples | Baixa | Baixo | Baixo | ✅ Alta |
| PDFs com tabelas complexas | Alta | Crítico | Médio | ⚠️ Parcial |
| PDFs escaneados (OCR) | Alta | Crítico | Médio-Alto | ⚠️ Condicional |
| Fluxogramas em imagens | Alta | Crítico | Médio | ⚠️ Apenas com multimodal |
| Wiki Confluence | Alta | Alto | Médio | ✅ Com API e graph chunking |
| Planilhas com fórmulas | Alta | Crítico | Alto → Médio | ❌ Exige arquitetura híbrida |

---

## 6. Arquitetura Proposta

### 6.1 Visão Geral

```
╔══════════════════════════════════════════════════════════════╗
║                    FONTES DE DADOS                           ║
║          SharePoint │ Confluence │ Planilhas                 ║
╚══════════════════════════════════╦═══════════════════════════╝
                                   ║
╔══════════════════════════════════▼═══════════════════════════╗
║                  PIPELINE DE INGESTÃO                        ║
║   Extração → Limpeza → Chunking → Embedding → Indexação      ║
╚══════════════════════════════════╦═══════════════════════════╝
                                   ║
          ╔════════════════════════▼════════════════════════╗
          ║              BANCO VETORIAL + BM25               ║
          ║     Qdrant / pgvector + Elasticsearch            ║
          ║     Metadados: fonte, área, data, tipo           ║
          ╚════════════════════════╦════════════════════════╝
                                   ║
╔══════════════════════════════════▼═══════════════════════════╗
║                   CAMADA DE RETRIEVAL                        ║
║   Query Embedding → Busca Híbrida → Re-ranking → Filtros     ║
║         (semântica + BM25 + filtro por metadado)             ║
╚══════════════════════════════════╦═══════════════════════════╝
                                   ║
╔══════════════════════════════════▼═══════════════════════════╗
║                CAMADA DE GERAÇÃO (LLM)                       ║
║    [System Prompt] + [Chunks rankeados] + [Query]            ║
║    Claude Sonnet 4.6 / GPT-4o                                ║
╚══════════════════════════════════╦═══════════════════════════╝
                                   ║
╔══════════════════════════════════▼═══════════════════════════╗
║                     INTERFACE                                ║
║          Chat Web │ Slack Bot │ Microsoft Teams              ║
╚══════════════════════════════════════════════════════════════╝
```

### 6.2 Decisões Técnicas e Justificativas

| Componente | Escolha Recomendada | Alternativa | Justificativa |
|---|---|---|---|
| LLM principal | Claude Sonnet 4.6 | GPT-4o | Melhor custo-benefício, janela de 128k tokens, forte em português |
| Embedding | Voyage AI `voyage-large-2` | OpenAI `text-embedding-3-large` | Superior em domínios técnicos e português corporativo |
| Banco vetorial | Qdrant (self-hosted) | pgvector | Performance, filtros por metadado, sem vendor lock-in |
| Busca híbrida | Qdrant + BM25 nativo | Elasticsearch | Evita infraestrutura adicional; BM25 integrado ao Qdrant |
| Re-ranker | Cohere Rerank v3 | BGE-Reranker-Large | Melhor precisão cross-lingual; latência aceitável (~200ms) |
| Orquestração | LangChain / LlamaIndex | Framework próprio | Abstração de LLM evita vendor lock-in |
| Cache semântico | GPTCache / Redis | Cache simples | Reduz 20–40% do custo de LLM em queries frequentes |

### 6.3 Arquitetura Híbrida para Conteúdo Computacional

Para planilhas com lógica computacional e queries que exigem cálculos dinâmicos, RAG puro é insuficiente. A solução é um **agente com tools**:

```
Pergunta do usuário
        │
        ▼
   Classificador de intent
        │
        ├── Query textual (política, processo, norma)
        │         └──► RAG padrão
        │
        ├── Query numérica estática (tabela de frete, preços)
        │         └──► Tool: consulta direta ao banco estruturado
        │
        └── Query computacional (simulações, cálculos)
                  └──► Tool: Code Interpreter (pandas/Python em sandbox)
```

### 6.4 Modelo de Controle de Acesso (RBAC)

```
Usuário autenticado (SSO corporativo)
        │
        ▼
   Perfil de acesso (área, cargo, permissões)
        │
        ▼
   Filtro de coleção no banco vetorial
        │
        ├── RH: acesso apenas a coleção "rh_publico"
        ├── Financeiro: coleção "financeiro" + "corporativo"
        ├── TI: todas as coleções técnicas
        └── Admin: acesso irrestrito

Documentos sensíveis (jurídico, financeiro confidencial)
   └──► Coleção isolada com permissão explícita
```

---

## 7. Estratégias de Ingestão, Chunking e Retrieval

### 7.1 Pipeline de Ingestão Detalhado

```
Documento de entrada
        │
        ▼
[ETAPA 1] EXTRAÇÃO POR TIPO
  ├── PDF com texto:     pdfplumber + PyMuPDF
  ├── PDF escaneado:     Azure AI Document Intelligence (OCR)
  ├── PDF com imagens:   Extração de imagens + Vision LLM
  ├── DOCX/PPTX:         python-docx / python-pptx
  ├── HTML/Web:          BeautifulSoup + remoção de boilerplate
  └── Confluence:        REST API com resolução de macros
        │
        ▼
[ETAPA 2] LIMPEZA E NORMALIZAÇÃO
  ├── Remoção de cabeçalhos/rodapés repetitivos
  ├── Normalização de encoding (UTF-8)
  ├── Detecção de idioma
  ├── Score de qualidade (docs abaixo do threshold → revisão manual)
  └── Deduplicação por hash de conteúdo
        │
        ▼
[ETAPA 3] CHUNKING (estratégia por tipo de conteúdo)
        │
        ▼
[ETAPA 4] ENRIQUECIMENTO DE METADADOS
  ├── fonte, URL de origem, autor, data de criação
  ├── data de modificação, área responsável, tipo de documento
  ├── ocr_confidence_score (para docs escaneados)
  └── versão do documento
        │
        ▼
[ETAPA 5] GERAÇÃO DE EMBEDDINGS
  └── Modelo: voyage-large-2 (1024 dimensões)
        │
        ▼
[ETAPA 6] INDEXAÇÃO
  ├── Vetores → Qdrant
  ├── Texto → BM25 (Qdrant nativo)
  └── Metadados → PostgreSQL
```

### 7.2 Estratégias de Chunking por Tipo de Conteúdo

| Tipo de Conteúdo | Tamanho do Chunk | Overlap | Estratégia |
|---|---|---|---|
| Texto corrido (políticas, manuais) | 400–600 tokens | 15% | Recursive splitting por parágrafo |
| Tabelas simples | 1 linha + cabeçalho | 0% | Table-aware com cabeçalho repetido |
| Tabelas complexas (15+ colunas) | Documento JSON completo | — | Unitário, sem fragmentação |
| FAQs e Q&A | Pergunta + resposta completa | 0% | Unitário — não fragmentar |
| Documentos técnicos longos | Por seção (H2/H3) | 10% | Hierárquico com metadado de seção |
| Fluxogramas (descrição gerada) | Descrição completa | 0% | Unitário — processo não pode ser fragmentado |
| Conteúdo curto (< 200 tokens) | Documento inteiro | — | Sem chunking |
| Páginas Confluence interligadas | Por cluster de dependência | 10% | Graph-aware chunking |

**Princípio orientador do chunking:** o chunk deve ser autossuficiente. Um leitor humano sem acesso ao documento original deve conseguir entender o chunk de forma isolada.

### 7.3 Pipeline de Retrieval e Busca Híbrida

```
Query do usuário
        │
        ├──► [Embedding da query] ──► Busca vetorial (top-20 por cosine similarity)
        │                                        │
        └──► [BM25 da query] ────► Busca keyword (top-20 por BM25 score)
                                                 │
                          ┌──────────────────────┘
                          ▼
              Fusão via RRF (Reciprocal Rank Fusion)
                          │
                          ▼
          Re-ranker neural — Cohere Rerank v3 (top 5–10)
                          │
                          ▼
              Filtro por metadado (área, data, tipo, permissão)
                          │
                          ▼
             Context Engineering: posicionamento dos chunks
             (relevantes ao início e fim; suporte ao meio)
                          │
                          ▼
                    Chunks finais → LLM
```

**Por que busca híbrida?**

A busca semântica captura intenção e sinônimos, mas falha em queries exatas (números, nomes próprios, versões). A busca BM25 captura keywords exatas, mas falha em paráfrases. A fusão via RRF supera ambas individualmente em **15–30% de precisão** em benchmarks de domínio corporativo.

---

## 8. Estimativas de Volume, Esforço e Custos

### 8.1 Estimativa de Volume Documental

| Fonte | Estimativa de Documentos | Chunks Estimados | Vetores no Índice |
|---|---|---|---|
| SharePoint (PDFs texto) | 5.000–15.000 | 50.000–200.000 | 50k–200k |
| SharePoint (PDFs escaneados) | 2.000–5.000 | 20.000–70.000 | 20k–70k |
| Confluence (páginas) | 3.000–10.000 | 30.000–100.000 | 30k–100k |
| Planilhas | 500–2.000 | 5.000–20.000 | 5k–20k |
| **Total estimado** | **10.500–32.000** | **105.000–390.000** | **105k–390k** |

> Qdrant suporta dezenas de milhões de vetores — o volume estimado está confortavelmente dentro da capacidade da infraestrutura proposta.

### 8.2 Fases de Implementação e Esforço

| Fase | Descrição | Duração | Equipe |
|---|---|---|---|
| **Fase 0** | Auditoria e curadoria da base documental | 3–4 semanas | 1 analista + 1 engenheiro |
| **Fase 1** | Pipeline de ingestão (2 fontes principais) | 6–8 semanas | 2 engenheiros backend |
| **Fase 2** | Infraestrutura vetorial + retrieval híbrido | 4–6 semanas | 1 eng. ML + 1 backend |
| **Fase 3** | Integração LLM + prompt engineering | 3–4 semanas | 1 eng. ML + 1 especialista LLM |
| **Fase 4** | Interface (chat web ou Slack/Teams) | 3–4 semanas | 1 frontend + 1 backend |
| **Fase 5** | Testes, avaliação e ajustes | 4 semanas | Squad completo |
| **Total** | | **~6 meses (MVP completo)** | **4–5 pessoas** |

### 8.3 Equipe Necessária

| Papel | Responsabilidades | Dedicação |
|---|---|---|
| Tech Lead / Arquiteto de IA | Pipeline, qualidade, decisões técnicas | 100% |
| Engenheiro Backend (×2) | Ingestão, APIs, infraestrutura, conectores | 100% |
| Engenheiro ML | Embeddings, retrieval, avaliação, re-ranker | 100% |
| Desenvolvedor Frontend | Interface do usuário, integração | 100% |
| Analista de Conteúdo | Curadoria documental, testes de qualidade | 50–100% |

> O analista de conteúdo é frequentemente omitido do planejamento e é um dos papéis mais críticos para o sucesso. Sem curadoria da base documental, a qualidade do assistente nunca atinge o nível esperado.

### 8.4 Estimativa de Custos Operacionais Mensais (Produção)

| Componente | Estimativa Mensal | Observações |
|---|---|---|
| LLM (Claude Sonnet 4.6) | $800–$2.000 | ~500 queries/dia, ~1.500 tokens/query média |
| Embedding (Voyage AI) | $50–$150 | Re-indexação incremental + queries |
| Re-ranker (Cohere Rerank v3) | $100–$300 | ~500 queries/dia |
| Banco vetorial (Qdrant Cloud) | $200–$500 | Até 5M vetores |
| Infraestrutura (compute, API gateway) | $300–$600 | Inclui monitoramento |
| Cache semântico (Redis) | $50–$100 | Reduz 20–40% do custo de LLM |
| **Total estimado** | **$1.500–$3.650/mês** | ~$1,25–$3,00/usuário ativo/mês |

> **Otimizações possíveis:** cache semântico para queries frequentes reduz custo de LLM em 20–40%; rate limiting por usuário evita uso descontrolado; modelo menor (Haiku 4.5) para queries simples com roteamento automático.

### 8.5 ROI Estimado

| Métrica | Antes | Depois | Ganho |
|---|---|---|---|
| Tempo médio de busca de informação | 45 min/dia/colaborador | 10 min/dia | 35 min economizados |
| Colaboradores impactados (estimativa) | — | 600 usuários ativos | — |
| Economia mensal (custo/hora ~R$50) | — | — | **~R$315.000/mês** |
| Custo mensal da solução | — | — | **~R$18.000–R$22.000/mês** |
| **ROI estimado** | | | **~14x** |

---

## 9. Riscos Técnicos e Estratégias de Mitigação

### 9.1 Matriz de Riscos

| Risco | Probabilidade | Impacto | Estratégia de Mitigação |
|---|---|---|---|
| Base documental desorganizada / desatualizada | Alta | Alto | Auditoria obrigatória na Fase 0. Política de governança documental como pré-requisito do projeto. |
| Chunks sem contexto suficiente (respostas truncadas) | Média | Alto | Chunking hierárquico com overlap. Testes sistemáticos com queries reais antes do go-live. |
| Alucinação do LLM quando contexto não é suficiente | Média | Alto | Instrução explícita no system prompt: "se não encontrar no contexto recuperado, declare que não possui a informação". Threshold mínimo de relevância no retrieval. |
| Dados sensíveis indexados sem controle de acesso | Média | Crítico | RBAC por documento e coleção desde o design inicial. Segregação obrigatória de documentos confidenciais (RH, jurídico, financeiro). |
| Baixa adoção por falta de confiança nas respostas | Alta | Alto | Sempre exibir fonte da resposta com link ao documento original. UI que indica "baseado em [documento X, seção Y]". Mecanismo de feedback por resposta. |
| Custo inesperado com LLM em alta escala | Baixa | Médio | Rate limiting por usuário. Cache semântico. Monitoramento de custo por usuário com alertas. |
| Respostas desatualizadas após mudança de política | Alta | Alto | Pipeline de re-indexação incremental com detecção de mudança (hash). Metadado de "última atualização" visível ao usuário. |
| Dependência de fornecedor de LLM (vendor lock-in) | Baixa | Médio | Abstrair o LLM via interface (LangChain/LlamaIndex). Troca de provider sem refatoração do pipeline. |
| Degradação de performance com crescimento da base | Baixa | Médio | Qdrant com sharding horizontal. Monitoramento de latência de retrieval com alertas de threshold. |
| OCR de baixa qualidade em documentos escaneados | Alta | Alto | Score de confiança do OCR como metadado. Threshold mínimo de qualidade para indexação. Processo de re-digitalização para documentos críticos abaixo do threshold. |

### 9.2 Limitações Que Não Devem Ser Ignoradas

> **Estes itens devem ser comunicados explicitamente aos stakeholders antes do início do projeto.**

1. **O assistente não é 100% preciso.** Qualidade das respostas é diretamente proporcional à qualidade dos documentos indexados.

2. **RAG não resolve problemas de documentação ruim.** Um assistente RAG sobre documentação desorganizada produz respostas desorganizadas com aparência de autoridade — o que é mais perigoso que não ter assistente.

3. **Planilhas com lógica computacional exigem arquitetura adicional.** Não é possível "calcular" via RAG puro — requer Code Interpreter ou API de consulta estruturada.

4. **Fluxogramas exigem processamento multimodal.** Sem pipeline específico, são invisíveis ao assistente.

5. **O assistente não substitui julgamento humano em decisões críticas.** Deve ser posicionado como ferramenta de suporte, não de autoridade.

---

## 10. Recomendação Técnica Final

### Recomendação: Implementação faseada com validação de valor em cada etapa

A implementação em fases reduz risco técnico, entrega valor incremental e cria pontos de decisão antes de escalar o investimento.

### 10.1 Roadmap de Implementação

```
MÊS 1-2: FUNDAÇÃO
  ├── Auditoria e curadoria da base documental (Fase 0)
  ├── Setup de infraestrutura (Qdrant, pipeline base)
  └── Conectores para as 2 fontes mais organizadas

MÊS 3: MVP (Fase 1 — Piloto Restrito)
  ├── Escopo: Confluence + PDFs de texto simples
  ├── Interface: Slack Bot
  ├── Sem histórico de conversa
  ├── Respostas com citação de fonte obrigatória
  └── VALIDAÇÃO: aceitação, qualidade, gaps documentais

MÊS 4-5: EXPANSÃO (Fase 2)
  ├── Adicionar SharePoint completo (com OCR e tabelas)
  ├── Re-ranker neural
  ├── Histórico de conversa
  ├── Controle de acesso por área (RBAC)
  └── VALIDAÇÃO: precisão, cobertura, custo operacional

MÊS 6: PRODUÇÃO (Fase 3)
  ├── Re-indexação incremental automática
  ├── Dashboard de uso e qualidade
  ├── Mecanismo de feedback do usuário
  ├── Integração SSO corporativo
  └── Documentação operacional e handoff
```

### 10.2 Critérios de Sucesso (Go/No-Go por Fase)

| Fase | Critério de Aprovação |
|---|---|
| MVP (Fase 1) | ≥70% das queries respondidas corretamente em testes com usuários reais |
| Expansão (Fase 2) | ≥80% de precisão, latência média < 5s, NPS > 40 |
| Produção (Fase 3) | Re-indexação < 24h após mudança de documento, 0 incidentes de acesso indevido |

### 10.3 Justificativa Técnica da Recomendação

A NovaTech reúne as condições ideais para o sucesso de um assistente RAG corporativo:

- **Base de usuários suficiente** (1.200 funcionários) para justificar o investimento e gerar dados de feedback para melhoria contínua
- **Problema real e mensurável** (tempo perdido em busca de informação) com ROI direto e calculável
- **Diversidade de fontes** que inviabiliza soluções mais simples (busca keyword pura)
- **Necessidade de rastreabilidade** que RAG atende nativamente

O risco do projeto não está na tecnologia — LLMs e RAG são tecnologias maduras e bem documentadas. O risco está na **governança documental**: o projeto só entrega valor proporcional à qualidade e organização dos documentos de entrada.

**A recomendação é iniciar com o menor escopo possível que ainda gere valor real, validar rapidamente, e escalar com base em evidências — não em premissas.**

---

## 11. Glossário

| Termo | Definição |
|---|---|
| **RAG** | Retrieval-Augmented Generation — arquitetura que combina busca em documentos indexados com geração de resposta por LLM |
| **LLM** | Large Language Model — modelo de linguagem de grande escala (ex: Claude, GPT-4) |
| **Embedding** | Representação vetorial numérica de um texto, que captura seu significado semântico |
| **Chunking** | Processo de dividir documentos em fragmentos menores para indexação e recuperação |
| **Re-ranker** | Modelo neural que re-ordena os chunks recuperados por relevância à query específica |
| **BM25** | Algoritmo de busca por relevância baseado em frequência de termos (keyword search) |
| **RRF** | Reciprocal Rank Fusion — algoritmo de fusão de rankings de múltiplas fontes de busca |
| **RBAC** | Role-Based Access Control — controle de acesso baseado em perfis e papéis |
| **Context Engineering** | Disciplina de otimizar o conteúdo, volume e posicionamento de informação na janela de contexto do LLM |
| **Lost-in-the-middle** | Fenômeno em que LLMs perdem atenção para informações posicionadas no meio de contextos longos |
| **OCR** | Optical Character Recognition — reconhecimento óptico de caracteres em documentos escaneados |
| **Janela de contexto** | Limite máximo de tokens que um LLM processa em uma única requisição |
| **Attention Budget** | Orçamento de atenção — quantidade de tokens disponíveis para contexto RAG após deduzir system prompt e histórico |
| **Graph-aware chunking** | Estratégia de chunking que considera dependências entre documentos antes de fragmentá-los |

---

*Documento gerado em Junho de 2026 · NovaTech · Arquitetura de IA Corporativa*
*Versão 1.0 — Para revisão técnica e aprovação de stakeholders*
