# -*- coding: utf-8 -*-
"""Fonte unica de verdade para traducoes: dimensoes, indicadores e strings de JS."""

LANGS = ['pt', 'en']

# ---------------------------------------------------------------- dimensoes
DIMS = [
 {'k': 'c1_declive', 'cod': 'C1', 'peso': 0.10,
  'nome': {'pt': 'Declive', 'en': 'Slope'},
  'curto': {'pt': 'Declive', 'en': 'Slope'},
  'desc': {'pt': 'Condições topográficas do concelho e das suas áreas urbanas.',
           'en': 'Topographic conditions of the municipality and of its urban areas.'}},
 {'k': 'c2_ambcon', 'cod': 'C2', 'peso': 0.25,
  'nome': {'pt': 'Ambiente construído', 'en': 'Built environment'},
  'curto': {'pt': 'Ambiente', 'en': 'Built env.'},
  'desc': {'pt': 'Densidade, diversidade de usos e desenho urbano, os três D que explicam a procura de mobilidade activa.',
           'en': 'Density, diversity of uses and urban design, the three Ds that drive demand for active mobility.'}},
 {'k': 'c3_infraest', 'cod': 'C3', 'peso': 0.25,
  'nome': {'pt': 'Infraestruturas', 'en': 'Infrastructure'},
  'curto': {'pt': 'Infraestruturas', 'en': 'Infrastructure'},
  'desc': {'pt': 'Extensão e cobertura da rede ciclável e existência de bicicletas partilhadas.',
           'en': 'Extent and coverage of the cycling network, and the presence of bike sharing.'}},
 {'k': 'c4_compolit', 'cod': 'C4', 'peso': 0.20,
  'nome': {'pt': 'Compromisso político', 'en': 'Political commitment'},
  'curto': {'pt': 'Político', 'en': 'Political'},
  'desc': {'pt': 'Investimento municipal em mobilidade sustentável no triénio 2023-2025.',
           'en': 'Municipal spending on sustainable mobility over the 2023-2025 period.'}},
 {'k': 'c5_utiliza', 'cod': 'C5', 'peso': 0.20,
  'nome': {'pt': 'Utilização', 'en': 'Cycling levels'},
  'curto': {'pt': 'Utilização', 'en': 'Cycling'},
  'desc': {'pt': 'Uso actual da bicicleta e dos modos activos, e o peso das mulheres entre quem pedala.',
           'en': 'Current cycling and active travel levels, and the share of women among cyclists.'}},
]

