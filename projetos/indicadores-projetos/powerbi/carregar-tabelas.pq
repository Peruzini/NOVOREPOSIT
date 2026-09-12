let
    // Ajuste este caminho. Nome sugerido para a consulta: TabelasProjetos.
    PastaDados = "C:\portfolio\NOVOREPOSIT\projetos\indicadores-projetos\dados\tratados",
    Ler = (Nome as text, Tipos as list) as table =>
        let
            Fonte = Csv.Document(File.Contents(PastaDados & "/" & Nome & ".csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
            Nulos = Table.ReplaceValue(Cabecalho, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalho)),
            Tipados = Table.TransformColumnTypes(Nulos, Tipos, "en-US")
        in Tipados,
    Calendario = Ler("DimCalendario", {{"Data", type date}, {"Ano", Int64.Type}, {"Mes", Int64.Type}, {"AnoMes", type text}, {"Dia", Int64.Type}}),
    Equipes = Ler("DimEquipe", {{"EquipeID", type text}, {"Equipe", type text}}),
    Demandas = Ler("FatoDemandas", {{"DemandaID", type text}, {"DataCriacao", type date}, {"DataInicio", type date}, {"DataConclusao", type date}, {"DataPrazo", type date}, {"EquipeID", type text}, {"TipoDemanda", type text}, {"Prioridade", type text}, {"Status", type text}, {"EsforcoPlanejadoHoras", Int64.Type}, {"EsforcoRealHoras", Int64.Type}, {"DataReferencia", type date}, {"TempoCicloDias", Int64.Type}, {"LeadTimeDias", Int64.Type}, {"EmAtraso", Int64.Type}, {"EntregueNoPrazo", Int64.Type}})
in
    [DimCalendario=Calendario, DimEquipe=Equipes, FatoDemandas=Demandas]
