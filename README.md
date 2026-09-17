# Portfólio de Dados — Power BI e Big Data | Rafael Peruzini

Estudos demonstrativos sobre indicadores, qualidade de dados, modelagem e análise de negócio. Os exemplos usam dados sintéticos e não representam operações ou resultados de empresas reais.

## Estudos disponíveis

| Estudo | Perguntas de negócio | Entrega |
| --- | --- | --- |
| [Fleet Analytics — Power BI + DAX Avançado](projetos/fleet-dax-advanced/README.md) | Quais equipamentos concentram perdas? Como produção, disponibilidade, falhas e custo determinam a criticidade da frota? | [FleetAnalytics.pbip](powerbi/fleet/FleetAnalytics.pbip): 4 páginas, modelo estrela, Power Query autossuficiente, 34 medidas DAX incorporadas e catálogo técnico com 50+ medidas. |
| [Análise comercial](projetos/analise-comercial/README.md) | Como evoluem receita e margem? Quais lojas e categorias concentram os resultados? | [Comercial.pbip](powerbi/comercial/Comercial.pbip): 3 páginas, 5 tabelas e 11 medidas DAX. |
| [Indicadores de projetos](projetos/indicadores-projetos/README.md) | Qual é o backlog? Quantas demandas estão atrasadas? Como variam os prazos entre equipes? | [Projetos.pbip](powerbi/projetos/Projetos.pbip): 3 páginas, 3 tabelas e 15 medidas DAX. |
| [EquipAnalytics — Big Data](projetos/big-data-equipamentos/README.md) | Como investigar consumo elevado e qualidade de dados de equipamentos? | PySpark, Parquet, Spark SQL, testes e processamento de eventos sintéticos. |

## Destaque: Fleet Analytics

O Fleet Analytics aprofunda a parte técnica do portfólio em Power BI e DAX. O modelo contém dimensões compartilhadas e múltiplas tabelas fato para operação, manutenção, abastecimento e metas.

Entre os indicadores e padrões implementados estão:

- Produção Total, Disponibilidade Física e Utilização;
- Produtividade, consumo específico e custo por tonelada;
- MTBF e MTTR;
- meta e aderência;
- mês anterior, ano anterior e rolling 30/90 dias;
- `RANKX`, `ALLSELECTED`, `MAXX`, `SUMX` e `TOPN`;
- normalização de indicadores;
- Índice, Ranking e Classe de Criticidade.

A versão PBIP é autossuficiente: os dados de demonstração de 2025–2026 são criados pelas consultas Power Query do próprio modelo. O estudo também mantém um gerador Python, SQL analítico e um catálogo DAX mais amplo para evolução do case.

## Abrir no Power BI

1. Baixe ou clone o repositório.
2. Abra um dos arquivos `.pbip` no Power BI Desktop para Windows:
   - `powerbi/fleet/FleetAnalytics.pbip`
   - `powerbi/comercial/Comercial.pbip`
   - `powerbi/projetos/Projetos.pbip`
3. Mantenha as pastas `.Report` e `.SemanticModel` ao lado do arquivo `.pbip`.
4. Atualize o modelo e revise cálculos, interações e aparência antes de publicar.

O Fleet Analytics não exige executar Python para carregar seu cenário padrão, pois a massa sintética já é gerada pelo Power Query.

## Estado de validação

Os projetos editáveis possuem estrutura PBIP/PBIR, modelos semânticos, consultas e medidas versionadas em texto. A validação completa de abertura, atualização, cálculo DAX e aparência ainda deve ser concluída no Power BI Desktop. Não há `.pbix` versionado nesta entrega.

## Organização

| Caminho | Conteúdo |
| --- | --- |
| `powerbi/fleet/` | Fleet Analytics — PBIP, relatório PBIR e modelo semântico |
| `projetos/fleet-dax-advanced/` | documentação, catálogo DAX, SQL e gerador Python do Fleet Analytics |
| `powerbi/comercial/` | projeto Power BI de análise comercial |
| `powerbi/projetos/` | projeto Power BI de indicadores de demandas/projetos |
| `projetos/big-data-equipamentos/` | estudo de Big Data com PySpark |
| `projetos/marketing-analytics/` | estudo de Marketing Analytics |
| `pipeline.py` | processamento dos estudos integrados ao pipeline da raiz |
| `tests/` | testes de regras e transformações dos estudos integrados |
| `docs/` | documentação geral do portfólio |

## Executar o pipeline dos estudos integrados

Requisito: Python 3.10 ou superior.

```bash
git clone https://github.com/Peruzini/NOVOREPOSIT.git
cd NOVOREPOSIT
python pipeline.py
python -m unittest discover -s tests -v
```

O Fleet Analytics possui geração independente em `projetos/fleet-dax-advanced/scripts/gerar_dados.py`, mas essa execução é opcional para o PBIP autossuficiente.

## Decisões técnicas

- os estudos usam dados sintéticos e regras documentadas;
- os modelos Power BI priorizam esquema estrela e relações de dimensão para fato;
- o Fleet Analytics gera seu cenário padrão via Power Query/M;
- medidas DAX são centralizadas em tabela técnica no modelo Fleet;
- versões textuais PBIP/PBIR facilitam revisão e versionamento no Git;
- SQL e Python complementam a camada de BI sem substituir a modelagem semântica.

## Referências

- [Modelo estrela no Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [Power BI Project (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [DAX](https://learn.microsoft.com/en-us/dax/)
- [Power Query M](https://learn.microsoft.com/en-us/powerquery-m/)

Os estudos são materiais de demonstração. Bases reais exigem revisão de regras de negócio, acessos, privacidade e autorização para divulgação.
