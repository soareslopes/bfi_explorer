/* ============================================================
   BFI · coropleto em SVG puro (sem CDN, funciona offline)
   ============================================================ */
(function () {
  'use strict';
  function cv(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }

  /* ------------------------------------------------------------------
     Fundo de mosaicos.
     A projeccao do SVG e Web Mercator com a longitude em graus, logo o
     alinhamento com uma grelha de mosaicos e uma transformacao linear:
     basta descobrir o zoom cujo tamanho de mundo se aproxima do nosso e
     escalar a grelha pela diferenca que sobra.
     ------------------------------------------------------------------ */
  function isDark() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t) return t === 'dark';
    return matchMedia('(prefers-color-scheme: dark)').matches;
  }
  /* Fonte de mosaicos. Por omissao usa os mosaicos padrao do OpenStreetMap,
     que nao exigem chave. Para producao convem contratar um fornecedor
     (MapTiler/OpenMapTiles, CARTO, Stadia) e sobrepor esta configuracao
     definindo window.BFI_TILES antes de carregar este ficheiro:
       window.BFI_TILES = { light: 'https://.../{z}/{x}/{y}.png?key=...',
                            dark:  '...', attrib: '...' }  */
  var TILES = window.BFI_TILES || {
    light: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    dark: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    invertOnDark: true
  };
  function tileURL(z, x, y) {
    var t = (isDark() ? TILES.dark : TILES.light) || TILES.light;
    return t.replace('{z}', z).replace('{x}', x).replace('{y}', y);
  }

  function drawTiles(host) {
    var G = window.BFI_GEO, proj = G && G.proj;
    var svg = host.querySelector('svg');
    if (!proj || !svg) return;
    var box = svg.getBoundingClientRect();
    if (!box.width || !box.height) return;
    /* o SVG pode estar recuado por padding dentro da caixa posicionada */
    var hb = host.getBoundingClientRect();
    var padL = box.left - hb.left - host.clientLeft;
    var padT = box.top - hb.top - host.clientTop;

    /* rectangulo realmente desenhado dentro do SVG (preserveAspectRatio meet) */
    var k = Math.min(box.width / G.w, box.height / G.h);
    var dw = G.w * k, dh = G.h * k;
    var par = svg.getAttribute('preserveAspectRatio') || 'xMidYMid';
    var ox = par.indexOf('xMin') === 0 ? 0
           : par.indexOf('xMax') === 0 ? box.width - dw
           : (box.width - dw) / 2;
    var oy = /YMin/.test(par) ? 0
           : /YMax/.test(par) ? box.height - dh
           : (box.height - dh) / 2;

    var sPx = proj.s * k;            /* pixeis por grau de longitude */
    var world = 360 * sPx;           /* largura do mundo nesta escala */
    /* +1 nivel de zoom deixa os mosaicos mais nitidos, mas quadruplica os
       pedidos; so se aplica quando a area coberta e pequena */
    var sharper = host.classList.contains('fullbleed') ? 0 : 1;
    var z = Math.max(1, Math.min(17, Math.round(Math.log(world / 256) / Math.LN2) + sharper));
    var worldZ = 256 * Math.pow(2, z);
    var f = world / worldZ;          /* escala a aplicar a grelha */

    /* canto superior esquerdo da area desenhada, em graus */
    var lonTL = proj.lon0 - proj.pad / proj.s;
    var mTL = proj.mdeg1 + proj.pad / proj.s;
    var px0 = (lonTL + 180) / 360 * worldZ;
    var py0 = (180 - mTL) / 360 * worldZ;

    /* fullBleed: a grelha continua para la do rectangulo do mapa e cobre
       toda a caixa, incluindo o que fica por baixo dos paineis */
    var full = host.classList.contains('fullbleed');
    var L0 = 0, T0 = 0, LW = host.clientWidth, LH = host.clientHeight;
    if (full) {
      px0 -= (padL + ox) / f;
      py0 -= (padT + oy) / f;
    } else {
      L0 = padL + ox; T0 = padT + oy; LW = dw; LH = dh;
    }

    var layer = host.querySelector('.tilelayer');
    if (!layer) {
      layer = document.createElement('div');
      layer.className = 'tilelayer';
      layer.appendChild(document.createElement('div')).className = 'tiles';
      host.insertBefore(layer, host.firstChild);
    }
    layer.style.left = L0 + 'px'; layer.style.top = T0 + 'px';
    layer.style.width = LW + 'px'; layer.style.height = LH + 'px';

    var inner = layer.firstChild;
    inner.style.transform = 'scale(' + f + ')';

    var n = Math.pow(2, z);
    var tx0 = Math.floor(px0 / 256), tx1 = Math.floor((px0 + LW / f) / 256);
    var ty0 = Math.floor(py0 / 256), ty1 = Math.floor((py0 + LH / f) / 256);
    var html = '';
    for (var ty = ty0; ty <= ty1; ty++) {
      if (ty < 0 || ty >= n) continue;
      for (var tx = tx0; tx <= tx1; tx++) {
        var wx = ((tx % n) + n) % n;
        html += '<img alt="" loading="lazy" src="' + tileURL(z, wx, ty) + '" style="left:' +
                (tx * 256 - px0) + 'px;top:' + (ty * 256 - py0) + 'px">';
      }
    }
    inner.innerHTML = html;
    host.classList.add('hastiles');
    layer.classList.toggle('invert', !!TILES.invertOnDark && isDark());
  }
  window.drawTiles = drawTiles;

  /* opts: { serie:'s25'|'s18'|'s18c'|'delta', campo:'bfi'|'c1'..'c5', scale, link:bool, height } */
  window.choropleth = function (host, opts) {
    opts = opts || {};
    var G = window.BFI_GEO;
    var state = {
      serie: opts.serie || 's25',
      campo: opts.campo || 'bfi',
      sel: opts.sel || null
    };
    host.classList.add('mapbox');
    host.innerHTML = '';
    var tip = h('div', { class: 'maptip' });
    var svg = el('svg', { viewBox: '0 0 ' + G.w + ' ' + G.h, role: 'img', 'aria-label': T.mapAria,
                          preserveAspectRatio: opts.par || null });
    var paths = {};

    function valueOf(m) {
      if (state.serie === 'delta') {
        if (!m.s25 || !m.s18c) return null;
        return m.s25[state.campo] - m.s18c[state.campo];
      }
      var s = m[state.serie];
      return s ? s[state.campo] : null;
    }
    function scaleName() {
      if (state.serie === 'delta') return 'delta';
      return state.campo === 'bfi' ? 'bfi' : 'dim';
    }

    M.all.forEach(function (m) {
      var d = G.paths[m.d];
      if (!d) return;
      var p = el('path', { d: d, class: 'mun', 'data-d': m.d });
      p.appendChild(el('title', {}, m.n));
      p.addEventListener('mousemove', function (ev) {
        var v = valueOf(m);
        var r = host.getBoundingClientRect();
        tip.innerHTML = '<b>' + esc(m.n) + '</b><span>' + (v === null ? T.nodata :
          (state.serie === 'delta' ? F.sign(v, 2) : F.n(v, 2)) +
          (state.serie === 'delta' ? ' ' + T.points : ' / 10')) +
          (m[state.serie] && m[state.serie].rank ? '<br>' + m[state.serie].rank + T.ofN : '') + '</span>';
        tip.classList.add('on');
        var tw = tip.offsetWidth, th = tip.offsetHeight;
        tip.style.left = Math.min(Math.max(6, ev.clientX - r.left - tw / 2), r.width - tw - 6) + 'px';
        tip.style.top = Math.max(6, ev.clientY - r.top - th - 14) + 'px';
      });
      p.addEventListener('mouseleave', function () { tip.classList.remove('on'); });
      if (opts.link !== false) {
        p.style.cursor = 'pointer';
        p.addEventListener('click', function () { location.href = (opts.base || 'municipio/') + m.slug + '.html'; });
      }
      if (opts.onSelect) p.addEventListener('click', function () { opts.onSelect(m); });
      paths[m.d] = p;
      svg.appendChild(p);
    });

    host.appendChild(svg);
    host.appendChild(tip);

    var tiles = !!opts.tiles;
    function refreshTiles() { if (tiles) drawTiles(host); }
    if (tiles) {
      /* o ResizeObserver dispara tambem na primeira observacao, o que evita
         desenhar antes de a caixa ter dimensao */
      /* o observador tem de ficar guardado: um ResizeObserver sem referencias
         pode ser recolhido antes de chegar a disparar */
      if (window.ResizeObserver) {
        host._ro = new ResizeObserver(function () {
          clearTimeout(host._tt);
          host._tt = setTimeout(refreshTiles, 60);
        });
        host._ro.observe(host);
      }
      requestAnimationFrame(refreshTiles);
      addEventListener('load', refreshTiles);
      addEventListener('resize', function () {
        clearTimeout(host._tt);
        host._tt = setTimeout(refreshTiles, 160);
      });
      document.addEventListener('bfi:theme', function () { setTimeout(refreshTiles, 30); });
    }

    function paint() {
      var sc = scaleName();
      M.all.forEach(function (m) {
        var p = paths[m.d]; if (!p) return;
        p.setAttribute('fill', colorOf(sc, valueOf(m)));
        p.classList.toggle('sel', state.sel === m.d);
      });
    }
    paint();
    host._redraw = function () { paint(); refreshTiles(); };
    host.setAttribute('data-redraw', '1');

    return {
      set: function (k, v) { state[k] = v; paint(); },
      state: state,
      scaleName: scaleName,
      repaint: paint,
      refreshTiles: refreshTiles
    };
  };

  /* legenda em barra de cor, com os valores nos extremos */
  window.mapLegend = function (host, scaleName, title, opts) {
    opts = opts || {};
    var S = SCALES[scaleName];
    var ends = (scaleName === 'delta' ? T.rampDelta : scaleName === 'dim' ? T.rampDim : T.rampBFI) || ['', ''];
    var swatches = S.vars.map(function (v) { return '<i style="background:' + cv(v) + '"></i>'; }).join('');
    var mid = scaleName === 'delta' ? '<span class="rl-mid">' + esc(T.noChange) + '</span>' : '';

    host.classList.add('ramplegend');
    host.classList.toggle('vert', !!opts.vertical);
    if (opts.vertical) {
      host.innerHTML =
        (title ? '<div class="rl-title">' + esc(title) + '</div>' : '') +
        '<div class="rl-v"><div class="rl-bar">' + swatches + '</div>' +
        '<div class="rl-ends"><span>' + esc(ends[1]) + '</span>' + mid +
        '<span>' + esc(ends[0]) + '</span></div></div>';
    } else {
      host.innerHTML =
        (title ? '<div class="rl-title">' + esc(title) + '</div>' : '') +
        '<div class="rl-bar">' + swatches + '</div>' +
        '<div class="rl-ends"><span>' + esc(ends[0]) + '</span>' + mid +
        '<span>' + esc(ends[1]) + '</span></div>';
    }
    host._redraw = function () { mapLegend(host, scaleName, title, opts); };
    host.setAttribute('data-redraw', '1');
  };

})();
