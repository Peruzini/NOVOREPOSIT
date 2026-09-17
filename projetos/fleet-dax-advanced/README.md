# Fleet Analytics — Power BI + DAX Avançado

Estudo demonstrativo de Business Intelligence aplicado à gestão de uma frota de equipamentos pesados. O objetivo é mostrar modelagem dimensional, definição de KPIs operacionais e uso de DAX avançado em um cenário próximo de operações industriais e mineração.

> **Dados 100% sintéticos.** O projeto não contém dados, indicadores ou resultados de empresas reais.

## Problema de negócio

Uma operação precisa acompanhar produtividade, disponibilidade, utilização, manutenção e consumo da frota e responder perguntas como:

- quais equipamentos concentram perda de disponibilidade e horas de manutenção?
- a produção está aderente às metas por período e tipo de equipamento?
- quais ativos apresentam pior combinação entre disponibilidade, falhas, custo e perda produtiva?
- como produção, disponibilidade e utilização evoluem contra mês anterior, ano anterior e janelas móveis?
- qual parcela das perdas está concentrada nos equipamentos mais críticos?

## O que este case demonstra

- modelo estrela com múltiplas tabelas fato;
- contexto de filtro e transição de contexto em DAX;
- `CALCULATE`, `FILTER`, `ALL`, `ALLSELECTED`, `REMOVEFILTERS` e `KEEPFILTERS`;
- iteradores como `SUMX`, `AVERAGEX`, `MINX`, `MAXX` e `RANKX`;
- tabelas virtuais com `TOPN`, `ADDCOLUMNS` e `SUMMARIZE`;
- inteligência temporal com MTD/YTD, períodos anteriores e rolling windows;
- Pareto de perdas e ranking dinâmico;
- cálculo de MTBF e MTTR;
- parâmetros desconectados para ponderação de criticidade;
- score normalizado de criticidade da frota;
- separação entre medidas-base, KPIs e medidas analíticas.

## Modelo dimensional

```text
                  DimData
                     |
                     | 1:N
                     |
          +----------+-----------+
          |                      |
          v                      v
   FatoOperacao            FatoManutencao
          ^                      ^
          |                      |
          +------ 1:N -----------+
                  |
           DimEquipamento
                  |
                  +-------------------+
                                      |
                                 FatoMeta
```

### Dimensões

- `DimData`: calendário contínuo, ano, mês, trimestre e chaves de ordenação.
- `DimEquipamento`: equipamento, tipo, modelo, capacidade, centro de custo e ano de fabricação.

### Fatos

- `FatoOperacao`: horas-calendário, horas disponíveis, horas operadas, ciclos, toneladas e combustível.
- `FatoManutencao`: eventos de manutenção, sistema afetado, duração da parada, custo e indicador de falha.
- `FatoMeta`: metas diárias por tipo de equipamento para produção, disponibilidade, utilização e consumo específico.

Veja também [modelo-dimensional.md](docs/modelo-dimensional.md).

## KPIs principais

| Indicador | Regra resumida |
| --- | --- |
| Disponibilidade Física | horas disponíveis / horas calendário |
| Utilização | horas operadas / horas disponíveis |
| Produtividade | toneladas / horas operadas |
| Consumo específico | litros / toneladas |
| MTBF | horas operadas / número de falhas |
| MTTR | horas de manutenção corretiva / falhas |
| Aderência à produção | produção realizada / meta de produção |
| Score de criticidade | combinação normalizada de disponibilidade, falhas, custo e gap produtivo |

## DAX avançado

O catálogo principal está em [`dax/medidas-avancadas.dax`](dax/medidas-avancadas.dax). As tabelas desconectadas utilizadas pelo score estão em [`dax/tabelas-parametros.dax`](dax/tabelas-parametros.dax).

O arquivo foi organizado em blocos:

1. medidas-base;
2. KPIs operacionais;
3. metas e desvios;
4. inteligência temporal;
5. ranking e Pareto;
6. normalização e score de criticidade;
7. medidas de diagnóstico de contexto.

## Score de criticidade

O destaque do estudo é um índice dinâmico que combina quatro dimensões:

- baixa disponibilidade;
- quantidade de falhas;
- custo de manutenção;
- gap de produção contra meta.

Os pesos são controlados por tabelas desconectadas e podem ser alterados pelo usuário no relatório. O score final é recalculado no contexto atual de filtros e gera um ranking dinâmico da frota.

## Dados sintéticos reproduzíveis

Execute:

```bash
python projetos/fleet-dax-advanced/scripts/gerar_dados.py
```

O script usa apenas a biblioteca padrão do Python e gera os CSVs dentro de `projetos/fleet-dax-advanced/dados/` com semente fixa, permitindo reproduzir o mesmo cenário.

## Estrutura

```text
fleet-dax-advanced/
├── README.md
├── dados/                 # CSVs gerados pelo script
├── dax/
│   ├── medidas-avancadas.dax
│   └── tabelas-parametros.dax
├── docs/
│   └── modelo-dimensional.md
├── scripts/
│   └── gerar_dados.py
└── sql/
    └── analises.sql
```

## Próxima etapa no Power BI

A versão de código e documentação foi preparada para que o modelo seja montado no Power BI Desktop/PBIP. O próximo passo visual é criar quatro páginas:

1. **Visão Executiva** — produção, disponibilidade, utilização, custo e aderência às metas;
2. **Performance da Frota** — ranking, tendência e comparação entre equipamentos;
3. **Manutenção & Pareto** — MTBF, MTTR, sistemas críticos e perdas acumuladas;
4. **Criticidade** — parâmetros de peso, score normalizado, ranking e matriz de risco.

## Competências demonstradas

`Power BI` · `DAX` · `Power Query` · `Modelagem Dimensional` · `SQL` · `Python` · `KPIs` · `Time Intelligence` · `Pareto` · `What-if Analysis` · `Data Analytics`
