# Arquitetura, desempenho e próximos passos

## Escolhas implementadas

- Spark range e expressões nativas geram eventos nos executores; não há UDF Python por linha.
- Dimensão pequena e conhecida com broadcast explícito. A validação de unicidade acontece antes da junção.
- Row number faz deduplicação com ordenação determinística; exige shuffle, com custo proporcional ao volume e à distribuição de chaves.
- Parquet organiza colunas e partições mensais. Consultas com filtro em year_month podem eliminar leitura de partições; examine EXPLAIN FORMATTED em sql/partition_pruning.sql.
- Adaptive Query Execution habilitado; shuffle partitions configurável na linha de comando.
- Bronze e Silver materializadas para reduzir recomputação da linhagem em etapas posteriores.
- coalesce(1) aplicado somente aos resultados agregados com limite de 10.000 grupos, nunca à Silver.
- collect limitado aos poucos códigos de rejeição e às análises pequenas do notebook; não coleta os eventos no driver.

Particionamento não garante melhoria em qualquer volume. Na amostra pequena, apenas acrescenta organização; o ganho precisa ser medido com leituras comparáveis e filtros seletivos.

## Limites concretos desta implementação

O modo padrão local[2] usa dois threads na mesma máquina. O parâmetro master permite configurar o Spark, mas o gerenciamento de caminhos, a pasta de execução e a escrita de metrics.json usam pathlib no driver. Portanto o CLI é uma demonstração local; não é um pipeline de nuvem pronto para implantação. Em cluster, seriam necessários armazenamento compartilhado, conectores, empacotamento e adaptação da escrita de metadados.

As saídas são protegidas contra sobrescrita por pasta, sem publicação atômica do conjunto de tabelas. Falhas podem deixar saídas parciais. Não há execução incremental, merge ACID, orquestrador, recuperação automática, autenticação, controle de acesso ou catálogo.

Não há cache dos grandes intermediários. As três saídas da classificação podem recomputar a deduplicação. Avaliar persist em memória/disco exige medir memória, recomputação e tempo; não há alegação de otimização já comprovada.

## Plano de benchmark reproduzível

| Rodada | Eventos únicos solicitados | Partições iniciais propostas |
| --- | ---: | ---: |
| Desenvolvimento | 100.000 | 4 |
| Volume intermediário | 1.000.000 | 8 |
| Experimento maior | 10.000.000 | 16 |

Registrar versão do código, CPU/RAM/SO/Java/Spark, master, duração, tamanho em disco, contagens e Spark UI (shuffle, spill, skew). Os volumes incluem duplicatas adicionais a cada 500 IDs. Repetir rodadas sob condições equivalentes; não comparar uma leitura com cache com outra sem cache.

Métricas do pipeline não medem custo de nuvem nem tempo de cluster. Testes de integração pequenos não substituem esses experimentos.

## Evolução proposta — não implementada

1. Validar fontes e regras de consumo com especialistas da operação.
2. Adaptar armazenamento para objeto distribuído e configurar credenciais fora do código.
3. Usar Delta Lake ou Iceberg para transações, evolução de esquema e cargas incrementais.
4. Adicionar catálogo, permissões, orquestração, observabilidade e estratégia de reprocessamento.
5. Estimar referências por categoria, carga e terreno com validação temporal antes de substituir o limiar ilustrativo.
6. Conectar uma camada SQL de serviço ao Power BI; avaliar importação e atualização incremental.

Não é necessário contratar nuvem para executar a demonstração.
