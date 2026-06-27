# Entregável — Exercício 3.1 (Harness Engineering)

## 1) Structured output com Zod

Schema definido em `/src/services/response-validator.ts` com formato fixo:

- `answer`: string obrigatória, com `trim` e tamanho mínimo 1.
- `source_document`: string obrigatória, com `trim` e tamanho mínimo 1.
- `confidence_score`: número obrigatório entre 0 e 1.

Reforço de validação:
- Uso de `.strict()` para rejeitar campos extras fora do contrato.

## 2) Implementação do response-validator com guardrails determinísticos

Função principal: `validateAssistantResponse(modelOutput)`.

Fluxo determinístico implementado:
1. Tenta parsear JSON quando a saída do modelo vem como string.
2. Valida no schema Zod antes de qualquer regra semântica.
3. Aplica guardrails de conteúdo.
4. Em qualquer falha, registra motivo em log e retorna resposta padrão segura.

Guardrail 1 (campo obrigatório):
- Se `source_document` estiver ausente/inválido, a resposta é rejeitada.

Guardrail 2 (carga perigosa + devolução):
- Se a resposta mencionar o tema, deve conter negativa explícita.
- Se houver afirmação de que devolução é possível para carga perigosa, a resposta é bloqueada.

Fallback seguro:
- Retorna mensagem padrão conservadora com fonte formal e confiança 0.

## 3) Code review rápido (Claude) com problemas reais e correções

### Problema 1
O detector de afirmação positiva podia gerar falso positivo quando a frase tinha negação, por exemplo: "não pode devolver".

Correção aplicada:
- Separação entre sinais positivos e negativos.
- Bloqueio só ocorre quando há sinal positivo sem sinal negativo correspondente.

### Problema 2
Cobertura linguística incompleta para variações de português em regras de devolução (ex.: "devoluções", "devolução não se aplica", "não há devolução").

Correção aplicada:
- Ampliação dos sinais de detecção no guardrail.
- Inclusão de variações de negação e afirmação para reduzir falso negativo.

## Distinção entre prompt e código (governança)

- Prompt: comportamento probabilístico (orienta o modelo).
- Código do validator: controle determinístico e bloqueante (garante política mínima, mesmo com erro do modelo).
