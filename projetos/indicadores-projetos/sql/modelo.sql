CREATE TABLE DimCalendario (Data TEXT PRIMARY KEY NOT NULL, Ano INTEGER NOT NULL, Mes INTEGER NOT NULL, AnoMes TEXT NOT NULL, Dia INTEGER NOT NULL);
CREATE TABLE DimEquipe (EquipeID TEXT PRIMARY KEY NOT NULL, Equipe TEXT NOT NULL);
CREATE TABLE FatoDemandas (
    DemandaID TEXT PRIMARY KEY NOT NULL,
    DataCriacao TEXT NOT NULL REFERENCES DimCalendario(Data),
    DataInicio TEXT,
    DataConclusao TEXT,
    DataPrazo TEXT NOT NULL,
    EquipeID TEXT NOT NULL REFERENCES DimEquipe(EquipeID),
    TipoDemanda TEXT NOT NULL,
    Prioridade TEXT NOT NULL,
    Status TEXT NOT NULL CHECK (Status IN ('Concluida', 'Em andamento', 'A fazer')),
    EsforcoPlanejadoHoras INTEGER NOT NULL CHECK (EsforcoPlanejadoHoras >= 0),
    EsforcoRealHoras INTEGER NOT NULL CHECK (EsforcoRealHoras >= 0),
    DataReferencia TEXT NOT NULL,
    TempoCicloDias INTEGER,
    LeadTimeDias INTEGER,
    EmAtraso INTEGER NOT NULL CHECK (EmAtraso IN (0, 1)),
    EntregueNoPrazo INTEGER CHECK (EntregueNoPrazo IN (0, 1)),
    CHECK (Status != 'Concluida' OR (DataInicio IS NOT NULL AND DataConclusao IS NOT NULL))
);
CREATE INDEX ix_demandas_equipe ON FatoDemandas(EquipeID);
CREATE INDEX ix_demandas_status_prazo ON FatoDemandas(Status, DataPrazo);
