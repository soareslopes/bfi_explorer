# -*- coding: utf-8 -*-
"""Layout partilhado bilingue: cabecalho, navegacao, alternador de lingua, rodape."""
import os
import time

# marca de versao para evitar cache de CSS/JS depois de cada geracao
V = "?v=" + time.strftime("%Y%m%d%H%M")

# Endereco onde o site fica publicado, usado nos canonical e hreflang.
# Mudar aqui, ou definir BFI_BASE_URL antes de correr a geracao:
#   BFI_BASE_URL=https://soareslopes.github.io/bfi_explorer/ python3 _build/2_paginas.py
BASE_URL = os.environ.get('BFI_BASE_URL', 'https://www.bikefriendlyindex.com/')
if not BASE_URL.endswith('/'):
    BASE_URL += '/'

# chave -> (caminho pt, caminho en, rotulo pt, rotulo en, aparece na barra)
PAGES = {
 'index':    ('index.html',           'en/index.html',        'Apresentação', 'About the index', True),
 'r2025':    ('resultados-2025.html', 'en/results-2025.html', 'BFI 2025',     'BFI 2025',        True),
 'r2018':    ('resultados-2018.html', 'en/results-2018.html', 'BFI 2018',     'BFI 2018',        True),
 'comp':     ('comparacao.html',      'en/comparison.html',   'Comparação',   'Comparison',      True),
 'muns':     ('municipios.html',      'en/municipalities.html','Municípios',  'Municipalities',  True),
 'explorer': ('explorador.html',      'en/explorer.html',     'Explorador',   'Explorer',        True),
 'method':   ('metodologia.html',     'en/methodology.html',  'Metodologia',  'Methodology',     True),
 'data':     ('dados.html',           'en/data.html',         'Dados',        'Data',            True),
 'compare':  ('comparar.html',        'en/compare.html',      'Comparar municípios', 'Compare municipalities', False),
 'about':    ('sobre.html',           'en/about.html',        'Equipa e citação', 'Team and citation', False),
}

MUN_DIR = {'pt': 'municipio', 'en': 'municipality'}

# o explorador da versao anterior, arquivado numa subpasta do mesmo site
LEGACY_DIR = 'explorador-v1/'


def file_of(key, lang):
    """Nome do ficheiro dentro da raiz da lingua."""
    pt, en = PAGES[key][0], PAGES[key][1]
    return pt if lang == 'pt' else en.split('/', 1)[1]


def label_of(key, lang):
    return PAGES[key][2] if lang == 'pt' else PAGES[key][3]


LOGO = ('<svg viewBox="0 0 32 32" fill="none" aria-hidden="true">'
        '<circle cx="8.5" cy="21.5" r="6" stroke="currentColor" stroke-width="2"/>'
        '<circle cx="23.5" cy="21.5" r="6" stroke="currentColor" stroke-width="2"/>'
        '<path d="M8.5 21.5 14 10h6l3.5 11.5M14 10h-3m3 0 4 11.5" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="20" cy="6.5" r="2.2" fill="currentColor"/></svg>')

ICON_SUN = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/>'
            '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')

ICON_MENU = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>')

ICON_INFO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
             '<path d="M12 11v5M12 7.5v.01"/></svg>')

ICON_WARN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" aria-hidden="true"><path d="M12 3.5 2.5 20h19L12 3.5Z"/>'
             '<path d="M12 10v4M12 17.5v.01"/></svg>')

TXT = {
 'tagline':  {'pt': 'Portugal', 'en': 'Portugal'},
 'theme':    {'pt': 'Modo claro / escuro', 'en': 'Light / dark mode'},
 'themeA':   {'pt': 'Alternar modo claro e escuro', 'en': 'Toggle light and dark mode'},
 'menu':     {'pt': 'Abrir menu', 'en': 'Open menu'},
 'switch':   {'pt': 'Read this page in English', 'en': 'Ler esta página em português'},
 'switchSh': {'pt': 'EN', 'en': 'PT'},
 'blurb':    {'pt': 'Índice de amigabilidade dos municípios de Portugal Continental para a '
                    'utilização da bicicleta como modo de transporte urbano. Edições de 2018 e 2025.',
              'en': 'An index of how friendly each mainland Portuguese municipality is to cycling '
                    'as a mode of urban transport. 2018 and 2025 editions.'},
 'citeLab':  {'pt': 'Como citar:', 'en': 'How to cite:'},
 'ftRes':    {'pt': 'Resultados', 'en': 'Results'},
 'ftExp':    {'pt': 'Explorar', 'en': 'Explore'},
 'ftPrj':    {'pt': 'Projecto', 'en': 'Project'},
 'ftRepo':   {'pt': 'Repositório', 'en': 'Repository'},
 'ftLegacy': {'pt': 'Explorador anterior', 'en': 'Previous explorer'},
 'ftAllMun': {'pt': 'Os 278 municípios', 'en': 'All 278 municipalities'},
 'ftMap':    {'pt': 'Mapa interactivo', 'en': 'Interactive map'},
 'ftData':   {'pt': 'Dados abertos', 'en': 'Open data'},
 'org':      {'pt': 'BEAM · Faculdade de Arquitectura · Universidade de Lisboa',
              'en': 'BEAM · Faculty of Architecture · University of Lisbon'},
}


