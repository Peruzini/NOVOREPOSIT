-- Marketing Analytics | dados sintéticos | SQLite

-- 1) Consolidado mensal
SELECT
    substr(f.Data, 1, 7) AS AnoMes,
    SUM(f.InvestimentoCentavos) / 100.0 AS Investimento,
    SUM(f.ReceitaCentavos) / 100.0 AS ReceitaAtribuida,
    SUM(f.Impressoes) AS Impressoes,
    SUM(f.Cliques) AS Cliques,
    SUM(f.Leads) AS Leads,
    SUM(f.Oportunidades) AS Oportunidades,
    SUM(f.Clientes) AS Clientes,
    1.0 * SUM(f.Cliques) / NULLIF(SUM(f.Impressoes), 0) AS CTR,
    (SUM(f.InvestimentoCentavos) / 100.0) / NULLIF(SUM(f.Leads), 0) AS CPL,
    (SUM(f.InvestimentoCentavos) / 100.0) / NULLIF(SUM(f.Clientes), 0) AS CAC,
    (SUM(f.ReceitaCentavos) / 100.0) / NULLIF(SUM(f.InvestimentoCentavos) / 100.0, 0) AS ROAS
FROM FatoMarketing f
GROUP BY substr(f.Data, 1, 7)
ORDER BY AnoMes;

-- 2) Eficiência por canal
SELECT
    c.Canal,
    SUM(f.InvestimentoCentavos) / 100.0 AS Investimento,
    SUM(f.ReceitaCentavos) / 100.0 AS ReceitaAtribuida,
    SUM(f.Leads) AS Leads,
    SUM(f.Clientes) AS Clientes,
    1.0 * SUM(f.Cliques) / NULLIF(SUM(f.Impressoes), 0) AS CTR,
    (SUM(f.InvestimentoCentavos) / 100.0) / NULLIF(SUM(f.Leads), 0) AS CPL,
    (SUM(f.InvestimentoCentavos) / 100.0) / NULLIF(SUM(f.Clientes), 0) AS CAC,
    (SUM(f.ReceitaCentavos) / 100.0) / NULLIF(SUM(f.InvestimentoCentavos) / 100.0, 0) AS ROAS
FROM FatoMarketing f
JOIN DimCanal c ON c.CanalID = f.CanalID
GROUP BY c.Canal
ORDER BY ROAS DESC;

-- 3) Ranking de campanhas
SELECT
    c.Canal,
    p.Campanha,
    p.Objetivo,
    SUM(f.InvestimentoCentavos) / 100.0 AS Investimento,
    SUM(f.ReceitaCentavos) / 100.0 AS ReceitaAtribuida,
    SUM(f.Leads) AS Leads,
    SUM(f.Clientes) AS Clientes,
    (SUM(f.InvestimentoCentavos) / 100.0) / NULLIF(SUM(f.Clientes), 0) AS CAC,
    (SUM(f.ReceitaCentavos) / 100.0) / NULLIF(SUM(f.InvestimentoCentavos) / 100.0, 0) AS ROAS
FROM FatoMarketing f
JOIN DimCampanha p ON p.CampanhaID = f.CampanhaID
JOIN DimCanal c ON c.CanalID = f.CanalID
GROUP BY c.Canal, p.Campanha, p.Objetivo
ORDER BY ROAS DESC;

-- 4) Funil por canal
SELECT
    c.Canal,
    SUM(f.Cliques) AS Cliques,
    SUM(f.Leads) AS Leads,
    SUM(f.Oportunidades) AS Oportunidades,
    SUM(f.Clientes) AS Clientes,
    1.0 * SUM(f.Leads) / NULLIF(SUM(f.Cliques), 0) AS TaxaCliqueLead,
    1.0 * SUM(f.Oportunidades) / NULLIF(SUM(f.Leads), 0) AS TaxaLeadOportunidade,
    1.0 * SUM(f.Clientes) / NULLIF(SUM(f.Oportunidades), 0) AS TaxaOportunidadeCliente,
    1.0 * SUM(f.Clientes) / NULLIF(SUM(f.Leads), 0) AS TaxaLeadCliente
FROM FatoMarketing f
JOIN DimCanal c ON c.CanalID = f.CanalID
GROUP BY c.Canal
ORDER BY Clientes DESC;
