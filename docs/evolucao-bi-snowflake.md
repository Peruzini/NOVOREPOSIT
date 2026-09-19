# Evolução de BI para consultas por IA no Snowflake

**Status: piloto implementado em código, com execução local.** Consulte [snowflake/fleet](../snowflake/fleet/README.md) para gerar dados, executar 11 testes e preparar os scripts Snowflake/Cortex. A validação no Power BI Desktop, a compilação/execução Snowflake e as respostas do agente ainda estão pendentes. Este documento mantém o roteiro de evolução e os critérios de aceite.

## Objetivo

Permitir que uma mesma pergunta de negócio tenha uma resposta conferível no painel, em SQL e em uma interface de IA. O primeiro recorte proposto é produção, manutenção e custo por equipamento e período.

A origem e o destino de uma migração real precisam ser definidos com o cliente: podem envolver dados, modelos, relatórios ou ambientes de publicação. Este estudo não presume que todos os painéis serão substituídos por agentes.

## Etapas e evidências esperadas

| Etapa | Trabalho | Evidência a produzir |
| --- | --- | --- |
| Diagnóstico | Inventariar fontes, tabelas, medidas, filtros e dependências | Inventário de um painel e lista priorizada de divergências |
| Regra canônica | Definir granularidade, numerador, denominador, período e exclusões de cada KPI | Dicionário de indicadores aprovado para o piloto |
| Reconciliação | Comparar SQL e Power BI com os mesmos dados e recortes | Tabela de esperado, observado, diferença e situação |
| Camada Snowflake | Preparar tabelas/views e documentar relações e métricas | Scripts de implantação e execução registrados |
| Consulta por IA | Configurar Cortex Analyst e, conforme o caso, Cortex Agents | Configuração do piloto e perguntas de referência |
| Aceite | Comparar respostas, filtros, permissões e custos observados | Relatório de execução e pendências |

Cortex Analyst oferece consultas em linguagem natural sobre dados estruturados por meio de uma camada semântica. Cortex Agents pode orquestrar ferramentas como Analyst e Search. O uso de Search deve responder a uma necessidade concreta de documentos ou conteúdo não estruturado. Ver [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) e [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents).

## Primeiro ajuste: alinhar o significado dos indicadores

A [documentação do Fleet](../projetos/fleet-dax-advanced/README.md) registra diferenças entre PBIP e catálogo. As decisões do primeiro piloto estão no [contrato de métricas](../snowflake/fleet/contrato-de-metricas.md). Os pontos que precisam ser explicitados em qualquer migração são:

- se “falha” inclui todos os eventos de manutenção ou apenas eventos corretivos sinalizados;
- se MTTR considera somente horas corretivas;
- se criticidade usa custo por tonelada ou custo total de manutenção;
- se a dimensão de perda significa horas de parada ou gap de produção;
- qual normalização, população de comparação e comportamento de filtro devem ser mantidos.

Uma medida DAX dependente de contexto de filtro não deve ser tratada como uma tradução textual para SQL. O critério de equivalência será o resultado da regra acordada para cada seleção.

## Perguntas do piloto

Os exemplos abaixo orientam a homologação. Há [resultados locais de referência](../snowflake/fleet/evaluation/local-expected.json) para produção, custo, manutenção e comparação mensal; as respostas do Power BI/Snowflake/Cortex ainda precisam ser observadas. Criticidade permanece fora do agente v1.

| Pergunta | Comparação necessária | Critério proposto |
| --- | --- | --- |
| Qual foi a produção em janeiro de 2026? | Soma de produção no mesmo período | Mesmo total na precisão armazenada |
| Qual foi o custo por tonelada por equipamento? | Soma de custos / soma de produção | Calcular a razão dos totais; tolerância monetária definida antes do teste |
| Quais cinco equipamentos tiveram mais horas de manutenção? | Ranking com regra de empate explícita | Mesmos equipamentos, horas e ordenação |
| Como a produção mudou em relação ao mês anterior? | Períodos completos e regra para denominador zero | Mesmo valor ou ausência de resultado conforme a regra |
| Qual equipamento é mais crítico? | Pesos, população e filtros explícitos | Pedir esclarecimento quando período ou universo estiverem indefinidos |
| Qual a produção de um período sem registros? | Tratamento acordado de ausência de dados | Diferenciar ausência de dados de produção zero |

Para cada execução, registrar pergunta, data, versão da base, filtros, SQL de referência, resposta do Power BI, resposta do agente e diferença. Nenhuma taxa de acerto está sendo declarada nesta proposta.

## Critérios para publicar como case concluído

1. Abrir, atualizar e conferir o PBIP no Power BI Desktop, registrando a versão utilizada.
2. Executar as consultas de referência e reconciliar totais, recortes e casos de ausência de dados.
3. Implantar o piloto Snowflake em ambiente autorizado e registrar a configuração.
4. Validar as perguntas com o perfil de acesso do usuário final e revisar as respostas.
5. Publicar capturas reais e um resumo de resultados medidos, incluindo divergências restantes.

## Organização do piloto

| Caminho implementado | Conteúdo |
| --- | --- |
| `snowflake/fleet/sql/` | DDL, views e consultas de referência |
| `snowflake/fleet/semantic/` | Definição da camada semântica e regras das métricas |
| `snowflake/fleet/agent/` | Configuração e instruções do agente |
| `snowflake/fleet/evaluation/` | Perguntas, resultados esperados e avaliações executadas |

As pastas contêm scripts e referências locais. O [contrato de métricas](../snowflake/fleet/contrato-de-metricas.md) define as regras adotadas no piloto; a existência dos scripts não significa implantação concluída. Criticidade e Pareto dependem de uma etapa adicional de equivalência de contexto.
