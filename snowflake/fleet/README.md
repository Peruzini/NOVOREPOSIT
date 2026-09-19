# Fleet — piloto Power BI, SQL e Snowflake Cortex

**Implementado para revisão:** gerador local, consultas de referência, scripts Snowflake, camada semântica e definição de agente. **Executado nesta entrega:** Python e SQLite, com 11 testes aprovados. **Pendente:** Power Query/DAX no Desktop, compilação e execução Snowflake e respostas reais do Cortex.

O objetivo é conferir o mesmo indicador no painel, em SQL e em uma conversa com IA. Todos os dados são sintéticos. O código local não usa credenciais e não acessa contas externas.

## O que foi corrigido no PBIP desta versão

| Problema observado | Ajuste |
| --- | --- |
| 731 dias incluíam 01/01/2027 | Calendário e fatos limitados aos 730 dias de 2025–2026 |
| Falhas contava qualquer manutenção | Contagem apenas de eventos corretivos; zero quando não há falhas |
| MTTR incluía horas preventivas e inspeções | Horas corretivas / falhas corretivas |
| Pareto acumulava horas com posição do ranking de criticidade | Acumulação por horas de manutenção, com desempate por nome |
| Gerador permitia operação acima das horas disponíveis | Horas de operação limitadas a 24 menos horas de manutenção; produção recalculada |

São alterações funcionais no [modelo PBIP](../../powerbi/fleet/FleetAnalytics.SemanticModel/model.bim). Os 34 nomes de medidas foram preservados para manter as referências dos visuais. Os números de produção, utilização, falhas, MTTR, MTBF e criticidade podem mudar. A aprovação visual e numérica deve usar esta mesma versão do modelo.

## Executar a parte local

Requisito: Python 3.10 ou superior, apenas biblioteca padrão. Execute na raiz do repositório:

```bash
python -m unittest discover -s snowflake/fleet/tests -v
python snowflake/fleet/pilot.py --database PORTFOLIO --schema FLEET_PILOT_V1 --warehouse COMPUTE_WH
```

Substitua os três nomes por identificadores do seu ambiente antes de gerar os scripts. Use letras maiúsculas, números e sublinhado. O script gera `snowflake/fleet/build/` com CSV, resultados esperados, manifesto e cinco scripts SQL com os nomes preenchidos. Essa pasta fica fora do Git. Para repetir, escolha uma pasta nova com `--output snowflake/fleet/build/segunda-execucao`.

A saída possui **5.840 linhas**, uma por dia e equipamento, cobrindo oito equipamentos entre 01/01/2025 e 31/12/2026. O gerador reproduz em Python as fórmulas sintéticas do Power Query desta versão; não executa M nem DAX. Arredondamento decimal e eventuais diferenças do motor precisam ser conferidos no Desktop.

## Conferir primeiro no Power BI Desktop

1. Baixe o repositório completo da branch deste piloto; mantenha `FleetAnalytics.pbip`, `.Report` e `.SemanticModel` juntos em `powerbi/fleet/`.
2. Abra `FleetAnalytics.pbip`, atualize e confira as quatro páginas.
3. Execute [desktop-check.dax](evaluation/desktop-check.dax) na Exibição de consulta DAX.
4. Compare o resultado com [local-expected.json](evaluation/local-expected.json), bloco `01_january_2026`.

| Indicador em janeiro de 2026 | Referência local esperada |
| --- | ---: |
| Produção | 42.950,0 t |
| Horas de operação | 4.576 h |
| Manutenção total | 75 h |
| Horas corretivas | 45 h |
| Falhas corretivas | 9 |
| Custo total | R$ 1.877.658,28 |
| Custo por tonelada | R$ 43,717306/t |
| Disponibilidade física | 98,739919% |
| Utilização | 77,862855% |
| MTTR | 5 h |
| MTBF | 508,444444 h |

