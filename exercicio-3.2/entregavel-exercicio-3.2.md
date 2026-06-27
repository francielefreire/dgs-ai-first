# Entregável — Exercício 3.2 (Revisão crítica de código gerado por IA)

## 1) Revisão própria (antes do Claude)

Problemas identificados no módulo original:

1. Uso de `as any` sem validação de entrada.
- Classificação: violação do AGENTS.md + bug potencial.
- Risco: payload inválido entra no sistema e pode quebrar persistência.

2. Uso de `console.log` no lugar de `pino`.
- Classificação: violação do AGENTS.md.
- Risco: logs sem estrutura, sem padronização operacional.

3. `require` dinâmico de `@azure/cosmos` dentro da função.
- Classificação: violação do AGENTS.md.
- Risco: perda de clareza de dependências e acoplamento em runtime.

4. Dado pessoal (`attendantEmail`) sendo logado.
- Classificação: problema de segurança/compliance.
- Risco: exposição de PII em logs.

5. Falta de tratamento de erro para JSON inválido, variável de ambiente ausente e falha no Cosmos.
- Classificação: bug potencial.
- Risco: falhas não tratadas e resposta incorreta para cliente.

## 2) Revisão do Claude (segunda revisão)

Pontos convergentes com a revisão própria:
- Entrada deve ser validada com Zod e schema estrito.
- Logging deve usar pino e nunca expor e-mail de atendente.
- Import do Cosmos deve ser estático no topo.
- Deve haver tratamento explícito de erro com respostas HTTP adequadas.

Pontos complementares:
- Limitar tamanho de `comment` para evitar payloads excessivos.
- Garantir faixa válida para `rating` (1 a 5).

## 3) Comparação (humano vs Claude)

- Concordância alta nos riscos críticos e nas violações do AGENTS.md.
- O Claude adicionou reforços úteis de robustez de payload (limite de `comment`, faixa de `rating`), incorporados no código final.

## 4) Código reescrito (Copilot)

Arquivo corrigido:
- `/src/functions/feedback/handler.ts`

Correções aplicadas no código final:
- Schema Zod estrito para entrada (`feedbackSchema`).
- Remoção de `any`.
- `pino` para logging estruturado.
- Sem log de PII (não registra `attendantEmail`).
- Import estático de `CosmosClient`.
- Tratamento de erro para JSON inválido, validação de payload e falhas de persistência.
- Respostas HTTP coerentes: 400 (payload inválido), 500 (erro interno), 200 (sucesso).
