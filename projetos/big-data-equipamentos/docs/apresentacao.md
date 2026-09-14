# Como apresentar em entrevista ou proposta

## Apresentação em dois minutos

“Este é um estudo demonstrativo de análise de consumo operacional de equipamentos. Organizei um pipeline PySpark que preserva dados recebidos, separa erros e versões duplicadas e produz indicadores mensais e um ranking de equipamentos para investigação.

O ponto de negócio é impedir que dados inválidos contaminem o painel e comparar consumo levando em conta as horas de operação. Por isso calculo litros totais divididos por horas totais, em vez de tirar a média dos índices individuais.

O projeto inclui SQL com janela, Parquet particionado e testes com resultados conhecidos. O gerador permite experimentar volumes maiores; eu só apresento como executados os volumes que tenham evidência nos logs. A demonstração local ainda não representa uma implantação em cluster.”

## Perguntas que você precisa saber responder

- Por que consumo não é igual a abastecimento? O estoque do tanque, perdas, transferências e intervalo de medição importam.
- Por que alertas permanecem na Silver? Valor alto pode ser uma observação válida; qualidade estrutural e desvio operacional são conceitos diferentes.
- Por que quarentena? Para investigar erros e reconciliar o recebimento com o resultado.
- Por que broadcast? A dimensão possui apenas 1.000 equipamentos; não generalizar para dimensão grande.
- Por que partição mensal? Facilita leitura por período sem criar uma partição por equipamento/evento.
- Por que não publicar um ganho percentual de performance? Não existe benchmark medido para sustentá-lo.
- O que falta para produção? Contratos reais, segurança, armazenamento compartilhado, transações, reprocessamento, monitoramento e testes de volume.

## Ofertas de serviço relacionadas

- Diagnóstico de qualidade de dados e organização de bases operacionais.
- Construção de indicadores e dashboards de consumo, manutenção e produtividade.
- Automação de tratamento e consolidação de dados com Python e SQL.
- Prova de conceito de processamento batch com PySpark.

Delimitar fontes, volumes, regras, infraestrutura, prazo e critérios de aceite antes de propor preço. Apresentar o estudo como portfólio demonstrativo, sem atribuir seus números a um trabalho realizado para uma empresa.
