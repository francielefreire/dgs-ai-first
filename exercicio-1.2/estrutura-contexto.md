# 2. Estrutura de Contexto

## 2.1 Contexto Estático

O contexto estático contém informações que são enviadas em todas as requisições e raramente sofrem alterações.

| Componente               | Descrição                                                                           | Estimativa de Tokens |
| ------------------------ | ----------------------------------------------------------------------------------- | -------------------- |
| Identidade do Assistente | Define o papel do assistente como especialista em documentação interna da NovaTech  | ~30                  |
| Objetivo                 | Define que as respostas devem ser baseadas exclusivamente na documentação fornecida | ~20                  |
| Guardrails               | Regras de negócio e segurança definidas pelo Product Specialist                     | ~120                 |
| Prioridade entre Fontes  | Define o tratamento de conflitos entre documentos                                   | ~50                  |
| Formato de Resposta      | Estrutura obrigatória para apresentação das respostas e citações                    | ~40                  |
| **Total Estimado**       |                                                                                     | **~260 tokens**      |

## 2.2 Contexto Dinâmico

O contexto dinâmico varia a cada consulta realizada pelo usuário.

| Componente            | Descrição                                             | Estimativa de Tokens |
| --------------------- | ----------------------------------------------------- | -------------------- |
| Pergunta do Usuário   | Solicitação realizada pelo atendente                  | ~10 a 30             |
| Chunks Recuperados    | Trechos de documentação relevantes para a consulta    | ~100 a 500           |
| Histórico da Conversa | Interações anteriores utilizadas para manter contexto | Variável             |
| Dados da Consulta     | Informações específicas do cliente ou da operação     | Variável             |

## 2.3 Ordem de Prioridade do Contexto

A composição do contexto segue a seguinte ordem de prioridade:

1. System Prompt (identidade e regras do assistente)
2. Guardrails de negócio
3. Chunks recuperados da documentação
4. Histórico da conversa
5. Pergunta atual do usuário

Essa ordem garante que as regras de segurança e comportamento do assistente tenham prioridade sobre informações recuperadas dinamicamente.

## 2.4 Estratégia para Limite de Contexto

Caso o volume de informações ultrapasse o limite de contexto do modelo:

* Priorizar os chunks mais relevantes para a pergunta.
* Remover partes antigas do histórico da conversa.
* Manter sempre o System Prompt e os guardrails.
* Preservar apenas documentos diretamente relacionados à consulta atual.

Essa estratégia reduz o consumo de tokens sem comprometer a qualidade das respostas.
