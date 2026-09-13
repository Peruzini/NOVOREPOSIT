# Portfólio Power BI — Rafael Peruzini

Estudos demonstrativos de Rafael Peruzini sobre indicadores, qualidade de dados e análise de negócio. Os exemplos usam dados totalmente sintéticos e não representam operações ou resultados de empresas reais.

## Estudos disponíveis

| Estudo | Perguntas de negócio | Projeto Power BI |
| --- | --- | --- |
| [Análise comercial](projetos/analise-comercial/README.md) | Como evoluem a receita e a margem? Quais lojas e categorias concentram os resultados? | [Comercial.pbip](powerbi/comercial/Comercial.pbip): 3 páginas, 5 tabelas e 11 medidas DAX. |
| [Indicadores de projetos](projetos/indicadores-projetos/README.md) | Qual é o backlog? Quantas demandas estão atrasadas? Como variam os prazos entre equipes? | [Projetos.pbip](powerbi/projetos/Projetos.pbip): 3 páginas, 3 tabelas e 15 medidas DAX. |

**Estado das entregas:** os projetos editáveis `.pbip` incluem modelos, consultas Power Query, medidas DAX, filtros e páginas em PBIR. A estrutura foi verificada contra esquemas da Microsoft, com checagem de campos, relacionamentos e totais dos CSVs. A abertura, a atualização, o cálculo DAX e a aparência final ainda precisam ser conferidos no Power BI Desktop. Não há `.pbix` nem capturas do Desktop nesta versão. As imagens nos estudos são gráficos estáticos gerados pelo Python.

## Abrir no Power BI

1. [Baixe o repositório completo em ZIP](https://github.com/Peruzini/NOVOREPOSIT/archive/refs/heads/main.zip) e extraia para uma pasta curta, como `C:\BI\Portfolio`.
2. Abra `powerbi/comercial/Comercial.pbip` ou `powerbi/projetos/Projetos.pbip` no Power BI Desktop para Windows. Mantenha as pastas `.Report` e `.SemanticModel` ao lado do arquivo.
3. Clique em **Atualizar**. Se a fonte solicitar credenciais, escolha **Anônimo** para `https://raw.githubusercontent.com`. Os projetos leem os CSVs sintéticos públicos de uma versão fixa deste repositório.
4. Compare os cartões e filtros com os [valores esperados](docs/validacao-power-bi.md). Salve o `.pbix` pelo Desktop após essa conferência.

O [guia de abertura](powerbi/README.md) explica as opções de visualização necessárias, a origem dos dados e a solução de problemas. Não é necessário executar Python ou Node.js para abrir os projetos.

## Leitura orientada

Comece pelos resultados e pelas perguntas do estudo que mais se aproxima do problema de negócio. Para examinar as decisões e completar a entrega:

- [Modelos de dados e relacionamentos](docs/modelos-de-dados.md)
- [Valores esperados para validar o Power BI](docs/validacao-power-bi.md)
- [Roteiro de apresentação de um estudo](docs/roteiro-de-apresentacao.md)
- [Passos para finalizar o Power BI](docs/como-publicar-power-bi.md)

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
| `projetos/indicadores-projetos/` | Estudo de prazos, backlog e entregas |
| `powerbi/comercial/` | Relatório Comercial e seu modelo semântico |
| `powerbi/projetos/` | Relatório Projetos e seu modelo semântico |
| `powerbi/tema.json` | Tema visual compartilhado |
| `powerbi/validacao-estrutural.json` | Evidências e limites da verificação estática |
| `scripts/` | Geração reproduzível dos projetos e validação estrutural |
| `docs/como-publicar-power-bi.md` | Passos para completar e publicar os arquivos do Power BI |

Cada estudo reúne `dados/brutos`, `dados/tratados`, `sql`, `powerbi` e `resultados`. As regras dos indicadores estão no README do próprio estudo. O código informa a semente aleatória e a data de referência; executar novamente produz os mesmos dados.

## Decisões técnicas

- Valores monetários são armazenados em centavos inteiros e convertidos para reais na apresentação.
- As transformações registram as linhas descartadas e o motivo. Cancelamento comercial e erro cadastral são motivos distintos.
- As consultas usam SQLite para facilitar a reprodução local. A adaptação para SQL Server ou Snowflake exige revisão das funções e tipos específicos de cada banco.
- Os projetos usam modelo estrela, relações de um para muitos e filtros da dimensão para a fato. No estudo de demandas, uma relação inativa permite analisar a data de conclusão.
- O Power Query dos projetos amplia o calendário para anos completos de 2025 e 2026. Os fatos comerciais permanecem em 2025 e a fotografia das demandas permanece em 31/12/2025.
- A fonte padrão do Power BI está fixada no commit `a0b11aefd23d71c05243a04217890980a41d47e0`. Executar o pipeline local não altera essa fonte; veja no guia como usar seus CSVs locais.
- Os testes conferem resultados conhecidos de exemplos pequenos e a conciliação entre Python e SQL.

## Referências

- [Modelo estrela no Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [Importação de arquivos CSV no Power Query](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)
- [Documentação do módulo sqlite3](https://docs.python.org/3/library/sqlite3.html)

Os estudos são material de demonstração. A utilização de bases reais requer revisão das regras de negócio, dos acessos e da autorização para divulgar os dados.
