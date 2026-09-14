let
    PastaCSV = "C:\BI\NOVOREPOSIT\projetos\big-data-equipamentos\data\run-100k\exports\monthly_kpis",
    Arquivos = Folder.Files(PastaCSV),
    Partes = Table.SelectRows(Arquivos, each Text.StartsWith([Name], "part-") and [Extension] = ".csv"),
    Tabelas = Table.AddColumn(Partes, "Tabela", each Table.PromoteHeaders(
        Csv.Document([Content], [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
        [PromoteAllScalars=true])),
    Combinado = if Table.RowCount(Tabelas) = 0 then
        error "Nenhum part-*.csv encontrado. Confirme a execução e a pasta."
        else Table.Combine(Tabelas[Tabela]),
    Tipos = Table.TransformColumnTypes(Combinado, {
        {"year_month", type text}, {"unit", type text}, {"equipment_type", type text},
        {"events", Int64.Type}, {"liters", type number}, {"operating_hours", type number},
        {"liters_per_hour", type number}, {"cost_brl", Currency.Type},
        {"high_consumption_events", Int64.Type}
    }, "en-US")
in
    Tipos
