# Exercício 2.1 — Entregável MCP (NovaTech Assistant)

## Premissas obrigatórias atendidas

- Apenas MCP Servers locais e gratuitos.
- Sem APIs pagas e sem serviços externos.
- Operação integral em ambiente local.
- Aplicação de menor privilégio por escopo.
- Sem acesso ao workspace inteiro.
- Sem incluir `.env`, `node_modules`, diretórios do usuário ou caminhos de sistema.

## Mapeamento de necessidades → MCP Servers

| Necessidade | MCP Server | Ferramentas Esperadas | Consumidor | Escopo/Pastas | Permissão | Justificativa |
|---|---|---|---|---|---|---|
| Ler e escrever código | filesystem-code | **Tools:** list/read/write/edit/move. **Resources:** arquivos do escopo. **Prompts:** não aplicável no server de filesystem. | Devs (Copilot/Claude Code), Tech Lead | `./src`, `./specs`, `./skills`, `./prompts`, `./tests`, `./infra`, `./docs/adr`, `./docs/runbooks` | Leitura/Escrita | Escopo mínimo para implementação e manutenção técnica sem abrir `./docs/novatech` nem `./data/retrieval-corpus` para escrita. |
| Ler documentação de negócio | filesystem-docs | **Tools:** list/read. **Resources:** markdowns de negócio. **Prompts:** n/a | Product Specialist, QA, Agentes de análise | `./docs/novatech` | Leitura | Isola a fonte de verdade de negócio em escopo dedicado, evitando acesso amplo ao repositório. |
| Consultar corpus RAG local | filesystem-corpus | **Tools:** list/read. **Resources:** chunks do corpus. **Prompts:** n/a | Agente de RAG, QA, avaliação de prompt/retrieval | `./data/retrieval-corpus` | Leitura | Mantém retrieval desacoplado de código e reduz risco de alteração acidental dos chunks. |
| Consultar histórico Git | git | **Tools:** status/log/show/blame/branch/diff (conforme implementação). **Resources:** metadados do repositório local. **Prompts:** n/a | Devs, Tech Lead, revisão técnica | Repositório local `.` | Leitura | Substitui dependência de GitHub remoto por histórico local auditável. |
| Consultar diff da branch atual | git | **Tools:** diff/status/show. **Resources:** estado local da árvore Git. **Prompts:** n/a | Devs, Tech Lead, QA técnico | Repositório local `.` | Leitura | Permite revisão de mudanças e troubleshooting sem ampliar permissões de filesystem. |
| Memória persistente de decisões | memory | **Tools:** criar/consultar entidades e relações. **Resources:** grafo de memória local. **Prompts:** templates de consulta (quando cliente suportar). | Todos os papéis/agents | Namespace local do projeto `novatech-assistant` | Leitura/Escrita | Guarda linguagem ubíqua e decisões sem serviço externo, com persistência local. |
| Descobrir padrões e conhecimento do projeto | memory + filesystem-code | **Tools (memory):** busca semântica de fatos. **Tools (filesystem):** leitura de specs/skills/prompts. | Copilot/Claude em onboarding e geração assistida | `memory namespace` + `./skills`, `./specs`, `./prompts` | Leitura (filesystem), Leitura/Escrita (memory) | Combina fonte documental local e memória incremental para reduzir respostas genéricas. |
| Explorar capacidades MCP em laboratório | everything | **Tools/Resources/Prompts:** superfícies de referência do server. | Tech Lead (POC/onboarding) | Sem pastas de negócio/código acopladas | Leitura | Útil para testes de integração MCP; manter fora do fluxo principal de produção. |
| Persistência tabular local (opcional) | sqlite | **Tools:** query/insert/select (conforme server). **Resources:** banco local. **Prompts:** n/a | QA, análise, relatórios internos | `./data/mcp-local.db` (arquivo local dedicado) | Leitura/Escrita controlada | Complementa memory com consultas determinísticas locais, sem serviços externos. |

## Disponibilidade dos servers (público vs custom)

