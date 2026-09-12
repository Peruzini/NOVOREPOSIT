-- 1. Totais de conciliacao em centavos, sem arredondamento monetario.
SELECT COUNT(*) AS linhas_validas,
       COALESCE(SUM(ReceitaLiquidaCentavos), 0) AS receita_liquida_centavos,
       COALESCE(SUM(LucroBrutoCentavos), 0) AS lucro_bruto_centavos
FROM FatoVendas;

-- 2. Receita e margem por loja. A margem e ponderada pela receita.
SELECT l.Loja, l.UF, COUNT(*) AS vendas,
       ROUND(SUM(v.ReceitaLiquidaCentavos) / 100.0, 2) AS receita_liquida_reais,
       ROUND(SUM(v.LucroBrutoCentavos) / 100.0, 2) AS lucro_bruto_reais,
       ROUND(100.0 * SUM(v.LucroBrutoCentavos) / NULLIF(SUM(v.ReceitaLiquidaCentavos), 0), 2) AS margem_pct
FROM FatoVendas v
JOIN DimLoja l ON l.LojaID = v.LojaID
GROUP BY l.LojaID, l.Loja, l.UF
ORDER BY receita_liquida_reais DESC, l.Loja;

-- 3. Evolucao mensal e ticket medio. Cada VendaID e um unico pedido neste exemplo.
SELECT c.AnoMes, COUNT(DISTINCT v.VendaID) AS pedidos,
       ROUND(SUM(v.ReceitaLiquidaCentavos) / 100.0, 2) AS receita_liquida_reais,
       ROUND(SUM(v.ReceitaLiquidaCentavos) / (100.0 * COUNT(DISTINCT v.VendaID)), 2) AS ticket_medio_reais
FROM FatoVendas v
JOIN DimCalendario c ON c.Data = v.Data
WHERE v.Data >= '2025-01-01' AND v.Data < '2026-01-01'
GROUP BY c.AnoMes
ORDER BY c.AnoMes;

-- 4. Mix de categorias.
SELECT p.Categoria, SUM(v.Quantidade) AS unidades,
       ROUND(SUM(v.ReceitaLiquidaCentavos) / 100.0, 2) AS receita_liquida_reais,
       ROUND(100.0 * SUM(v.LucroBrutoCentavos) / NULLIF(SUM(v.ReceitaLiquidaCentavos), 0), 2) AS margem_pct
FROM FatoVendas v
JOIN DimProduto p ON p.ProdutoID = v.ProdutoID
GROUP BY p.Categoria
ORDER BY receita_liquida_reais DESC, p.Categoria;

-- 5. Faturamento de vendedores. Nao interpreta volume como produtividade sem horas ou metas.
SELECT d.Vendedor, COUNT(DISTINCT v.VendaID) AS pedidos,
       ROUND(SUM(v.ReceitaLiquidaCentavos) / 100.0, 2) AS receita_liquida_reais
FROM FatoVendas v
JOIN DimVendedor d ON d.VendedorID = v.VendedorID
GROUP BY d.VendedorID, d.Vendedor
ORDER BY receita_liquida_reais DESC, d.Vendedor;
