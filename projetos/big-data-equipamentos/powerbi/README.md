# Consumir os resultados no Power BI

Esta entrega contém consulta M, medidas DAX e orientação de layout. Não contém PBIX/PBIP de EquipAnalytics; os relatórios Power BI existentes no restante do repositório são outros estudos.

## Teste com os resultados conhecidos

1. Power BI Desktop → Obter dados → Texto/CSV.
2. Selecione examples/monthly_kpis.csv deste projeto.
3. Renomeie a consulta para FatoConsumo.
4. Use localidade Inglês (Estados Unidos) para ler números com ponto decimal; eventos e alertas são inteiros.
5. Mantenha year_month como texto e os demais campos numéricos como números decimais.
6. Crie as medidas de medidas.dax, uma por vez.
7. Confira 360 L, 4 horas, R$ 2.160, 90 L/h e taxa de alertas 25%.

Esse CSV é um resultado esperado calculado para a amostra; execute os testes para confrontá-lo com o Spark.

## Dados gerados pelo pipeline

Use a consulta de importar.m e ajuste PastaCSV para a pasta exports/monthly_kpis de uma execução concluída. Ela combina somente arquivos part-*.csv, excluindo _SUCCESS e arquivos de controle.

Modelo inicial: fato agregada por mês × unidade × categoria. Se criar dimensões, extraia chaves distintas dessa fato, conecte em um-para-muitos com filtro único da dimensão para a fato. Não relacione gold/equipment diretamente ao agregado: o agregado mensal não tem equipment_id. Para uma página de equipamentos, importe o CSV equipment_alerts como segunda fato e compartilhe dimensões de unidade/categoria se necessário.

## Layout sugerido

- Cartões: consumo, custo estimado, horas, L/h ponderado e taxa de alertas.
- Segmentações: mês, unidade e categoria.
- Linha: evolução mensal de consumo.
- Barras: L/h por categoria e unidade; contextualizar referências antes de comparar.
- Tabela: equipamentos, quantidade de alertas e custo, com ranking de investigação.
- Qualidade em página própria: métricas de rejeição da execução, sem relacioná-las indevidamente aos filtros mensais.

As métricas de qualidade de metrics.json descrevem a execução completa. Não variam por mês/unidade sem uma agregação adicional de qualidade, que não está implementada.

A taxa de rejeição não aparece no CSV mensal porque a Silver já excluiu erros. Uma página de qualidade deve identificar explicitamente o escopo da execução.

Para volume maior, importar agregados ou usar uma camada SQL adequada ao ambiente; evitar importar milhões de linhas só para exibir somas mensais.
