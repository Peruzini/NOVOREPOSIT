-- Rode em uma sessão Spark que tenha criado silver_events a partir do Parquet.
-- Ajuste o mês à execução. EXPLAIN permite inspecionar PartitionFilters.
EXPLAIN FORMATTED
SELECT unit, SUM(liters) AS liters
FROM silver_events
WHERE year_month = '2025-01'
GROUP BY unit
