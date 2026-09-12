let
    // Ajuste este caminho. Nome sugerido para a consulta: TabelasComerciais.
    PastaDados = "C:\portfolio\NOVOREPOSIT\projetos\analise-comercial\dados\tratados",
    Ler = (Nome as text, Tipos as list) as table =>
        let
            Fonte = Csv.Document(File.Contents(PastaDados & "/" & Nome & ".csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
            Nulos = Table.ReplaceValue(Cabecalho, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalho)),
            Tipados = Table.TransformColumnTypes(Nulos, Tipos, "en-US")
        in Tipados,
    Calendario = Ler("DimCalendario", {{"Data", type date}, {"Ano", Int64.Type}, {"Mes", Int64.Type}, {"AnoMes", type text}, {"Dia", Int64.Type}}),
    Lojas = Ler("DimLoja", {{"LojaID", type text}, {"Loja", type text}, {"UF", type text}}),
    Produtos = Ler("DimProduto", {{"ProdutoID", type text}, {"Produto", type text}, {"Categoria", type text}}),
    Vendedores = Ler("DimVendedor", {{"VendedorID", type text}, {"Vendedor", type text}}),
    Vendas = Ler("FatoVendas", {{"VendaID", type text}, {"Data", type date}, {"LojaID", type text}, {"ProdutoID", type text}, {"VendedorID", type text}, {"Quantidade", Int64.Type}, {"PrecoUnitarioCentavos", Int64.Type}, {"CustoUnitarioCentavos", Int64.Type}, {"DescontoPct", Int64.Type}, {"Status", type text}, {"ReceitaBrutaCentavos", Int64.Type}, {"DescontoCentavos", Int64.Type}, {"ReceitaLiquidaCentavos", Int64.Type}, {"CustoCentavos", Int64.Type}, {"LucroBrutoCentavos", Int64.Type}})
in
    [DimCalendario=Calendario, DimLoja=Lojas, DimProduto=Produtos, DimVendedor=Vendedores, FatoVendas=Vendas]