# ------------------------------------------------------------- indicadores
# (codigo, dimensao, peso, nome pt, nome en, unidade pt, unidade en, formato)
IND = [
 ('DEC1','c1_declive',.15,'Área do concelho com declive inferior a 5%','Municipal area with slope under 5%','%','%','pct'),
 ('DEC2','c1_declive',.35,'Área urbana com declive inferior a 5%','Urban area with slope under 5%','%','%','pct'),
 ('DEC3','c1_declive',.15,'Área do concelho com declive inferior a 10%','Municipal area with slope under 10%','%','%','pct'),
 ('DEC4','c1_declive',.35,'Área urbana com declive inferior a 10%','Urban area with slope under 10%','%','%','pct'),
 ('AMB1','c2_ambcon',.14,'Densidade populacional na área urbana','Population density in the urban area','hab/km²','pop/km²','num'),
 ('AMB2','c2_ambcon',.06,'Densidade populacional no concelho','Population density in the municipality','hab/km²','pop/km²','num'),
 ('AMB3','c2_ambcon',.14,'Densidade de alojamentos na área urbana','Dwelling density in the urban area','aloj/km²','dwellings/km²','num'),
 ('AMB4','c2_ambcon',.06,'Densidade de alojamentos no concelho','Dwelling density in the municipality','aloj/km²','dwellings/km²','num'),
 ('AMB5','c2_ambcon',.15,'Variedade de usos no concelho','Mix of uses in the municipality','%','%','num'),
 ('AMB6','c2_ambcon',.15,'Variedade de usos na área urbana','Mix of uses in the urban area','%','%','num'),
 ('AMB7','c2_ambcon',.10,'Amenidades por 10 mil habitantes','Amenities per 10,000 residents','n.º','count','num'),
 ('AMB8','c2_ambcon',.10,'Densidade de nós da rede urbana','Node density of the urban network','nós/km²','nodes/km²','num'),
 ('AMB9','c2_ambcon',.10,'Comprimento médio de bloco','Average block length','m','m','num'),
 ('INF1','c3_infraest',.09,'Ciclovias por área do concelho','Cycle lanes per municipal area','m/km²','m/km²','num'),
 ('INF2','c3_infraest',.28,'Ciclovias por área urbana','Cycle lanes per urban area','m/km²','m/km²','num'),
 ('INF3','c3_infraest',.09,'Ciclovias por habitante do concelho','Cycle lanes per municipal resident','m/1000 hab','m/1,000 pop','num'),
 ('INF4','c3_infraest',.28,'Ciclovias por habitante da área urbana','Cycle lanes per urban resident','m/1000 hab','m/1,000 pop','num'),
 ('INF5','c3_infraest',.12,'Rácio ciclovias sobre vias principais','Cycle lanes to major roads ratio','rácio','ratio','num'),
 ('INF6','c3_infraest',.14,'Sistema de bicicletas partilhadas','Bike sharing scheme','sim/não','yes/no','bool'),
 ('POL1','c4_compolit',.20,'Investimento por km²','Spending per km²','€/km²','€/km²','eur'),
 ('POL2','c4_compolit',.40,'Investimento por mil habitantes','Spending per thousand residents','€/1000 hab','€/1,000 pop','eur'),
 ('POL3','c4_compolit',.40,'Peso da mobilidade na despesa municipal','Mobility share of municipal spending','%','%','num'),
 ('UTI1','c5_utiliza',.50,'Peso da bicicleta na repartição modal','Cycling mode share','%','%','frac'),
 ('UTI2','c5_utiliza',.30,'Mulheres entre quem usa bicicleta','Women among cyclists','% do total','% of cyclists','frac'),
 ('UTI3','c5_utiliza',.20,'Deslocações em modos activos','Trips by active modes','%','%','frac'),
]

