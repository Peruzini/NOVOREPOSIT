CREATE TABLE DimCalendario (Data TEXT PRIMARY KEY NOT NULL, Ano INTEGER NOT NULL, Mes INTEGER NOT NULL, AnoMes TEXT NOT NULL, Dia INTEGER NOT NULL);
CREATE TABLE DimLoja (LojaID TEXT PRIMARY KEY NOT NULL, Loja TEXT NOT NULL, UF TEXT NOT NULL);
CREATE TABLE DimProduto (ProdutoID TEXT PRIMARY KEY NOT NULL, Produto TEXT NOT NULL, Categoria TEXT NOT NULL);
CREATE TABLE DimVendedor (VendedorID TEXT PRIMARY KEY NOT NULL, Vendedor TEXT NOT NULL);
CREATE TABLE FatoVendas (
    VendaID TEXT PRIMARY KEY NOT NULL,
    Data TEXT NOT NULL REFERENCES DimCalendario(Data),
    LojaID TEXT NOT NULL REFERENCES DimLoja(LojaID),
    ProdutoID TEXT NOT NULL REFERENCES DimProduto(ProdutoID),
    VendedorID TEXT NOT NULL REFERENCES DimVendedor(VendedorID),
    Quantidade INTEGER NOT NULL CHECK (Quantidade > 0),
    PrecoUnitarioCentavos INTEGER NOT NULL CHECK (PrecoUnitarioCentavos >= 0),
    CustoUnitarioCentavos INTEGER NOT NULL CHECK (CustoUnitarioCentavos >= 0),
    DescontoPct INTEGER NOT NULL CHECK (DescontoPct BETWEEN 0 AND 100),
    Status TEXT NOT NULL CHECK (Status = 'Concluida'),
    ReceitaBrutaCentavos INTEGER NOT NULL,
    DescontoCentavos INTEGER NOT NULL,
    ReceitaLiquidaCentavos INTEGER NOT NULL,
    CustoCentavos INTEGER NOT NULL,
    LucroBrutoCentavos INTEGER NOT NULL,
    CHECK (ReceitaLiquidaCentavos = ReceitaBrutaCentavos - DescontoCentavos),
    CHECK (LucroBrutoCentavos = ReceitaLiquidaCentavos - CustoCentavos)
);
CREATE INDEX ix_vendas_data ON FatoVendas(Data);
CREATE INDEX ix_vendas_loja ON FatoVendas(LojaID);
