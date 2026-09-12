# Validações da execução

Dados sintéticos. Relatório gerado por `python pipeline.py`.

- Linhas brutas: 188
- Linhas válidas: 180
- Linhas excluídas: 8
- Entrada = linhas válidas + linhas excluídas: OK
- Chaves primárias únicas e não nulas: OK
- Integridade referencial no SQLite: OK
- Indicadores calculados em Python conciliados com SQL: OK

## Exclusões

| Motivo | Linhas |
| --- | ---: |
| conclusao_sem_datas | 1 |
| data_invalida | 1 |
| duplicata_identica | 5 |
| equipe_invalida | 1 |

Os motivos são mutuamente exclusivos neste relatório. Para um ID conflitante, todas as linhas do ID são excluídas.
Uma linha com mais de um problema recebe o primeiro motivo detectado. Veja o CSV para identificar a linha da base bruta.
