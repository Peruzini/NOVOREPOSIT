-- 1. Totais da fotografia de 31/12/2025, conciliados com Python.
SELECT COUNT(*) AS linhas_validas,
       COALESCE(SUM(CASE WHEN Status = 'Concluida' THEN 1 ELSE 0 END), 0) AS concluidas,
       COALESCE(SUM(CASE WHEN Status != 'Concluida' THEN 1 ELSE 0 END), 0) AS backlog,
       COALESCE(SUM(EmAtraso), 0) AS em_atraso
FROM FatoDemandas;

-- 2. Prazo e ciclo por equipe. A taxa no prazo considera somente demandas concluidas.
SELECT e.Equipe, COUNT(*) AS demandas,
       SUM(CASE WHEN f.Status = 'Concluida' THEN 1 ELSE 0 END) AS concluidas,
       SUM(f.EmAtraso) AS abertas_em_atraso,
       ROUND(AVG(f.TempoCicloDias), 2) AS ciclo_medio_dias_corridos,
       ROUND(100.0 * SUM(f.EntregueNoPrazo) / NULLIF(SUM(CASE WHEN f.Status = 'Concluida' THEN 1 ELSE 0 END), 0), 2) AS entregas_no_prazo_pct
FROM FatoDemandas f
JOIN DimEquipe e ON e.EquipeID = f.EquipeID
GROUP BY e.EquipeID, e.Equipe
ORDER BY abertas_em_atraso DESC, e.Equipe;

-- 3. Entregas por mes de conclusao, independente da data de criacao.
SELECT SUBSTR(DataConclusao, 1, 7) AS mes_entrega, COUNT(*) AS concluidas,
       ROUND(AVG(TempoCicloDias), 2) AS ciclo_medio_dias_corridos
FROM FatoDemandas
WHERE Status = 'Concluida'
GROUP BY SUBSTR(DataConclusao, 1, 7)
ORDER BY mes_entrega;

-- 4. Trabalho em progresso e backlog sao indicadores distintos.
SELECT Status, COUNT(*) AS demandas, SUM(EsforcoPlanejadoHoras) AS horas_planejadas
FROM FatoDemandas
GROUP BY Status
ORDER BY Status;

-- 5. Demandas vencidas e abertas, usando a data fixa do estudo e nao a data atual.
SELECT DemandaID, EquipeID, Prioridade, Status, DataPrazo,
       CAST(julianday(DataReferencia) - julianday(DataPrazo) AS INTEGER) AS dias_atraso
FROM FatoDemandas
WHERE EmAtraso = 1
ORDER BY DataPrazo, DemandaID;
