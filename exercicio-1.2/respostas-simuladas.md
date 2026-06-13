# Respostas Simuladas — Assistente NovaTech (RAG)

**Exercício:** 1.2 — Validação de Comportamento do System Prompt  
**Data:** Junho 2026  
**System Prompt utilizado:** system-prompt-v1.md  
**Documentos consultados:** POL-001, SLA-2024, PROC-042-v2

---

## Query 1 — "Qual o prazo de devolução para carga perigosa?"

**Resposta:** Cargas perigosas classificadas nas classes 1 a 6 da ANTT não são elegíveis para devolução pelo processo padrão. Não há prazo definido para esse tipo de carga.

**Detalhes/condições:** O processo padrão de 7 dias úteis não se aplica a explosivos (classe 1), gases (classe 2), líquidos inflamáveis (classe 3), sólidos inflamáveis (classe 4), oxidantes e peróxidos (classe 5) e substâncias tóxicas ou infectantes (classe 6). O cliente deve contatar o setor de Gestão de Riscos (ramal 4500) para tratamento individual.

**Fonte:** POL-001, seção 3.2 — Diretoria de Operações, versão 3.1 (15/01/2024)

---

## Query 2 — "Meu cliente é Gold, qual o SLA de resolução?"

**Resposta:** Para clientes Gold, o SLA de resolução é de até 24 horas úteis para chamados gerais e até 4 horas para incidentes críticos.

**Detalhes/condições:**
- O relógio de SLA para chamados gerais pausa fora do horário comercial (08h–18h, dias úteis).
- Para incidentes críticos de clientes Gold, o relógio **não pausa** — corre 24/7.
- Um incidente é classificado como crítico quando, por exemplo: carga com valor acima de R$ 100.000 está com status desconhecido há mais de 6 horas, ou qualquer irregularidade com carga perigosa.

**Fonte:** SLA-2024, seções 2 e 3 — Diretoria Comercial + Diretoria de Operações, versão 2024.1 (02/01/2024)

---

## Query 3 — "Quanto custa o frete para 600kg para Manaus?"

**Resposta:** O frete especial para 600 kg com destino a Manaus (região Norte) é calculado como: **Valor base × 1,8 × 1,0**.

**Detalhes/condições:** Não é possível informar o valor final porque o Valor base não consta nos documentos fornecidos — ele é publicado mensalmente na tabela de fretes. Os parâmetros aplicáveis são:

- Multiplicador regional (Norte): **1,8**
- Fator de peso (500 kg a 1.000 kg): **1,0**

Confirme o valor base na tabela comercial vigente antes de informar ao cliente.

> Atenção: se a carga for perigosa, este cálculo não se aplica. Cargas perigosas acima de 500 kg seguem a PROC-043 (Frete de Cargas Perigosas), que está em revisão pelo Compliance.

**Fonte:** PROC-042-v2, seções 2 e 2.1 — Diretoria Comercial, versão 2.0 (10/11/2023)

---

## Análise dos Comportamentos Observados

| Query | Chunks utilizados | Comportamento do assistente | Risco se guardrail falhar |
|---|---|---|---|
| Carga perigosa | POL-001, seção 3.2 | Abstenção correta de prazo + escalonamento para Gestão de Riscos | Inventar prazo inexistente (ex: "30 dias") |
| SLA Gold | SLA-2024, seções 2 e 3 | Resposta direta da tabela com detalhe sobre incidente crítico | Confundir tier Gold com Silver |
| Frete Manaus | PROC-042-v2, seções 2 e 2.1 | Resposta parcial com abstenção do valor base + alerta de carga perigosa | Calcular com valor base inventado |

### Padrões identificados

- **Abstenção com fonte:** nas queries 1 e 3, o assistente não possui todos os dados para responder completamente — e declara isso explicitamente, citando o trecho do documento que delimita o escopo conhecido.
- **Dado parcial útil:** na query 3, fornecer a fórmula e os multiplicadores já tem valor operacional, mesmo sem o valor base.
- **Condição de borda sinalizada:** na query 3, o assistente identificou proativamente que carga perigosa segue tabela diferente — informação presente no documento, não inferida.
