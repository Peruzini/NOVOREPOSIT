# Fleet Analytics — Power BI + DAX Avançado

Estudo demonstrativo de Business Intelligence aplicado à gestão de uma frota de equipamentos pesados. O projeto foi desenhado para demonstrar modelagem dimensional, Power Query, indicadores operacionais e DAX avançado em um cenário próximo de mineração e operações industriais.

> **Dados 100% sintéticos.** O projeto não contém dados, indicadores ou resultados de empresas reais.

## Entrega Power BI

O projeto possui uma versão editável em **Power BI Project (PBIP)**:

[`../../powerbi/fleet/FleetAnalytics.pbip`](../../powerbi/fleet/FleetAnalytics.pbip)

> **Importante:** não baixe somente o arquivo `FleetAnalytics.pbip`. O formato PBIP referencia arquivos externos do projeto e precisa ser aberto junto das pastas `FleetAnalytics.Report` e `FleetAnalytics.SemanticModel`. Baixe/extrate o repositório completo e mantenha os três itens dentro de `powerbi/fleet/` antes de abrir o `.pbip` no Power BI Desktop.

A estrutura esperada é:

```text
powerbi/fleet/
├── FleetAnalytics.pbip
├── FleetAnalytics.Report/
│   ├── definition.pbir
│   └── definition/
└── FleetAnalytics.SemanticModel/
    ├── definition.pbism
    └── model.bim
```

O modelo é autossuficiente: a massa demonstrativa de 2025–2026 é gerada no próprio Power Query, portanto o PBIP não depende de arquivos privados, credenciais ou bases corporativas para construir o cenário.

### Páginas

1. **Visão Executiva** — produção, aderência à meta e custo por tonelada;
2. **Performance da Frota** — utilização, produtividade e ranking de equipamentos;
3. **Manutenção & Pareto** — falhas, horas de manutenção, custo e participação nas perdas;
4. **Criticidade** — índice composto, ranking e classe de criticidade.

A versão PBIP contém um núcleo de **34 medidas DAX incorporadas ao modelo semântico**. O catálogo técnico em [`dax/medidas-avancadas.dax`](dax/medidas-avancadas.dax) ultrapassa 50 medidas e inclui variações e exemplos adicionais para estudo e evolução do relatório.

## Escopo das duas implementações

O PBIP e o catálogo DAX representam versões diferentes do estudo. O catálogo é uma referência para evolução e exige adaptação de tabelas, colunas e regras antes de ser usado no modelo atual.

| Regra | Modelo PBIP atual | Catálogo DAX |
| --- | --- | --- |
| Falhas | Contagem de linhas de manutenção | Contagem filtrada por `FalhaFlag = 1` |
| MTTR | Horas de manutenção / contagem de eventos | Horas corretivas / falhas sinalizadas |
| Componente de custo da criticidade | Custo por tonelada, normalizado pelo máximo selecionado | Custo de manutenção, normalizado por min-max |
| Componente de perda da criticidade | Horas de manutenção | Gap positivo de produção |
| Pesos | Fixos no índice | Medidas baseadas em tabelas de parâmetros |

Essas diferenças afetam a interpretação dos resultados. Antes de uma migração ou exposição das métricas a um agente de IA, definir uma regra canônica e conferir resultados por equipamento e período. Esta comparação é uma revisão estática dos arquivos; não substitui execução no Power BI Desktop.

Veja a [proposta de evolução para Snowflake e IA](../../docs/evolucao-bi-snowflake.md).

## Problema de negócio

O cenário procura responder perguntas como:

- quais equipamentos concentram perdas de disponibilidade e manutenção?
- a produção está aderente às metas?
- quais ativos apresentam a pior combinação de disponibilidade, falhas, custo e perda operacional?
- como produção e desempenho variam entre períodos?
- qual é o ranking de equipamentos por produção e por criticidade?

## Modelo dimensional

O modelo utiliza dimensões compartilhadas por múltiplas tabelas fato:

