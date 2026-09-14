# Contrato de dados e indicadores

## Grão e período

Cada linha representa um intervalo de operação de um equipamento e seu consumo estimado em litros. Não é um evento de abastecimento: compras, estoque em tanque e abastecimento não permitem inferir diretamente consumo horário.

O gerador distribui IDs entre 1.000 equipamentos. A cada mil eventos avança uma hora, a partir de 01/01/2025 00:00 UTC. Aumentar o volume amplia o horizonte temporal. A semente afeta o ruído de consumo e o preço; os defeitos são injetados por divisibilidade do ID. Não existe aleatoriedade dependente da quantidade de partições.

## Entrada Bronze

| Campo | Tipo de entrada | Regra |
| --- | --- | --- |
| event_id | string | Convertível para inteiro longo, não negativo |
| equipment_id | string | Chave de 0 a 999 na dimensão de referência |
| event_time | string | yyyy-MM-dd HH:mm:ss, tratado como UTC |
| liters | string | Decimal positivo; NaN, infinito e texto são inválidos |
| operating_minutes | string | Decimal maior que zero e até 1.440 |
| price_cents_per_liter | string | Decimal positivo em centavos por litro |
| ingest_sequence | long | Ordem técnica usada para selecionar versão |

O contrato do gerador usa strings inteiras para IDs; o pipeline usa casts do Spark. Formatos não padronizados de ID precisam de uma validação lexical adicional antes de ingestão real. Não há ingestão genérica de fontes reais.

## Deduplicação e qualidade

1. Converter tipos em modo não ANSI para que valores não convertíveis virem nulos.
2. Para IDs convertíveis, reter maior ingest_sequence; desempatar por SHA-256 dos campos brutos.
3. Guardar versões anteriores separadamente. IDs ausentes ou não convertíveis seguem individualmente para rejeição.
4. Aplicar as regras em ordem: ID, timestamp, equipamento, litros, minutos, preço.
5. Registrar somente o primeiro motivo por registro; a métrica por motivo soma o total de rejeitados.

Uma versão mais recente inválida vai para quarentena. Não se recupera silenciosamente uma versão antiga válida. Duplicatas exatas empatadas são semanticamente idênticas; qualquer cópia preserva o mesmo conteúdo.

A dimensão deve ter chave única; duplicidade bloqueia o processamento para impedir multiplicação de fatos em uma junção.

## Indicadores

| Indicador | Definição |
| --- | --- |
| Eventos | Quantidade de linhas Silver |
| Consumo | Soma de litros dos eventos válidos |
| Horas operacionais | Soma de operating_minutes / 60 |
| Consumo horário | Soma de litros / soma de horas; não média de L/h por evento |
| Custo estimado | Soma do custo de cada evento; litros × centavos por litro / 100, arredondado por evento a 2 casas |
| Alerta de consumo | L/h do evento estritamente maior que 1,5 × referência da categoria |
| Taxa de alertas | Eventos com alerta / eventos válidos |
| Rejeição após deduplicação | Rejeitados / (válidos + rejeitados) |
| Reconciliação | Bronze = válidos + rejeitados + versões duplicadas |

Referências inteiramente fictícias: caminhão 90 L/h, escavadeira 50 L/h e carregadeira 70 L/h. Não são especificações de fabricantes, padrões de engenharia ou limites legais. A fronteira exata de 1,5 vez a referência não dispara alerta. Os alertas são mantidos nos indicadores, sem excluir valores altos arbitrariamente.

Não há garantia de ausência de sobreposição temporal em fontes externas; em produção, validar intervalos, horímetro, calibração e duplicidade de medições entre sistemas.
