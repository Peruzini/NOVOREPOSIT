-- Ranking operacional; sinal de investigação, não diagnóstico.
WITH equipment AS (
  SELECT equipment_id, unit, equipment_type,
         COUNT(*) AS events, SUM(liters) AS liters,
         SUM(operating_minutes) / 60.0 AS operating_hours,
         SUM(liters) * 60.0 / SUM(operating_minutes) AS liters_per_hour,
         SUM(cost_brl) AS cost_brl,
         SUM(CASE WHEN high_consumption THEN 1 ELSE 0 END) AS alerts
  FROM silver_events
  GROUP BY equipment_id, unit, equipment_type
)
SELECT *, DENSE_RANK() OVER (ORDER BY alerts DESC, cost_brl DESC) AS investigation_rank
FROM equipment
ORDER BY investigation_rank, equipment_id
