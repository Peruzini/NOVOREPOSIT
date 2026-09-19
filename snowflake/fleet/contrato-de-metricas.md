# Contrato de métricas — Fleet Pilot v1

Regra canônica proposta para este piloto demonstrativo. Não representa regras aprovadas por cliente. A versão PBIP desta branch implementa as correções; a conferência do motor DAX está pendente.

## Grão e filtros

- Uma linha por data × equipamento na tabela `FLEET_DAILY`.
- Período fechado: 01/01/2025 a 31/12/2026.
- Dimensões disponíveis no agente: dia, equipamento, tipo de equipamento e área.
- Custos em BRL, produção em toneladas, duração em horas.
- As somas consideram os mesmos filtros em todos os componentes de uma razão.
- Não há custo de pessoal, depreciação ou estoque. Custo total significa combustível mais manutenção do cenário.

## Definições

| Medida Power BI | Definição canônica | Colunas do piloto |
| --- | --- | --- |
| Produção Total | Soma da produção | `PRODUCAO_TON` |
| Horas Operação | Soma de horas efetivamente operadas | `HORAS_OPERACAO` |
| Horas Manutenção | Soma de corretiva, preventiva e inspeção | `HORAS_MANUTENCAO` |
| Falhas | Quantidade de eventos corretivos, zero sem eventos | `FALHAS` |
| MTTR | Soma de horas corretivas / quantidade de falhas corretivas | `HORAS_CORRETIVAS`, `FALHAS` |
| MTBF | Soma de horas operadas / quantidade de falhas corretivas | `HORAS_OPERACAO`, `FALHAS` |
| Custo Total | Soma de manutenção mais combustível | `CUSTO_MANUTENCAO`, `CUSTO_COMBUSTIVEL` |
| Custo por Tonelada | Custo total / produção total | Razão das somas |
| Disponibilidade Física % | (Horas calendário − manutenção total) / horas calendário | Razão das somas |
| Utilização % | Horas operadas / (horas calendário − manutenção total) | Razão das somas |
| Aderência Meta % | Produção total / meta total | `PRODUCAO_TON`, `META_PRODUCAO_TON` |

Denominador zero produz `BLANK` no DAX e `NULL` no SQL. Sem registros, produção fica vazia; falhas retorna zero. Nunca interpretar ausência de dados como produção zero. As razões são números de 0 a 1 antes da formatação percentual; aderência pode superar 1.

O MTBF é uma aproximação agregada em horas operadas por evento corretivo, não uma análise de sobrevivência nem uma média de intervalos cronológicos entre reparos.

## Criticidade e Pareto

O PBIP preserva pesos 35/25/20/20. O primeiro componente é `1 - disponibilidade`; custo por tonelada, falhas e horas de manutenção usam razão para o máximo no contexto selecionado. Não é normalização min-max. O catálogo didático continua com componentes, pesos e esquema distintos.

O Pareto do PBIP ordena manutenção em horas, de forma decrescente, e desempata por nome do equipamento. A definição do Top 5 SQL desempata por ID; é uma consulta independente, não uma prova de equivalência do Pareto.

Criticidade e Pareto ficam fora do agente v1 porque exigem homologar o universo de comparação e o contexto equivalente a `ALLSELECTED`. Uma pergunta sobre esses assuntos deve ser identificada como fora do escopo, sem cálculo improvisado.

## Evidência ainda necessária

Uma migração só pode ser declarada validada após comparar a mesma versão da base em Power Query/DAX, SQL Snowflake e resposta do agente. Os testes locais comprovam regras da referência Python/SQLite, não compilação ou execução dos demais motores.
