# Exercício 2.1 — Evidências de Execução (local)

## Contexto

- Repositório: `novatech-assistant`
- Ambiente: local
- Objetivo: comprovar leitura de docs, recuperação de chunk e consulta ao Git

## Evidência A — Leitura de documentação (`docs/novatech`)

### Comando

```bash
ls docs/novatech
```

### Saída observada

```text
anexo-a-documentacao-simulada-novatech.md
FAQ-atendimento.md
POL-001-politica-devolucao.md
PROC-042-frete-especial-v1.md
PROC-042-v2-frete-especial-revisado.md
SLA-2024-tabela-sla-clientes.md
```

### Comando

```bash
sed -n '1,40p' docs/novatech/POL-001-politica-devolucao.md
```

### Resultado

Trecho lido com sucesso contendo título, versão e regras de devolução da POL-001 (incluindo seção 3.1 e 3.2).

## Evidência B — Recuperação de chunk relevante (`data/retrieval-corpus`)

Pergunta de referência (Anexo B): **"Frete para 600kg para Manaus?"**

### Comando

```bash
grep -n "Frete para 600kg para Manaus\|PROC-042v2-B\|PROC-042v2-A" data/retrieval-corpus/chunks-referencia-rag.md
```

### Saída observada

```text
51:**Chunk PROC-042v2-A** — Seção 2: Fórmula atualizada
54:**Chunk PROC-042v2-B** — Seção 2.1: Multiplicadores regionais atualizados
116:| "Frete para 600kg para Manaus?" | PROC-042v2-B, PROC-042v2-A | PROC-042-B (versão antiga — risco de contradição) |
```

### Validação

- Chunks recuperados batem com o gabarito do mapa de cobertura do Anexo B: `PROC-042v2-B` e `PROC-042v2-A`.

## Evidência C — Consulta Git local (histórico/diff/branch)

### Comando

```bash
git status --short && echo '---' && git branch --show-current && echo '---' && git log --oneline -n 5
```

### Saída observada

```text
---
main
---
05c0687 (HEAD -> main) chore: bootstrap novatech-assistant
```

### Interpretação

- `status`, `branch` e `log` confirmam acesso ao estado e histórico Git local.

## Conclusão

- Evidência de leitura de docs: **ok**
- Evidência de recuperação de chunk: **ok**
- Evidência de consulta Git: **ok** (estado/diff/branch/histórico)
