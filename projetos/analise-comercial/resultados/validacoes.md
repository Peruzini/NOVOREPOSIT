# Validações da execução

Dados sintéticos. Relatório gerado por `python pipeline.py`.

- Linhas brutas: 1217
- Linhas válidas: 1129
- Linhas excluídas: 88
- Entrada = linhas válidas + linhas excluídas: OK
- Chaves primárias únicas e não nulas: OK
- Integridade referencial no SQLite: OK
- Indicadores calculados em Python conciliados com SQL: OK

## Exclusões

| Motivo | Linhas |
| --- | ---: |
| chave_LojaID_invalida | 1 |
| chave_ProdutoID_invalida | 1 |
| data_invalida | 1 |
| desconto_invalido | 1 |
| duplicata_identica | 10 |
| id_conflitante | 2 |
| quantidade_invalida | 1 |
| valor_negativo | 1 |
| venda_cancelada | 70 |

Os motivos são mutuamente exclusivos neste relatório. Para um ID conflitante, todas as linhas do ID são excluídas.
Uma linha com mais de um problema recebe o primeiro motivo detectado. Veja o CSV para identificar a linha da base bruta.
