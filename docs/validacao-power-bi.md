# Conferir os resultados no Power BI

Os valores abaixo foram recalculados dos CSVs tratados publicados. São referências para validação manual; não representam testes já executados no Power BI Desktop.

Antes de comparar, remova filtros de página, relatório e visual, limpe as seleções nos gráficos e confira o caminho da fonte. Use os CSVs dos respectivos estudos.

## Análise comercial

| Seleção | Pedidos | Receita líquida | Lucro bruto |
| --- | ---: | ---: | ---: |
| Sem filtros | 1.129 | R$ 450.903,00 | R$ 179.268,00 |
| AnoMes = 2025-01 | 89 | R$ 38.839,90 | R$ 15.617,40 |
| Loja = Loja 04 | 143 | R$ 60.297,55 | R$ 24.223,05 |
| Janeiro de 2025 e Loja 04 | 15 | R$ 6.559,80 | R$ 2.674,80 |

Sem filtros, a margem deve ser **39,76%** e o ticket médio **R$ 399,38**. Não some margens ou tickets dos grupos: calcule a razão no contexto selecionado.

Teste a medida `Variacao Receita Mensal` em janeiro de 2025, que não tem mês anterior na base, e em janeiro de 2026, que não tem vendas atuais. Nos dois casos, a variação deve ficar em branco. Em um mês com receita anterior igual a zero, `DIVIDE` também devolve vazio sem um resultado alternativo.

## Projetos e demandas

| Seleção de equipe, sem filtro de calendário/status | Demandas | Concluídas | Backlog | Abertas em atraso |
| --- | ---: | ---: | ---: | ---: |
| Todas | 180 | 102 | 78 | 68 |
| BI | 42 | 26 | 16 | 14 |
| Engenharia de Dados | 46 | 24 | 22 | 20 |
| Automação | 47 | 25 | 22 | 21 |
| Processos | 45 | 27 | 18 | 13 |

Sem filtros, confira também **42 em andamento**, **64 entregas no prazo**, **62,75% de entregas no prazo**, **17,85 dias de ciclo médio** e **21,37 dias de lead time médio**.

Para testar a data de entrega, crie uma tabela com `DimCalendario[AnoMes]` e `Concluidas por Data de Entrega`. Janeiro de 2025 deve mostrar **2** conclusões e dezembro **14**; o total é **102**. O calendário de criação não pode ser usado como substituto do calendário de conclusão.

Escolha apenas demandas abertas: ciclo médio e taxa de entrega no prazo devem ficar vazios. Uma demanda aberta vencida conta em atraso mesmo que ainda não tenha data de início.

## Se os números divergirem

| Sintoma | Onde começar a investigar |
| --- | --- |
| Dinheiro cem vezes maior | Conversão de centavos para reais |
| Total muda ao adicionar nome da dimensão | Duplicidade da chave, relacionamento ou filtro de visual |
| Margem total diferente da razão dos totais | Média simples de percentuais ou medida implícita |
| Conclusões aparecem no mês errado | Relação ativa de criação e uso de USERELATIONSHIP |
| Uma seleção não altera o gráfico esperado | Interações do relatório e direção de filtro |

Registre a versão do Desktop, a data e os recortes conferidos ao concluir. Salve e reabra o `.pbix`, teste a atualização e só então publique as capturas do próprio relatório.

## Evidências de referência

- [Resumo comercial](../projetos/analise-comercial/resultados/resumo.json)
- [Consultas comerciais](../projetos/analise-comercial/resultados/consultas.json)
- [Resumo de projetos](../projetos/indicadores-projetos/resultados/resumo.json)
- [Consultas de projetos](../projetos/indicadores-projetos/resultados/consultas.json)
- [ISBLANK no DAX](https://learn.microsoft.com/en-us/dax/isblank-function-dax)

[Voltar ao portfólio](../README.md)
