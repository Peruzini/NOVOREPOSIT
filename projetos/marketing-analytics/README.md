# Marketing Analytics — Power BI

Estudo demonstrativo de Marketing Analytics com dados **100% sintéticos**, criado para mostrar a construção de indicadores de aquisição, funil e eficiência de mídia no Power BI.

## Perguntas de negócio

- Quanto foi investido e qual receita foi atribuída às campanhas?
- Quais canais geram mais leads e clientes?
- Como CTR, CPC, CPL e CAC variam entre canais e campanhas?
- Onde o funil perde mais volume entre clique, lead, oportunidade e cliente?
- Quais campanhas combinam escala e eficiência?
- Como ROAS e custo de aquisição evoluem ao longo do ano?

## Escopo

Período: janeiro a dezembro de 2025.

Canais simulados: Google Ads, Meta Ads, LinkedIn Ads e E-mail. São 8 campanhas distribuídas entre geração de leads, conversão e nutrição.

Os valores são fictícios. A receita é uma atribuição simplificada por campanha; não representa faturamento real nem modelo de atribuição multi-touch.

## Modelo de dados

Modelo estrela com quatro tabelas:

- `DimCalendario`: mês de referência.
- `DimCanal`: canal, tipo e papel no funil.
- `DimCampanha`: campanha, canal e objetivo.
- `FatoMarketing`: investimento, impressões, cliques, leads, oportunidades, clientes e receita atribuída.

Relacionamentos esperados:

- `FatoMarketing[Data]` → `DimCalendario[Data]`
- `FatoMarketing[CanalID]` → `DimCanal[CanalID]`
- `FatoMarketing[CampanhaID]` → `DimCampanha[CampanhaID]`

## KPIs principais

| Indicador | Definição |
| --- | --- |
| Investimento | Soma do investimento de mídia/canal |
| Receita atribuída | Receita sintética atribuída às campanhas |
| CTR | Cliques / Impressões |
| CPC | Investimento / Cliques |
| CPL | Investimento / Leads |
| CAC | Investimento / Clientes |
| Conversão Lead → Cliente | Clientes / Leads |
| ROAS | Receita atribuída / Investimento |
| ROI de mídia | (Receita atribuída - Investimento) / Investimento |
| Receita por cliente | Receita atribuída / Clientes |

### Resultado global esperado

Com a base versionada:

- Investimento: **R$ 536.699,00**
- Receita atribuída: **R$ 4.843.591,00**
- Impressões: **13.080.567**
- Cliques: **335.115**
- Leads: **30.933**
- Oportunidades: **8.855**
- Clientes: **2.360**
- CTR: **2,56%**
- CPL: **R$ 17,35**
- CAC: **R$ 227,41**
- Conversão Lead → Cliente: **7,63%**
- ROAS: **9,02x**

## Estrutura

```text
marketing-analytics/
├─ dados/tratados/
│  ├─ DimCalendario.csv
│  ├─ DimCanal.csv
│  ├─ DimCampanha.csv
│  └─ FatoMarketing.csv
├─ powerbi/
│  └─ medidas.dax
├─ resultados/
│  ├─ kpis-esperados.csv
│  └─ kpis-por-canal.csv
├─ sql/
│  └─ marketing_analytics.sql
├─ tests/
│  └─ test_marketing.py
├─ pipeline.py
└─ README.md
```

## Power BI

A entrega atual inclui dados sintéticos, pipeline Python, SQL, resultados esperados e medidas DAX em [powerbi/medidas.dax](powerbi/medidas.dax). **Ainda não há um arquivo PBIP de Marketing versionado neste repositório.**

Páginas propostas para uma futura implementação no Power BI:

1. **Visão geral** — investimento, receita, leads, clientes, ROAS e evolução mensal.
2. **Aquisição** — CTR, CPC, CPL, conversão e volume por canal.
3. **Eficiência** — CAC, ROAS, receita por cliente e ranking de campanhas.

As medidas DAX também estão documentadas em `powerbi/medidas.dax`.

### Limite de validação

As medidas DAX são material de implementação e ainda precisam de validação no motor do Power BI. Quando o relatório for criado, conferir abertura, atualização, calendário, cálculos, interações e aparência no Power BI Desktop. Não há relatório publicado no Power BI Service documentado nesta entrega.

## SQL

`sql/marketing_analytics.sql` contém consultas de referência para consolidado mensal, desempenho por canal, desempenho por campanha e funil/taxas de conversão. As consultas usam SQLite para facilitar a reprodução.

## Reproduzir a base

Na pasta do estudo:

```bash
python pipeline.py
python -m unittest discover -s tests -v
```

A semente é fixa, portanto a execução recria os mesmos dados e os mesmos totais.

## Interpretação

ROAS alto não significa lucro. A receita atribuída não considera custo do produto/serviço, impostos, despesas comerciais, churn ou efeitos incrementais. O objetivo do estudo é demonstrar modelagem, transformação, DAX, visualização e leitura de indicadores de marketing — não recomendar investimento real em mídia.
