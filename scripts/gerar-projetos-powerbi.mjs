/**
 * Gera projetos PBIP/PBIR editáveis a partir das especificações deste portfólio.
 * Não executa o motor DAX/M nem substitui a validação no Power BI Desktop.
 * Node.js 18+. Execute na raiz: node scripts/gerar-projetos-powerbi.mjs
 * Fontes: Microsoft Learn e microsoft/json-schemas (links em powerbi/README.md).
 */
import { existsSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dataCommit = 'a0b11aefd23d71c05243a04217890980a41d47e0';
const schemaRoot = 'https://developer.microsoft.com/json-schemas/fabric/';
const schema = (path) => schemaRoot + path + '/schema.json';
const palette = { blue: '#2563EB', teal: '#0F766E', amber: '#D97706', ink: '#0F172A', muted: '#475569', red: '#DC2626', bg: '#F8FAFC', border: '#E2E8F0', white: '#FFFFFF' };
const theme = {
  name: 'Portfolio Rafael Peruzini',
  dataColors: [palette.blue, palette.teal, palette.amber, '#7C3AED', palette.red, '#0891B2'],
  background: palette.white, foreground: palette.ink, tableAccent: palette.blue,
  textClasses: {
    label: { fontFace: 'Segoe UI', fontSize: 11, color: palette.muted },
    title: { fontFace: 'Segoe UI Semibold', fontSize: 13, color: palette.ink },
    callout: { fontFace: 'Segoe UI Semibold', fontSize: 24, color: palette.ink }
  }
};
const studies = [
  { id: 'comercial', name: 'Comercial', folder: 'analise-comercial', fact: 'FatoVendas', tables: ['DimCalendario', 'DimLoja', 'DimProduto', 'DimVendedor', 'FatoVendas'],
    relations: [['Data', 'DimCalendario', 'Data', true], ['LojaID', 'DimLoja', 'LojaID', true], ['ProdutoID', 'DimProduto', 'ProdutoID', true], ['VendedorID', 'DimVendedor', 'VendedorID', true]] },
  { id: 'projetos', name: 'Projetos', folder: 'indicadores-projetos', fact: 'FatoDemandas', tables: ['DimCalendario', 'DimEquipe', 'FatoDemandas'],
    relations: [['DataCriacao', 'DimCalendario', 'Data', true], ['DataConclusao', 'DimCalendario', 'Data', false], ['EquipeID', 'DimEquipe', 'EquipeID', true]] }
];
const textColumns = new Set(['Loja', 'UF', 'Produto', 'Categoria', 'Vendedor', 'Equipe', 'TipoDemanda', 'Prioridade', 'Status', 'AnoMes']);
const moneyMeasures = new Set(['Receita Bruta', 'Descontos', 'Receita Liquida', 'Custo', 'Lucro Bruto', 'Ticket Medio', 'Receita Mes Anterior']);
const measureDescriptions = {
  'Receita Bruta': 'Vendas válidas e concluídas antes dos descontos. Centavos convertidos em reais.',
  'Descontos': 'Desconto calculado e arredondado por linha, em reais.',
  'Receita Liquida': 'Receita bruta menos descontos. Não inclui impostos, frete ou devoluções.',
  'Custo': 'Quantidade vendida multiplicada pelo custo unitário, em reais.',
  'Lucro Bruto': 'Receita líquida menos custo da mercadoria; não é lucro líquido.',
  'Margem Bruta': 'Lucro bruto total dividido pela receita líquida total, com ponderação pelo faturamento.',
  'Pedidos': 'Contagem distinta de VendaID. Neste exemplo cada pedido tem um único item.',
  'Unidades Vendidas': 'Soma das quantidades das vendas válidas.',
  'Ticket Medio': 'Receita líquida dividida pela quantidade distinta de pedidos.',
  'Receita Mes Anterior': 'Receita no conjunto de datas deslocado um mês para trás. Use em análise mensal.',
  'Variacao Receita Mensal': 'Variação relativa ao mês anterior; em branco se um dos períodos não tem receita.',
  'Demandas': 'Contagem distinta das demandas válidas na fotografia de 31/12/2025.',
  'Concluidas': 'Demandas com status Concluida, respeitando a seleção de status.',
  'Backlog Aberto': 'Demandas a fazer ou em andamento na data fixa de referência.',
  'Em Andamento': 'Demandas com trabalho iniciado e ainda não concluído na fotografia.',
  'Abertas em Atraso': 'Demandas abertas cujo prazo é anterior a 31/12/2025.',
  'Entregas no Prazo': 'Demandas concluídas até o prazo inclusive; abertas têm indicador nulo.',
  'Taxa de Entregas no Prazo': 'Entregas no prazo divididas pelas concluídas, sob o filtro de criação.',
  'Tempo Medio de Ciclo': 'Média de conclusão menos início, em dias corridos; somente concluídas.',
  'Lead Time Medio': 'Média de conclusão menos criação, em dias corridos; somente concluídas.',
  'Data de Referencia': 'Data fixa da fotografia, sem dependência do relógio do computador.',
  'Concluidas por Data de Entrega': 'Concluídas filtradas pelo calendário de conclusão, usando USERELATIONSHIP.',
  'Percentual do Backlog em Atraso': 'Abertas vencidas divididas pelo backlog aberto.',
  'No Prazo por Data de Entrega': 'Concluídas no prazo filtradas pela data de conclusão.',
  'Taxa no Prazo por Data de Entrega': 'Proporção de entregas no prazo entre as concluídas no período de entrega.',
  'Ciclo por Data de Entrega': 'Tempo médio de ciclo das concluídas no período de entrega.'
};

function measures(study) {
  const source = readFileSync(resolve(root, `projetos/${study.folder}/powerbi/medidas.dax`), 'utf8').replace(/^\s*\/\/.*$/gm, '').trim();
  return source.split(/\n\s*\n/).map(block => {
    const separator = block.indexOf('=');
    if (separator < 1) throw new Error('Medida sem definição: ' + block);
    const name = block.slice(0, separator).trim();
    const formatString = moneyMeasures.has(name) ? '"R$" #,0.00'
      : /Margem|Variacao|Taxa|Percentual/.test(name) ? '0.00%'
      : /Ciclo|Lead Time/.test(name) ? '0.00'
      : name === 'Data de Referencia' ? 'dd/MM/yyyy' : '#,0';
    if (!measureDescriptions[name]) throw new Error('Documente a nova medida: ' + name);
    return { name, expression: block.slice(separator + 1).trim().split('\n'), formatString, description: measureDescriptions[name] };
  });
}

function typeOf(name) {
  if (name.startsWith('Data')) return { dataType: 'dateTime', m: 'type date' };
  if (name.endsWith('ID') || textColumns.has(name)) return { dataType: 'string', m: 'type text' };
  return { dataType: 'int64', m: 'Int64.Type' };
}

function queryM(study, table, columns) {
  const relative = `Peruzini/NOVOREPOSIT/${dataCommit}/projetos/${study.folder}/dados/tratados/${table}.csv`;
  const lines = [
    'let',
    '    Fonte = Csv.Document(',
    '        Web.Contents("https://raw.githubusercontent.com",',
    `            [RelativePath="${relative}"]),`,
    '        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
    '    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),',
    '    Nulos = Table.ReplaceValue(Cabecalho, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalho)),',
    '    Tipos = Table.TransformColumnTypes(Nulos, {' + columns.map(c => `{"${c}", ${typeOf(c).m}}`).join(', ') + '}, "en-US")'
  ];
  if (table === 'DimCalendario') {
    lines[lines.length - 1] += ',';
    lines.push(
      '    Inicio = Date.StartOfYear(List.Min(Tipos[Data])),',
      '    Fim = Date.EndOfYear(List.Max(Tipos[Data])),',
      '    Datas = Table.FromList(List.Dates(Inicio, Duration.Days(Fim - Inicio) + 1, #duration(1, 0, 0, 0)), Splitter.SplitByNothing(), {"Data"}),',
      '    DataTipada = Table.TransformColumnTypes(Datas, {{"Data", type date}}),',
      '    Ano = Table.AddColumn(DataTipada, "Ano", each Date.Year([Data]), Int64.Type),',
      '    Mes = Table.AddColumn(Ano, "Mes", each Date.Month([Data]), Int64.Type),',
      '    AnoMes = Table.AddColumn(Mes, "AnoMes", each Date.ToText([Data], "yyyy-MM", "en-US"), type text),',
      '    Completo = Table.AddColumn(AnoMes, "Dia", each Date.Day([Data]), Int64.Type)',
      'in', '    Completo'
    );
  } else lines.push('in', '    Tipos');
  return lines;
}

function semanticModel(study) {
  const tables = study.tables.map(name => {
    const csv = readFileSync(resolve(root, `projetos/${study.folder}/dados/tratados/${name}.csv`), 'utf8');
    const columns = csv.split(/\r?\n/, 1)[0].split(',');
    const table = {
      name,
      columns: columns.map((column, index) => {
        const definition = { name: column, dataType: typeOf(column).dataType, sourceColumn: column, summarizeBy: 'none' };
        if (name.startsWith('Dim') && index === 0) definition.isKey = true;
        if (column.endsWith('ID') || column.endsWith('Centavos')) definition.isHidden = true;
        if (definition.dataType === 'dateTime') {
          definition.formatString = 'dd/MM/yyyy';
          definition.annotations = [{ name: 'UnderlyingDateTimeDataType', value: 'Date' }];
        }
        return definition;
      }),
      partitions: [{ name, mode: 'import', source: { type: 'm', expression: queryM(study, name, columns) } }]
    };
    if (name === 'DimCalendario') table.dataCategory = 'Time';
    if (name === study.fact) table.measures = measures(study);
    return table;
  });
  return {
    name: study.name, compatibilityLevel: 1600,
    model: {
      culture: 'pt-BR', defaultPowerBIDataSourceVersion: 'powerBI_V3', sourceQueryCulture: 'en-US', tables,
      relationships: study.relations.map(([fromColumn, toTable, toColumn, isActive]) => ({
        name: `${study.fact}_${fromColumn}_${toTable}`, fromTable: study.fact, fromColumn, fromCardinality: 'many',
        toTable, toColumn, toCardinality: 'one', crossFilteringBehavior: 'oneDirection', isActive
      })),
      annotations: [{ name: '__PBI_TimeIntelligenceEnabled', value: '0' }, { name: 'PBI_QueryOrder', value: JSON.stringify(study.tables) }]
    }
  };
}

const literal = value => ({ expr: { Literal: { Value: typeof value === 'string' ? "'" + value.replace(/'/g, "''") + "'" : typeof value === 'number' ? value + 'D' : String(value) } } });
const fill = color => ({ solid: { color: literal(color) } });
const properties = (values, selector) => [{ properties: values, ...(selector ? { selector } : {}) }];
const padding = size => properties(Object.fromEntries(['top', 'bottom', 'left', 'right'].map(side => [side, literal(size)])));
const uid = value => createHash('sha256').update(value).digest('hex').slice(0, 20);
const projection = (kind, table, name, label = name) => ({
  field: { [kind]: { Expression: { SourceRef: { Entity: table } }, Property: name } },
  queryRef: table + '.' + name, nativeQueryRef: name, displayName: label
});
const column = (table, name, label) => projection('Column', table, name, label);
const metric = (study, name, label) => projection('Measure', study.fact, name, label);
const chrome = (title = '', inset = 12) => ({
  background: properties({ show: literal(true), color: fill(palette.white), transparency: literal(0) }),
  border: properties({ show: literal(true), color: fill(palette.border), radius: literal(8), width: literal(1) }),
  padding: padding(inset),
  title: properties({ show: literal(Boolean(title)), text: literal(title), fontSize: literal(12), fontColor: fill(palette.ink), fontFamily: literal('Segoe UI Semibold') }),
  subTitle: properties({ show: literal(false) }),
  visualHeader: properties({ show: literal(false) })
});

function visualPage(study, spec) {
  const visuals = [];
  function add(key, type, x, y, width, height, body) {
    const serial = visuals.length + 1;
    const result = {
      $schema: schema('item/report/definition/visualContainer/2.9.0'),
      name: uid(`${study.id}/${spec.key}/${key}`),
      position: { x, y, width, height, z: serial * 1000, tabOrder: serial * 1000 },
      visual: { visualType: type, ...body }
    };
    visuals.push(result);
    return result;
  }
  function textbox(key, text, y, height, size, color, bold = false) {
    return add(key, 'textbox', 24, y, 1232, height, {
      objects: { general: properties({ paragraphs: [{ textRuns: [{ value: text, textStyle: { fontFamily: bold ? 'Segoe UI Semibold' : 'Segoe UI', fontSize: size + 'px', color } }], horizontalTextAlignment: 'left' }] }) },
      visualContainerObjects: { background: properties({ show: literal(false) }), border: properties({ show: literal(false) }), padding: padding(0), title: properties({ show: literal(false) }), visualHeader: properties({ show: literal(false) }) }
    });
  }
  // Reserve room for Desktop's textbox line box, which can exceed the font size.
  textbox('title', spec.title, 8, 48, 28, palette.ink, true);
  textbox('subtitle', spec.subtitle, 60, 24, 13, palette.muted);
  spec.slicers.forEach(([table, name, label], i) => add('slicer' + i, 'slicer', 24 + 416 * i, 92, 400, 80, {
    query: { queryState: { Values: { projections: [column(table, name, label)] } } },
    objects: {
      data: properties({ mode: literal('Dropdown') }),
      header: properties({ show: literal(true), text: literal(label), fontSize: literal(11), fontColor: fill(palette.ink) }),
      items: properties({ fontSize: literal(11), fontColor: fill(palette.muted) })
    }, visualContainerObjects: chrome('', 8)
  }));
  spec.cards.forEach(([name, label, color = palette.ink], i) => {
    const selector = { id: 'default' };
    add('card' + i, 'cardVisual', 24 + 312 * i, 184, 296, 120, {
      query: { queryState: { Data: { projections: [metric(study, name, label)] } } },
      objects: {
        value: properties({ fontSize: literal(24), fontColor: fill(color), displayUnits: literal(0) }, selector),
        label: properties({ show: literal(true), text: literal(label), fontSize: literal(11), fontColor: fill(palette.muted) }, selector),
        outline: properties({ show: literal(false) }, selector),
        padding: properties({ paddingUniform: literal(8) }, selector),
        layout: properties({ paddingUniform: literal(0) }, selector),
        spacing: properties({ verticalSpacing: literal(6) }, selector)
      }, visualContainerObjects: chrome()
    });
  });
  spec.charts.forEach((chart, i) => {
    const measures = chart.measures.map(([name, label]) => metric(study, name, label));
    const categories = chart.columns.map(([table, name, label]) => column(table, name, label));
    const colors = chart.colors || [palette.blue, palette.teal];
    const sortField = chart.type === 'lineChart' ? categories[0].field : measures[0].field;
    const query = { queryState: chart.type === 'tableEx' ? { Values: { projections: [...categories, ...measures] } } : { Category: { projections: categories }, Y: { projections: measures } }, sortDefinition: { sort: [{ field: sortField, direction: chart.type === 'lineChart' ? 'Ascending' : 'Descending' }] } };
    const objects = chart.type === 'tableEx' ? {
      columnHeaders: properties({ autoSizeColumnWidth: literal(true), columnAdjustment: literal('growToFit'), fontSize: literal(10), fontColor: fill(palette.ink), backColor: fill(palette.bg) }),
      values: properties({ fontSize: literal(10), backColorPrimary: fill(palette.white), backColorSecondary: fill(palette.bg), fontColorPrimary: fill(palette.ink), fontColorSecondary: fill(palette.ink) })
    } : {
      categoryAxis: properties({ show: literal(true), fontSize: literal(10), labelColor: fill(palette.muted) }),
      valueAxis: properties({ show: literal(true), fontSize: literal(10), labelColor: fill(palette.muted) }),
      legend: properties({ show: literal(measures.length > 1), fontSize: literal(10) }),
      labels: properties({ show: literal(chart.type !== 'lineChart'), fontSize: literal(10), color: fill(palette.ink) }),
      // A single measure without a legend uses the default color. Metadata
      // selectors are retained for multiple measures, preserving distinct series.
      dataPoint: measures.length === 1
        ? properties({ defaultColor: fill(colors[0]) })
        : measures.flatMap((m, index) => properties({ fill: fill(colors[index % colors.length]) }, { metadata: m.queryRef }))
    };
    add('chart' + i, chart.type, chart.x, 324, chart.width, 340, {
      query, objects, visualContainerObjects: {
        ...chrome(chart.title),
        ...(chart.type === 'tableEx' ? { stylePreset: properties({ name: literal('None') }) } : {})
      }, drillFilterOtherVisuals: true
    });
  });
  textbox('footer', spec.footer, 684, 24, 12, palette.muted);
  const chartTypes = new Set(['tableEx', 'clusteredBarChart', 'lineChart']);
  const targets = visuals.filter(v => chartTypes.has(v.visual.visualType) || v.visual.visualType === 'cardVisual');
  const page = {
    $schema: schema('item/report/definition/page/2.1.0'), name: uid(study.id + '/' + spec.key), displayName: spec.name,
    displayOption: 'FitToPage', height: 720, width: 1280,
    objects: { background: properties({ color: fill(palette.bg), transparency: literal(0) }) },
    visualInteractions: visuals.filter(v => chartTypes.has(v.visual.visualType)).flatMap(source => targets.filter(target => target.name !== source.name).map(target => ({ source: source.name, target: target.name, type: 'DataFilter' })))
  };
  return { page, visuals };
}

const month = ['DimCalendario', 'AnoMes', 'Mês'];
const loja = ['DimLoja', 'Loja', 'Loja'];
const categoria = ['DimProduto', 'Categoria', 'Categoria'];
const equipe = ['DimEquipe', 'Equipe', 'Equipe'];
const prioridade = ['FatoDemandas', 'Prioridade', 'Prioridade'];
const pages = {
  comercial: [
    { key: 'visao-geral', name: '1 | Visão geral', title: 'ANÁLISE COMERCIAL', subtitle: 'Receita, margem e evolução mensal · Dados sintéticos de 2025 · Rafael Peruzini',
      slicers: [month, ['DimLoja', 'UF', 'Estado'], categoria],
      cards: [['Receita Liquida', 'Receita líquida', palette.blue], ['Lucro Bruto', 'Lucro bruto', palette.teal], ['Margem Bruta', 'Margem bruta'], ['Ticket Medio', 'Ticket médio']],
      charts: [
        { type: 'lineChart', x: 24, width: 744, title: 'Evolução da receita líquida', columns: [month], measures: [['Receita Liquida', 'Receita líquida']] },
        { type: 'clusteredBarChart', x: 784, width: 472, title: 'Receita líquida por loja', columns: [loja], measures: [['Receita Liquida', 'Receita líquida']] }
      ], footer: 'Margem = lucro bruto / receita líquida. Receita considera descontos; impostos, frete e devoluções não foram modelados.' },
    { key: 'lojas-categorias', name: '2 | Lojas e categorias', title: 'LOJAS E CATEGORIAS', subtitle: 'Compare receita, margem e composição das vendas · Dados sintéticos · Rafael Peruzini',
      slicers: [month, loja, categoria],
      cards: [['Receita Liquida', 'Receita líquida', palette.blue], ['Margem Bruta', 'Margem bruta', palette.teal], ['Pedidos', 'Pedidos'], ['Unidades Vendidas', 'Unidades vendidas']],
      charts: [
        { type: 'clusteredBarChart', x: 24, width: 440, title: 'Receita por categoria', columns: [categoria], measures: [['Receita Liquida', 'Receita líquida']] },
        { type: 'tableEx', x: 480, width: 776, title: 'Resultado por loja', columns: [loja, ['DimLoja', 'UF', 'UF']], measures: [['Receita Liquida', 'Receita líquida'], ['Lucro Bruto', 'Lucro bruto'], ['Margem Bruta', 'Margem']] }
      ], footer: 'O ranking indica onde investigar. Compare mix, descontos e custo antes de recomendar uma ação comercial.' },
    { key: 'vendedores', name: '3 | Vendedores', title: 'DESEMPENHO DE VENDAS', subtitle: 'Distribuição de pedidos, receita e ticket médio · Dados sintéticos · Rafael Peruzini',
      slicers: [month, loja, ['DimVendedor', 'Vendedor', 'Vendedor']],
      cards: [['Receita Liquida', 'Receita líquida', palette.blue], ['Pedidos', 'Pedidos', palette.teal], ['Ticket Medio', 'Ticket médio'], ['Unidades Vendidas', 'Unidades vendidas']],
      charts: [
        { type: 'clusteredBarChart', x: 24, width: 512, title: 'Receita por vendedor', columns: [['DimVendedor', 'Vendedor', 'Vendedor']], measures: [['Receita Liquida', 'Receita líquida']] },
        { type: 'tableEx', x: 552, width: 704, title: 'Pedidos e ticket por vendedor', columns: [['DimVendedor', 'Vendedor', 'Vendedor']], measures: [['Pedidos', 'Pedidos'], ['Receita Liquida', 'Receita líquida'], ['Ticket Medio', 'Ticket médio']] }
      ], footer: 'Volume de vendas não mede produtividade individual sem metas, horas trabalhadas e oportunidades atendidas.' }
  ],
  projetos: [
    { key: 'carteira', name: '1 | Carteira', title: 'CARTEIRA DE DEMANDAS', subtitle: 'Fotografia de 31/12/2025 · Dados sintéticos · Rafael Peruzini',
      slicers: [equipe, prioridade, ['FatoDemandas', 'TipoDemanda', 'Tipo de demanda']],
      cards: [['Demandas', 'Demandas', palette.blue], ['Concluidas', 'Concluídas', palette.teal], ['Backlog Aberto', 'Backlog aberto'], ['Abertas em Atraso', 'Abertas em atraso', palette.red]],
      charts: [
        { type: 'clusteredBarChart', x: 24, width: 600, title: 'Demandas por situação', columns: [['FatoDemandas', 'Status', 'Situação']], measures: [['Demandas', 'Demandas']] },
        { type: 'clusteredBarChart', x: 640, width: 616, title: 'Abertas em atraso por equipe', columns: [equipe], measures: [['Abertas em Atraso', 'Abertas em atraso']], colors: [palette.red] }
      ], footer: 'Atraso: demanda aberta com prazo anterior a 31/12/2025. Esta fotografia não reconstitui o backlog histórico diário.' },
    { key: 'prazos', name: '2 | Prazos', title: 'PRAZOS E FLUXO', subtitle: 'Tempos de atendimento e cumprimento de prazo · Seleção por data de criação · Dados sintéticos',
      slicers: [equipe, prioridade, ['DimCalendario', 'AnoMes', 'Mês de criação']],
      cards: [['Tempo Medio de Ciclo', 'Ciclo médio · dias', palette.blue], ['Lead Time Medio', 'Lead time médio · dias'], ['Taxa de Entregas no Prazo', 'Entregas no prazo', palette.teal], ['Percentual do Backlog em Atraso', 'Backlog em atraso', palette.red]],
      charts: [
        { type: 'clusteredBarChart', x: 24, width: 600, title: 'Ciclo e lead time por equipe · dias', columns: [equipe], measures: [['Tempo Medio de Ciclo', 'Ciclo'], ['Lead Time Medio', 'Lead time']] },
        { type: 'tableEx', x: 640, width: 616, title: 'Cumprimento de prazo por equipe', columns: [equipe], measures: [['Concluidas', 'Concluídas'], ['Entregas no Prazo', 'No prazo'], ['Taxa de Entregas no Prazo', 'Taxa no prazo']] }
      ], footer: 'Tempos em dias corridos, somente entre concluídas. Diferenças entre equipes não controlam complexidade ou capacidade.' },
    { key: 'entregas', name: '3 | Entregas', title: 'EVOLUÇÃO DAS ENTREGAS', subtitle: 'Indicadores filtrados pela data de conclusão · Dados sintéticos · Rafael Peruzini',
      slicers: [['DimCalendario', 'AnoMes', 'Mês de entrega'], equipe, prioridade],
      cards: [['Concluidas por Data de Entrega', 'Concluídas', palette.blue], ['No Prazo por Data de Entrega', 'Concluídas no prazo', palette.teal], ['Taxa no Prazo por Data de Entrega', 'Taxa de entregas no prazo'], ['Ciclo por Data de Entrega', 'Ciclo médio · dias']],
      charts: [
        { type: 'lineChart', x: 24, width: 744, title: 'Entregas por mês de conclusão', columns: [month], measures: [['Concluidas por Data de Entrega', 'Concluídas']] },
        { type: 'clusteredBarChart', x: 784, width: 472, title: 'Entregas no prazo por equipe', columns: [equipe], measures: [['Taxa no Prazo por Data de Entrega', 'Taxa no prazo']], colors: [palette.teal] }
      ], footer: 'As medidas desta página usam a data de conclusão (USERELATIONSHIP). Demandas abertas não entram no denominador.' }
  ]
};

const files = [];
const put = (path, value) => files.push({ path, content: JSON.stringify(value, null, 2) + '\n' });
const inventory = [];
for (const study of studies) {
  const base = `powerbi/${study.id}`;
  const report = `${base}/${study.name}.Report`;
  const model = `${base}/${study.name}.SemanticModel`;
  put(`${base}/${study.name}.pbip`, { $schema: schema('pbip/pbipProperties/1.0.0'), version: '1.0', artifacts: [{ report: { path: `${study.name}.Report` } }], settings: { enableAutoRecovery: true } });
  put(`${report}/definition.pbir`, { $schema: schema('item/report/definitionProperties/2.0.0'), version: '4.0', datasetReference: { byPath: { path: `../${study.name}.SemanticModel` } } });
  put(`${model}/definition.pbism`, { $schema: schema('item/semanticModel/definitionProperties/1.0.0'), version: '1.0', settings: { qnaEnabled: false } });
  const bim = semanticModel(study);
  put(`${model}/model.bim`, bim);
  put(`${report}/definition/version.json`, { $schema: schema('item/report/definition/versionMetadata/1.0.0'), version: '2.0.0' });
  const themeFile = 'Portfolio-' + uid(JSON.stringify(theme)) + '.json';
  put(`${report}/StaticResources/RegisteredResources/${themeFile}`, theme);
  put(`${report}/definition/report.json`, {
    $schema: schema('item/report/definition/report/3.3.0'),
    themeCollection: { customTheme: { name: themeFile, reportVersionAtImport: { visual: '2.9.0', report: '3.3.0', page: '2.1.0' }, type: 'RegisteredResources' } },
    resourcePackages: [{ name: 'RegisteredResources', type: 'RegisteredResources', items: [{ name: themeFile, path: themeFile, type: 'CustomTheme' }] }]
  });
  const definitions = pages[study.id].map(spec => visualPage(study, spec));
  put(`${report}/definition/pages/pages.json`, { $schema: schema('item/report/definition/pagesMetadata/1.0.0'), pageOrder: definitions.map(p => p.page.name), activePageName: definitions[0].page.name });
  for (const { page, visuals } of definitions) {
    const pagePath = `${report}/definition/pages/${page.name}`;
    put(`${pagePath}/page.json`, page);
    for (const visual of visuals) put(`${pagePath}/visuals/${visual.name}/visual.json`, visual);
  }
  inventory.push({ project: study.name, tables: study.tables.length, measures: bim.model.tables.flatMap(t => t.measures || []).length, relationships: bim.model.relationships.length, pages: definitions.map(d => ({ name: d.page.displayName, id: d.page.name, visuals: d.visuals.length })) });
}
put('powerbi/tema.json', theme);

// Avoid silently replacing work saved later by the user in Power BI Desktop.
const changes = files.filter(file => existsSync(resolve(root, file.path)) && readFileSync(resolve(root, file.path), 'utf8') !== file.content);
if (changes.length && !process.argv.includes('--overwrite')) {
  throw new Error('Arquivos existentes seriam alterados. Preserve suas edições antes de usar --overwrite:\n' + changes.map(f => f.path).join('\n'));
}
for (const file of files) {
  mkdirSync(dirname(resolve(root, file.path)), { recursive: true });
  writeFileSync(resolve(root, file.path), file.content, 'utf8');
}
console.log(JSON.stringify({ files: files.length, dataCommit, inventory, desktopValidation: 'Pendente: abrir, atualizar, conferir interações e salvar PBIX no Power BI Desktop.' }, null, 2));
