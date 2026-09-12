# Completar a entrega do Power BI

Os dois estudos já têm dados, SQL, medidas DAX e consultas M. Para apresentar um dashboard finalizado no portfólio, complete os passos no Power BI Desktop e publique o arquivo resultante.

1. Siga o roteiro do README do estudo e aponte `PastaDados` para os CSVs tratados. As consultas auxiliares `TabelasComerciais` e `TabelasProjetos` retornam registros de tabelas; mantenha desabilitada a carga dessas auxiliares e carregue as consultas individuais das fatos e dimensões.
2. Confira os tipos, as chaves e os relacionamentos. Colunas de dinheiro em centavos são inteiras; as medidas fazem a conversão para reais.
3. Crie as medidas separadamente. Os arquivos `.dax` não são scripts para colar inteiros em uma única medida.
4. Monte as páginas sugeridas, incluindo filtros de período e dimensões pertinentes. Use títulos que expressem o indicador e a unidade.
5. Valide o total geral com o resumo JSON. Use o [roteiro de validação](validacao-power-bi.md) para conferir recortes de mês e loja/equipe, incluindo seleções sem dados.
6. Revise as interações entre gráficos, os filtros, os totais e o tratamento de seleções sem dados. Evite mostrar zero quando a taxa não puder ser calculada.
7. Salve `analise-comercial.pbix` ou `indicadores-projetos.pbix` na pasta `powerbi` do respectivo estudo. Feche e abra o arquivo para confirmar que ele funciona.
8. Capture as páginas do próprio Power BI e salve as imagens em uma pasta `imagens` do estudo. Atualize o README para apontar às capturas reais e informar a versão do Desktop usada na validação.
9. Publique os arquivos pelo GitHub e confira os links. O README deve refletir o estado efetivo da entrega.

## Aparência

O tema compartilhado usa azul `#2563EB`, verde-água `#14B8A6`, fundo claro `#F8FAFC` e texto escuro `#0F172A`. Use cinza `#475569` em texto secundário e vermelho `#DC2626` apenas para chamar atenção a situações que exijam ação, sem depender exclusivamente da cor.

Priorize espaçamento consistente, poucas cores por página, rótulos legíveis e unidades explícitas. Use uma captura do painel em tamanho confortável para leitura no README.

## O que deve acompanhar o arquivo

- Origem e natureza dos dados, com a identificação de que são sintéticos neste caso.
- Perguntas de negócio, definições dos indicadores e premissas.
- Modelo de dados e instruções para atualizar a fonte no computador de outra pessoa.
- Evidências de validação, limitações e principais decisões técnicas.

Um `.pbix` pode carregar dados importados. Use neste portfólio os exemplos sintéticos ou bases cuja divulgação esteja autorizada. Os arquivos pessoais da seleção FIESC e seus materiais restritos não fazem parte destes estudos.