```text
                     DimData
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
 FatoOperacao    FatoManutencao   FatoAbastecimento
       ^                ^                ^
       |                |                |
       +---------- DimEquipamento -------+
                        |
                        v
                     FatoMeta
```

### Tabelas principais

- `DimData` — calendário contínuo de 2025 e 2026;
- `DimEquipamento` — equipamento, tipo, modelo e área;
- `FatoOperacao` — produção, horas operadas e horas-calendário;
- `FatoManutencao` — eventos, tipo de parada, duração e custo;
- `FatoAbastecimento` — litros e custo de combustível;
- `FatoMeta` — meta diária por equipamento;
- `Medidas` — tabela técnica para centralizar as medidas DAX.

Veja também [`docs/modelo-dimensional.md`](docs/modelo-dimensional.md).

## DAX incorporado ao PBIP

Entre as medidas disponíveis no modelo estão:

- Produção Total;
- Disponibilidade Física %;
- Utilização %;
- Produtividade t/h;
- Consumo L/t;
- Custo Combustível;
- Custo Manutenção;
- Custo Total;
- Custo por Tonelada;
- Falhas;
- MTBF e MTTR;
- Meta Produção e Aderência Meta %;
- Produção Mês Anterior e Variação MoM %;
- Produção Ano Anterior e Variação YoY %;
- Rolling 30 e 90 dias;
- Ranking Equipamento;
- Participação e perdas acumuladas;
- scores normalizados de disponibilidade, falhas, custo e perda;
- Índice de Criticidade;
- Ranking e Classe de Criticidade.

O modelo usa funções e padrões como `CALCULATE`, `DATEADD`, `DATESINPERIOD`, `DIVIDE`, `RANKX`, `ALLSELECTED`, `MAXX`, `SUMX`, `TOPN`, variáveis e contexto dinâmico de filtro.

## Índice de criticidade

A versão executável do PBIP utiliza a seguinte ponderação-base:

| Dimensão | Peso |
| --- | ---: |
| Baixa disponibilidade | 35% |
| Custo por tonelada | 25% |
| Falhas | 20% |
| Horas de perda/manutenção | 20% |

Cada componente é normalizado no contexto selecionado antes de compor o índice. Isso permite comparar ativos com métricas de escalas diferentes e gerar um ranking relativo da frota.

O arquivo [`dax/tabelas-parametros.dax`](dax/tabelas-parametros.dax) documenta a evolução para pesos controlados por tabelas desconectadas/What-if Parameters.

## Dados e reprodutibilidade

Além do PBIP autossuficiente, o estudo mantém um gerador Python independente:

```bash
python projetos/fleet-dax-advanced/scripts/gerar_dados.py
```

Esse script usa somente a biblioteca padrão e permite gerar CSVs sintéticos para testar o mesmo domínio fora do Power BI.

## SQL

[`sql/analises.sql`](sql/analises.sql) contém consultas analíticas complementares, incluindo agregações e funções de janela para examinar o cenário também pela camada SQL.

## Estrutura

```text
projetos/fleet-dax-advanced/
├── README.md
├── dax/
│   ├── medidas-avancadas.dax
│   └── tabelas-parametros.dax
├── docs/
│   └── modelo-dimensional.md
├── scripts/
│   └── gerar_dados.py
└── sql/
    └── analises.sql

powerbi/fleet/
├── FleetAnalytics.pbip
├── FleetAnalytics.Report/
└── FleetAnalytics.SemanticModel/
```

## Estado de validação

A estrutura PBIP/PBIR e os arquivos JSON foram montados no mesmo padrão técnico dos outros projetos do portfólio. Ainda é necessária a **validação final no Power BI Desktop** para confirmar atualização das consultas M, cálculo das medidas, aparência e interações dos visuais após a abertura local.

## Competências demonstradas

`Power BI` · `DAX` · `Power Query/M` · `Modelagem Dimensional` · `SQL` · `Python` · `KPIs` · `Time Intelligence` · `RANKX` · `TOPN` · `ALLSELECTED` · `MTBF/MTTR` · `Analytics`