| MCP Server | Tipo | Situação no projeto |
|---|---|---|
| `filesystem` | Público (reference server) | Utilizado em 3 instâncias (`filesystem-code`, `filesystem-docs`, `filesystem-corpus`) com escopo mínimo. |
| `git` | Público (reference/community server) | Utilizado localmente para histórico e diff do repositório. |
| `memory` | Público (reference server) | Utilizado para memória persistente local do projeto. |
| `everything` | Público (reference server) | Utilizado apenas para laboratório/onboarding de MCP. |
| `sqlite` | Público/comunitário (opcional) | Mapeado como opcional; não ativado no `mcp.json` atual. |
| Azure AI Search | Substituição local nesta fase | Necessidade coberta por `filesystem-corpus` (chunks locais em `./data/retrieval-corpus`). |
| Azure OpenAI | Fora do escopo MCP local desta fase | Não configurado como MCP server; fase atual foca acesso local a artefatos e contexto. |
| Azure DevOps | Substituição local nesta fase | Necessidades de tracking/auditoria operacionalmente cobertas por `git` + documentação local. |
| Confluence | Substituição local nesta fase | Necessidade coberta por `filesystem-docs` em `./docs/novatech` (read-only no workflow). |

## Aderência a Least Privilege (concreta)

1. Separação por função de acesso:
   - `filesystem-code`: somente áreas de engenharia.
   - `filesystem-docs`: somente docs de negócio.
   - `filesystem-corpus`: somente corpus RAG.
2. Sem escopo para raiz do workspace completo.
3. Sem inclusão de caminhos sensíveis (`.env`, `node_modules`, home do usuário, OS).
4. Acesso Git isolado no server `git`, evitando ampliar `filesystem` para metadata Git.

## Avaliação de segurança e mitigação por server

### 1) filesystem-code

- **Riscos:** alteração indevida de código/infra; criação de arquivos maliciosos.
- **Excesso potencial:** incluir pastas além do necessário (ex.: raiz inteira).
- **Mitigação:** escopo mínimo já aplicado; revisão humana obrigatória antes de merge; policy de branch + CI.

### 2) filesystem-docs

- **Riscos:** mutação de documentação normativa; envenenamento de contexto.
- **Excesso potencial:** permissão de escrita em pasta que deveria ser fonte estável.
- **Mitigação:** tratar como read-only no workflow do agente + proteção no SO (ACL/chmod para negar escrita ao usuário do processo).

### 3) filesystem-corpus

- **Riscos:** alteração de chunks e quebra de rastreabilidade de retrieval.
- **Excesso potencial:** escrita habilitada em corpus de referência.
- **Mitigação:** read-only no workflow + controle de integridade (hash/checksum) em CI local.

### 4) git

- **Riscos:** comandos destrutivos (reset/checkout indevido) se expostos.
- **Excesso potencial:** permitir ações mutáveis sem gate.
- **Mitigação:** restringir uso operacional a leitura (`status/log/diff/show/blame`) e exigir intervenção humana para operações mutáveis.

### 5) memory

- **Riscos:** persistência de fatos errados; vazamento de dado sensível no grafo.
- **Excesso potencial:** namespace compartilhado entre projetos.
- **Mitigação:** namespace exclusivo do projeto; política de curadoria/expiração; revisão periódica de memória.

### 6) sqlite (opcional)

- **Riscos:** injeção por query livre; armazenamento de segredo indevido.
- **Excesso potencial:** banco em caminho amplo com acesso geral.
- **Mitigação:** banco dedicado em `./data`; schema mínimo; não armazenar credenciais; backups locais controlados.

### 7) everything

- **Riscos:** superfície ampla e imprevisível para operação de rotina.
- **Excesso potencial:** uso em produção sem necessidade.
- **Mitigação:** habilitar somente em POC/laboratório; desabilitar em fluxo padrão do time.

## Configuração alvo (`.mcp/mcp.json`)

A configuração ativa deve manter o recorte por domínio com permissões mínimas de escopo:
- `filesystem-code`
- `filesystem-docs`
- `filesystem-corpus`
- `git`
- `memory`
- `everything`

Observação: o server `filesystem` não impõe read-only por si só em todos os clientes; o controle de escrita deve ser reforçado por política de execução do agente e permissões do sistema operacional.