# ----------------------------------------------- strings usadas pelo JS
JS = {
  'locale':        {'pt': 'pt-PT', 'en': 'en-GB'},
  'nodata':        {'pt': 'sem dados', 'en': 'no data'},
  'points':        {'pt': 'pontos', 'en': 'points'},
  'ofN':           {'pt': '.º de 278', 'en': 'th of 278'},
  'mapAria':       {'pt': 'Mapa dos municípios de Portugal Continental',
                    'en': 'Map of mainland Portugal municipalities'},
  'profileTitle':  {'pt': 'Perfil por dimensão', 'en': 'Profile by dimension'},
  'chartCompare':  {'pt': 'Comparação', 'en': 'Comparison'},
  'chartDist':     {'pt': 'Distribuição', 'en': 'Distribution'},
  'chartScatter':  {'pt': 'Dispersão', 'en': 'Scatter plot'},
  'municipalities':{'pt': 'municípios', 'en': 'municipalities'},
  'bfiScale':      {'pt': 'BFI (0 a 10)', 'en': 'BFI (0 to 10)'},
  'noChange':      {'pt': 'sem variação', 'en': 'no change'},
  'improved':      {'pt': 'Melhorou', 'en': 'Improved'},
  'worsened':      {'pt': 'Piorou', 'en': 'Worsened'},
  'xScatter':      {'pt': 'BFI 2018 (série comparável)', 'en': 'BFI 2018 (comparable series)'},
  'yScatter':      {'pt': 'BFI 2025', 'en': 'BFI 2025'},
  'natAvg':        {'pt': 'Média nacional', 'en': 'National average'},
  'avg':           {'pt': 'média', 'en': 'average'},
  # tabela
  'colRank':       {'pt': '#', 'en': '#'},
  'colMun':        {'pt': 'Município', 'en': 'Municipality'},
  'colDist':       {'pt': 'Distrito', 'en': 'District'},
  'colPop':        {'pt': 'População', 'en': 'Population'},
  'colCic':        {'pt': 'Ciclovias km', 'en': 'Cycle lanes km'},
  'search':        {'pt': 'Procurar', 'en': 'Search'},
  'searchPh':      {'pt': 'Procurar município...', 'en': 'Search municipality...'},
  'district':      {'pt': 'Distrito', 'en': 'District'},
  'all':           {'pt': 'Todos', 'en': 'All'},
  'allDistricts':  {'pt': 'Todos os distritos', 'en': 'All districts'},
  'capitals':      {'pt': 'Capitais de distrito', 'en': 'District capitals'},
  'withBS':        {'pt': 'Com bicicletas partilhadas', 'en': 'With bike sharing'},
  'downloadCSV':   {'pt': 'Descarregar CSV', 'en': 'Download CSV'},
  'sortBy':        {'pt': 'Ordenar por', 'en': 'Sort by'},
  'of':            {'pt': 'de', 'en': 'of'},
  'capital':       {'pt': 'capital', 'en': 'capital'},
  'dimLabels':     {'pt': ['C1 Declive', 'C2 Ambiente', 'C3 Infraest.', 'C4 Político', 'C5 Utilização'],
                    'en': ['C1 Slope', 'C2 Built env.', 'C3 Infrastr.', 'C4 Political', 'C5 Cycling']},
  'scaleBFI':      {'pt': ['< 1,0', '1,0 - 1,5', '1,5 - 2,0', '2,0 - 2,5', '2,5 - 3,0', '3,0 - 4,0', '>= 4,0'],
                    'en': ['< 1.0', '1.0 - 1.5', '1.5 - 2.0', '2.0 - 2.5', '2.5 - 3.0', '3.0 - 4.0', '>= 4.0']},
  'scaleDim':      {'pt': ['< 1', '1 - 2', '2 - 3', '3 - 4', '4 - 6', '6 - 8', '>= 8'],
                    'en': ['< 1', '1 - 2', '2 - 3', '3 - 4', '4 - 6', '6 - 8', '>= 8']},
  'scaleDelta':    {'pt': ['< -1,0', '-1,0 a -0,5', '-0,5 a -0,1', 'sem variação', '+0,1 a +0,5', '+0,5 a +1,0', '> +1,0'],
                    'en': ['< -1.0', '-1.0 to -0.5', '-0.5 to -0.1', 'no change', '+0.1 to +0.5', '+0.5 to +1.0', '> +1.0']},
  'rampBFI':       {'pt': ['0', '6+'], 'en': ['0', '6+']},
  'rampDim':       {'pt': ['0', '10'], 'en': ['0', '10']},
  'rampDelta':     {'pt': ['-1,0 piorou', 'melhorou +1,0'], 'en': ['-1.0 worse', 'better +1.0']},
  'bfiChange':     {'pt': 'Variação BFI', 'en': 'BFI change'},
  'warnLabel':     {'pt': 'Aviso metodológico', 'en': 'Methodological caveat'},
  'back':          {'pt': 'Voltar', 'en': 'Back'},
  'backList':      {'pt': 'Voltar à lista', 'en': 'Back to the list'},
  'basemapOn':     {'pt': 'Fundo de mapa', 'en': 'Basemap'},
  'attrib':        {'pt': 'Mosaicos e dados © colaboradores do OpenStreetMap',
                    'en': 'Tiles and data © OpenStreetMap contributors'},
  'themeToggle':   {'pt': 'Alternar modo claro e escuro', 'en': 'Toggle light and dark mode'},
  'openMenu':      {'pt': 'Abrir menu', 'en': 'Open menu'},
}


def js_bundle():
    """Gera o conteudo de assets/js/i18n.js."""
    import json
    out = {}
    for lang in LANGS:
        out[lang] = {k: v[lang] for k, v in JS.items()}
    return 'window.STRINGS = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
