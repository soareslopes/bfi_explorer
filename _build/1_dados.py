# -*- coding: utf-8 -*-
"""Gera assets/js/data.js e assets/js/geo.js a partir de _novo_site/dados_site."""
import json, csv, os, math, unicodedata, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import i18n
SITE = os.path.dirname(HERE)
SRC  = os.path.join(os.path.dirname(SITE), 'dados_site')
JS   = os.path.join(SITE, 'assets', 'js')
os.makedirs(JS, exist_ok=True)

DISTRITOS = {'01':'Aveiro','02':'Beja','03':'Braga','04':'Bragança','05':'Castelo Branco',
 '06':'Coimbra','07':'Évora','08':'Faro','09':'Guarda','10':'Leiria','11':'Lisboa',
 '12':'Portalegre','13':'Porto','14':'Santarém','15':'Setúbal','16':'Viana do Castelo',
 '17':'Vila Real','18':'Viseu'}

CAPITAIS = {'0105':'Aveiro','0202':'Beja','0303':'Braga','0402':'Bragança','0505':'Castelo Branco',
 '0603':'Coimbra','0705':'Évora','0805':'Faro','0909':'Guarda','1010':'Leiria','1106':'Lisboa',
 '1210':'Portalegre','1312':'Porto','1414':'Santarém','1508':'Setúbal','1616':'Viana do Castelo',
 '1714':'Vila Real','1823':'Viseu'}

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip('-').lower()
    return s

def r(x, n=3):
    if x is None: return None
    try: return round(float(x), n)
    except (TypeError, ValueError): return None

# ---------------- dimensoes e indicadores (bilingue) ----------------
DIMS = [{'k': d['k'], 'cod': d['cod'], 'peso': d['peso'],
         'nome': d['nome'], 'curto': d['curto'], 'desc': d['desc']} for d in i18n.DIMS]

IND = [{'k': k, 'dim': dim, 'peso': p,
        'nome': {'pt': npt, 'en': nen}, 'un': {'pt': upt, 'en': uen}, 'fmt': fmt}
       for k, dim, p, npt, nen, upt, uen, fmt in i18n.IND]

IND_CODES = [x['k'] for x in IND]

# ---------------- leitura ----------------
rows = list(csv.DictReader(open(os.path.join(SRC, 'bfi_municipios.csv'), encoding='utf8')))
by = {}
for row in rows:
    by.setdefault(row['dtmn'], {})[(row['ano'], row['serie'])] = row

g25 = json.load(open(os.path.join(SRC, 'bfi_2025.geojson'), encoding='utf8'))
ctx = {f['properties']['dtmn']: f['properties'] for f in g25['features']}

ind_rows = list(csv.DictReader(open(os.path.join(SRC, 'bfi_indicadores.csv'), encoding='utf8')))
ind_by = {}
for row in ind_rows:
    ind_by.setdefault(row['dtmn'], {})[row['indicador']] = row

nacional = json.load(open(os.path.join(SRC, 'portugal.json'), encoding='utf8'))

DK = ['c1_declive', 'c2_ambcon', 'c3_infraest', 'c4_compolit', 'c5_utiliza']

def serie(d, key):
    row = by[d].get(key)
    if not row: return None
    out = {k[1:3]: r(row[k]) for k in DK}
    out = {'c1': r(row['c1_declive']), 'c2': r(row['c2_ambcon']), 'c3': r(row['c3_infraest']),
           'c4': r(row['c4_compolit']), 'c5': r(row['c5_utiliza']),
           'bfi': r(row['bfi']), 'rank': int(float(row['ranking']))}
    return out

municipios = []
for d in sorted(by):
    c = ctx.get(d, {})
    nome = by[d][('2025', 'metodo_2025')]['municipio']
    m = {
      'd': d, 'n': nome, 'slug': slug(nome),
      'dist': DISTRITOS[d[:2]], 'cap': d in CAPITAIS,
      'pop': c.get('PopResidente_2021'), 'area': r(c.get('area_km2'), 2),
      'cic': r((c.get('ExtensaoCiclovias_conc') or 0) / 1000, 2),
      'cicU': r((c.get('ExtCic_AURB') or 0) / 1000, 2),
      'bs': bool(c.get('BikeSharing')),
      'inv': r(c.get('Total_Valor_Euros'), 0),
      'ub': r(c.get('UtilizacaoBicicleta'), 5),
      'um': r(c.get('UtilizacaoMulheres'), 4),
      's25': serie(d, ('2025', 'metodo_2025')),
      's18': serie(d, ('2018', 'original_2018')),
      's18c': serie(d, ('2018', 'metodo_2025')),
    }
    ii = ind_by.get(d, {})
    m['ind'] = {k: [r(ii.get(k, {}).get('bruto_2025'), 4),
                    r(ii.get(k, {}).get('norm_2025'), 4),
                    r(ii.get(k, {}).get('norm_2018'), 4)] for k in IND_CODES}
    municipios.append(m)

# vizinhos por distrito (para a comparacao na ficha)
for m in municipios:
    viz = [x['d'] for x in municipios if x['dist'] == m['dist'] and x['d'] != m['d']]
    m['viz'] = viz

out = {
  'municipios': municipios,
  'dims': DIMS,
  'ind': IND,
  'nacional': nacional,
  'distritos': sorted(set(DISTRITOS.values())),
}
with open(os.path.join(JS, 'data.js'), 'w', encoding='utf8') as fh:
    fh.write('window.BFI = ')
    json.dump(out, fh, ensure_ascii=False, separators=(',', ':'))
    fh.write(';\n')

# ---------------- strings de interface ----------------
with open(os.path.join(JS, 'i18n.js'), 'w', encoding='utf8') as fh:
    fh.write(i18n.js_bundle())

# ---------------- geometria projectada ----------------
W, PAD = 1000.0, 12.0
lons, lats = [], []
def walk(c, fn):
    if isinstance(c[0], (int, float)): fn(c)
    else:
        for x in c: walk(x, fn)
for f in g25['features']:
    walk(f['geometry']['coordinates'], lambda p: (lons.append(p[0]), lats.append(p[1])))

# Mercator: x e y na mesma unidade (graus), senao o mapa sai achatado
def merc(lat): return math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))
x0, x1 = min(lons), max(lons)
y0, y1 = merc(min(lats)), merc(max(lats))
s = (W - 2 * PAD) / (x1 - x0)
H = round((y1 - y0) * s + 2 * PAD)
ox = PAD
oy = PAD

def proj(p):
    return (round(ox + (p[0] - x0) * s, 1), round(oy + (y1 - merc(p[1])) * s, 1))

geo = {}
for f in g25['features']:
    d = f['properties']['dtmn']
    g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    path = []
    for poly in polys:
        for ring in poly:
            pts = [proj(p) for p in ring]
            path.append('M' + 'L'.join(f'{a} {b}' for a, b in pts) + 'Z')
    geo[d] = ''.join(path)

with open(os.path.join(JS, 'geo.js'), 'w', encoding='utf8') as fh:
    fh.write('window.BFI_GEO = ')
    json.dump({'w': W, 'h': H, 'paths': geo,
               # parametros da projeccao, para alinhar um fundo de mosaicos Web Mercator
               'proj': {'lon0': x0, 'mdeg1': y1, 's': s, 'pad': PAD}},
              fh, ensure_ascii=False, separators=(',', ':'))
    fh.write(';\n')

print('data.js  ', os.path.getsize(os.path.join(JS, 'data.js')) // 1024, 'KB,', len(municipios), 'municipios')
print('geo.js   ', os.path.getsize(os.path.join(JS, 'geo.js')) // 1024, 'KB')
