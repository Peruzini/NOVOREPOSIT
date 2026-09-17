# Portfólio de Dados — Power BI e Big Data | Rafael Peruzini

Estudos demonstrativos de Rafael Peruzini sobre indicadores, qualidade de dados e análise de negócio. Os exemplos usam dados totalmente sintéticos e não representam operações ou resultados de empresas reais.

## Página de serviços

A [primeira versão do site de serviços](site-servicos/README.md) reúne as ofertas, os estudos demonstrativos e contato por e-mail. Os arquivos HTML/CSS estão prontos para hospedagem; o site ainda não está publicado em um domínio.

## Estudos disponíveis

| Estudo | Perguntas de negócio | Entrega |
| --- | --- | --- |
| [Fleet Analytics — DAX Avançado](projetos/fleet-dax-advanced/README.md) | Quais equipamentos concentram perdas? Como produção, disponibilidade, falhas, custo e metas determinam a criticidade da frota? | 50+ medidas DAX, TREATAS, time intelligence, Pareto, tabelas virtuais, MTBF/MTTR, score parametrizado, SQL e gerador sintético. |
| [Análise comercial](projetos/analise-comercial/README.md) | Como evoluem a receita e a margem? Quais lojas e categorias concentram os resultados? | [Comercial.pbip](powerbi/comercial/Comercial.pbip): 3 páginas, 5 tabelas e 11 medidas DAX. |
| [Indicadores de projetos](projetos/indicadores-projetos/README.md) | Qual é o backlog? Quantas demandas estão atrasadas? Como variam os prazos entre equipes? | [Projetos.pbip](powerbi/projetos/Projetos.pbip): 3 páginas, 3 tabelas e 15 medidas DAX. |
| [EquipAnalytics — Big Data](projetos/big-data-equipamentos/README.md) | Como investigar consumo elevado e qualidade de dados de equipamentos? | PySpark, Parquet, Spark SQL, testes, notebook e agregados para Power BI. |

**Estado das entregas Power BI:** os projetos editáveis `.pbip` incluem modelos, consultas Power Query, medidas DAX, filtros e páginas em PBIR. A estrutura foi verificada contra esquemas da Microsoft, com checagem de campos, relacionamentos e totais dos CSVs. A validação completa de abertura, atualização, cálculo DAX e aparência final ainda precisa ser concluída no Power BI Desktop. Não há `.pbix` nem capturas do Desktop nesta versão. As imagens nos estudos são gráficos estáticos gerados pelo Python. O Fleet Analytics está atualmente na etapa de código, modelagem e documentação; a entrega visual PBIP está indicada como próxima etapa no README do próprio estudo.

