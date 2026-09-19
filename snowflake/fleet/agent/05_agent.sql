USE DATABASE __DATABASE__;
USE SCHEMA __DATABASE__.__SCHEMA__;
-- Requires Cortex availability and privileges. Not executed by local tests.
CREATE AGENT FLEET_ASSISTANT
  COMMENT = 'Piloto sobre dados sinteticos; reconciliacao Power BI/SQL pendente.'
  FROM SPECIFICATION
  $$
models:
  orchestration: auto
instructions:
  response: >-
    Responda em portugues. Informe periodo, filtros, unidades e que os dados sao sinteticos.
    Diferencie ausencia de dados de zero. Apresente percentuais a partir de razoes 0-1.
    Nao estime economia, retorno ou desempenho real de empresas.
  orchestration: >-
    Use FleetAnalyst para todas as perguntas numericas. Se faltar periodo, pergunte antes
    de consultar. Se a ferramenta falhar, informe a falha e nao complete numeros por memoria.
    Falhas inclui somente corretivas; MTTR usa horas corretivas. Percentuais e custo por
    tonelada sao razoes dos totais. Ao pedir top 5, desempate por EQUIPAMENTO_ID crescente.
    Criticidade, Pareto acumulado e filtro por tipo de manutencao nao foram implementados
    nesta camada; explique esse limite. Nao extrapole o periodo 2025-2026.
  sample_questions:
    - question: Qual foi a producao total em janeiro de 2026?
    - question: Qual foi o custo por tonelada por equipamento em janeiro de 2026?
    - question: Quais cinco equipamentos tiveram mais horas de manutencao em janeiro de 2026?
tools:
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: FleetAnalyst
      description: Consulta indicadores de frota em uma base sintetica diaria de 2025 a 2026.
tool_resources:
  FleetAnalyst:
    semantic_view: __DATABASE__.__SCHEMA__.FLEET_ANALYTICS
    execution_environment:
      type: warehouse
      warehouse: __WAREHOUSE__
      query_timeout: 60
$$;
