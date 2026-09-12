# Portfólio de Business Intelligence

Estudos demonstrativos de Rafael Peruzini sobre indicadores, qualidade de dados e análise de negócio. Os exemplos usam dados totalmente sintéticos e não representam operações ou resultados de empresas reais.

## Estudos disponíveis

| Estudo | Perguntas de negócio | Entregas |
| --- | --- | --- |
| [Análise comercial](projetos/analise-comercial/README.md) | Como evoluem a receita e a margem? Quais lojas e categorias concentram os resultados? | Dados, ETL em Python, SQL, validações, visualização estática e medidas DAX. |
| [Indicadores de projetos](projetos/indicadores-projetos/README.md) | Qual é o backlog? Quantas demandas estão atrasadas? Como variam os prazos entre equipes? | Dados, ETL em Python, SQL, validações, visualização estática e medidas DAX. |

**Estado das entregas:** a geração dos dados, o tratamento e as consultas SQL são executáveis. Os arquivos de Power Query, DAX, tema e roteiros apoiam a montagem dos dashboards. Este repositório ainda não inclui arquivos `.pbix` nem capturas de um relatório executado no Power BI Desktop.

## Executar os estudos

Requisito: Python 3.10 ou superior. O processamento usa apenas a biblioteca padrão do Python; não é necessário instalar pacotes.

```bash
git clone https://github.com/Peruzini/NOVOREPOSIT.git
cd NOVOREPOSIT
python pipeline.py
python -m unittest discover -s tests -v
```

No Windows, se o comando `python` não estiver disponível, use `py -3` no lugar dele.

O primeiro comando de processamento gera as bases brutas, as tabelas tratadas, um banco SQLite local e os resultados de cada estudo. A execução regrava apenas as saídas geradas dentro das pastas dos estudos; preserve eventuais alterações manuais nesses arquivos antes de executar novamente.

Os CSVs e os resumos já versionados permitem examinar o material sem instalar Python. Os bancos `.sqlite` são gerados localmente e não são versionados.

## Organização

| Caminho | Conteúdo |
| --- | --- |
| `pipeline.py` | Geração reproduzível, ETL, criação do banco e verificação dos indicadores |
| `tests/` | Casos pequenos que verificam deduplicação, rejeições e definições dos indicadores |
| `projetos/analise-comercial/` | Estudo de receita e margem |
| `projetos/indicadores-projetos/` | Estudo de prazos, backlog e produtividade |
| `powerbi/tema.json` | Tema visual compartilhado |
| `docs/como-publicar-power-bi.md` | Passos para completar e publicar os arquivos do Power BI |

Cada estudo reúne `dados/brutos`, `dados/tratados`, `sql`, `powerbi` e `resultados`. As regras dos indicadores estão no README do próprio estudo. O código informa a semente aleatória e a data de referência; executar novamente produz os mesmos dados.

## Decisões técnicas

- Valores monetários são armazenados em centavos inteiros e convertidos para reais na apresentação.
- As transformações registram as linhas descartadas e o motivo. Cancelamento comercial e erro cadastral são motivos distintos.
- As consultas usam SQLite para facilitar a reprodução local. A adaptação para SQL Server ou Snowflake exige revisão das funções e tipos específicos de cada banco.
- As tabelas tratadas estão preparadas para um modelo dimensional no Power BI.
- Os testes conferem resultados conhecidos de exemplos pequenos e a conciliação entre Python e SQL.

## Referências

- [Modelo estrela no Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [Importação de arquivos CSV no Power Query](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)
- [Documentação do módulo sqlite3](https://docs.python.org/3/library/sqlite3.html)

Os estudos são material de demonstração. A utilização de bases reais requer revisão das regras de negócio, dos acessos e da autorização para divulgar os dados.
