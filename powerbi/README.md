# Abrir e personalizar os projetos Power BI

O portfólio inclui dois projetos editáveis, com modelo semântico em `model.bim` e páginas no formato PBIR. Os dados são sintéticos e públicos. A estrutura foi validada; a execução e a aparência ainda precisam ser verificadas no Power BI Desktop.

## Primeira abertura

1. Use o **Power BI Desktop para Windows** com suporte a PBIP e PBIR. A edição otimizada para Power BI Report Server não oferece suporte a esses projetos.
2. Em **Arquivo → Opções e configurações → Opções → Recursos de visualização**, habilite as opções de projeto Power BI `.pbip` e formato aprimorado de relatório PBIR, se aparecerem na sua versão. Reinicie o Desktop quando solicitado.
3. [Baixe o ZIP completo](https://github.com/Peruzini/NOVOREPOSIT/archive/refs/heads/main.zip), extraia e use uma pasta curta, como `C:\BI\Portfolio`. Abra o arquivo na pasta extraída, não dentro do ZIP.
4. Abra [Comercial.pbip](comercial/Comercial.pbip) ou [Projetos.pbip](projetos/Projetos.pbip). Baixar apenas o `.pbip` é insuficiente: ele aponta para as pastas do relatório e do modelo.
5. Clique em **Atualizar**. Escolha autenticação **Anônimo** para `https://raw.githubusercontent.com` se solicitado. A primeira atualização exige internet, pois não há cache de dados incluído.
6. Sem filtros, compare os cartões com os números abaixo e faça os recortes do [roteiro de validação](../docs/validacao-power-bi.md).

| Projeto e página inicial | Valores esperados |
| --- | --- |
| Comercial — Visão geral | Receita: **R$ 450.903,00**; lucro bruto: **R$ 179.268,00**; margem: **39,76%**; ticket: **R$ 399,38** |
| Projetos — Carteira | **180** demandas; **102** concluídas; **78** abertas; **68** abertas em atraso |

Também é possível abrir `Comercial.Report/definition.pbir` ou `Projetos.Report/definition.pbir`; cada um referencia seu modelo por um caminho relativo.

## O que cada página responde

| Projeto | Página | Foco |
| --- | --- | --- |
| Comercial | Visão geral | Receita, lucro, margem, ticket e evolução mensal |
| Comercial | Lojas e categorias | Composição das vendas e resultado por loja |
| Comercial | Vendedores | Pedidos, receita e ticket por vendedor |
| Projetos | Carteira | Situação das demandas e backlog vencido |
| Projetos | Prazos | Ciclo, lead time e cumprimento de prazo, com seleção por **mês de criação** |
| Projetos | Entregas | Conclusões e entregas no prazo, com seleção por **mês de conclusão** |

Os filtros são independentes entre páginas. Uma seleção em uma página não deve ser presumida na seguinte. Os gráficos e as tabelas filtram os indicadores da própria página.

Na página **Entregas**, todas as medidas usam a relação de conclusão com o calendário, diretamente por `USERELATIONSHIP` ou por medidas que o utilizam. Nas outras páginas de demandas, a relação temporal padrão é a de criação. As demandas abertas ficam fora do cálculo de ciclo e da taxa de entregas no prazo.

## Dados e atualização

As consultas carregam os CSVs de `dados/tratados` do commit **a0b11aefd23d71c05243a04217890980a41d47e0**, publicado antes da criação dos relatórios. Fixar a versão mantém os resultados de demonstração reproduzíveis; os projetos não acompanham automaticamente mudanças posteriores na branch `main`.

Os valores monetários são inteiros em centavos, convertidos em reais nas medidas DAX. O calendário é ampliado no Power Query para **01/01/2025 a 31/12/2026**, com datas contínuas, únicas e anos completos. Essa ampliação não cria novas vendas ou demandas.

Para usar resultados de uma execução local do Python, abra **Transformar dados → Editor Avançado** em cada tabela e substitua apenas a chamada `Web.Contents(...)` por `File.Contents(...)`, apontando para o CSV correspondente. Exemplo de expressão M:

```powerquery
File.Contents("C:\BI\Portfolio\projetos\analise-comercial\dados\tratados\FatoVendas.csv")
```

Mantenha `Csv.Document`, os tipos e as demais etapas. Faça a troca também nas dimensões e no calendário, para não misturar fontes. A expressão acima deve entrar no lugar de `Web.Contents(...)`, e não substituir toda a consulta.

## Concluir a validação no Desktop

Confira os relacionamentos na exibição de modelo, a tabela de datas, os filtros e as interações. Verifique os cartões e os recortes de mês e loja. Revise o texto, a legibilidade e eventuais barras de rolagem, especialmente na comparação de vendedores.

Salve, feche e reabra o projeto; execute outra atualização. Depois use **Arquivo → Salvar como → Power BI `.pbix`**. Registre a versão do Desktop e os recortes conferidos, e publique capturas do relatório efetivamente aberto. Atualize o estado da entrega nos READMEs somente depois dessa etapa.

O arquivo [validacao-estrutural.json](validacao-estrutural.json) registra o que foi verificado por código. A validação de esquema não executa Power Query, DAX nem a renderização dos visuais.

Uma primeira captura da página Carteira confirmou os totais e os agrupamentos sem filtros. A [revisão visual registrada](../docs/validacao-power-bi.md#revisão-visual-recebida--página-carteira) descreve essa evidência e os ajustes de cor e altura do título. Para receber alterações publicadas depois de baixar o projeto, extraia o ZIP atualizado em outra pasta e abra essa cópia, preservando suas edições anteriores. O botão Atualizar busca dados; ele não baixa alterações na definição do relatório do GitHub.

## Solução de problemas

| Sintoma | Ação |
| --- | --- |
| Modelo ou relatório não encontrado | Extraia o ZIP inteiro e preserve a estrutura de pastas |
| Cartões vazios na primeira abertura | Execute Atualizar; o repositório não inclui cache de dados |
| Credenciais recusadas | Revise as permissões da fonte `raw.githubusercontent.com` e selecione Anônimo |
| Formato ou versão não reconhecidos | Confira suporte a PBIP/PBIR e as opções de visualização do Desktop |
| Indicadores diferentes dos exemplos | Limpe filtros, seleções e verifique a fonte; siga o roteiro de validação |
| Um mês não tem resultados | Há vendas somente em 2025; meses adicionais do calendário podem não ter fatos |

Se surgir um erro ao abrir, registre a mensagem completa e o arquivo indicado pelo Desktop para localizar o ajuste necessário.

## Reproduzir os arquivos por código — opcional

Os arquivos já estão incluídos. Para regenerá-los, use Node.js 18 ou superior, na raiz do repositório:

```bash
node scripts/gerar-projetos-powerbi.mjs
```

O gerador lê os cabeçalhos dos CSVs e os arquivos de medidas DAX dos estudos. Ele interrompe a execução se uma saída existente tiver conteúdo diferente. Preserve edições feitas no Desktop antes de usar a opção `--overwrite`; ela restaura a definição gerada. Ao alterar o tema no gerador, um nome baseado no conteúdo atualiza sua referência no relatório.

Para repetir a validação estática, use Python com `jsonschema >= 4.18` e uma cópia do repositório oficial de esquemas:

```bash
python -m pip install "jsonschema>=4.18"
git clone https://github.com/microsoft/json-schemas.git ../json-schemas
python scripts/validar-projetos-powerbi.py --schemas ../json-schemas --write-report
```

Essas ferramentas de desenvolvimento não são necessárias para abrir os relatórios. O pipeline de dados continua usando somente a biblioteca padrão do Python.

## Referências técnicas

- [Projetos Power BI Desktop e conversão para PBIX](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Estrutura do relatório e formato PBIR](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [Modelo semântico e arquivo model.bim](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset)
- [Esquemas JSON oficiais](https://github.com/microsoft/json-schemas)

[Voltar ao portfólio](../README.md)
