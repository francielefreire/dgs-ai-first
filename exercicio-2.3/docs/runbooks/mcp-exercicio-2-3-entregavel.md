# Entregável — Exercício 2.3 (Skills para agentes)

Data: 20/06/2026

## 1) Árvore de skills proposta

```text
skills/
  foundation/
    api-contract-validation-observability/   <- Skill base (SKILL.md)
    error-handling/
    env-and-config/
    typescript-conventions/
    project-structure/
  domain/
    azure-functions-endpoint/
    azure-ai-search-integration/
    prompt-builder-and-response-validator/
    testing-patterns/
    react-components/
  artifact/
    create-rag-endpoint/
    create-integration-test/
    create-react-card/
    create-query-task-spec/
```

### Justificativa de coerência com o projeto

- A camada **Foundation** cobre padrões transversais já exigidos no cenário (`TypeScript`, `Zod`, `pino`, config por env, tratamento de erro).
- A camada **Domain** mapeia os blocos reais do repositório (`src/functions`, `src/services`, `src/web`, `tests`).
- A camada **Artifact** oferece receitas de geração repetíveis para os artefatos mais frequentes do time (endpoint, testes, componentes e specs de tasking).

---

## 2) Mapeamento de criação/consumo por skill

| Skill | Descrição (frase-ativação) | Quem cria | Quem consome (papel + agentes) | Frequência |
|---|---|---|---|---|
| `foundation/api-contract-validation-observability` | “Quando criar/alterar endpoint, aplique contrato Zod, logging estruturado e error handling padrão.” | Tech Lead + Staff Backend | Backend Engineer (`Copilot`), QA Engineer (`Copilot`), SRE (`Copilot`) | **Alta** (todo endpoint) |
| `foundation/error-handling` | “Ao capturar erro, padronize status code, payload seguro e log com contexto.” | Tech Lead + SRE | Backend Engineer (`Copilot`), QA (`Copilot`) | **Alta** |
| `foundation/env-and-config` | “Ao adicionar dependência externa, registre env vars, validação e fallback.” | SRE + Tech Lead | Backend (`Copilot`), Data/AI Engineer (`Copilot`) | **Média-Alta** |
| `foundation/typescript-conventions` | “Ao escrever TypeScript, siga naming, tipagem explícita e imports do projeto.” | Tech Lead | Todo time dev (`Copilot`) | **Alta** |
| `foundation/project-structure` | “Ao criar arquivo novo, siga a estrutura oficial por camada.” | Tech Lead | Todo time dev (`Copilot`, `Claude`) | **Alta** |
| `domain/azure-functions-endpoint` | “Criar endpoint HTTP Azure Functions v4 com rota, authLevel e handler padrão.” | Backend Lead | Backend Engineer (`Copilot`) | **Alta** |
| `domain/azure-ai-search-integration` | “Integrar busca top-k no Azure AI Search com filtro e metadados.” | Data/AI Lead | Backend + Data/AI (`Copilot`) | **Média** |
| `domain/prompt-builder-and-response-validator` | “Montar prompt com budget e validar output com schema.” | AI Engineer + Tech Lead | Backend/AI Engineer (`Copilot`) | **Média-Alta** |
| `domain/testing-patterns` | “Escrever teste unit/integration com mocks consistentes do projeto.” | QA Lead + Tech Lead | QA Engineer (`Copilot`), Backend (`Copilot`) | **Alta** |
| `domain/react-components` | “Criar componente React seguindo organização e props tipadas.” | Frontend Lead | Frontend Engineer (`Copilot`) | **Média** |
| `artifact/create-rag-endpoint` | “Gerar esqueleto de endpoint RAG completo (handler, validator, services, tests).” | Tech Lead | Backend Engineer (`Copilot`) | **Média-Alta** |
| `artifact/create-integration-test` | “Gerar teste de integração para endpoint com mocks de serviços Azure.” | QA Lead | QA/Backend (`Copilot`) | **Média-Alta** |
| `artifact/create-react-card` | “Gerar card React reutilizável com tipagem e testes.” | Frontend Lead | Frontend (`Copilot`) | **Média** |
| `artifact/create-query-task-spec` | “Converter plan.md em tasks atômicas com critérios verificáveis.” | Product Specialist + Tech Lead | Product Specialist (`Claude`), Tech Lead (`Claude`) | **Média** |

---

## 3) Skill Foundation mais importante

A skill Foundation-base escolhida foi:

- `foundation/api-contract-validation-observability`

Motivo:
- é pré-requisito para todas as outras skills de backend/domain/artifact;
- define o “jeito oficial” de criar endpoints seguros e auditáveis;
- reduz retrabalho em review (contrato, erro, log, correlação, status code).

O arquivo `SKILL.md` foi criado em:

- `novatech-assistant/skills/foundation/api-contract-validation-observability/SKILL.md`

Ele contém:
- contexto de uso;
- regras prescritivas;
- exemplos DO/DON’T com código TypeScript realista para Azure Functions v4 + Zod + pino;
- anti-padrões comuns de geração por copilots/agentes.
