USE DATABASE __DATABASE__;
USE SCHEMA __DATABASE__.__SCHEMA__;
-- Draft definition: validate compilation and results in your Snowflake account.
CREATE SEMANTIC VIEW FLEET_ANALYTICS
  TABLES (
    fleet AS __DATABASE__.__SCHEMA__.FLEET_DAILY
      PRIMARY KEY (DATA, EQUIPAMENTO_ID)
      COMMENT = 'Dados sinteticos diarios por equipamento; piloto 2025-2026.'
  )
  DIMENSIONS (
    fleet.dia AS DATA COMMENT = 'Data de operacao; periodo fechado 2025-2026.',
    fleet.equipamento_id AS EQUIPAMENTO_ID,
    fleet.equipamento AS EQUIPAMENTO,
    fleet.tipo AS TIPO,
    fleet.area AS AREA
  )
  METRICS (
    fleet.total_producao_ton AS SUM(PRODUCAO_TON) COMMENT = 'Producao sintetica em toneladas.',
    fleet.total_horas_operacao AS SUM(HORAS_OPERACAO),
    fleet.total_horas_manutencao AS SUM(HORAS_MANUTENCAO) COMMENT = 'Inclui corretiva, preventiva e inspecao.',
    fleet.total_horas_corretivas AS SUM(HORAS_CORRETIVAS),
    fleet.total_falhas AS COALESCE(SUM(FALHAS), 0) COMMENT = 'Somente eventos corretivos; zero na ausencia de falhas.',
    fleet.custo_total AS SUM(CUSTO_MANUTENCAO + CUSTO_COMBUSTIVEL),
    fleet.custo_por_tonelada AS SUM(CUSTO_MANUTENCAO + CUSTO_COMBUSTIVEL) / NULLIF(SUM(PRODUCAO_TON), 0)
      COMMENT = 'Razao dos totais em BRL/t; nunca media das razoes diarias.',
    fleet.disponibilidade AS (SUM(HORAS_CALENDARIO) - SUM(HORAS_MANUTENCAO)) / NULLIF(SUM(HORAS_CALENDARIO), 0),
    fleet.utilizacao AS SUM(HORAS_OPERACAO) / NULLIF(SUM(HORAS_CALENDARIO) - SUM(HORAS_MANUTENCAO), 0),
    fleet.mttr AS SUM(HORAS_CORRETIVAS) / NULLIF(SUM(FALHAS), 0) COMMENT = 'Horas corretivas por falha; NULL sem falhas.',
    fleet.mtbf AS SUM(HORAS_OPERACAO) / NULLIF(SUM(FALHAS), 0) COMMENT = 'Horas operadas por falha; NULL sem falhas.',
    fleet.aderencia_meta AS SUM(PRODUCAO_TON) / NULLIF(SUM(META_PRODUCAO_TON), 0)
  )
  COMMENT = 'Piloto de reconciliacao com Fleet PBIP; nao contem dados empresariais.'
  AI_SQL_GENERATION 'Use apenas as metricas definidas. Sempre explicite periodo, unidade e filtros. Custos estao em BRL. Percentuais sao razoes 0-1. Nunca use AVG para custo por tonelada, disponibilidade ou utilizacao. Criticidade, Pareto acumulado e filtro por tipo de manutencao estao fora deste piloto. Nao invente dados para periodos sem registros.';
