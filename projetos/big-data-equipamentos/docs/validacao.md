# Validação e evidências

## Estado desta versão

O código inclui testes automatizados e um workflow de GitHub Actions. O resultado de cada execução deve ser consultado em **Actions → Big Data EquipAnalytics**, no commit correspondente. A presença do workflow não significa que ele passou.

Não foram executados benchmarks de 1 milhão ou 10 milhões de eventos, implantação em cluster, Docker ou renderização de um relatório no Power BI. Nenhum tempo de execução foi inventado.

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
