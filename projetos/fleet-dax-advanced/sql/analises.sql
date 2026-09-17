-- Fleet Analytics — consultas de apoio e validação
-- Sintaxe deliberadamente próxima de SQL ANSI/SQLite para facilitar reprodução.

-- 1. Produção e utilização por equipamento
SELECT
    o.EquipamentoID,
    e.Equipamento,
    e.TipoEquipamento,
    ROUND(SUM(o.Toneladas), 2) AS ProducaoTotalTon,
    ROUND(SUM(o.HorasOperadas), 2) AS HorasOperadas,
    ROUND(
        SUM(o.HorasOperadas) / NULLIF(SUM(o.HorasDisponiveis), 0),
        4
    ) AS UtilizacaoPct,
    ROUND(
        SUM(o.Toneladas) / NULLIF(SUM(o.HorasOperadas), 0),
        2
    ) AS ProdutividadeTonHora
FROM FatoOperacao o
JOIN DimEquipamento e
  ON e.EquipamentoID = o.EquipamentoID
GROUP BY
    o.EquipamentoID,
    e.Equipamento,
    e.TipoEquipamento;

-- 2. Disponibilidade física por equipamento
SELECT
    o.EquipamentoID,
    ROUND(
        SUM(o.HorasDisponiveis) / NULLIF(SUM(o.HorasCalendario), 0),
        4
    ) AS DisponibilidadeFisicaPct
FROM FatoOperacao o
GROUP BY o.EquipamentoID
ORDER BY DisponibilidadeFisicaPct ASC;

-- 3. MTBF e MTTR por equipamento
WITH falhas AS (
    SELECT
        EquipamentoID,
        COUNT(*) AS QtdeFalhas,
        SUM(CASE WHEN TipoManutencao = 'Corretiva' THEN HorasParada ELSE 0 END) AS HorasCorretivas
    FROM FatoManutencao
    WHERE FalhaFlag = 1
    GROUP BY EquipamentoID
),
operacao AS (
    SELECT
        EquipamentoID,
        SUM(HorasOperadas) AS HorasOperadas
    FROM FatoOperacao
    GROUP BY EquipamentoID
)
SELECT
    o.EquipamentoID,
    ROUND(o.HorasOperadas / NULLIF(f.QtdeFalhas, 0), 2) AS MTBF_h,
    ROUND(f.HorasCorretivas / NULLIF(f.QtdeFalhas, 0), 2) AS MTTR_h,
    f.QtdeFalhas
FROM operacao o
LEFT JOIN falhas f
  ON f.EquipamentoID = o.EquipamentoID
ORDER BY MTBF_h ASC;

-- 4. Pareto de horas de manutenção usando funções de janela
WITH base AS (
    SELECT
        m.EquipamentoID,
        e.Equipamento,
        SUM(m.HorasParada) AS HorasManutencao
    FROM FatoManutencao m
    JOIN DimEquipamento e
      ON e.EquipamentoID = m.EquipamentoID
    GROUP BY m.EquipamentoID, e.Equipamento
),
pareto AS (
    SELECT
        *,
        SUM(HorasManutencao) OVER (
            ORDER BY HorasManutencao DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS HorasAcumuladas,
        SUM(HorasManutencao) OVER () AS HorasTotais
    FROM base
)
SELECT
    EquipamentoID,
    Equipamento,
    ROUND(HorasManutencao, 2) AS HorasManutencao,
    ROUND(HorasAcumuladas / NULLIF(HorasTotais, 0), 4) AS ParetoAcumuladoPct,
    CASE
        WHEN HorasAcumuladas / NULLIF(HorasTotais, 0) <= 0.80 THEN 'A'
        WHEN HorasAcumuladas / NULLIF(HorasTotais, 0) <= 0.95 THEN 'B'
        ELSE 'C'
    END AS ClassePareto
FROM pareto
ORDER BY HorasManutencao DESC;

-- 5. Produção mensal e média móvel de 3 meses
WITH mensal AS (
    SELECT
        substr(Data, 1, 7) AS AnoMes,
        SUM(Toneladas) AS ProducaoTon
    FROM FatoOperacao
    GROUP BY substr(Data, 1, 7)
)
SELECT
    AnoMes,
    ROUND(ProducaoTon, 2) AS ProducaoTon,
    ROUND(
        AVG(ProducaoTon) OVER (
            ORDER BY AnoMes
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS MediaMovel3Meses
FROM mensal
ORDER BY AnoMes;

-- 6. Custo de manutenção por sistema e participação no total
WITH sistema AS (
    SELECT
        Sistema,
        SUM(CustoManutencao) AS Custo
    FROM FatoManutencao
    GROUP BY Sistema
)
SELECT
    Sistema,
    ROUND(Custo, 2) AS Custo,
    ROUND(Custo / NULLIF(SUM(Custo) OVER (), 0), 4) AS ParticipacaoPct
FROM sistema
ORDER BY Custo DESC;
