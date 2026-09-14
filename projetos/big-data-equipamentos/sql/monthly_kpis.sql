-- Razão entre somas: não calcular média simples de L/h.
SELECT year_month, unit, equipment_type,
       COUNT(*) AS events,
       SUM(liters) AS liters,
       SUM(operating_minutes) / 60.0 AS operating_hours,
       SUM(liters) * 60.0 / SUM(operating_minutes) AS liters_per_hour,
       SUM(cost_brl) AS cost_brl,
       SUM(CASE WHEN high_consumption THEN 1 ELSE 0 END) AS high_consumption_events
FROM silver_events
GROUP BY year_month, unit, equipment_type
ORDER BY year_month, unit, equipment_type