def nav(lang, active, up_lang, alt_href):
    links = []
    for key, spec in PAGES.items():
        if not spec[4]:
            continue
        cur = ' aria-current="page"' if key == active else ''
        links.append('<a href="%s%s"%s>%s</a>' % (up_lang, file_of(key, lang), cur, label_of(key, lang)))
    other = 'en' if lang == 'pt' else 'pt'
    switch = ('<a class="langswitch" href="%s" hreflang="%s" lang="%s" title="%s">%s</a>'
              % (alt_href, other, other, TXT['switch'][lang], TXT['switchSh'][lang]))
    return (
      '<header class="nav"><div class="nav-in">'
      '<a class="brand" href="%sindex.html">%s<b>Bike Friendly Index</b>&nbsp;<span>%s</span></a>'
      '<button class="icon-btn nav-toggle" data-nav-toggle aria-label="%s">%s</button>'
      '<nav class="nav-links">%s'
      '<span class="nav-tools">%s'
      '<button class="icon-btn" onclick="toggleTheme()" aria-label="%s" title="%s">%s</button>'
      '</span></nav></div></header>'
    ) % (up_lang, LOGO, TXT['tagline'][lang], TXT['menu'][lang], ICON_MENU,
         ''.join(links), switch, TXT['themeA'][lang], TXT['theme'][lang], ICON_SUN)


def footer(lang, up_lang, up_site=''):
    def L(key):
        return up_lang + file_of(key, lang)
    cols = [
      (TXT['ftRes'][lang], [(L('r2025'), label_of('r2025', lang)),
                            (L('r2018'), label_of('r2018', lang)),
                            (L('comp'), label_of('comp', lang)),
                            (L('muns'), TXT['ftAllMun'][lang])]),
      (TXT['ftExp'][lang], [(L('explorer'), TXT['ftMap'][lang]),
                            (L('compare'), label_of('compare', lang)),
                            (L('data'), TXT['ftData'][lang])]),
      (TXT['ftPrj'][lang], [(L('method'), label_of('method', lang)),
                            (L('about'), label_of('about', lang)),
                            (up_site + LEGACY_DIR, TXT['ftLegacy'][lang]),
                            ('https://github.com/soareslopes/bfi_explorer', TXT['ftRepo'][lang])]),
    ]
    out = []
    for title, items in cols:
        links = ''.join('<a href="%s"%s>%s</a>' % (
            l, ' target="_blank" rel="noopener"' if l.startswith('http') else '', t)
            for l, t in items)
        out.append('<div><h4>%s</h4>%s</div>' % (title, links))
    return (
      '<footer class="ft"><div class="wrap"><div class="ft-grid">'
      '<div><a class="brand" href="%sindex.html" style="margin-bottom:12px">%s<b>Bike Friendly Index</b></a>'
      '<p class="cite">%s</p>'
      '<p class="cite" style="margin-top:14px"><strong>%s</strong><br>'
      'Figueiredo, A. P., Vale, D. S. &amp; Lopes, A. S. (2025). '
      '<em>Bike Friendly Index Portugal 2025</em>. BEAM, Faculdade de Arquitectura, '
      'Universidade de Lisboa.</p></div>'
      '%s'
      '</div><div class="ft-base">'
      '<span>%s</span>'
      '<span><a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" '
      'rel="noopener">CC BY-NC-SA 4.0</a></span>'
      '</div></div></footer>'
    ) % (up_lang, LOGO, TXT['blurb'][lang], TXT['citeLab'][lang], ''.join(out), TXT['org'][lang])


def page(lang, title, body, active='', up_assets='', up_lang='', alt_href='#',
         alt_abs='', self_abs='', desc='', scripts='', extra_head=''):
    other = 'en' if lang == 'pt' else 'pt'
    hreflang = ''
    if self_abs and alt_abs:
        site = BASE_URL
        hreflang = (
          '<link rel="canonical" href="%s%s">\n'
          '<link rel="alternate" hreflang="%s" href="%s%s">\n'
          '<link rel="alternate" hreflang="%s" href="%s%s">\n'
          '<link rel="alternate" hreflang="x-default" href="%s%s">'
          % (site, self_abs, lang, site, self_abs, other, site, alt_abs,
             site, self_abs if lang == 'en' else alt_abs))
    return (
'''<!doctype html>
<html lang="''' + ('pt-PT' if lang == 'pt' else 'en') + '''">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>''' + title + '''</title>
<meta name="description" content="''' + desc + '''">
''' + hreflang + '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="''' + up_assets + '''assets/css/site.css''' + V + '''">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='26'%3E%F0%9F%9A%B2%3C/text%3E%3C/svg%3E">
<script>window.LANG = "''' + lang + '''";</script>
''' + extra_head + '''
</head>
<body>
''' + nav(lang, active, up_lang, alt_href) + '''
<main>
''' + body + '''
</main>
''' + footer(lang, up_lang, up_assets) + '''
<script src="''' + up_assets + '''assets/js/i18n.js''' + V + '''"></script>
<script src="''' + up_assets + '''assets/js/data.js''' + V + '''"></script>
<script src="''' + up_assets + '''assets/js/geo.js''' + V + '''"></script>
<script src="''' + up_assets + '''assets/js/app.js''' + V + '''"></script>
<script src="''' + up_assets + '''assets/js/charts.js''' + V + '''"></script>
<script src="''' + up_assets + '''assets/js/map.js''' + V + '''"></script>
<script src="''' + up_assets + '''assets/js/table.js''' + V + '''"></script>
''' + scripts + '''
</body>
</html>
''')