**Revisão visual parcial:** uma captura da página Carteira confirmou os cartões e os dois gráficos sem filtros. Os ajustes de cor e de espaço do título, as demais páginas e as interações continuam pendentes de conferência. Os valores observados estão registrados no [roteiro de validação](docs/validacao-power-bi.md#revisão-visual-recebida--página-carteira).

## Estudo de DAX avançado

O [Fleet Analytics](projetos/fleet-dax-advanced/README.md) foi criado para aprofundar o portfólio de Power BI em modelagem e cálculo. O catálogo inclui mais de 50 medidas, com contexto de filtro, `TREATAS`, `ALLSELECTED`, iteradores, tabelas virtuais, inteligência temporal, Pareto, MTBF/MTTR e um score de criticidade com pesos controlados por tabelas desconectadas.

## Big Data e análise operacional

O [EquipAnalytics](projetos/big-data-equipamentos/README.md) demonstra geração sintética em volume configurável, camadas Bronze/Silver/Gold, deduplicação, quarentena e indicadores de consumo de equipamentos. Possui execução própria com PySpark; não é executado por `pipeline.py` da raiz. A prévia mostra uma amostra controlada, e os limites de validação e escala estão documentados no estudo.

## Abrir no Power BI

1. [Baixe o repositório completo em ZIP](https://github.com/Peruzini/NOVOREPOSIT/archive/refs/heads/main.zip) e extraia para uma pasta curta, como `C:\BI\Portfolio`.
2. Abra `powerbi/comercial/Comercial.pbip` ou `powerbi/projetos/Projetos.pbip` no Power BI Desktop para Windows. Mantenha as pastas `.Report` e `.SemanticModel` ao lado do arquivo.
3. Clique em **Atualizar**. Se a fonte solicitar credenciais, escolha **Anônimo** para `https://raw.githubusercontent.com`. Os projetos leem os CSVs sintéticos públicos de uma versão fixa deste repositório.
4. Compare os cartões e filtros com os [valores esperados](docs/validacao-power-bi.md). Salve o `.pbix` pelo Desktop após essa conferência.

Para o Fleet Analytics, execute primeiro `python projetos/fleet-dax-advanced/scripts/gerar_dados.py` e siga o modelo e as medidas descritos no README do estudo.

O [guia de abertura](powerbi/README.md) explica as opções de visualização necessárias, a origem dos dados e a solução de problemas. Não é necessário executar Python ou Node.js para abrir os dois projetos PBIP já existentes.

## Leitura orientada

Comece pelos resultados e pelas perguntas do estudo que mais se aproxima do problema de negócio. Para examinar as decisões e completar a entrega:

- [Modelos de dados e relacionamentos](docs/modelos-de-dados.md)
- [Valores esperados para validar o Power BI](docs/validacao-power-bi.md)
- [Roteiro de apresentação de um estudo](docs/roteiro-de-apresentacao.md)
- [Passos para finalizar o Power BI](docs/como-publicar-power-bi.md)

## Executar os dois estudos Power BI existentes

Requisito: Python 3.10 ou superior. O processamento usa apenas a biblioteca padrão do Python; não é necessário instalar pacotes.

```bash
git clone https://github.com/Peruzini/NOVOREPOSIT.git
cd NOVOREPOSIT
python pipeline.py
python -m unittest discover -s tests -v
```

No Windows, se o comando `python` não estiver disponível, use `py -3` no lugar dele.

O primeiro comando de processamento gera as bases brutas, as tabelas tratadas, um banco SQLite local e os resultados dos estudos integrados ao pipeline da raiz. A execução regrava apenas as saídas geradas dentro das pastas desses estudos; preserve eventuais alterações manuais nesses arquivos antes de executar novamente.

Os CSVs e os resumos já versionados permitem examinar o material sem instalar Python. Os bancos `.sqlite` são gerados localmente e não são versionados.

## Organização

| Caminho | Conteúdo |
| --- | --- |
| `pipeline.py` | Geração reproduzível, ETL, criação do banco e verificação dos indicadores |
| `tests/` | Casos pequenos que verificam deduplicação, rejeições e definições dos indicadores |
| `projetos/fleet-dax-advanced/` | Estudo de Power BI e DAX avançado aplicado à performance e criticidade de frota |
| `projetos/analise-comercial/` | Estudo de receita e margem |
| `projetos/indicadores-projetos/` | Estudo de prazos, backlog e entregas |
| `projetos/big-data-equipamentos/` | Estudo independente de Big Data, consumo operacional e qualidade com PySpark |
| `powerbi/comercial/` | Relatório Comercial e seu modelo semântico |
| `powerbi/projetos/` | Relatório Projetos e seu modelo semântico |
| `powerbi/tema.json` | Tema visual compartilhado |
| `powerbi/validacao-estrutural.json` | Evidências e limites da verificação estática |
| `scripts/` | Geração reproduzível dos projetos e validação estrutural |
| `docs/como-publicar-power-bi.md` | Passos para completar e publicar os arquivos do Power BI |

Os estudos reúnem dados, regras de negócio, código e documentação conforme a necessidade de cada case. O Fleet Analytics mantém seu gerador de dados separado para preservar a independência do estudo e facilitar a leitura técnica.

## Decisões técnicas

- Valores monetários dos estudos integrados são armazenados em centavos inteiros e convertidos para reais na apresentação.
- As transformações registram as linhas descartadas e o motivo. Cancelamento comercial e erro cadastral são motivos distintos.
- As consultas usam SQLite para facilitar a reprodução local. A adaptação para SQL Server ou Snowflake exige revisão das funções e tipos específicos de cada banco.
- Os projetos usam modelo estrela, relações de um para muitos e filtros da dimensão para a fato. No estudo de demandas, uma relação inativa permite analisar a data de conclusão.
- O Fleet Analytics mantém metas em granularidade de tipo de equipamento e usa `TREATAS` nas medidas para transferir explicitamente esse contexto, evitando uma relação muitos-para-muitos desnecessária.
- O Power Query dos projetos existentes amplia o calendário para anos completos de 2025 e 2026. Os fatos comerciais permanecem em 2025 e a fotografia das demandas permanece em 31/12/2025.
- A fonte padrão do Power BI está fixada no commit `a0b11aefd23d71c05243a04217890980a41d47e0`. Executar o pipeline local não altera essa fonte; veja no guia como usar seus CSVs locais.
- Os testes conferem resultados conhecidos de exemplos pequenos e a conciliação entre Python e SQL.

## Referências

- [Modelo estrela no Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [Importação de arquivos CSV no Power Query](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)
- [Documentação do módulo sqlite3](https://docs.python.org/3/library/sqlite3.html)

Os estudos são material de demonstração. A utilização de bases reais requer revisão das regras de negócio, dos acessos e da autorização para divulgar os dados.
