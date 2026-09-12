# Apresentar um estudo de BI em 15 minutos

Roteiro de preparação para explicar os projetos deste portfólio. Os exemplos usam dados sintéticos. Adapte a fala ao que você executou, validou e consegue demonstrar; resultados de demonstração não são resultados profissionais.

## Sequência sugerida

| Tempo | Mensagem | Evidência para mostrar |
| --- | --- | --- |
| 0–2 min | Qual decisão o estudo apoia e o que cada indicador significa | Perguntas de negócio e definições no README |
| 2–4 min | De onde vêm os dados e como as inconsistências foram tratadas | CSV bruto, motivos de exclusão e uma regra do Python |
| 4–7 min | O que uma linha representa e como as tabelas se relacionam | Modelo, chaves, uma consulta SQL e uma medida DAX |
| 7–11 min | Dois ou três achados, seus limites e uma investigação proposta | Resumo, gráficos e recortes validados |
| 11–13 min | Como os números foram conferidos e como outra pessoa reproduz | Testes existentes, resultados e instruções de execução |
| 13–15 min | O que seria necessário para uso real e qual o próximo passo | Limitações e prioridade de evolução |

Escolha um estudo principal. O de projetos favorece uma conversa sobre planejamento, prazos e acompanhamento de demandas; o comercial oferece um exemplo complementar de margem ponderada e agregação financeira.

## Exemplo de leitura do estudo de projetos

“Este cenário sintético tem 180 demandas na fotografia de 31 de dezembro de 2025. São 78 abertas, das quais 68 estão vencidas. Minha primeira investigação seria separar esse estoque por prioridade, idade e bloqueio. Automação reúne 21 demandas abertas vencidas, mas o volume não permite concluir que a equipe seja menos produtiva: falta controlar a complexidade e a capacidade.”

Depois explique a diferença entre **68 de 78 abertas vencidas** e **64 de 102 concluídas no prazo**. São populações e denominadores distintos. Mostre por que demandas abertas têm tempo de ciclo nulo e por que a data de criação não substitui a data de conclusão.

## Perguntas técnicas para ensaiar

| Pergunta | Resposta que precisa ser sustentada pelo projeto |
| --- | --- |
| Por que separar fato e dimensões? | Explicar a granularidade, as chaves e os agrupamentos usados; mostrar uma junção que não multiplica linhas. |
| Como tratou duplicidade? | Distinguir cópia idêntica de registros conflitantes e mostrar os motivos de exclusão. |
| Como validou o ETL? | Demonstrar conciliação de entrada, linhas válidas e excluídas, além de uma regra de negócio em um exemplo pequeno. |
| Como calcula margem? | Dividir lucro total por receita total no contexto do filtro; explicar por que a média simples das margens por linha distorce o resultado. |
| Por que existe uma relação inativa de calendário? | Explicar os papéis de criação e conclusão e o cálculo com USERELATIONSHIP. |
| Como investigaria uma consulta lenta? | Observar o plano de execução, seletividade, volume e cardinalidade das junções; medir antes e depois de alterar índices ou consulta. |
| Onde entram Python, SQL e Power BI? | Python gera e trata os exemplos; SQL consulta e confere resultados; Power Query importa; DAX define medidas no contexto analítico. |
| O que falta para produção? | Regras validadas com o negócio, origem real autorizada, operação de atualização e monitoramento, além do relatório finalizado. |

Os scripts SQLite já incluem índices em data e loja nas vendas, e em equipe e status/prazo nas demandas. A presença desses índices não comprova ganho de desempenho. Não há benchmark publicado. Para investigar no SQLite, consulte [EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html) e registre o resultado e o ambiente de cada medição.

## Demonstrar a própria experiência

Prepare um exemplo profissional verdadeiro para cada tema: indicador que você definiu; problema de qualidade que resolveu; automação que implementou; necessidade de negócio que traduziu em relatório. Em cada exemplo, descreva o contexto, sua responsabilidade, a ação e o resultado observado. Use números apenas quando puder comprová-los.

Conhecer as decisões do estudo é mais útil do que decorar trechos de código. Antes de apresentá-lo, execute o material, altere um filtro, confira a resposta e explique o motivo.

[Voltar ao portfólio](../README.md)