Esses valores foram calculados em Python/SQLite. Ainda não são resultados observados no Power BI ou no Snowflake. Compare valores brutos: contagens/horas devem coincidir, produção até 0,1 t e dinheiro até R$ 0,01 no total; razões com tolerância absoluta de 0,000001. Investigue qualquer diferença acima disso antes de ajustar tolerâncias.

No Pareto, ordene o visual por horas de manutenção decrescentes e nome crescente para os empates. Confira se o acumulado é crescente e termina em 100%; o total da medida fica vazio. Teste também sem falhas e seleções de equipamento. Registre versão do Desktop, commit, data e filtros da captura.

## Executar no Snowflake

Use uma conta autorizada, banco existente, warehouse existente e perfil com permissões para os objetos do piloto e Cortex. Não há conexão Snowflake disponível nesta revisão; estes passos serão executados no seu ambiente.

1. Em uma worksheet Snowsight, execute `build/01_setup.sql`. O schema escolhido precisa ser novo. Se houver erro, pare; o script não substitui objetos existentes.
2. Envie `build/fleet_daily.csv` para o stage `FLEET_STAGE`, preservando o nome.
3. Execute `build/02_load.sql` somente com a tabela vazia. Não force a recarga nem renomeie o CSV para carregá-lo novamente.
4. Execute `build/03_quality.sql`: confira 5.840 linhas, oito equipamentos, datas corretas e zero resultados nas consultas de inconsistências.
5. Execute os cinco arquivos de [evaluation/queries](evaluation/queries) no banco/schema do piloto e compare com o JSON de referência. A execução local desses mesmos SELECTs usa SQLite, não valida o dialeto de implantação Snowflake.
6. Execute `build/04_semantic.sql` e `build/05_agent.sql`. Confira compilação, permissões e disponibilidade das funções na conta.
7. Em Snowsight, abra o agente `FLEET_ASSISTANT`, teste as perguntas abaixo e registre respostas e SQL gerado.

| Pergunta de avaliação | Referência |
| --- | --- |
| Qual foi a produção total em janeiro de 2026? | `01_january_2026` |
| Qual foi o custo por tonelada de cada equipamento em janeiro de 2026? | `02_equipment_january` |
| Quais cinco equipamentos tiveram mais horas de manutenção em janeiro de 2026? | `03_top5_maintenance` |
| Como a produção de janeiro de 2026 mudou em relação a dezembro de 2025? | `04_month_comparison` |
| Qual foi a produção em janeiro de 2027? | `05_empty_period`: ausência de dados, sem produção inventada |
| Qual foi a produção? | Pedir período antes de responder |
| Qual equipamento é mais crítico? | Explicar que criticidade está fora da camada semântica deste piloto |

As instruções do agente não garantem comportamento. A homologação precisa observar respostas, SQL, contexto e permissões do usuário final. Não há taxa de acerto publicada nesta versão.

## Regras e limites

Leia [contrato-de-metricas.md](contrato-de-metricas.md). A tabela diária consolida cada fato no mesmo grão para evitar multiplicação de linhas. O piloto usa métricas aditivas e razões dos totais; não oferece criticidade, Pareto acumulado ou filtro por tipo de manutenção ao agente. Esses cálculos exigem uma etapa específica para reproduzir o contexto de seleção do Power BI.

O gerador Python antigo em `projetos/fleet-dax-advanced/scripts/gerar_dados.py` é um cenário independente. Seus CSVs não são a base de reconciliação deste piloto. Use o CSV produzido por `snowflake/fleet/pilot.py`.

Os arquivos de `evaluation/local-*` registram referências desta revisão; `local-manifest.json` inclui o hash do modelo usado. Qualquer alteração no modelo ou no gerador exige uma nova comparação e atualização das evidências.

## Fontes de implementação

- [CREATE SEMANTIC VIEW](https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view)
- [CREATE AGENT](https://docs.snowflake.com/en/sql-reference/sql/create-agent)
- [Recursos de ferramentas Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-rest-api)

[Voltar ao portfólio](../../README.md)
