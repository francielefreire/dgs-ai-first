## Estratégia de Chunking

Para este protótipo foi adotada uma estratégia de chunking baseada em tamanho fixo com sobreposição (overlap).

### Configuração

* Tamanho do chunk: 500 caracteres
* Overlap: 100 caracteres

### Justificativa

A documentação da NovaTech é composta por políticas, procedimentos e tabelas de SLA, contendo informações que frequentemente dependem do contexto das linhas anteriores e posteriores.

A utilização de chunks muito pequenos poderia fragmentar informações importantes, reduzindo a qualidade da recuperação semântica. Por outro lado, chunks muito grandes poderiam misturar assuntos distintos, diminuindo a precisão da busca.

O tamanho de 500 caracteres foi escolhido por representar um equilíbrio entre:

* Preservação do contexto semântico;
* Precisão na recuperação de informações;
* Baixo consumo de tokens no prompt final;
* Melhor qualidade dos embeddings.

Além disso, foi utilizado overlap de 100 caracteres para evitar perda de contexto entre chunks consecutivos. Essa estratégia reduz o risco de informações relevantes ficarem divididas entre dois chunks diferentes, especialmente em casos de:

* Regras de negócio distribuídas em múltiplos parágrafos;
* Tabelas de SLA;
* Políticas com exceções e observações.

### Exemplo

Sem overlap:

Chunk 1:
"Cliente Gold — resposta em até 2h"

Chunk 2:
"resolução em até 24h"

Nesse cenário, uma busca pode recuperar apenas parte da informação.

Com overlap:

Chunk 1:
"Cliente Gold — resposta em até 2h, resolução em até 24h"

Chunk 2:
"resolução em até 24h..."

Dessa forma, as informações permanecem semanticamente completas e aumentam a probabilidade de recuperação correta pelo mecanismo de busca vetorial.

### Possíveis Melhorias

Em um ambiente de produção, uma estratégia mais avançada seria realizar chunking baseado na estrutura do documento (títulos, seções e tabelas), preservando melhor o significado do conteúdo e reduzindo a fragmentação de informações relacionadas.
