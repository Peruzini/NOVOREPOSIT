# Validação e evidências

## Estado desta versão

O código inclui testes automatizados e um workflow de GitHub Actions. O resultado de cada execução deve ser consultado em **Actions → Big Data EquipAnalytics**, no commit correspondente. A presença do workflow não significa que ele passou.

Não foram executados benchmarks de 1 milhão ou 10 milhões de eventos, implantação em cluster, Docker ou renderização de um relatório no Power BI. Nenhum tempo de execução foi inventado.

## Execução confirmada

Em 14/09/2026, o [GitHub Actions — execução 34867957046](https://github.com/Peruzini/NOVOREPOSIT/actions/runs/34867957046) concluiu com sucesso os 7 testes e a demonstração de 100.000 eventos sintéticos. O código validado está no commit 7c6576f3c6260ab6c37392cfc13526fcc1440b44.

| Medida da execução | Resultado observado |
| --- | ---: |
| Testes aprovados | 7 |
| Eventos únicos solicitados | 100.000 |
| Bronze com versões duplicadas | 100.200 |
| Silver | 99.698 |
| Rejeições | 302 |
| Versões duplicadas | 200 |
| Rejeição após deduplicação | 0,302% |

Os rejeitados foram 102 timestamps inválidos, 100 equipamentos desconhecidos e 100 valores de litros inválidos. A contagem por prioridade também foi conferida independentemente a partir das regras de injeção dos defeitos.

Spark 3.5.7, master local[2]. Os testes levaram 17,025 s; o temporizador parcial do pipeline registrou 11,002 s antes das exportações SQL. Esses tempos pertencem a uma única execução em runner GitHub e não são promessa de desempenho ou benchmark de cluster.

O [registro persistente da evidência](../results/ci-100k.json) preserva os metadados essenciais; os artefatos completos do workflow têm retenção de 14 dias.

## Amostra controlada

examples/events.csv contém 10 registros. examples/expected.json registra o oráculo manual:

| Verificação | Esperado |
| --- | ---: |
| Bronze | 10 |
| Versões duplicadas | 1 |
| Rejeições | 5 |
| Eventos Silver | 4 |
| Consumo | 360 L |
| Horas operacionais | 4 h |
| L/h ponderado | 90 |
| Custo estimado | R$ 2.160,00 |
| Eventos com alerta | 1 |

Reconciliação: 10 = 1 + 5 + 4. Rejeições: 2 por litros inválidos, 1 por equipamento desconhecido, 1 por data inválida e 1 por duração zero.

A imagem do README usa exclusivamente este oráculo. Ela é uma apresentação estática da amostra, não uma captura de Power BI ou de um job Spark.

## Cobertura dos testes

- Reconciliação e totais conhecidos da amostra.
- Política de versão: última versão inválida não recupera versão antiga.
- L/h ponderado com durações diferentes e fronteira estrita do alerta.
- NaN, infinito, texto, nulos e IDs inválidos.
- Bloqueio de chaves duplicadas na dimensão.
- Cardinalidade e reprodutibilidade da geração com diferentes partições.
- Gravação e leitura Parquet, execução SQL, exportação CSV e proteção de saídas.

Para repetir:

~~~bash
python -m unittest discover -s tests -v
~~~

Um job opcional de demonstração no workflow processa 100.000 eventos únicos sintéticos e publica os metadados e agregados como artefato da execução. Consulte os logs para saber se essa etapa foi concluída. O total Bronze inclui versões duplicadas.

O CI não utiliza dados reais, credenciais de nuvem nem serviços externos além da instalação de dependências e dos serviços do GitHub.
