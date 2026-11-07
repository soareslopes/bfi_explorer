# -*- coding: utf-8 -*-
"""Gera todas as paginas HTML do site BFI, em portugues e em ingles.

Portugues na raiz, ingles em /en/. O texto vive nas chamadas a L(pt, en),
ao lado do sitio onde e usado, em vez de num dicionario de chaves a parte.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from layout import page, file_of, label_of, MUN_DIR, PAGES, ICON_INFO, ICON_WARN

_raw = open(os.path.join(SITE, 'assets/js/data.js'), encoding='utf8').read()
DATA = json.loads(_raw.split('=', 1)[1].strip().rstrip(';\n').rstrip(';'))
MUN = DATA['municipios']
DIMS = DATA['dims']
IND = DATA['ind']
NAC = DATA['nacional']
SER = NAC['series']

BY = {m['d']: m for m in MUN}
DIMK = ['c1', 'c2', 'c3', 'c4', 'c5']
DIMFULL = ['c1_declive', 'c2_ambcon', 'c3_infraest', 'c4_compolit', 'c5_utiliza']

LANG = 'pt'


# --------------------------------------------------------------- helpers
def L(pt, en):
    return pt if LANG == 'pt' else en

def T(d):
    """Resolve um dicionario {pt, en}."""
    return d[LANG]

def n(v, d=2):
    if v is None: return '-'
    s = ('%.' + str(d) + 'f') % v
    return s.replace('.', ',') if LANG == 'pt' else s

def i(v):
    if v is None: return '-'
    s = format(int(round(v)), ',')
    return s.replace(',', ' ') if LANG == 'pt' else s

def sign(v, d=2):
    if v is None: return '-'
    return ('+' if v > 0 else '') + n(v, d)

def eur(v):
    if v is None: return '-'
    if v >= 1e6: return n(v / 1e6, 1) + ' M€'
    return i(v) + ' €'

def ordinal(k):
    return ('%d.º' % k) if LANG == 'pt' else ('%d%s' % (k, 'th' if 10 <= k % 100 <= 20
            else {1: 'st', 2: 'nd', 3: 'rd'}.get(k % 10, 'th')))

def P(key):
    """Ficheiro de outra pagina, dentro da raiz da lingua activa."""
    return file_of(key, LANG)

def MD():
    return MUN_DIR[LANG] + '/'


def LEGACY():
    """Caminho para o explorador arquivado, a partir da raiz da lingua activa."""
    return ('../' if LANG == 'en' else '') + 'explorador-v1/'

def write(path, html):
    p = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(p) or SITE, exist_ok=True)
    open(p, 'w', encoding='utf8').write(html)

def emit(key, title, body, desc='', scripts=''):
    """Escreve uma pagina de raiz na lingua activa."""
    pt_file, en_rel = PAGES[key][0], PAGES[key][1]
    if LANG == 'pt':
        out, up_assets, alt = pt_file, '', 'en/' + en_rel.split('/', 1)[1]
        self_abs, alt_abs = pt_file, en_rel
    else:
        out, up_assets, alt = en_rel, '../', '../' + pt_file
        self_abs, alt_abs = en_rel, pt_file
    write(out, page(LANG, title, body, key, up_assets, '', alt, alt_abs, self_abs, desc, scripts))

ICON_ALERT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M12 3.6 2.2 20.4h19.6L12 3.6Z"/><path d="M12 10v4.2M12 17.6v.01"/></svg>')


def alertpop(html):
    """Icone de alerta que abre o aviso numa janela flutuante."""
    lab = L('Aviso metodológico', 'Methodological caveat')
    return ('<button type="button" class="alertpop" aria-expanded="false" aria-label="%s" title="%s">'
            '%s<span class="pop" role="note">%s</span></button>' % (lab, lab, ICON_ALERT, html))


ICON_I = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
          'stroke-linecap="round" aria-hidden="true"><path d="M12 10.5v7M12 6.6v.01"/></svg>')


def infopop(html):
    """Nota de leitura, em janela flutuante accionada por um (i)."""
    lab = L('Nota de leitura', 'Reading note')
    return ('<button type="button" class="alertpop neutral" aria-expanded="false" '
            'aria-label="%s" title="%s">%s<span class="pop" role="note">%s</span></button>'
            % (lab, lab, ICON_I, html))


def callout(kind, icon, html):
    return '<div class="callout %s">%s<div>%s</div></div>' % (kind, icon, html)

def infotip_down(txt):
    return ('<i class="infotip down" tabindex="0" role="note" aria-label="%s">i<span>%s</span></i>'
            % (txt.replace('"', '&quot;'), txt))


def infotip(txt):
    return ('<i class="infotip" tabindex="0" role="note" aria-label="%s">i<span>%s</span></i>'
            % (txt.replace('"', '&quot;'), txt))


def tiles(items):
    return '<div class="tiles">%s</div>' % ''.join(
      '<div class="tile"><div class="k">%s</div><div class="v">%s</div><div class="s">%s</div></div>'
      % (k, v, s) for k, v, s in items)


# --------------------------------------------------- numeros de apoio
S25, S18, S18C = SER['2025'], SER['2018_original'], SER['2018_metodo2025']
top25 = sorted([m for m in MUN if m['s25']], key=lambda m: -m['s25']['bfi'])
melhor, pior = top25[0], top25[-1]
delta = [(m, m['s25']['bfi'] - m['s18c']['bfi']) for m in MUN if m['s25'] and m['s18c']]
subiu = sum(1 for _, d in delta if d > 0)
desceu = sum(1 for _, d in delta if d < 0)
rank_mov = sorted([(m, m['s18c']['rank'] - m['s25']['rank']) for m in MUN if m['s25'] and m['s18c']],
                  key=lambda t: -t[1])
capitais = sorted([m for m in MUN if m['cap']], key=lambda m: m['s25']['rank'])


# ===========================================================================
#  1 · APRESENTACAO
# ===========================================================================
def pg_index():
    body = '''
<section class="hero">
  <div class="wrap">
    <div class="hero-grid tall">
      <div>
        <p class="eyebrow">''' + L('Edição 2025 · 278 municípios de Portugal Continental',
                                   '2025 edition · 278 mainland Portuguese municipalities') + '''</p>
        <h1>''' + L('Portugal é amigo da bicicleta?',
                    'Is Portugal bike friendly?') + '''</h1>
        <p class="lead">''' + L(
          'O Bike Friendly Index mede a amigabilidade de cada município português para a '
          'utilização da bicicleta como modo de transporte urbano. Cinco dimensões, vinte e '
          'cinco indicadores, só com dados abertos.',
          'The Bike Friendly Index measures how friendly each Portuguese municipality is to '
          'cycling as a mode of urban transport. Five dimensions, twenty-five indicators, '
          'built entirely from open data.') + '''</p>
        <div class="hero-number">
          <span class="v">''' + n(S25['bfi_media']) + '''</span>
          <span class="u">''' + L('média nacional,<br>de 0 a 10',
                                  'national average,<br>0 to 10') + '''</span>
        </div>
        <div class="btn-row">
          <a class="btn" href="''' + P('r2025') + '''">''' + L('Ver os resultados de 2025', 'See the 2025 results') + '''</a>
          <a class="btn ghost" href="''' + P('muns') + '''">''' + L('Procurar o meu município', 'Find my municipality') + '''</a>
        </div>
      </div>
      <div>
        <div class="mapbox" id="heroMap" style="max-width:280px;margin-inline:auto;border:0;background:transparent"></div>
      </div>
    </div>
  </div>
</section>

<hr class="rule">

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Retrato do país', 'The country at a glance') + '''</p>
      <h2>''' + L('Portugal em 2025, em seis números', 'Portugal in 2025, in six numbers') + '''</h2>
      <p>''' + L('Valores apurados para os 278 municípios de Portugal Continental.',
                 'Figures computed for the 278 municipalities of mainland Portugal.') + '''</p>
    </div>
    ''' + tiles([
      (L('Média nacional', 'National average'), n(S25['bfi_media']),
       L('Numa escala de 0 a 10. Média simples dos 278 municípios',
         'On a 0 to 10 scale. Unweighted mean of the 278 municipalities')),
      (L('Ponderada pela população', 'Population weighted'), n(S25['bfi_media_ponderada_pop']),
       L('Quem vive onde o BFI é mais alto pesa mais',
         'People living where the BFI is higher count for more')),
      (L('Melhor município', 'Top municipality'), melhor['n'],
       L('BFI ' + n(melhor['s25']['bfi']) + ', o único acima de 5',
         'BFI ' + n(melhor['s25']['bfi']) + ', the only one above 5')),
      (L('Ciclovias', 'Cycle lanes'), i(NAC['ciclovias_km_concelho']) + ' km',
       i(NAC['ciclovias_km_area_urbana']) + L(' km dentro de área urbana', ' km inside urban areas')),
      (L('Investimento 2023-2025', 'Spending 2023-2025'), n(NAC['investimento_total_eur_2023_2025'] / 1e6, 1) + ' M€',
       L('Cerca de ' + n(NAC['investimento_total_eur_2023_2025'] / NAC['populacao_2021'], 2) + ' € por habitante',
         'About €' + n(NAC['investimento_total_eur_2023_2025'] / NAC['populacao_2021'], 2) + ' per resident')),
      (L('Bicicletas partilhadas', 'Bike sharing'),
       str(NAC['municipios_com_bikesharing']),
       L('municípios, ' + str(round(NAC['municipios_com_bikesharing'] / 278 * 100)) + '% do continente',
         'municipalities, ' + str(round(NAC['municipios_com_bikesharing'] / 278 * 100)) + '% of the mainland')),
    ]) + '''
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="grid-2">
      <div class="card">
        <p class="eyebrow">''' + L('Onde estamos fracos', 'Where the country is weak') + '''</p>
        <h3 style="margin-bottom:16px">''' + L('As cinco dimensões, média nacional',
                                               'The five dimensions, national average') + '''</h3>
        <div id="dimNac"></div>
        <p class="small muted" style="margin:16px 0 0">''' + L(
          'Compromisso político e infraestruturas continuam a ser as dimensões mais fracas, '
          'tal como em 2018. São também as duas que mais subiram desde então.',
          'Political commitment and infrastructure remain the weakest dimensions, just as in '
          '2018. They are also the two that have risen the most since.') + '''</p>
      </div>
      <div class="card fill">
        <p class="eyebrow">''' + L('Como se distribuem', 'How they are spread') + '''</p>
        <h3 style="margin-bottom:6px">''' + L('Os 278 municípios por valor de BFI',
                                              'The 278 municipalities by BFI score') + '''</h3>
        <div class="chartslot" id="histNac"></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('O índice', 'The index') + '''</p>
      <h2>''' + L('Cinco dimensões, vinte e cinco indicadores',
                  'Five dimensions, twenty-five indicators') + '''</h2>
      <p>''' + L('Cada dimensão pesa de forma diferente no resultado final. Os pesos de 2025 '
                 'reforçam aquilo que depende de decisão política e retiram peso ao que é '
                 'herdado do território.',
                 'Each dimension carries a different weight. The 2025 weights give more room to '
                 'what depends on policy decisions and less to what the territory simply '
                 'inherited.') + '''</p>
    </div>
    <div class="grid-3" id="dimCards"></div>
    <div class="btn-row">
      <a class="btn ghost" href="''' + P('method') + '''">''' + L('Como é calculado', 'How it is calculated') + '''</a>
      <a class="btn ghost" href="''' + P('data') + '''">''' + L('Descarregar os dados', 'Download the data') + '''</a>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="card" style="display:grid;grid-template-columns:1fr auto;gap:28px;align-items:center">
      <div>
        <p class="eyebrow">''' + L('2018 contra 2025', '2018 versus 2025') + '''</p>
        <h2 style="margin-bottom:10px">''' + L('Portugal melhorou, mas pouco',
                                               'Portugal improved, but only just') + '''</h2>
        <p class="muted" style="margin-bottom:0">''' + L(
          'Na série comparável, ' + str(subiu) + ' dos 278 municípios melhoraram e ' + str(desceu) +
          ' pioraram. A média nacional subiu de ' + n(S18C['bfi_media']) + ' para ' + n(S25['bfi_media']) +
          '. Nenhum município chega a 6 numa escala de 0 a 10.',
          'On the comparable series, ' + str(subiu) + ' of the 278 municipalities improved and ' +
          str(desceu) + ' got worse. The national average rose from ' + n(S18C['bfi_media']) + ' to ' +
          n(S25['bfi_media']) + '. No municipality reaches 6 on a 0 to 10 scale.') + '''</p>
      </div>
      <a class="btn" href="''' + P('comp') + '''">''' + L('Ver a comparação', 'See the comparison') + '''</a>
    </div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  choropleth(document.getElementById('heroMap'), {serie:'s25', campo:'bfi', base:'%(md)s'});

  var dn = document.getElementById('dimNac');
  function drawDim(){
    var nac = MEDIA.s25, out = '';
    M.dims.forEach(function(d,ix){
      var k = ['c1','c2','c3','c4','c5'][ix], v = nac[k];
      out += '<div class="dimrow"><div class="lab"><b>'+d.cod+' '+d.nome+'</b></div>'+
        '<div class="track"><i class="fill" style="width:'+(v/10*100).toFixed(1)+'%%;background:'+colorOf('dim',v)+'"></i></div>'+
        '<div class="val">'+F.n(v,2)+'</div></div>';
    });
    dn.innerHTML = '<div class="dimbar">'+out+'</div>';
  }
  drawDim(); dn._redraw = drawDim; dn.setAttribute('data-redraw','1');

  var hn = document.getElementById('histNac');
  function drawHist(){
    histogram(hn, M.all.filter(function(m){return m.s25;}).map(function(m){return m.s25.bfi;}),
      {marks:[{v:MEDIA.s25.bfi, label:T.avg+' '+F.n(MEDIA.s25.bfi,2)}]});
  }
  drawHist(); hn._redraw = drawHist; hn.setAttribute('data-redraw','1');

  var dc = document.getElementById('dimCards');
  M.dims.forEach(function(d,ix){
    var k = ['c1','c2','c3','c4','c5'][ix], v = MEDIA.s25[k];
    dc.appendChild(h('div',{class:'card'},
      '<p class="eyebrow" style="margin-bottom:6px">'+d.cod+' · %(weight)s '+Math.round(d.peso*100)+'%%</p>'+
      '<h3 style="margin-bottom:8px">'+esc(d.nome)+'</h3>'+
      '<p class="small muted">'+esc(d.desc)+'</p>'+
      '<div style="display:flex;align-items:center;gap:8px;margin-top:14px">'+
      '<span style="width:11px;height:11px;border-radius:3px;display:inline-block;background:'+colorOf('dim',v)+'"></span>'+
      '<b style="font-family:var(--font-display);font-size:2rem;line-height:1">'+F.n(v,2)+'</b>'+
      '<span class="small muted">%(natavg)s</span></div>'));
  });
})();
</script>''' % {'md': MD(), 'weight': L('peso', 'weight'), 'natavg': L('média nacional', 'national average')}

    emit('index',
      L('Bike Friendly Index Portugal · Edição 2025', 'Bike Friendly Index Portugal · 2025 edition'),
      body,
      L('Índice de amigabilidade dos 278 municípios de Portugal Continental para a utilização da bicicleta. Edição 2025.',
        'How friendly the 278 municipalities of mainland Portugal are to cycling. 2025 edition.'),
      scripts)


# ===========================================================================
#  2 · RESULTADOS 2025
# ===========================================================================
def pg_2025():
    def row(m):
        return ('<tr><td class="n">%d</td><td class="nm"><a href="%s%s.html">%s</a></td>'
                '<td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>'
                % (m['s25']['rank'], MD(), m['slug'], m['n'], m['dist'], n(m['s25']['bfi']),
                   sign(m['s25']['bfi'] - m['s18c']['bfi']) if m['s18c'] else '-'))
    top_rows = ''.join(row(m) for m in top25[:10])
    bot_rows = ''.join(row(m) for m in top25[-10:])
    cap_rows = ''.join(
      '<tr><td class="n">%d</td><td class="nm"><a href="%s%s.html">%s</a></td>'
      '<td class="n">%s</td><td class="n">%s</td><td class="n">%s</td>'
      '<td class="n">%s</td><td class="n">%s</td><td class="n">%s</td></tr>'
      % (m['s25']['rank'], MD(), m['slug'], m['n'], n(m['s25']['bfi']),
         n(m['s25']['c1']), n(m['s25']['c2']), n(m['s25']['c3']),
         n(m['s25']['c4']), n(m['s25']['c5']))
      for m in capitais)

    segs = ''.join(
      '<button type="button" data-k="%s"%s>%s</button>'
      % (k, ' aria-pressed="true"' if k == 'bfi' else '', lab)
      for k, lab in [('bfi', L('BFI total', 'Overall BFI'))] +
                    [(DIMK[ix], d['cod'] + ' ' + T(d['curto'])) for ix, d in enumerate(DIMS)])

    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('Resultados · edição 2025', 'Results · 2025 edition') + '''</p>
    <h1 style="max-width:16ch">''' + L('O BFI 2025 em Portugal Continental',
                                       'The 2025 BFI across mainland Portugal') + '''</h1>
    <p class="lead" style="max-width:56ch">''' + L(
      'Média nacional de ' + n(S25['bfi_media']) + ' numa escala de 0 a 10. Nenhum dos 278 '
      'municípios chega a 6.',
      'A national average of ' + n(S25['bfi_media']) + ' on a 0 to 10 scale. None of the 278 '
      'municipalities reaches 6.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    ''' + tiles([
      (L('Média nacional', 'National average'), n(S25['bfi_media']),
       L('Média simples dos 278 municípios', 'Unweighted mean of the 278 municipalities')),
      (L('Ponderada pela população', 'Population weighted'), n(S25['bfi_media_ponderada_pop']),
       L('Os ' + i(NAC['populacao_2021']) + ' residentes contam',
         'All ' + i(NAC['populacao_2021']) + ' residents counted')),
      (L('Máximo', 'Highest'), n(melhor['s25']['bfi']),
       melhor['n'] + L(', o único acima de 5', ', the only one above 5')),
      (L('Mínimo', 'Lowest'), n(pior['s25']['bfi']),
       pior['n'] + L(', o valor mais baixo do país', ', the lowest score in the country')),
    ]) + '''
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Mapa', 'Map') + '''</p>
      <h2>''' + L('Onde o índice é mais alto', 'Where the index runs highest') + '''</h2>
      <p>''' + L(
        'O litoral, as áreas metropolitanas e a faixa da Ria de Aveiro concentram os valores '
        'mais altos. O interior norte e as zonas de relevo acentuado ficam no fundo da escala. '
        'Escolha a dimensão para ver como cada uma se distribui.',
        'The coast, the metropolitan areas and the Ria de Aveiro belt hold the highest scores. '
        'The northern interior and the steeper terrain sit at the bottom. Pick a dimension to '
        'see how each one is distributed.') + '''</p>
    </div>
    <div class="controls">
      <div class="seg" id="segDim">''' + segs + '''</div>
    </div>
    <div class="grid-2" style="grid-template-columns:420px 1fr">
      <div class="mapcol">
        <div class="mapbox" id="map25"></div>
        <div class="map-info">''' + infotip_down(L('Clique num município para abrir a ficha.',
                                        'Click a municipality to open its card.')) + '''</div>
        <div class="map-legend-v" id="leg25"></div>
      </div>
      <div class="card">
        <h3 id="distTitle">''' + L('Distribuição dos valores', 'Distribution of scores') + '''</h3>
        <div id="hist25"></div>
        <div style="margin-top:22px">
          <h3>''' + L('As cinco dimensões', 'The five dimensions') + '''</h3>
          <div id="dim25"></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid-2">
      <div class="card card-pad-0">
        <div style="padding:20px 22px 0"><p class="eyebrow" style="margin-bottom:4px">''' + L('Topo', 'Top') + '''</p>
        <h3>''' + L('Os 10 melhores em 2025', 'The top 10 in 2025') + '''</h3></div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
        <table class="tbl"><thead><tr><th>#</th><th>''' + L('Município', 'Municipality') + '''</th>
        <th>''' + L('Distrito', 'District') + '''</th>
        <th style="text-align:right">BFI</th><th style="text-align:right">''' + L('vs 2018', 'vs 2018') + '''</th></tr></thead>
        <tbody>''' + top_rows + '''</tbody></table></div>
      </div>
      <div class="card card-pad-0">
        <div style="padding:20px 22px 0"><p class="eyebrow" style="margin-bottom:4px">''' + L('Cauda', 'Bottom') + '''</p>
        <h3>''' + L('Os 10 com valor mais baixo', 'The 10 lowest scores') + '''</h3></div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
        <table class="tbl"><thead><tr><th>#</th><th>''' + L('Município', 'Municipality') + '''</th>
        <th>''' + L('Distrito', 'District') + '''</th>
        <th style="text-align:right">BFI</th><th style="text-align:right">vs 2018</th></tr></thead>
        <tbody>''' + bot_rows + '''</tbody></table></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Capitais de distrito', 'District capitals') + '''</p>
      <h2>''' + L('As dezoito capitais', 'The eighteen capitals') + '''</h2>
      <p>''' + L('Lisboa e Porto destacam-se. Abaixo delas, nenhuma capital de distrito '
                 'ultrapassa 3,4. Sete ficam abaixo da posição 100 no ranking nacional.',
                 'Lisbon and Porto stand apart. Below them, no district capital goes above 3.4. '
                 'Seven sit below rank 100 nationally.') + '''</p>
    </div>
    <div class="tbl-wrap">
      <table class="tbl"><thead><tr><th>#</th><th>''' + L('Capital', 'Capital') + '''</th>
      <th style="text-align:right">BFI</th><th style="text-align:right">C1</th>
      <th style="text-align:right">C2</th><th style="text-align:right">C3</th>
      <th style="text-align:right">C4</th><th style="text-align:right">C5</th></tr></thead>
      <tbody>''' + cap_rows + '''</tbody></table>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Ranking completo', 'Full ranking') + '''</p>
      <h2>''' + L('Os 278 municípios', 'All 278 municipalities') + '''</h2>
      <p>''' + L('Ordene por qualquer coluna, filtre por distrito ou procure pelo nome. '
                 'A tabela pode ser descarregada em CSV.',
                 'Sort by any column, filter by district or search by name. The table can be '
                 'downloaded as CSV.') + '''</p>
    </div>
    <div id="tabela25"></div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var map = choropleth(document.getElementById('map25'), {serie:'s25', campo:'bfi', base:'%(md)s'});
  var leg = document.getElementById('leg25'), hist = document.getElementById('hist25');
  var dim = document.getElementById('dim25');
  var campo = 'bfi';
  var NOMES = {bfi:'%(total)s'};
  M.dims.forEach(function(d,ix){ NOMES[['c1','c2','c3','c4','c5'][ix]] = d.cod+' '+d.nome; });

  function drawHist(){
    var vals = M.all.filter(function(m){return m.s25;}).map(function(m){return m.s25[campo];});
    histogram(hist, vals, {max: campo==='bfi'?6.5:10, bins: campo==='bfi'?26:25,
      scale: campo==='bfi'?'bfi':'dim', xlabel: NOMES[campo]+' (0 %(to)s 10)',
      marks:[{v: MEDIA.s25[campo], label:T.avg+' '+F.n(MEDIA.s25[campo],2)}]});
  }
  function drawDim(){
    var out = '';
    M.dims.forEach(function(d,ix){
      var k = ['c1','c2','c3','c4','c5'][ix], v = MEDIA.s25[k], v18 = MEDIA.s18c[k];
      out += '<div class="dimrow"><div class="lab"><b>'+d.cod+' '+d.nome+'</b>%(weight)s '+Math.round(d.peso*100)+'%%</div>'+
        '<div class="track"><i class="fill" style="width:'+(v/10*100).toFixed(1)+'%%;background:'+colorOf('dim',v)+'"></i>'+
        '<span class="ref" style="left:'+(v18/10*100).toFixed(1)+'%%" title="2018"></span></div>'+
        '<div class="val">'+F.n(v,2)+'</div></div>';
    });
    dim.innerHTML = '<div class="dimbar">'+out+'</div>'+
      '<p class="small muted" style="margin:12px 0 0">%(barnote)s</p>';
  }
  function redraw(){
    map.set('campo', campo);
    mapLegend(leg, map.scaleName(), campo==='bfi' ? 'BFI 2025' : NOMES[campo], {vertical:true});
    document.getElementById('distTitle').textContent = '%(dist)s · ' + NOMES[campo];
    drawHist(); drawDim();
  }
  document.getElementById('segDim').addEventListener('click', function(ev){
    var b = ev.target.closest('button[data-k]'); if(!b) return;
    campo = b.dataset.k;
    this.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true');
    redraw();
  });
  redraw();
  hist._redraw = drawHist; hist.setAttribute('data-redraw','1');
  dim._redraw = drawDim; dim.setAttribute('data-redraw','1');
  rankingTable(document.getElementById('tabela25'), {serie:'s25', base:'%(md)s'});
})();
</script>''' % {'md': MD(), 'total': L('BFI total', 'Overall BFI'), 'to': L('a', 'to'),
                'weight': L('peso', 'weight'), 'dist': L('Distribuição', 'Distribution'),
                'barnote': L('A barra mostra 2025. A marca vertical mostra 2018 na série comparável.',
                             'The bar shows 2025. The vertical tick shows 2018 on the comparable series.')}

    emit('r2025', L('BFI 2025 · Resultados · Bike Friendly Index',
                    'BFI 2025 · Results · Bike Friendly Index'), body,
      L('Resultados do Bike Friendly Index 2025 para os 278 municípios de Portugal Continental.',
        'Bike Friendly Index 2025 results for the 278 municipalities of mainland Portugal.'),
      scripts)


# ===========================================================================
#  3 · RESULTADOS 2018
# ===========================================================================
def pg_2018():
    t18 = sorted([m for m in MUN if m['s18']], key=lambda m: m['s18']['rank'])
    top_rows = ''.join(
      '<tr><td class="n">%d</td><td class="nm"><a href="%s%s.html">%s</a></td>'
      '<td>%s</td><td class="n">%s</td><td class="n">%s</td></tr>'
      % (m['s18']['rank'], MD(), m['slug'], m['n'], m['dist'], n(m['s18']['bfi']), n(m['s18c']['bfi']))
      for m in t18[:10])

    body = '''
<section class="tight">
  <div class="wrap alertzone">
    ''' + alertpop(L(
      '<p><strong>Não compare estes valores directamente com os de 2025.</strong> A edição de '
      '2025 mudou os pesos das dimensões, o número de indicadores e a forma de normalizar. '
      'A média de 2018 publicada é ' + n(S18['bfi_media']) + ', mas reaplicando os pesos de '
      '2025 aos mesmos dados de 2018 o valor passa a ' + n(S18C['bfi_media']) + '.</p>'
      '<p>A página de <a href="' + P('comp') + '">comparação</a> explica porquê e usa a série '
      'comparável.</p>',
      '<p><strong>Do not compare these figures directly with 2025.</strong> The 2025 edition '
      'changed the dimension weights, the number of indicators and the way values are '
      'normalised. The published 2018 average is ' + n(S18['bfi_media']) + ', but reapplying '
      'the 2025 weights to the same 2018 data gives ' + n(S18C['bfi_media']) + '.</p>'
      '<p>The <a href="' + P('comp') + '">comparison page</a> explains why, and uses the '
      'comparable series throughout.</p>')) + '''
    <p class="eyebrow">''' + L('Arquivo · edição 2018', 'Archive · 2018 edition') + '''</p>
    <h1 style="max-width:16ch">''' + L('O BFI 2018, tal como foi publicado',
                                       'The 2018 BFI, exactly as published') + '''</h1>
    <p class="lead" style="max-width:62ch">''' + L(
      'A primeira edição do índice, com 12 indicadores, Censos de 2011 e investimento público '
      'do triénio 2015-2017. Fica aqui no formato original, para quem cita o estudo de 2018.',
      'The first edition of the index, with 12 indicators, the 2011 Census and public spending '
      'from 2015 to 2017. Kept here in its original form, for anyone citing the 2018 study.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    ''' + tiles([
      (L('Média nacional 2018', '2018 national average'), n(S18['bfi_media']),
       L('Com os pesos originais de 2018', 'With the original 2018 weights')),
      (L('Com os pesos de 2025', 'With the 2025 weights'), n(S18C['bfi_media']),
       L('A mesma base de dados, nova fórmula', 'The same underlying data, new formula')),
      (L('Infraestruturas', 'Infrastructure'), n(S18['c3_infraest']),
       L('A dimensão mais fraca em 2018', 'The weakest dimension in 2018')),
      (L('Compromisso político', 'Political commitment'), n(S18['c4_compolit']),
       L('Perto de zero na maioria dos municípios', 'Close to zero in most municipalities')),
    ]) + '''
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Mapa', 'Map') + '''</p>
      <h2>''' + L('O retrato de 2018', 'The 2018 picture') + '''</h2>
      <p>''' + L('Escolha a série: os valores publicados em 2018, ou os mesmos dados '
                 'recalculados com a fórmula de 2025, que é a única forma correcta de os pôr '
                 'lado a lado com a edição actual.',
                 'Pick a series: the figures published in 2018, or the same data recomputed with '
                 'the 2025 formula, which is the only sound way to set them beside the current '
                 'edition.') + '''</p>
    </div>
    <div class="controls">
      <div class="seg" id="segSerie">
        <button type="button" data-s="s18" aria-pressed="true">''' + L('Valores publicados em 2018', 'As published in 2018') + '''</button>
        <button type="button" data-s="s18c">''' + L('Recalculado com o método de 2025', 'Recomputed with the 2025 method') + '''</button>
      </div>
    </div>
    <div class="grid-2" style="grid-template-columns:420px 1fr">
      <div class="mapcol">
        <div class="mapbox" id="map18"></div>
        <div class="map-info">''' + infotip_down(L('Clique num município para abrir a ficha.',
                                        'Click a municipality to open its card.')) + '''</div>
        <div class="map-legend-v" id="leg18"></div>
      </div>
      <div class="card">
        <h3>''' + L('Distribuição dos valores', 'Distribution of scores') + '''</h3>
        <div id="hist18"></div>
        <div style="margin-top:22px">
          <h3>''' + L('As cinco dimensões em 2018', 'The five dimensions in 2018') + '''</h3>
          <div id="dim18"></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid-2" style="grid-template-columns:1fr 1fr">
      <div class="card card-pad-0">
        <div style="padding:20px 22px 0"><p class="eyebrow" style="margin-bottom:4px">''' + L('Topo de 2018', 'Top in 2018') + '''</p>
        <h3>''' + L('Os 10 melhores', 'The top 10') + '''</h3></div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
        <table class="tbl"><thead><tr><th>#</th><th>''' + L('Município', 'Municipality') + '''</th>
        <th>''' + L('Distrito', 'District') + '''</th>
        <th style="text-align:right">BFI 2018</th>
        <th style="text-align:right">''' + L('Comparável', 'Comparable') + '''</th></tr></thead>
        <tbody>''' + top_rows + '''</tbody></table></div>
      </div>
      <div class="card">
        <p class="eyebrow">''' + L('O que dizia o relatório de 2018', 'What the 2018 report said') + '''</p>
        <h3>''' + L('Um país no início do caminho', 'A country at the start of the road') + '''</h3>
        <p class="muted small">''' + L(
          'Em 2018 a extensão de ciclovias em área urbana no continente era de cerca de 360 km, '
          'o investimento municipal em mobilidade sustentável no triénio 2015-2017 rondou os 50 '
          'milhões de euros, e as mulheres representavam cerca de 15% de quem usava a bicicleta.',
          'In 2018 there were about 360 km of cycle lanes inside mainland urban areas, municipal '
          'spending on sustainable mobility over 2015-2017 came to roughly 50 million euros, and '
          'women made up about 15% of cyclists.') + '''</p>
        <p class="muted small">''' + L(
          'Em 2025 as ciclovias em área urbana são ' + i(NAC['ciclovias_km_area_urbana']) + ' km, '
          'o investimento subiu para ' + n(NAC['investimento_total_eur_2023_2025'] / 1e6, 1) +
          ' milhões de euros e há ' + str(NAC['municipios_com_bikesharing']) + ' municípios com '
          'sistema de bicicletas partilhadas.',
          'In 2025 urban cycle lanes reach ' + i(NAC['ciclovias_km_area_urbana']) + ' km, spending '
          'has risen to ' + n(NAC['investimento_total_eur_2023_2025'] / 1e6, 1) + ' million euros, '
          'and ' + str(NAC['municipios_com_bikesharing']) + ' municipalities run a bike sharing '
          'scheme.') + '''</p>
        <a class="btn ghost" href="''' + P('comp') + '''" style="margin-top:8px">''' + L(
          'Ver a comparação completa', 'See the full comparison') + '''</a>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Ranking completo de 2018', 'Full 2018 ranking') + '''</p>
      <h2>''' + L('Os 278 municípios em 2018', 'All 278 municipalities in 2018') + '''</h2>
    </div>
    <div id="tabela18"></div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var serie = 's18';
  var map = choropleth(document.getElementById('map18'), {serie:serie, campo:'bfi', base:'%(md)s'});
  var leg = document.getElementById('leg18'), hist = document.getElementById('hist18');
  var dim = document.getElementById('dim18');
  var tab = rankingTable(document.getElementById('tabela18'), {serie:'s18', base:'%(md)s'});

  function cur(){ return serie==='s18' ? MEDIA.s18 : MEDIA.s18c; }
  function drawHist(){
    histogram(hist, M.all.filter(function(m){return m[serie];}).map(function(m){return m[serie].bfi;}),
      {marks:[{v:cur().bfi, label:T.avg+' '+F.n(cur().bfi,2)}]});
  }
  function drawDim(){
    var c = cur(), out='';
    M.dims.forEach(function(d,ix){
      var k=['c1','c2','c3','c4','c5'][ix], v=c[k];
      out += '<div class="dimrow"><div class="lab"><b>'+d.cod+' '+d.nome+'</b></div>'+
        '<div class="track"><i class="fill" style="width:'+(v/10*100).toFixed(1)+'%%;background:'+colorOf('dim',v)+'"></i>'+
        '<span class="ref" style="left:'+(MEDIA.s25[k]/10*100).toFixed(1)+'%%" title="2025"></span></div>'+
        '<div class="val">'+F.n(v,2)+'</div></div>';
    });
    dim.innerHTML='<div class="dimbar">'+out+'</div>'+
      '<p class="small muted" style="margin:12px 0 0">%(note)s</p>';
  }
  function redraw(){
    map.set('serie', serie);
    mapLegend(leg, 'bfi', 'BFI 2018', {vertical:true});
    drawHist(); drawDim(); tab.setSerie(serie);
  }
  document.getElementById('segSerie').addEventListener('click', function(ev){
    var b = ev.target.closest('button[data-s]'); if(!b) return;
    serie = b.dataset.s;
    this.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true');
    redraw();
  });
  redraw();
  hist._redraw = drawHist; hist.setAttribute('data-redraw','1');
  dim._redraw = drawDim; dim.setAttribute('data-redraw','1');
})();
</script>''' % {'md': MD(),
                'note': L('A marca vertical mostra o valor de 2025.',
                          'The vertical tick shows the 2025 value.'),
                'pub': L('BFI 2018 publicado', 'BFI 2018 as published'),
                'rec': L('BFI 2018 recalculado', 'BFI 2018 recomputed')}

    emit('r2018', L('BFI 2018 · Arquivo · Bike Friendly Index',
                    'BFI 2018 · Archive · Bike Friendly Index'), body,
      L('Os resultados originais do Bike Friendly Index 2018.',
        'The original Bike Friendly Index 2018 results.'), scripts)


# ===========================================================================
#  4 · COMPARACAO
# ===========================================================================
def pg_comparacao():
    def mv(rows):
        return ''.join(
          '<tr><td class="nm one" title="%s"><a href="%s%s.html">%s</a></td>'
          '<td class="n">%d</td><td class="n">%d</td><td class="n"><span class="delta %s">%s</span></td>'
          '<td class="n">%s</td></tr>'
          % (m['dist'], MD(), m['slug'], m['n'], m['s18c']['rank'], m['s25']['rank'],
             'up' if d > 0 else 'down', ('+' if d > 0 else '') + str(d),
             sign(m['s25']['bfi'] - m['s18c']['bfi']))
          for m, d in rows)

    dims_tbl = ''.join(
      '<tr><td><strong>%s</strong> %s</td><td class="n">%s</td><td class="n">%s</td>'
      '<td class="n">%s</td><td class="n"><span class="delta %s">%s</span></td></tr>'
      % (d['cod'], T(d['nome']), n(S18[k]), n(S18C[k]), n(S25[k]),
         'up' if S25[k] - S18C[k] > 0 else 'down', sign(S25[k] - S18C[k]))
      for d, k in zip(DIMS, DIMFULL))

    segs = ''.join('<button type="button" data-k="%s"%s>%s</button>'
                   % (k, ' aria-pressed="true"' if k == 'bfi' else '', lab)
                   for k, lab in [('bfi', L('BFI total', 'Overall BFI'))] +
                                 [(DIMK[ix], d['cod']) for ix, d in enumerate(DIMS)])

    body = '''
<section class="tight">
  <div class="wrap">
    <div class="alertzone">
      ''' + alertpop(L(
        '<p><strong>Leia isto antes dos números.</strong> A média nacional publicada em 2018 foi '
        + n(S18['bfi_media']) + '. A de 2025 é ' + n(S25['bfi_media']) + '. Mas as duas edições '
        'não usam os mesmos pesos nem o mesmo conjunto de indicadores, por isso a diferença '
        'entre elas não mede evolução nenhuma.</p>'
        '<p>Reaplicando os pesos de 2025 aos indicadores de 2018 obtém-se a <strong>série '
        'comparável</strong>: 2018 passa a valer ' + n(S18C['bfi_media']) + ' e 2025 mantém-se em '
        + n(S25['bfi_media']) + '. É esta a série usada em todo o resto da página.</p>'
        '<p class="small">Ressalva que fica por resolver: este recálculo corrige os pesos, não '
        'corrige a base de normalização. Os indicadores de 2018 continuam normalizados contra os '
        'máximos de 2018 e os de 2025 contra os máximos de 2025. Uma série temporal plenamente '
        'comparável exige renormalizar os dois anos contra um referencial comum, trabalho que '
        'está em curso.</p>',
        '<p><strong>Read this before the numbers.</strong> The national average published in 2018 '
        'was ' + n(S18['bfi_media']) + '. The 2025 figure is ' + n(S25['bfi_media']) + '. But the '
        'two editions do not share the same weights or the same set of indicators, so the gap '
        'between them measures no change at all.</p>'
        '<p>Reapplying the 2025 weights to the 2018 indicators gives the <strong>comparable '
        'series</strong>: 2018 becomes ' + n(S18C['bfi_media']) + ' and 2025 stays at '
        + n(S25['bfi_media']) + '. That is the series used throughout the rest of this page.</p>'
        '<p class="small">One caveat remains open: this recalculation fixes the weights, not the '
        'normalisation base. The 2018 indicators are still normalised against 2018 maxima and the '
        '2025 ones against 2025 maxima. A fully comparable time series requires renormalising both '
        'years against a shared benchmark, work that is under way.</p>')) + '''
      <p class="eyebrow">''' + L('2018 contra 2025', '2018 versus 2025') + '''</p>
      <h1>''' + L('O que mudou em 7 anos', 'What changed in 7 years') + '''</h1>
      <p class="lead" style="max-width:56ch">''' + L(
        'A comparação parece dizer que Portugal piorou. Não é isso que acontece: a queda é um '
        'efeito da mudança de metodologia, e a série comparável mostra o contrário.',
        'The comparison seems to say Portugal got worse. It did not: the fall is an artefact of '
        'the change in method, and the comparable series shows the opposite.') + '''</p>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    ''' + tiles([
      (L('2018, como publicado', '2018, as published'), n(S18['bfi_media']),
       L('Pesos 15/30/25/15/15, 12 indicadores', 'Weights 15/30/25/15/15, 12 indicators')),
      (L('2018, série comparável', '2018, comparable series'), n(S18C['bfi_media']),
       L('Os mesmos dados com os pesos de 2025', 'The same data with the 2025 weights')),
      ('2025', n(S25['bfi_media']),
       L('Pesos 10/25/25/20/20, 25 indicadores', 'Weights 10/25/25/20/20, 25 indicators')),
      (L('Variação real', 'Actual change'), sign(S25['bfi_media'] - S18C['bfi_media']),
       L(str(subiu) + ' municípios sobem, ' + str(desceu) + ' descem',
         str(subiu) + ' municipalities rise, ' + str(desceu) + ' fall')),
    ]) + '''
  </div>
</section>

<section>
  <div class="wrap">
    <div class="grid-2" style="grid-template-columns:1fr 1fr">
      <div class="card fill alertzone">
        ''' + infopop(L(
          '<p><strong>Infraestruturas e compromisso político são as que mais sobem.</strong> '
          'São também as duas dimensões que dependem directamente de decisão municipal.</p>'
          '<p>Ambiente construído e declive descem porque mudaram as fontes de base (Censos '
          '2021, CAOP 2024, Carta de Ocupação do Solo) e a forma de normalizar, não porque o '
          'território tenha mudado.</p>',
          '<p><strong>Infrastructure and political commitment rise the most.</strong> They are '
          'also the two dimensions that depend directly on municipal decisions.</p>'
          '<p>Built environment and slope fall because the underlying sources changed (2021 '
          'Census, CAOP 2024, land cover) along with the normalisation, not because the '
          'territory changed.</p>')) + '''
        <p class="eyebrow">''' + L('Dimensão a dimensão', 'Dimension by dimension') + '''</p>
        <h3>''' + L('Onde houve progresso', 'Where there was progress') + '''</h3>
        <div class="chartslot" id="cmpDims"></div>
      </div>
      <div class="card card-pad-0">
        <div style="padding:22px 22px 0">
          <p class="eyebrow">''' + L('Tabela', 'Table') + '''</p>
          <h3>''' + L('Médias nacionais por dimensão', 'National averages by dimension') + '''</h3>
        </div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
          <table class="tbl"><thead><tr><th>''' + L('Dimensão', 'Dimension') + '''</th>
          <th style="text-align:right">''' + L('2018 publ.', '2018 publ.') + '''</th>
          <th style="text-align:right">''' + L('2018 comp.', '2018 comp.') + '''</th>
          <th style="text-align:right">2025</th>
          <th style="text-align:right">''' + L('Variação', 'Change') + '''</th></tr></thead>
          <tbody>''' + dims_tbl + '''</tbody></table>
        </div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head">
      <p class="eyebrow">''' + L('Mapa da variação', 'Change map') + '''</p>
      <h2>''' + L('Quem subiu e quem desceu', 'Who went up and who went down') + '''</h2>
      <p>''' + L('Diferença de pontos de índice entre 2025 e 2018, na série comparável. '
                 'Azul significa que subiu, vermelho que desceu.',
                 'Difference in index points between 2025 and 2018, on the comparable series. '
                 'Blue means up, red means down.') + '''</p>
    </div>
    <div class="controls">
      <div class="seg" id="segVar">''' + segs + '''</div>
    </div>
    <div class="grid-2" style="grid-template-columns:420px 1fr">
      <div class="mapcol tall">
        <div class="mapbox" id="mapVar"></div>
        <div class="map-info">''' + infotip_down(L('Clique num município para abrir a ficha.',
                                        'Click a municipality to open its card.')) + '''</div>
        <div class="map-legend-v" id="legVar"></div>
      </div>
      <div class="card fill">
        <p class="eyebrow">''' + L('Cada ponto é um município', 'Each dot is a municipality') + '''</p>
        <h3 style="margin-bottom:4px">''' + L('2018 contra 2025', '2018 versus 2025') + '''</h3>
        <p class="small muted">''' + L('Acima da diagonal, melhorou. Abaixo, piorou. '
                                       'Clique num ponto para abrir a ficha.',
                                       'Above the diagonal, it improved. Below, it got worse. '
                                       'Click a dot to open the card.') + '''</p>
        <div class="chartslot" id="scat"></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head alertzone" style="max-width:none">
      ''' + alertpop(L(
        '<p><strong>Leia estes movimentos com cuidado.</strong> Variações desta magnitude em '
        'municípios pequenos merecem leitura cuidada. Uma subida de duzentas posições resulta '
        'muitas vezes de um único contrato público ou de um troço de ciclovia novo sobre uma '
        'base populacional reduzida, e não de uma transformação da mobilidade local.</p>'
        '<p class="small">A equipa está a validar estes casos um a um.</p>',
        '<p><strong>Read these movements with care.</strong> Swings of this size in small '
        'municipalities deserve a careful read. A climb of two hundred places often comes from '
        'a single public contract or one new stretch of cycle lane over a small population '
        'base, rather than from any transformation of local mobility.</p>'
        '<p class="small">The team is checking these cases one by one.</p>')) + '''
      <p class="eyebrow">''' + L('Movimentos', 'Movements') + '''</p>
      <h2>''' + L('Maiores movimentos no ranking', 'Biggest moves in the ranking') + '''</h2>
    </div>
    <div class="grid-2">
      <div class="card card-pad-0">
        <div style="padding:20px 22px 0"><p class="eyebrow" style="margin-bottom:4px">''' + L('Subidas', 'Risers') + '''</p>
        <h3>''' + L('Quem mais subiu no ranking', 'Biggest climbs in the ranking') + '''</h3></div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
        <table class="tbl"><thead><tr><th>''' + L('Município', 'Municipality') + '''</th>
        <th style="text-align:right">2018</th><th style="text-align:right">2025</th>
        <th style="text-align:right">''' + L('Posições', 'Places') + '''</th>
        <th style="text-align:right">BFI</th></tr></thead>
        <tbody>''' + mv(rank_mov[:12]) + '''</tbody></table></div>
      </div>
      <div class="card card-pad-0">
        <div style="padding:20px 22px 0"><p class="eyebrow" style="margin-bottom:4px">''' + L('Descidas', 'Fallers') + '''</p>
        <h3>''' + L('Quem mais desceu', 'Biggest drops') + '''</h3></div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
        <table class="tbl"><thead><tr><th>''' + L('Município', 'Municipality') + '''</th>
        <th style="text-align:right">2018</th><th style="text-align:right">2025</th>
        <th style="text-align:right">''' + L('Posições', 'Places') + '''</th>
        <th style="text-align:right">BFI</th></tr></thead>
        <tbody>''' + mv(list(reversed(rank_mov[-12:]))) + '''</tbody></table></div>
      </div>
    </div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var campo = 'bfi';
  var map = choropleth(document.getElementById('mapVar'), {serie:'delta', campo:'bfi', base:'%(md)s'});
  var leg = document.getElementById('legVar');
  var NOMES = {bfi:'%(total)s'};
  M.dims.forEach(function(d,ix){ NOMES[['c1','c2','c3','c4','c5'][ix]] = d.cod+' '+d.nome; });
  function redraw(){
    map.set('campo', campo);
    mapLegend(leg, 'delta', T.bfiChange + (campo==='bfi' ? '' : ' · ' + campo.toUpperCase()),
              {vertical:true});
  }
  document.getElementById('segVar').addEventListener('click', function(ev){
    var b = ev.target.closest('button[data-k]'); if(!b) return;
    campo = b.dataset.k;
    this.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true');
    redraw();
  });
  redraw();

  var sc = document.getElementById('scat');
  function drawScat(){
    scatter(sc, M.all.filter(function(m){return m.s25&&m.s18c;}).map(function(m){
      var hi = m.s25.rank<=6 || Math.abs(m.s25.bfi-m.s18c.bfi)>1.4;
      return {x:m.s18c.bfi, y:m.s25.bfi, n:m.n, hi:hi, label:hi, href:'%(md)s'+m.slug+'.html'};
    }), {});
  }
  drawScat(); sc._redraw = drawScat; sc.setAttribute('data-redraw','1');

  var cd = document.getElementById('cmpDims');
  function drawCmp(){
    groupedBars(cd, M.dims.map(function(d){ return d.cod+' '+d.curto; }),
      [{name:'2018 %(cs)s', v:['c1','c2','c3','c4','c5'].map(function(k){return MEDIA.s18c[k];})},
       {name:'2025', v:['c1','c2','c3','c4','c5'].map(function(k){return MEDIA.s25[k];})}],
      {max:7, width:460, height:330, fontSize:12.5, directLabels:false});
  }
  drawCmp(); cd._redraw = drawCmp; cd.setAttribute('data-redraw','1');
})();
</script>''' % {'md': MD(), 'total': L('BFI total', 'Overall BFI'),
                'chg': L('Variação 2018 a 2025', 'Change 2018 to 2025'),
                'cs': L('comparável', 'comparable')}

    emit('comp', L('Comparação 2018-2025 · Bike Friendly Index',
                   'Comparison 2018-2025 · Bike Friendly Index'), body,
      L('Como evoluiu o Bike Friendly Index entre 2018 e 2025, com a série comparável.',
        'How the Bike Friendly Index evolved between 2018 and 2025, using the comparable series.'),
      scripts)


# ===========================================================================
#  5 · MUNICIPIOS
# ===========================================================================
def pg_municipios():
    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('Os 278 municípios', 'All 278 municipalities') + '''</p>
    <h1 style="max-width:16ch">''' + L('Cartões por município', 'A card for every municipality') + '''</h1>
    <p class="lead" style="max-width:60ch">''' + L(
      'Uma ficha para cada município de Portugal Continental: score, posição, perfil nas cinco '
      'dimensões, os vinte e cinco indicadores em bruto e a evolução desde 2018.',
      'One card per mainland Portuguese municipality: score, rank, profile across the five '
      'dimensions, all twenty-five raw indicators and the change since 2018.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="controls">
      <div class="field"><label>''' + L('Procurar', 'Search') + '''</label>
        <input type="search" id="q" placeholder="''' + L('Nome do município...', 'Municipality name...') + '''"
               aria-label="''' + L('Procurar município', 'Search municipality') + '''"></div>
      <div class="field"><label>''' + L('Distrito', 'District') + '''</label>
        <select id="dist" aria-label="''' + L('Filtrar por distrito', 'Filter by district') + '''"></select></div>
      <div class="field"><label>''' + L('Ordenar', 'Sort') + '''</label>
        <select id="ord" aria-label="''' + L('Ordenar', 'Sort') + '''">
        <option value="rank">''' + L('Melhor BFI primeiro', 'Highest BFI first') + '''</option>
        <option value="rank-">''' + L('Pior BFI primeiro', 'Lowest BFI first') + '''</option>
        <option value="nome">''' + L('Nome A a Z', 'Name A to Z') + '''</option>
        <option value="delta">''' + L('Maior subida desde 2018', 'Biggest rise since 2018') + '''</option>
        <option value="delta-">''' + L('Maior descida desde 2018', 'Biggest fall since 2018') + '''</option>
        <option value="pop">''' + L('População', 'Population') + '''</option>
      </select></div>
      <div class="seg" id="filtro">
        <button type="button" data-f="" aria-pressed="true">''' + L('Todos', 'All') + '''</button>
        <button type="button" data-f="cap">''' + L('Capitais', 'Capitals') + '''</button>
        <button type="button" data-f="bs">''' + L('Com bicicletas partilhadas', 'With bike sharing') + '''</button>
      </div>
    </div>
    <p class="small muted" id="cnt" style="margin:-4px 0 14px"></p>
    <div class="mcards" id="cards"></div>
    <p id="vazio" class="muted" style="display:none;padding:40px 0;text-align:center">''' + L(
      'Nenhum município corresponde a esta procura.',
      'No municipality matches this search.') + '''</p>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var q='', dist='', ord='rank', filtro='';
  var cards = document.getElementById('cards'), selD = document.getElementById('dist');
  selD.appendChild(h('option',{value:''}, T.allDistricts));
  M.distritos.forEach(function(d){ selD.appendChild(h('option',{value:d},d)); });
  function norm(s){ return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,''); }

  function lista(){
    var out = M.all.filter(function(m){
      if(!m.s25) return false;
      if(dist && m.dist!==dist) return false;
      if(filtro==='cap' && !m.cap) return false;
      if(filtro==='bs' && !m.bs) return false;
      if(q && norm(m.n+' '+m.dist).indexOf(q)<0) return false;
      return true;
    });
    var d = function(m){ return m.s18c ? m.s25.bfi-m.s18c.bfi : 0; };
    return out.sort({
      'rank':  function(a,b){ return a.s25.rank-b.s25.rank; },
      'rank-': function(a,b){ return b.s25.rank-a.s25.rank; },
      'nome':  function(a,b){ return a.n.localeCompare(b.n,'pt'); },
      'delta': function(a,b){ return d(b)-d(a); },
      'delta-':function(a,b){ return d(a)-d(b); },
      'pop':   function(a,b){ return (b.pop||0)-(a.pop||0); }
    }[ord]);
  }

  function draw(){
    var data = lista();
    document.getElementById('cnt').textContent = data.length+' '+T.of+' '+M.all.length+' '+T.municipalities;
    document.getElementById('vazio').style.display = data.length ? 'none' : 'block';
    cards.innerHTML = '';
    var frag = document.createDocumentFragment();
    data.forEach(function(m){
      var dv = m.s18c ? m.s25.bfi-m.s18c.bfi : null;
      var dcls = dv===null ? 'flat' : (dv>0.05?'up':(dv<-0.05?'down':'flat'));
      frag.appendChild(h('a',{class:'mcard', href:'%(md)s'+m.slug+'.html'},
        '<span class="rank">'+m.s25.rank+'%(ord)s</span>'+
        '<div class="nm">'+esc(m.n)+'</div>'+
        '<div class="ds">'+esc(m.dist)+(m.cap?' · '+T.capital:'')+'</div>'+
        '<div class="sc"><b>'+F.n(m.s25.bfi,2)+'</b><i>BFI 2025</i>'+
        (dv===null?'':'<span class="delta '+dcls+'" style="margin-left:auto">'+F.sign(dv,2)+'</span>')+'</div>'+
        '<div class="spark" title="C1-C5">'+sparkDims(m.s25)+'</div>'));
    });
    cards.appendChild(frag);
  }

  document.getElementById('q').addEventListener('input', function(){ q=norm(this.value.trim()); draw(); });
  selD.addEventListener('change', function(){ dist=this.value; draw(); });
  document.getElementById('ord').addEventListener('change', function(){ ord=this.value; draw(); });
  document.getElementById('filtro').addEventListener('click', function(ev){
    var b=ev.target.closest('button[data-f]'); if(!b) return;
    filtro=b.dataset.f;
    this.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false');});
    b.setAttribute('aria-pressed','true'); draw();
  });
  draw();
  cards._redraw = draw; cards.setAttribute('data-redraw','1');
})();
</script>''' % {'md': MD(), 'ord': L('.º', '')}

    emit('muns', L('Os 278 municípios · Bike Friendly Index',
                   'All 278 municipalities · Bike Friendly Index'), body,
      L('Fichas do Bike Friendly Index para os 278 municípios de Portugal Continental.',
        'Bike Friendly Index cards for the 278 municipalities of mainland Portugal.'), scripts)


# ===========================================================================
#  6 · EXPLORADOR
# ===========================================================================
def pg_explorador():
    opts_campo = ''.join('<option value="%s">%s</option>' % (k, lab)
      for k, lab in [('bfi', L('BFI total', 'Overall BFI'))] +
                    [(DIMK[ix], d['cod'] + ' ' + T(d['nome'])) for ix, d in enumerate(DIMS)])
    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('Mapa interactivo', 'Interactive map') + '''</p>
    <h1 style="max-width:16ch">''' + L('Explorador', 'Explorer') + '''</h1>
    <p class="lead" style="max-width:60ch">''' + L(
      'Cruze ano, série e dimensão. Passe o rato sobre o mapa para ver os valores, clique '
      'para abrir a ficha completa.',
      'Cross year, series and dimension. Hover the map to read the values, click to open the '
      'full card.') + '''</p>
    <p class="small muted" style="margin-top:-6px">''' + L(
      'A versão anterior do explorador continua disponível em '
      '<a href="' + LEGACY() + '">explorador-v1</a>, tal como foi publicada.',
      'The previous version of the explorer is still available at '
      '<a href="' + LEGACY() + '">explorador-v1</a>, exactly as it was published.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="controls">
      <div class="field"><label>''' + L('Série', 'Series') + '''</label><select id="serie">
        <option value="s25">BFI 2025</option>
        <option value="s18c">''' + L('BFI 2018 comparável', 'BFI 2018 comparable') + '''</option>
        <option value="s18">''' + L('BFI 2018 publicado', 'BFI 2018 as published') + '''</option>
        <option value="delta">''' + L('Variação 2018 a 2025', 'Change 2018 to 2025') + '''</option>
      </select></div>
      <div class="field"><label>''' + L('Indicador', 'Indicator') + '''</label>
        <select id="campo">''' + opts_campo + '''</select></div>
      <div class="field"><label>''' + L('Procurar', 'Search') + '''</label>
        <input type="search" id="busca" placeholder="''' + L('Ir para um município...', 'Jump to a municipality...') + '''"
               aria-label="''' + L('Procurar município', 'Search municipality') + '''"></div>
    </div>
    <div class="explorer">
      <div class="mapbox fullbleed" id="mapa"></div>
      <div class="map-overlay">
        <div id="leg"></div>
        <p class="map-attrib" id="attrib"></p>
      </div>
      <div class="explorer-panels">
        <div class="card" id="painel"></div>
        <div class="card">
          <p class="eyebrow">''' + L('Extremos da vista actual', 'Extremes of the current view') + '''</p>
          <div id="extremos"></div>
        </div>
      </div>
    </div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var serie='s25', campo='bfi';
  var host = document.getElementById('mapa');
  var map = choropleth(host, {serie:serie, campo:campo, link:false, tiles:true,
    par:'xMinYMid meet',
    onSelect:function(m){ map.set('sel', m.d); painel(m); }});
  document.getElementById('attrib').textContent = T.attrib;
  var leg = document.getElementById('leg');
  var NOMES = {bfi:'%(total)s'};
  M.dims.forEach(function(d,ix){ NOMES[['c1','c2','c3','c4','c5'][ix]] = d.cod+' '+d.nome; });
  var SNOME = {s25:'BFI 2025', s18c:'%(s18c)s', s18:'%(s18)s', delta:'%(chg)s'};

  function val(m){
    if(serie==='delta'){ return (m.s25&&m.s18c) ? m.s25[campo]-m.s18c[campo] : null; }
    return m[serie] ? m[serie][campo] : null;
  }

  function painel(m){
    var p = document.getElementById('painel');
    if(!m){
      p.innerHTML = '<p class="eyebrow">%(pick)s</p><h3>%(none)s</h3>'+
        '<p class="small muted">%(hint)s</p>';
      return;
    }
    var s = m.s25, d = m.s18c ? s.bfi-m.s18c.bfi : null;
    p.innerHTML = '<p class="eyebrow">'+esc(m.dist)+(m.cap?' · '+T.capital:'')+'</p>'+
      '<h3 style="margin-bottom:10px">'+esc(m.n)+'</h3>'+
      '<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:14px">'+
      '<b style="font-family:var(--font-display);font-size:2.6rem;line-height:1;color:var(--accent)">'+F.n(s.bfi,2)+'</b>'+
      '<span class="small muted">BFI 2025 · '+s.rank+T.ofN+'</span>'+
      (d===null?'':'<span class="delta '+(d>0?'up':'down')+'" style="margin-left:auto">'+F.sign(d,2)+'</span>')+'</div>'+
      '<div id="radarP"></div>'+
      '<div class="kv" style="margin-top:14px">'+
      '<div><div class="k">%(pop)s</div><div class="v">'+F.i(m.pop)+'</div></div>'+
      '<div><div class="k">%(cic)s</div><div class="v">'+F.n(m.cic,1)+' <small>km</small></div></div>'+
      '<div><div class="k">%(bike)s</div><div class="v">'+F.pct(m.ub||0,1)+'</div></div>'+
      '</div>'+
      '<a class="btn" style="margin-top:16px;width:100%%;justify-content:center" href="%(md)s'+m.slug+'.html">%(full)s</a>';
    radar(document.getElementById('radarP'),
      [{name:m.n, v:s}, {name:T.natAvg, v:MEDIA.s25, dashed:true}]);
  }

  function extremos(){
    var rows = M.all.map(function(m){ return {m:m, v:val(m)}; })
                    .filter(function(r){ return r.v!==null && !isNaN(r.v); })
                    .sort(function(a,b){ return b.v-a.v; });
    function blk(t, arr){
      return '<p class="small" style="font-weight:600;margin:10px 0 6px">'+t+'</p>'+
        arr.map(function(r){
          return '<div style="display:flex;justify-content:space-between;gap:10px;padding:3px 0;font-size:.88rem">'+
          '<a href="%(md)s'+r.m.slug+'.html" style="color:inherit;text-decoration:none">'+esc(r.m.n)+'</a>'+
          '<span class="num" style="font-weight:600"><b style="display:inline-block;width:9px;height:9px;'+
          'border-radius:2px;margin-right:6px;background:'+colorOf(map.scaleName(), r.v)+'"></b>'+
          (serie==='delta'?F.sign(r.v,2):F.n(r.v,2))+'</span></div>';
        }).join('');
    }
    document.getElementById('extremos').innerHTML =
      blk('%(hi)s', rows.slice(0,5)) + blk('%(lo)s', rows.slice(-5).reverse());
  }

  function redraw(){
    map.set('serie', serie); map.set('campo', campo);
    mapLegend(leg, map.scaleName(), SNOME[serie] + ' · ' + NOMES[campo]);
    extremos();
  }
  document.getElementById('serie').addEventListener('change', function(){ serie=this.value; redraw(); });
  document.getElementById('campo').addEventListener('change', function(){ campo=this.value; redraw(); });
  document.getElementById('busca').addEventListener('input', function(){
    var q=this.value.trim().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
    if(q.length<3) return;
    var hit = M.all.filter(function(m){
      return m.n.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').indexOf(q)===0; })[0];
    if(hit){ map.set('sel', hit.d); painel(hit); }
  });
  painel(null); redraw();
  host.setAttribute('data-redraw','1');
})();
</script>''' % {'md': MD(), 'total': L('BFI total', 'Overall BFI'),
                's18c': L('BFI 2018 comparável', 'BFI 2018 comparable'),
                's18': L('BFI 2018 publicado', 'BFI 2018 as published'),
                'chg': L('Variação 2018 a 2025', 'Change 2018 to 2025'),
                'pick': L('Seleccione', 'Select'),
                'none': L('Nenhum município seleccionado', 'No municipality selected'),
                'hint': L('Clique no mapa ou use a caixa de procura para ver o perfil de um '
                          'município nas cinco dimensões.',
                          'Click the map or use the search box to see a municipality profile '
                          'across the five dimensions.'),
                'pop': L('População', 'Population'), 'cic': L('Ciclovias', 'Cycle lanes'),
                'bike': L('Bicicleta', 'Cycling'),
                'full': L('Ver a ficha completa', 'Open the full card'),
                'hi': L('Cinco valores mais altos', 'Five highest'),
                'lo': L('Cinco valores mais baixos', 'Five lowest')}

    emit('explorer', L('Explorador · Bike Friendly Index', 'Explorer · Bike Friendly Index'), body,
      L('Mapa interactivo do Bike Friendly Index por ano, série e dimensão.',
        'Interactive Bike Friendly Index map by year, series and dimension.'), scripts)


# ===========================================================================
#  7 · COMPARAR MUNICIPIOS
# ===========================================================================
def pg_comparar():
    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('Lado a lado', 'Side by side') + '''</p>
    <h1 style="max-width:18ch">''' + L('Comparar municípios', 'Compare municipalities') + '''</h1>
    <p class="lead" style="max-width:60ch">''' + L(
      'Escolha até três municípios e veja-os lado a lado nas cinco dimensões, nos indicadores '
      'de contexto e na evolução desde 2018.',
      'Pick up to three municipalities and set them side by side across the five dimensions, '
      'the context indicators and the change since 2018.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="controls" id="pick"></div>
    <div id="out"></div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var escolha = ['1106','1312','0105'];
  var pick = document.getElementById('pick'), out = document.getElementById('out');
  var ordenados = M.all.slice().sort(function(a,b){ return a.n.localeCompare(b.n,'pt'); });

  for(var i=0;i<3;i++){
    (function(ix){
      var f = h('div',{class:'field'});
      f.appendChild(h('label',{}, '%(mun)s ' + (ix+1)));
      var s = h('select',{'aria-label':'%(mun)s '+(ix+1)});
      s.appendChild(h('option',{value:''},'%(nonesel)s'));
      ordenados.forEach(function(m){
        var o = h('option',{value:m.d}, m.n + ' · ' + m.dist);
        if(m.d===escolha[ix]) o.setAttribute('selected','');
        s.appendChild(o);
      });
      s.addEventListener('change', function(){ escolha[ix]=this.value; draw(); });
      f.appendChild(s); pick.appendChild(f);
    })(i);
  }

  function draw(){
    var ms = escolha.map(function(d){ return d ? M.get(d) : null; }).filter(Boolean);
    if(!ms.length){ out.innerHTML='<p class="muted">%(atleast)s</p>'; return; }
    out.innerHTML =
      '<div class="grid-3" id="fichas" style="grid-template-columns:repeat('+ms.length+',1fr)"></div>'+
      '<div class="card" style="margin-top:20px"><p class="eyebrow">%(profile)s</p>'+
      '<h3>%(sbs)s</h3><div id="cmpBars"></div></div>'+
      '<div class="card card-pad-0" style="margin-top:20px">'+
      '<div style="padding:22px 22px 0"><p class="eyebrow">%(detail)s</p><h3>%(ctx)s</h3></div>'+
      '<div class="tbl-wrap" style="border:0;border-radius:0"><table class="tbl" id="cmpTbl"></table></div></div>';

    var f = document.getElementById('fichas');
    ms.forEach(function(m){
      var d = m.s18c ? m.s25.bfi-m.s18c.bfi : null;
      f.appendChild(h('div',{class:'card'},
        '<p class="eyebrow" style="margin-bottom:4px">'+esc(m.dist)+'</p>'+
        '<h3 style="margin-bottom:10px"><a href="%(md)s'+m.slug+'.html" style="color:inherit;text-decoration:none">'+esc(m.n)+'</a></h3>'+
        '<div style="display:flex;align-items:baseline;gap:9px">'+
        '<b style="font-family:var(--font-display);font-size:2.6rem;line-height:1;color:var(--accent)">'+F.n(m.s25.bfi,2)+'</b>'+
        '<span class="small muted">'+m.s25.rank+T.ofN+'</span></div>'+
        (d===null?'':'<p class="small" style="margin-top:8px"><span class="delta '+(d>0?'up':'down')+'">'+
          F.sign(d,2)+'</span> <span class="muted">%(since)s</span></p>')));
    });

    groupedBars(document.getElementById('cmpBars'),
      M.dims.map(function(d){ return d.cod+' '+d.curto; }),
      ms.map(function(m){ return {name:m.n, v:['c1','c2','c3','c4','c5'].map(function(k){ return m.s25[k]; })}; }),
      {max:10, height:300});

    var LIN = [
      ['%(l1)s', function(m){ return F.i(m.pop); }],
      ['%(l2)s', function(m){ return F.n(m.area,1)+' km²'; }],
      ['%(l3)s', function(m){ return F.n(m.cic,1)+' km'; }],
      ['%(l4)s', function(m){ return F.n(m.cicU,1)+' km'; }],
      ['%(l5)s', function(m){ return m.bs?'%(yes)s':'%(no)s'; }],
      ['%(l6)s', function(m){ return F.eur(m.inv); }],
      ['%(l7)s', function(m){ return F.pct(m.ub||0,2); }],
      ['%(l8)s', function(m){ return F.pct(m.um||0,1); }],
      ['%(l9)s', function(m){ return m.s18?F.n(m.s18.bfi,2):'-'; }],
      ['%(l10)s', function(m){ return m.s18c?F.n(m.s18c.bfi,2):'-'; }],
      ['BFI 2025', function(m){ return F.n(m.s25.bfi,2); }]
    ];
    document.getElementById('cmpTbl').innerHTML =
      '<thead><tr><th>%(ind)s</th>'+ms.map(function(m){return '<th style="text-align:right">'+esc(m.n)+'</th>';}).join('')+'</tr></thead>'+
      '<tbody>'+LIN.map(function(l){
        return '<tr><td>'+l[0]+'</td>'+ms.map(function(m){return '<td class="n">'+l[1](m)+'</td>';}).join('')+'</tr>';
      }).join('')+'</tbody>';
  }
  draw();
  out._redraw = draw; out.setAttribute('data-redraw','1');
})();
</script>''' % {'md': MD(), 'mun': L('Município', 'Municipality'),
                'nonesel': L('(nenhum)', '(none)'),
                'atleast': L('Escolha pelo menos um município.', 'Pick at least one municipality.'),
                'profile': L('Perfil', 'Profile'),
                'sbs': L('As cinco dimensões, lado a lado', 'The five dimensions, side by side'),
                'detail': L('Detalhe', 'Detail'),
                'ctx': L('Indicadores de contexto', 'Context indicators'),
                'since': L('desde 2018', 'since 2018'),
                'ind': L('Indicador', 'Indicator'),
                'yes': L('Sim', 'Yes'), 'no': L('Não', 'No'),
                'l1': L('População 2021', 'Population 2021'),
                'l2': L('Área', 'Area'),
                'l3': L('Ciclovias no concelho', 'Cycle lanes in the municipality'),
                'l4': L('Ciclovias em área urbana', 'Cycle lanes in urban areas'),
                'l5': L('Bicicletas partilhadas', 'Bike sharing'),
                'l6': L('Investimento 2023-2025', 'Spending 2023-2025'),
                'l7': L('Bicicleta na repartição modal', 'Cycling mode share'),
                'l8': L('Mulheres entre quem pedala', 'Women among cyclists'),
                'l9': L('BFI 2018 publicado', 'BFI 2018 as published'),
                'l10': L('BFI 2018 comparável', 'BFI 2018 comparable')}

    emit('compare', L('Comparar municípios · Bike Friendly Index',
                      'Compare municipalities · Bike Friendly Index'), body,
      L('Compare até três municípios portugueses no Bike Friendly Index.',
        'Compare up to three Portuguese municipalities on the Bike Friendly Index.'), scripts)


# ===========================================================================
#  8 · METODOLOGIA
# ===========================================================================
PESOS_2018 = {'C1': '15%', 'C2': '30%', 'C3': '25%', 'C4': '15%', 'C5': '15%'}

def pg_metodologia():
    pesos = ''.join(
      '<tr><td><strong>%s</strong> %s</td><td class="n">%s</td><td class="n">%d%%</td></tr>'
      % (d['cod'], T(d['nome']), PESOS_2018[d['cod']], round(d['peso'] * 100)) for d in DIMS)

    grupos = {}
    for x in IND:
        grupos.setdefault(x['dim'], []).append(x)
    gl = []
    for d in DIMS:
        itens = grupos.get(d['k'], [])
        linhas = ''.join(
          '<tr><td class="num">%s</td><td>%s</td><td class="muted small">%s</td></tr>'
          % (x['k'], T(x['nome']), T(x['un'])) for x in itens)
        gl.append(
          '<h3>%s %s <span class="muted" style="font-weight:400">· %d%% %s · %d %s</span></h3>'
          '<p class="muted">%s</p>'
          '<table><thead><tr><th>%s</th><th>%s</th><th>%s</th>'
          '</tr></thead><tbody>%s</tbody></table>'
          % (d['cod'], T(d['nome']), round(d['peso'] * 100),
             L('do índice', 'of the index'), len(itens), L('indicadores', 'indicators'),
             T(d['desc']), L('Código', 'Code'), L('Indicador', 'Indicator'),
             L('Unidade', 'Unit'), linhas))

    fontes = [
      ('INE, Censos e BGRI' if LANG == 'pt' else 'Statistics Portugal, Census and BGRI',
       L('População, alojamentos, repartição modal, diversidade de usos',
         'Population, dwellings, mode share, mix of uses'),
       L('Censos 2011', '2011 Census'), L('Censos 2021', '2021 Census')),
      ('DGT', L('Limites administrativos e áreas urbanas', 'Administrative boundaries and urban areas'),
       L('BGRI 2011 e CORINE Land Cover 2012', 'BGRI 2011 and CORINE Land Cover 2012'),
       L('CAOP 2024 e Carta de Ocupação do Solo', 'CAOP 2024 and national land cover map')),
      ('OpenStreetMap', L('Rede ciclável, rede viária, amenidades, bicicletas partilhadas',
                          'Cycle network, road network, amenities, bike sharing'),
       L('Extracção de 2018', '2018 extract'), L('Extracção de 2025', '2025 extract')),
      ('Base.gov', L('Contratação pública em mobilidade sustentável',
                     'Public procurement in sustainable mobility'),
       L('Triénio 2015-2017', '2015-2017'), L('Triénio 2023-2025', '2023-2025')),
      (L('Modelo digital de elevação', 'Digital elevation model'),
       L('Declive do terreno', 'Terrain slope'),
       L('EU-DEM, Copernicus', 'EU-DEM, Copernicus'),
       L('Modelo de alta resolução', 'High resolution model')),
    ]
    fontes_tbl = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % f for f in fontes)

    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('Como é calculado', 'How it is calculated') + '''</p>
    <h1 style="max-width:14ch">''' + L('Metodologia', 'Methodology') + '''</h1>
    <p class="lead" style="max-width:64ch">''' + L(
      'Cinco dimensões, vinte e cinco indicadores, 278 municípios, exclusivamente a partir de '
      'dados abertos.',
      'Five dimensions, twenty-five indicators, 278 municipalities, built entirely from open '
      'data.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="prose">
      <h2>''' + L('A ideia', 'The idea') + '''</h2>
      <p>''' + L(
        'O Bike Friendly Index avalia a amigabilidade de um município para a utilização da '
        'bicicleta como modo de transporte urbano. Foi construído a partir da literatura '
        'científica sobre os factores que explicam os níveis de utilização da bicicleta, aos '
        'quais se acrescentou o compromisso político, para medir quanto cada município está '
        'efectivamente a investir na promoção da bicicleta e da mobilidade urbana sustentável.',
        'The Bike Friendly Index assesses how friendly a municipality is to cycling as a mode '
        'of urban transport. It was built on the scientific literature about what drives '
        'cycling levels, with political commitment added on top, to capture how much each '
        'municipality is actually investing in cycling and in sustainable urban mobility.') + '''</p>
      <p>''' + L(
        'Os valores são normalizados numa escala de 0 a 10. O índice final é uma média '
        'ponderada das cinco dimensões, e cada dimensão é por sua vez uma média ponderada dos '
        'seus indicadores.',
        'Values are normalised on a 0 to 10 scale. The final index is a weighted mean of the '
        'five dimensions, and each dimension is itself a weighted mean of its indicators.') + '''</p>

      <h2>''' + L('Os pesos mudaram em 2025', 'The weights changed in 2025') + '''</h2>
      <p>''' + L(
        'A edição de 2025 reequilibra os pesos: retira importância ao que é herdado do '
        'território, como o declive, e reforça o que depende de decisão política e de '
        'comportamento, como o investimento municipal e a utilização efectiva.',
        'The 2025 edition rebalances the weights: it takes weight away from what the territory '
        'simply inherited, such as slope, and gives more to what depends on policy and '
        'behaviour, such as municipal spending and actual cycling levels.') + '''</p>
      <table><thead><tr><th>''' + L('Dimensão', 'Dimension') + '''</th>
      <th style="text-align:right">''' + L('Peso em 2018', 'Weight in 2018') + '''</th>
      <th style="text-align:right">''' + L('Peso em 2025', 'Weight in 2025') + '''</th></tr></thead>
      <tbody>''' + pesos + '''</tbody></table>

      <h2>''' + L('Normalização', 'Normalisation') + '''</h2>
      <p>''' + L(
        'Indicadores com unidades tão diferentes (quilómetros, euros, percentagens, habitantes '
        'por km²) só se combinam depois de levados para a mesma escala de 0 a 10. A escolha da '
        'régua é feita indicador a indicador, conforme o que ele mede: uns são medidos contra o '
        'melhor resultado do país, noutros existe um patamar a partir do qual mais não acrescenta '
        'à mobilidade ciclável, e noutros ainda usa-se a amplitude observada entre municípios. '
        'Sempre que um valor mais baixo é melhor, a escala é invertida.',
        'Indicators in very different units (kilometres, euros, percentages, people per km²) '
        'can only be combined once brought onto the same 0 to 10 scale. The yardstick is chosen '
        'indicator by indicator, according to what it measures: some are measured against the '
        'best result in the country, some have a level beyond which more adds nothing for '
        'cycling, and others use the range observed across municipalities. Where a lower value '
        'is better, the scale is inverted.') + '''</p>
      <p>''' + L(
        'Os parâmetros exactos desta etapa não são publicados. Os valores medidos de cada '
        'indicador e os resultados finais por dimensão são abertos.',
        'The exact parameters of this step are not published. The measured values of each '
        'indicator and the final results by dimension are open.') + '''</p>

      <h2>''' + L('Os vinte e cinco indicadores', 'The twenty-five indicators') + '''</h2>
      ''' + ''.join(gl) + '''

      <h2>''' + L('Fontes', 'Sources') + '''</h2>
      <p>''' + L(
        'Só foram usados dados abertos, por duas razões: garantir acesso sem restrições '
        'proprietárias e permitir que qualquer pessoa corrija e complemente as bases de partida.',
        'Only open data was used, for two reasons: to guarantee access without proprietary '
        'restrictions and to let anyone correct and extend the underlying datasets.') + '''</p>
      <table><thead><tr><th>''' + L('Fonte', 'Source') + '''</th>
      <th>''' + L('O que fornece', 'What it provides') + '''</th>
      <th>''' + L('Edição 2018', '2018 edition') + '''</th>
      <th>''' + L('Edição 2025', '2025 edition') + '''</th></tr></thead>
      <tbody>''' + fontes_tbl + '''</tbody></table>

      <h2>''' + L('Limitações conhecidas', 'Known limitations') + '''</h2>
      <ul>
        <li>''' + L(
          'A cobertura do OpenStreetMap é desigual, sobretudo em áreas de menor densidade '
          'populacional. O BFI devolve informação a essa base sempre que recolhe dados '
          'complementares.',
          'OpenStreetMap coverage is uneven, particularly in less densely populated areas. The '
          'BFI feeds information back into that database whenever it gathers complementary '
          'data.') + '''</li>
        <li>''' + L(
          'A existência de sistemas de bicicletas partilhadas é tratada como sim ou não. Não há '
          'dados actualizados e credíveis sobre número de bicicletas, docas ou cobertura '
          'territorial de cada sistema.',
          'Bike sharing is treated as a yes or no. There is no current, reliable data on the '
          'number of bikes, docks or territorial coverage of each scheme.') + '''</li>
        <li>''' + L(
          'O compromisso político mede investimento contratado, não investimento executado nem '
          'qualidade da intervenção. Um único contrato de dimensão elevada pode deslocar muito '
          'a posição de um município pequeno.',
          'Political commitment measures contracted spending, not spending delivered nor the '
          'quality of the works. A single large contract can move a small municipality a long '
          'way up the ranking.') + '''</li>
        <li>''' + L(
          'Em municípios de baixa densidade, denominadores pequenos tornam os indicadores per '
          'capita e por km² voláteis entre edições.',
          'In low density municipalities, small denominators make per capita and per km² '
          'indicators volatile between editions.') + '''</li>
      </ul>

      <div class="alertzone" style="margin-top:2em">
        ''' + alertpop(L(
          '<p>Mudaram os pesos, o conjunto de indicadores e as fontes de base. Por isso os valores '
          'publicados em 2018 e em 2025 <strong>não são directamente comparáveis</strong>. Para a '
          'comparação usa-se uma série recalculada, em que os pesos de 2025 são aplicados aos '
          'indicadores de 2018.</p>'
          '<p>Mesmo essa série tem um limite por resolver: a base de normalização continua a ser '
          'a de cada ano. Está em curso o trabalho de renormalizar ambas as edições contra um '
          'referencial comum.</p>',
          '<p>The weights, the indicator set and the underlying sources all changed. The figures '
          'published in 2018 and in 2025 are therefore <strong>not directly comparable</strong>. '
          'For comparison we use a recomputed series, applying the 2025 weights to the 2018 '
          'indicators.</p>'
          '<p>Even that series has an open limit: the normalisation base is still each year’s '
          'own. Work to renormalise both editions against a shared benchmark is under way.</p>')) + '''
        <h2 style="margin-top:0">''' + L('Comparabilidade entre edições', 'Comparability across editions') + '''</h2>
      </div>
      <p>''' + L(
        'Os valores publicados em 2018 e em 2025 não são directamente comparáveis. A comparação '
        'usa uma série recalculada, com os pesos de 2025 aplicados aos indicadores de 2018.',
        'The figures published in 2018 and in 2025 are not directly comparable. The comparison '
        'uses a recomputed series, applying the 2025 weights to the 2018 indicators.') + '''</p>

      <h2>''' + L('Licença e citação', 'Licence and citation') + '''</h2>
      <p>''' + L(
        'O BFI é disponibilizado sob licença <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" '
        'target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>, que permite remisturar, adaptar e '
        'reutilizar para fins não comerciais, com crédito e partilha nos mesmos termos.',
        'The BFI is released under a <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" '
        'target="_blank" rel="noopener">CC BY-NC-SA 4.0</a> licence, which allows remixing, '
        'adaptation and reuse for non-commercial purposes, with credit and sharing on the same '
        'terms.') + '''</p>
      <blockquote>Figueiredo, A. P., Vale, D. S. &amp; Lopes, A. S. (2025).
      <em>Bike Friendly Index Portugal 2025</em>. BEAM, Faculdade de Arquitectura,
      Universidade de Lisboa.</blockquote>
      <p class="small muted">''' + L(
        'Edição de 2018: Figueiredo, A. P. e Vale, D. S. (2018). <em>BikeFriendlyIndex, um '
        'índice para avaliação da amigabilidade de um concelho para a utilização da bicicleta '
        'enquanto modo de transporte urbano</em>.',
        '2018 edition: Figueiredo, A. P. and Vale, D. S. (2018). <em>BikeFriendlyIndex, an '
        'index to assess how friendly a municipality is to cycling as a mode of urban '
        'transport</em>.') + '''</p>
    </div>
  </div>
</section>
'''
    emit('method', L('Metodologia · Bike Friendly Index', 'Methodology · Bike Friendly Index'), body,
      L('Como é calculado o Bike Friendly Index: dimensões, indicadores, pesos, normalização e fontes.',
        'How the Bike Friendly Index is calculated: dimensions, indicators, weights, normalisation and sources.'))


# ===========================================================================
#  9 · DADOS
# ===========================================================================
def pg_dados():
    up = '../' if LANG == 'en' else ''
    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('Dados abertos', 'Open data') + '''</p>
    <h1 style="max-width:14ch">''' + L('Descarregar', 'Download') + '''</h1>
    <p class="lead" style="max-width:62ch">''' + L(
      'Tudo o que alimenta este site está disponível em formatos abertos, sob licença '
      'CC BY-NC-SA 4.0.',
      'Everything behind this site is available in open formats, under a CC BY-NC-SA 4.0 '
      'licence.') + '''</p>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="grid-2">
      <div class="card">
        <p class="eyebrow">''' + L('Tabelas', 'Tables') + '''</p>
        <h3>''' + L('Resultados por município', 'Results by municipality') + '''</h3>
        <p class="small muted">''' + L(
          'Formato longo, 834 linhas: os 278 municípios nas três séries (2018 publicado, 2018 '
          'comparável, 2025), com as cinco dimensões, o BFI e a posição.',
          'Long format, 834 rows: the 278 municipalities across the three series (2018 as '
          'published, 2018 comparable, 2025), with the five dimensions, the BFI and the rank.') + '''</p>
        <div class="btn-row" style="margin-top:14px">
          <a class="btn ghost" href="''' + up + '''dados/bfi_municipios.csv" download>bfi_municipios.csv</a>
          <button class="btn ghost" type="button" id="dlAll">''' + L('Gerar CSV completo', 'Build full CSV') + '''</button>
        </div>
      </div>
      <div class="card">
        <p class="eyebrow">''' + L('Tabelas', 'Tables') + '''</p>
        <h3>''' + L('Indicadores detalhados', 'Detailed indicators') + '''</h3>
        <p class="small muted">''' + L(
          'Os 25 indicadores por município, com o valor medido em 2025 e a posição no país.',
          'All 25 indicators per municipality, with the value measured in 2025 and the position '
          'in Portugal.') + '''</p>
        <div class="btn-row" style="margin-top:14px">
          <a class="btn ghost" href="''' + up + '''dados/bfi_indicadores.csv" download>bfi_indicadores.csv</a>
        </div>
      </div>
      <div class="card">
        <p class="eyebrow">''' + L('Geografia', 'Geography') + '''</p>
        <h3>GeoJSON</h3>
        <p class="small muted">''' + L(
          'Geometria simplificada dos 278 municípios com os resultados associados. Uma camada '
          'por série.',
          'Simplified geometry for the 278 municipalities with the results attached. One layer '
          'per series.') + '''</p>
        <div class="btn-row" style="margin-top:14px">
          <a class="btn ghost" href="''' + up + '''dados/bfi_2025.geojson" download>bfi_2025.geojson</a>
          <a class="btn ghost" href="''' + up + '''dados/bfi_2018_original.geojson" download>bfi_2018_original.geojson</a>
          <a class="btn ghost" href="''' + up + '''dados/bfi_2018_metodo2025.geojson" download>bfi_2018_metodo2025.geojson</a>
        </div>
      </div>
      <div class="card">
        <p class="eyebrow">''' + L('Agregados', 'Aggregates') + '''</p>
        <h3>''' + L('Valores nacionais', 'National figures') + '''</h3>
        <p class="small muted">''' + L(
          'Médias por série e dimensão, investimento total, extensão de ciclovias e número de '
          'municípios com bicicletas partilhadas.',
          'Averages by series and dimension, total spending, cycle lane length and the number '
          'of municipalities with bike sharing.') + '''</p>
        <div class="btn-row" style="margin-top:14px">
          <a class="btn ghost" href="''' + up + '''dados/portugal.json" download>portugal.json</a>
        </div>
      </div>
    </div>

    ''' + callout('info', ICON_INFO, L(
      '<p><strong>Esquema das tabelas.</strong> <code>dtmn</code> é o código de município com '
      'quatro dígitos e zeros à esquerda. <code>serie</code> distingue <code>original_2018</code> '
      'de <code>metodo_2025</code>. As colunas <code>c1_declive</code> a <code>c5_utiliza</code> '
      'e <code>bfi</code> estão na escala de 0 a 10.</p>',
      '<p><strong>Table schema.</strong> <code>dtmn</code> is the four digit municipality code, '
      'zero padded. <code>serie</code> separates <code>original_2018</code> from '
      '<code>metodo_2025</code>. Columns <code>c1_declive</code> through <code>c5_utiliza</code> '
      'and <code>bfi</code> are on the 0 to 10 scale.</p>')) + '''

    <div class="card" style="margin-top:4px">
      <p class="eyebrow">''' + L('Acesso e uso', 'Access and use') + '''</p>
      <h3>''' + L('O que está e o que não está publicado', 'What is and is not published') + '''</h3>
      <p class="small muted">''' + L(
        'Estão publicados os resultados finais (BFI, cinco dimensões e posição), os valores '
        'medidos de cada indicador e a geografia. Não estão publicados os parâmetros de '
        'normalização nem os pesos dos indicadores dentro de cada dimensão. Para trabalho de '
        'investigação que precise da especificação completa, contacte a equipa do projecto.',
        'Published here are the final results (BFI, five dimensions and rank), the measured '
        'values of each indicator and the geography. The normalisation parameters and the weights '
        'of indicators inside each dimension are not published. For research that needs the '
        'full specification, contact the project team.') + '''</p>
    </div>
  </div>
</section>
'''
    scripts = '''<script>
document.getElementById('dlAll').addEventListener('click', function(){
  var head=['dtmn','municipality','district','capital','population_2021','area_km2',
    'cycle_lanes_km','urban_cycle_lanes_km','bike_sharing','spending_eur',
    'cycling_mode_share','women_share',
    'bfi_2025','rank_2025','c1_2025','c2_2025','c3_2025','c4_2025','c5_2025',
    'bfi_2018_published','rank_2018_published','bfi_2018_comparable','rank_2018_comparable'];
  var rows=[head];
  M.all.forEach(function(m){
    var a=m.s25||{}, b=m.s18||{}, c=m.s18c||{};
    rows.push([m.d,m.n,m.dist,m.cap?1:0,m.pop,m.area,m.cic,m.cicU,m.bs?1:0,m.inv,m.ub,m.um,
      a.bfi,a.rank,a.c1,a.c2,a.c3,a.c4,a.c5,b.bfi,b.rank,c.bfi,c.rank]);
  });
  downloadCSV('bfi_full.csv', rows);
});
</script>'''
    emit('data', L('Dados abertos · Bike Friendly Index', 'Open data · Bike Friendly Index'), body,
      L('Descarregue os dados do Bike Friendly Index em CSV, GeoJSON e JSON.',
        'Download the Bike Friendly Index data as CSV, GeoJSON and JSON.'), scripts)


# ===========================================================================
#  10 · SOBRE
# ===========================================================================
def pg_sobre():
    body = '''
<section class="tight">
  <div class="wrap">
    <p class="eyebrow">''' + L('O projecto', 'The project') + '''</p>
    <h1 style="max-width:16ch">''' + L('Quem faz o BFI', 'Who makes the BFI') + '''</h1>
  </div>
</section>
<section class="tight">
  <div class="wrap">
    <div class="prose">
      <p class="lead">''' + L(
        'O Bike Friendly Index é uma iniciativa do grupo de investigação BEAM, na Faculdade de '
        'Arquitectura da Universidade de Lisboa, e resulta de experiência acumulada de '
        'investigação e projecto na área da mobilidade activa.',
        'The Bike Friendly Index is an initiative of the BEAM research group at the Faculty of '
        'Architecture, University of Lisbon, drawing on years of research and practice in '
        'active mobility.') + '''</p>

      <h2>''' + L('Equipa', 'Team') + '''</h2>
      <p>A. P. Figueiredo, D. S. Vale ''' + L('e', 'and') + ''' A. S. Lopes.<br>
      ''' + L('BEAM · Faculdade de Arquitectura · Universidade de Lisboa',
              'BEAM · Faculty of Architecture · University of Lisbon') + '''</p>

      <h2>''' + L('Edições', 'Editions') + '''</h2>
      <p>''' + L(
        'A primeira edição do índice foi publicada em 2018, com 12 indicadores e dados dos '
        'Censos de 2011. A edição de 2025 alarga o conjunto para 25 indicadores, actualiza '
        'todas as fontes de base e reequilibra os pesos das cinco dimensões.',
        'The first edition was published in 2018, with 12 indicators and 2011 Census data. The '
        '2025 edition widens the set to 25 indicators, refreshes every underlying source and '
        'rebalances the weights of the five dimensions.') + '''</p>
      <p>''' + L(
        'O objectivo é que o índice seja recalculado regularmente, de forma a acompanhar a '
        'evolução do panorama nacional e a identificar os municípios que se vão destacando na '
        'promoção da bicicleta.',
        'The aim is to recompute the index regularly, so as to track how the national picture '
        'evolves and to identify the municipalities that stand out in promoting cycling.') + '''</p>

      <h2>''' + L('Como citar', 'How to cite') + '''</h2>
      <blockquote>Figueiredo, A. P., Vale, D. S. &amp; Lopes, A. S. (2025).
      <em>Bike Friendly Index Portugal 2025</em>. BEAM, Faculdade de Arquitectura,
      Universidade de Lisboa.</blockquote>

      <h2>''' + L('Licença', 'Licence') + '''</h2>
      <p>''' + L(
        'O BFI é cedido segundo a licença <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" '
        'target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>. Pode ser remisturado, adaptado e '
        'usado noutros trabalhos com fins não comerciais, desde que seja atribuído o devido '
        'crédito e que as novas criações sejam licenciadas nos mesmos termos.',
        'The BFI is released under a <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" '
        'target="_blank" rel="noopener">CC BY-NC-SA 4.0</a> licence. It may be remixed, adapted '
        'and used in other work for non-commercial purposes, as long as credit is given and new '
        'work is licensed on the same terms.') + '''</p>

      <h2>''' + L('Correcções', 'Corrections') + '''</h2>
      <p>''' + L(
        'Se detectar uma incorrecção ou uma omissão, nos dados ou no site, queremos saber. '
        'Como o índice assenta em dados abertos, uma correcção comunicada pode ser incorporada '
        'na base de origem e reflectir-se na edição seguinte.',
        'If you spot an error or an omission, in the data or on the site, we want to hear about '
        'it. Because the index rests on open data, a correction can be folded back into the '
        'source database and show up in the next edition.') + '''</p>
    </div>
  </div>
</section>
'''
    emit('about', L('Equipa e citação · Bike Friendly Index', 'Team and citation · Bike Friendly Index'),
      body, L('Quem faz o Bike Friendly Index, como citar e sob que licença é disponibilizado.',
              'Who makes the Bike Friendly Index, how to cite it and under what licence it is released.'))


# ===========================================================================
#  11 · FICHAS DE MUNICIPIO
# ===========================================================================
def fmt_ind(v, fmt):
    if v is None: return '-'
    if fmt == 'bool': return L('Sim', 'Yes') if v else L('Não', 'No')
    if fmt == 'frac': return n(v * 100, 2) + '%'
    if fmt == 'pct':  return n(v, 1) + '%'
    if fmt == 'eur':
        return (n(v / 1e6, 2) + ' M€') if v >= 1e6 else (i(v) + ' €')
    return i(v) if v >= 1000 else n(v, 2)


def ficha(m, ordem):
    s25, s18, s18c = m['s25'], m['s18'], m['s18c']
    d_bfi = s25['bfi'] - s18c['bfi'] if s18c else None
    d_rank = (s18c['rank'] - s25['rank']) if s18c else None

    pos_dist = sorted([x for x in MUN if x['dist'] == m['dist'] and x['s25']],
                      key=lambda x: x['s25']['rank'])
    pos_i = [x['d'] for x in pos_dist].index(m['d']) + 1

    idx = ordem.index(m['d'])
    prev = BY[ordem[idx - 1]] if idx > 0 else None
    nxt = BY[ordem[idx + 1]] if idx < len(ordem) - 1 else None

    kv = [
      (L('População 2021', 'Population 2021'), i(m['pop']), ''),
      (L('Área', 'Area'), n(m['area'], 1), 'km²'),
      (L('Ciclovias', 'Cycle lanes'), n(m['cic'], 1), L('km no concelho', 'km in the municipality')),
      (L('Em área urbana', 'In urban areas'), n(m['cicU'], 1), 'km'),
      (L('Bicicletas partilhadas', 'Bike sharing'), L('Sim', 'Yes') if m['bs'] else L('Não', 'No'), ''),
      (L('Investimento 2023-2025', 'Spending 2023-2025'), eur(m['inv']), ''),
      (L('Bicicleta no total', 'Cycling mode share'), n((m['ub'] or 0) * 100, 2),
       L('% das deslocações', '% of trips')),
      (L('Mulheres', 'Women'), n((m['um'] or 0) * 100, 1), L('% de quem pedala', '% of cyclists')),
    ]
    kv_html = ''.join('<div><div class="k">%s</div><div class="v">%s%s</div></div>'
                      % (k, v, (' <small>%s</small>' % u) if u else '') for k, v, u in kv)

    drows = []
    for ix, d in enumerate(DIMS):
        k = DIMK[ix]
        v, v18 = s25[k], (s18c[k] if s18c else None)
        nac = S25[DIMFULL[ix]]
        dd = (v - v18) if v18 is not None else None
        cls = 'up' if (dd or 0) > 0.05 else ('down' if (dd or 0) < -0.05 else 'flat')
        drows.append(
          '<tr><td><strong>%s</strong> %s<br><span class="small muted">%s %d%%</span></td>'
          '<td class="n cellbar"><i style="width:%.0f%%;background:var(--seq-300)"></i><span>%s</span></td>'
          '<td class="n">%s</td><td class="n"><span class="delta %s">%s</span></td>'
          '<td class="n muted">%s</td></tr>'
          % (d['cod'], T(d['nome']), L('peso', 'weight'), round(d['peso'] * 100),
             max(2, min(100, v / 10 * 100)), n(v),
             n(v18) if v18 is not None else '-', cls,
             sign(dd) if dd is not None else '-', n(nac)))

    grupos = {}
    for x in IND:
        grupos.setdefault(x['dim'], []).append(x)
    irows = []
    for d in DIMS:
        irows.append('<tr><td colspan="4" style="background:var(--surface-2);font-weight:650;'
                     'font-size:.82rem;letter-spacing:.03em">%s %s</td></tr>'
                     % (d['cod'], T(d['nome']).upper()))
        for x in grupos.get(d['k'], []):
            raw, pos = m['ind'].get(x['k'], [None, None])
            frac = (1 - (pos - 1) / 277.0) if pos else 0
            irows.append(
              '<tr><td class="num small">%s</td><td>%s <span class="small muted">%s</span></td>'
              '<td class="n">%s</td><td class="n cellbar">'
              '<i style="width:%.0f%%;background:var(--seq-250)"></i><span>%s</span></td></tr>'
              % (x['k'], T(x['nome']), T(x['un']), fmt_ind(raw, x['fmt']),
                 max(2, min(100, frac * 100)), ordinal(pos) if pos else '-'))

    viz_rows = ''.join(
      '<tr%s><td class="n">%d</td><td class="nm"><a href="%s.html">%s</a></td>'
      '<td class="n">%s</td></tr>'
      % (' style="background:var(--accent-soft)"' if x['d'] == m['d'] else '',
         x['s25']['rank'], x['slug'], x['n'], n(x['s25']['bfi']))
      for x in pos_dist)

    nav_prev = ('<a href="%s.html">&larr; %s %s</a>' % (prev['slug'], ordinal(prev['s25']['rank']), prev['n'])) if prev else '<span></span>'
    nav_next = ('<a href="%s.html">%s %s &rarr;</a>' % (nxt['slug'], ordinal(nxt['s25']['rank']), nxt['n'])) if nxt else '<span></span>'
    dcls = 'up' if (d_bfi or 0) > 0.05 else ('down' if (d_bfi or 0) < -0.05 else 'flat')

    body = '''
<section class="tight">
  <div class="wrap">
    <div class="ficha-top">
      <p class="small muted" style="margin:0">
        <a href="../''' + P('index') + '''" style="color:inherit">''' + L('Início', 'Home') + '''</a> ·
        <a href="../''' + P('muns') + '''" style="color:inherit">''' + L('Municípios', 'Municipalities') + '''</a> ·
        <span>''' + m['dist'] + '''</span></p>
      <button type="button" class="backbtn" onclick="bfiBack('../''' + P('muns') + '''')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M15 5l-7 7 7 7"/></svg>''' + L('Voltar', 'Back') + '''</button>
    </div>
    <div class="mhead">
      <div>
        <p class="eyebrow" style="margin-bottom:6px">''' + m['dist'] + (
          L(' · capital de distrito', ' · district capital') if m['cap'] else '') + '''</p>
        <h1 style="margin-bottom:12px">''' + m['n'] + '''</h1>
        <div class="score-big">
          <b>''' + n(s25['bfi']) + '''</b>
          <i>''' + L('BFI 2025<br>escala 0 a 10', 'BFI 2025<br>0 to 10 scale') + '''</i>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px;align-items:flex-start">
        <span class="rankpill"><b>''' + ordinal(s25['rank']) + '''</b><span>''' + L(
          'de 278 municípios', 'of 278 municipalities') + '''</span></span>
        <span class="rankpill"><b>''' + ordinal(pos_i) + '''</b><span>''' + L(
          'no distrito de ' + m['dist'], 'in ' + m['dist'] + ' district') + '''</span></span>
        ''' + ('<span class="rankpill"><b class="delta ' + dcls + '">' + sign(d_bfi) +
               '</b><span>' + L('desde 2018 · ', 'since 2018 · ') +
               (('+%d' % d_rank) if (d_rank or 0) > 0 else str(d_rank)) +
               L(' posições', ' places') + '</span></span>' if d_bfi is not None else '') + '''
      </div>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap"><div class="kv">''' + kv_html + '''</div></div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="grid-2" style="grid-template-columns:380px 1fr;align-items:start">
      <div class="card">
        <p class="eyebrow">''' + L('Perfil', 'Profile') + '''</p>
        <h3 style="margin-bottom:2px">''' + L(m['n'] + ' contra a média nacional',
                                              m['n'] + ' against the national average') + '''</h3>
        <div id="radarM" style="margin-top:6px"></div>
      </div>
      <div class="card card-pad-0">
        <div style="padding:22px 22px 0"><p class="eyebrow">''' + L('Dimensões', 'Dimensions') + '''</p>
        <h3>''' + L('Onde ganha e onde perde', 'Where it wins and where it loses') + '''</h3></div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
          <table class="tbl"><thead><tr><th>''' + L('Dimensão', 'Dimension') + '''</th>
          <th style="text-align:right">2025</th>
          <th style="text-align:right">''' + L('2018 comp.', '2018 comp.') + '''</th>
          <th style="text-align:right">''' + L('Variação', 'Change') + '''</th>
          <th style="text-align:right">''' + L('Média PT', 'PT average') + '''</th></tr></thead>
          <tbody>''' + ''.join(drows) + '''</tbody></table>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="grid-2" style="grid-template-columns:1fr 340px">
      <div class="ficha-det"><div class="card card-pad-0">
        <div style="padding:22px 22px 0">
          <p class="eyebrow">''' + L('Detalhe', 'Detail') + '''</p>
          <h3>''' + L('Os vinte e cinco indicadores', 'The twenty-five indicators') + '''</h3>
          <p class="small muted">''' + L(
            'O valor medido e a posição do município entre os 278, em cada indicador '
            '(1.º é o melhor).',
            'The measured value and the municipality’s position among the 278, on each '
            'indicator (1st is best).') + '''</p>
        </div>
        <div class="tbl-wrap" style="border:0;border-radius:0">
          <table class="tbl"><thead><tr><th>''' + L('Cód.', 'Code') + '''</th>
          <th>''' + L('Indicador', 'Indicator') + '''</th>
          <th style="text-align:right">''' + L('Valor', 'Value') + '''</th>
          <th style="text-align:right">''' + L('Posição no país', 'Position in Portugal') + '''</th></tr></thead>
          <tbody>''' + ''.join(irows) + '''</tbody></table>
        </div>
      </div></div>
      <div class="ficha-side">
        <div class="card">
          <p class="eyebrow">''' + L('Localização', 'Location') + '''</p>
          <div class="mapbox" id="miniMapa" style="border:0;max-width:200px;margin-inline:auto"></div>
        </div>
        <div class="card card-pad-0">
          <div style="padding:20px 20px 0"><p class="eyebrow">''' + L('Vizinhança', 'Neighbourhood') + '''</p>
          <h3>''' + L('Distrito de ' + m['dist'], m['dist'] + ' district') + '''</h3></div>
          <div class="tbl-wrap" style="border:0;border-radius:0;max-height:330px;overflow-y:auto">
            <table class="tbl"><thead><tr><th>#</th>
            <th>''' + L('Município', 'Municipality') + '''</th>
            <th style="text-align:right">BFI</th></tr></thead>
            <tbody>''' + viz_rows + '''</tbody></table>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap">
    <div class="prevnext">''' + nav_prev + nav_next + '''</div>
    <div class="btn-row">
      <a class="btn ghost" href="../''' + P('compare') + '''">''' + L(
        'Comparar com outro município', 'Compare with another municipality') + '''</a>
      <a class="btn ghost" href="../''' + P('explorer') + '''">''' + L('Ver no mapa', 'See it on the map') + '''</a>
      <a class="btn ghost" href="../''' + P('method') + '''">''' + L('Como é calculado', 'How it is calculated') + '''</a>
    </div>
  </div>
</section>
'''
    scripts = '''<script>
(function(){
  var m = M.get("''' + m['d'] + '''");
  var r = document.getElementById('radarM');
  function draw(){ radar(r, [{name:m.n, v:m.s25}, {name:T.natAvg, v:MEDIA.s25, dashed:true}]); }
  draw(); r._redraw = draw; r.setAttribute('data-redraw','1');
  choropleth(document.getElementById('miniMapa'), {serie:'s25', campo:'bfi', sel:m.d, base:''});
})();
</script>'''

    if LANG == 'pt':
        out = 'municipio/%s.html' % m['slug']
        up_assets, alt = '../', '../en/municipality/%s.html' % m['slug']
        self_abs, alt_abs = out, 'en/municipality/%s.html' % m['slug']
    else:
        out = 'en/municipality/%s.html' % m['slug']
        up_assets, alt = '../../', '../../municipio/%s.html' % m['slug']
        self_abs, alt_abs = out, 'municipio/%s.html' % m['slug']

    html = page(LANG, m['n'] + ' · BFI ' + n(s25['bfi']) + ' · Bike Friendly Index',
      body, '', up_assets, '../', alt, alt_abs, self_abs,
      L('Bike Friendly Index 2025 de ' + m['n'] + ': ' + n(s25['bfi']) + ' numa escala de 0 a 10, '
        + ordinal(s25['rank']) + ' de 278 municípios de Portugal Continental.',
        'Bike Friendly Index 2025 for ' + m['n'] + ': ' + n(s25['bfi']) + ' on a 0 to 10 scale, '
        + 'ranked ' + str(s25['rank']) + ' of 278 mainland Portuguese municipalities.'),
      scripts)
    write(out, html)


def pg_fichas():
    ordem = [m['d'] for m in top25]
    k = 0
    for m in MUN:
        if not m['s25']: continue
        ficha(m, ordem)
        k += 1
    return k


# ===========================================================================
def build(lang):
    global LANG
    LANG = lang
    pg_index(); pg_2025(); pg_2018(); pg_comparacao(); pg_municipios()
    pg_explorador(); pg_comparar(); pg_metodologia(); pg_dados(); pg_sobre()
    k = pg_fichas()
    print('  %s: 10 páginas + %d fichas' % (lang, k))


def main():
    for lang in ('pt', 'en'):
        build(lang)

if __name__ == '__main__':
    main()
