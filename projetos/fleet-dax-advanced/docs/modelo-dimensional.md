# Modelo dimensional — Fleet Analytics

## Grão das tabelas

| Tabela | Grão |
| --- | --- |
| `DimData` | uma linha por data |
| `DimEquipamento` | uma linha por equipamento |
| `FatoOperacao` | uma linha por equipamento por dia |
| `FatoManutencao` | uma linha por evento de manutenção |
| `FatoMeta` | uma linha por data e tipo de equipamento |

## Relacionamentos recomendados

| Origem | Destino | Cardinalidade | Direção |
| --- | --- | --- | --- |
| `DimData[Data]` | `FatoOperacao[Data]` | 1:N | simples |
| `DimData[Data]` | `FatoManutencao[DataInicio]` | 1:N | simples |
| `DimData[Data]` | `FatoMeta[Data]` | 1:N | simples |
| `DimEquipamento[EquipamentoID]` | `FatoOperacao[EquipamentoID]` | 1:N | simples |
| `DimEquipamento[EquipamentoID]` | `FatoManutencao[EquipamentoID]` | 1:N | simples |

`FatoMeta` não possui relação direta com `DimEquipamento`. As metas existem no grão de **tipo de equipamento**, enquanto `DimEquipamento` está no grão de ativo. As medidas de meta usam `TREATAS` para transferir explicitamente o conjunto de tipos selecionados para `FatoMeta[TipoEquipamento]`.

Esse desenho evita criar uma relação muitos-para-muitos apenas para atender às metas e torna explícita, no DAX, a mudança de granularidade.

## Regras de modelagem

1. filtros devem fluir das dimensões para as fatos;
2. evitar relacionamentos bidirecionais sem necessidade comprovada;
3. `DimData` deve ser marcada como tabela de datas;
4. ocultar chaves técnicas e colunas numéricas usadas apenas para ordenação;
5. concentrar cálculos de negócio em medidas, não em colunas calculadas da fato;
6. usar uma tabela exclusiva de medidas no Power BI para organização do modelo;
7. formatar percentuais como `%`, custos como moeda e horas com duas casas decimais.

## Contexto de filtro explorado no case

O projeto foi desenhado para demonstrar três comportamentos importantes do DAX:

### `ALLSELECTED`

Usado em rankings, Pareto e normalização para remover o filtro da linha atual sem ignorar os filtros externos aplicados pelo usuário.

### `TREATAS`

Usado para transferir os tipos de equipamento selecionados em `DimEquipamento` para `FatoMeta`, que opera em granularidade diferente.

### Tabelas virtuais

`ADDCOLUMNS`, `TOPN`, `MINX`, `MAXX` e `SUMX` constroem conjuntos temporários usados no Pareto e no score de criticidade sem materializar novas tabelas físicas no modelo.

## Score de criticidade

O score usa normalização min-max dentro do conjunto atualmente selecionado:

```text
score_normalizado = (valor - mínimo) / (máximo - mínimo)
```

Para disponibilidade, a direção é invertida porque valores menores representam maior criticidade:

```text
score_disp = (máximo - disponibilidade_atual) / (máximo - mínimo)
```

O score final é a média ponderada de:

- baixa disponibilidade;
- falhas;
- custo de manutenção;
- gap positivo de produção.

Os pesos vêm de tabelas desconectadas, permitindo simular prioridades operacionais sem alterar o modelo físico.

## Páginas sugeridas

### 1. Visão Executiva

Cards de produção, disponibilidade, utilização, custo, MTBF e aderência. Linha temporal com realizado x meta e segmentadores de período, tipo e centro de custo.

### 2. Performance da Frota

Matriz de equipamentos com ranking, produção, produtividade, disponibilidade, utilização e consumo específico. Dispersão entre produtividade e disponibilidade.

### 3. Manutenção & Pareto

Pareto de horas de manutenção, custo por sistema, MTBF, MTTR, taxa de falha por 1.000 h e evolução das paradas.

### 4. Criticidade

Segmentadores para os quatro pesos, ranking dinâmico, score, faixa de criticidade e matriz que cruza impacto produtivo e confiabilidade.
