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

  /* rectangulo realmente desenhado pelo SVG para uma dada vista
     (preserveAspectRatio meet): escala k, tamanho e deslocamento dentro da caixa */
  function layoutOf(svg, view) {
    var box = svg.getBoundingClientRect();
    var k = Math.min(box.width / view.w, box.height / view.h);
    var dw = view.w * k, dh = view.h * k;
    var par = svg.getAttribute('preserveAspectRatio') || 'xMidYMid';
    var ox = par.indexOf('xMin') === 0 ? 0
           : par.indexOf('xMax') === 0 ? box.width - dw
           : (box.width - dw) / 2;
    var oy = /YMin/.test(par) ? 0
           : /YMax/.test(par) ? box.height - dh
           : (box.height - dh) / 2;
    return { box: box, k: k, dw: dw, dh: dh, ox: ox, oy: oy };
  }

  function drawTiles(host) {
    var G = window.BFI_GEO, proj = G && G.proj;
    var svg = host.querySelector('svg');
    if (!proj || !svg) return;
    var view = host._view || { x: 0, y: 0, w: G.w, h: G.h };
    var lo = layoutOf(svg, view), box = lo.box;
    if (!box.width || !box.height) return;
    /* o SVG pode estar recuado por padding dentro da caixa posicionada */
    var hb = host.getBoundingClientRect();
    var padL = box.left - hb.left - host.clientLeft;
    var padT = box.top - hb.top - host.clientTop;
    var k = lo.k, dw = lo.dw, dh = lo.dh, ox = lo.ox, oy = lo.oy;

    var sPx = proj.s * k;            /* pixeis por grau de longitude */
    var world = 360 * sPx;           /* largura do mundo nesta escala */
    /* +1 nivel de zoom deixa os mosaicos mais nitidos, mas quadruplica os
       pedidos; so se aplica quando a area coberta e pequena */
    var full = host.classList.contains('fullbleed');
    var sharper = full ? 0 : 1;
    var z = Math.max(1, Math.min(17, Math.round(Math.log(world / 256) / Math.LN2) + sharper));

    /* geometria da grelha para um nivel de zoom zz */
    function geom(zz) {
      var worldZ = 256 * Math.pow(2, zz);
      var f = world / worldZ;
      /* canto superior esquerdo da vista, em graus */
      var lonTL = proj.lon0 - proj.pad / proj.s + view.x / proj.s;
      var mTL = proj.mdeg1 + proj.pad / proj.s - view.y / proj.s;
      var px0 = (lonTL + 180) / 360 * worldZ;
      var py0 = (180 - mTL) / 360 * worldZ;
      /* fullBleed: a grelha continua para la do rectangulo do mapa e cobre
         toda a caixa, incluindo o que fica por baixo dos paineis */
      if (full) { px0 -= (padL + ox) / f; py0 -= (padT + oy) / f; }
      return { worldZ: worldZ, f: f, px0: px0, py0: py0 };
    }
    var L0 = 0, T0 = 0, LW = host.clientWidth, LH = host.clientHeight;
    if (!full) { L0 = padL + ox; T0 = padT + oy; LW = dw; LH = dh; }

    var layer = host.querySelector('.tilelayer');
    if (!layer) {
      layer = document.createElement('div');
      layer.className = 'tilelayer';
      host.insertBefore(layer, host.firstChild);
    }
    layer.style.left = L0 + 'px'; layer.style.top = T0 + 'px';
    layer.style.width = LW + 'px'; layer.style.height = LH + 'px';

    /* um contentor por nivel de zoom: o anterior fica por baixo ate o novo
       carregar, para o fundo nao piscar a branco ao mudar de nivel */
    var lv = layer._lv = layer._lv || {};
    function level(zz) {
      if (!lv[zz]) {
        var c = document.createElement('div');
        c.className = 'tiles';
        c.setAttribute('data-z', zz);
        layer.appendChild(c);
        lv[zz] = { el: c, imgs: {}, t: 0 };
      }
      lv[zz].t = Date.now();
      return lv[zz];
    }
    var cur = level(z);
    Object.keys(lv).forEach(function (zz) {
      var g = geom(+zz), L = lv[zz];
      L.el.style.transform = 'scale(' + g.f + ')';
      L.el.style.zIndex = (+zz === z) ? 2 : 1;
      Object.keys(L.imgs).forEach(function (key) {
        var im = L.imgs[key];
        im.style.left = (im._tx * 256 - g.px0) + 'px';
        im.style.top = (im._ty * 256 - g.py0) + 'px';
      });
    });

    var g = geom(z), n = Math.pow(2, z);
    var tx0 = Math.floor(g.px0 / 256), tx1 = Math.floor((g.px0 + LW / g.f) / 256);
    var ty0 = Math.floor(g.py0 / 256), ty1 = Math.floor((g.py0 + LH / g.f) / 256);
    var need = {};
    var pending = 0;
    for (var ty = ty0; ty <= ty1; ty++) {
      if (ty < 0 || ty >= n) continue;
      for (var tx = tx0; tx <= tx1; tx++) {
        var wx = ((tx % n) + n) % n, key = tx + '/' + ty;
        need[key] = 1;
        if (cur.imgs[key]) continue;
        var im = document.createElement('img');
        im.alt = ''; im.loading = 'lazy'; im.src = tileURL(z, wx, ty);
        im._tx = tx; im._ty = ty;
        im.style.left = (tx * 256 - g.px0) + 'px';
        im.style.top = (ty * 256 - g.py0) + 'px';
        pending++;
        im.addEventListener('load', function () { settle(); });
        im.addEventListener('error', function () { settle(); });
        cur.el.appendChild(im);
        cur.imgs[key] = im;
      }
    }
    /* tira os mosaicos que ja nao estao na vista */
    Object.keys(cur.imgs).forEach(function (key) {
      if (!need[key]) { cur.el.removeChild(cur.imgs[key]); delete cur.imgs[key]; }
    });
    /* quando o nivel actual carregou, deita fora os outros */
    function settle() {
      clearTimeout(layer._st);
      layer._st = setTimeout(function () {
        Object.keys(lv).forEach(function (zz) {
          if (+zz !== z) { layer.removeChild(lv[zz].el); delete lv[zz]; }
        });
      }, 250);
    }
    if (!pending) settle();

    host.classList.add('hastiles');
    layer.classList.toggle('invert', !!TILES.invertOnDark && isDark());
  }
  window.drawTiles = drawTiles;

  /* opts: { serie:'s25'|'s18'|'s18c'|'delta', campo:'bfi'|'c1'..'c5', scale, link:bool, height,
            zoom:bool (roda, arrastar, botoes), focus:codigo (enquadra o municipio), dim:bool } */
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
    var view = { x: 0, y: 0, w: G.w, h: G.h };
    host._view = view;
    var MINW = G.w / 70, MAXW = G.w * 1.25;
    host._moved = false;

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
        if (host._dragging) { tip.classList.remove('on'); return; }
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
        p.addEventListener('click', function () {
          if (host._moved) return;
          location.href = (opts.base || 'municipio/') + m.slug + '.html';
        });
      }
      if (opts.onSelect) p.addEventListener('click', function () {
        if (host._moved) return;
        opts.onSelect(m);
      });
      paths[m.d] = p;
      svg.appendChild(p);
    });

    host.appendChild(svg);
    host.appendChild(tip);

    var tiles = !!opts.tiles;
    function refreshTiles() { if (tiles) drawTiles(host); }
    var tq = 0;
    function scheduleTiles() {
      if (!tiles || tq) return;
      /* setTimeout e nao requestAnimationFrame: este ultimo fica suspenso em separadores
         escondidos e o fundo nunca se actualizava */
      tq = setTimeout(function () { tq = 0; drawTiles(host); }, 24);
    }

    /* ---------------- vista: zoom e deslocamento ---------------- */
    function clampView() {
      view.w = Math.min(MAXW, Math.max(MINW, view.w));
      view.h = view.w * (view._r || view.h / view.w);
      view.x = Math.min(Math.max(view.x, -view.w * 0.4), G.w - view.w * 0.6);
      view.y = Math.min(Math.max(view.y, -view.h * 0.4), G.h - view.h * 0.6);
    }
    function applyView() {
      svg.setAttribute('viewBox', view.x + ' ' + view.y + ' ' + view.w + ' ' + view.h);
      scheduleTiles();
    }
    function boxAspect() {
      var b = svg.getBoundingClientRect();
      return (b.width && b.height) ? b.width / b.height : G.w / G.h;
    }
    /* enquadra um rectangulo (em unidades do SVG) com folga relativa */
    function fitBBox(bb, pad) {
      var a = boxAspect();
      var w = bb.width * (1 + 2 * pad), hh = bb.height * (1 + 2 * pad);
      if (w / hh < a) w = hh * a; else hh = w / a;
      view.w = w; view.h = hh; view._r = hh / w;
      view.x = bb.x + bb.width / 2 - w / 2;
      view.y = bb.y + bb.height / 2 - hh / 2;
      clampView(); applyView();
    }
    function focus(code, pad) {
      var pth = paths[code];
      if (!pth) return;
      var bb = pth.getBBox();
      /* municipios minusculos nao devem ficar com um enquadramento absurdo */
      var minSide = G.w / 22;
      if (bb.width < minSide || bb.height < minSide) {
        var cx = bb.x + bb.width / 2, cy = bb.y + bb.height / 2;
        bb = { x: cx - minSide / 2, y: cy - minSide / 2, width: minSide, height: minSide };
      }
      fitBBox(bb, pad == null ? 0.35 : pad);
    }
    function reset() { fitBBox({ x: 0, y: 0, width: G.w, height: G.h }, 0); }
    function toSvg(cx, cy) {
      var lo = layoutOf(svg, view);
      return { x: view.x + (cx - lo.box.left - lo.ox) / lo.k, y: view.y + (cy - lo.box.top - lo.oy) / lo.k, k: lo.k };
    }
    function zoomBy(f, cx, cy) {
      var b = svg.getBoundingClientRect();
      if (cx == null) { cx = b.left + b.width / 2; cy = b.top + b.height / 2; }
      var pt = toSvg(cx, cy);
      var nw = Math.min(MAXW, Math.max(MINW, view.w * f));
      var ratio = nw / view.w;
      view.x = pt.x - (pt.x - view.x) * ratio;
      view.y = pt.y - (pt.y - view.y) * ratio;
      view.w = nw; view.h = view.h * ratio; view._r = view.h / view.w;
      clampView(); applyView();
    }

    if (opts.zoom) {
      host.classList.add('zoomable');
      /* roda do rato: so quando o cursor esta sobre o mapa */
      svg.addEventListener('wheel', function (ev) {
        ev.preventDefault();
        zoomBy(ev.deltaY > 0 ? 1.18 : 1 / 1.18, ev.clientX, ev.clientY);
      }, { passive: false });
      svg.addEventListener('dblclick', function (ev) {
        ev.preventDefault(); zoomBy(0.5, ev.clientX, ev.clientY);
      });
      /* arrastar com um dedo/rato, pinca com dois */
      var ptrs = {}, last = null, dist0 = 0, w0 = 0, start = null;
      svg.addEventListener('pointerdown', function (ev) {
        ptrs[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
        host._moved = false;
        var ids = Object.keys(ptrs);
        if (ids.length === 1) { last = { x: ev.clientX, y: ev.clientY }; start = { x: ev.clientX, y: ev.clientY }; }
        if (ids.length === 2) {
          var a = ptrs[ids[0]], b2 = ptrs[ids[1]];
          dist0 = Math.hypot(a.x - b2.x, a.y - b2.y); w0 = view.w;
          host._moved = true;
        }
      });
      svg.addEventListener('pointermove', function (ev) {
        if (!ptrs[ev.pointerId]) return;
        ptrs[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
        var ids = Object.keys(ptrs);
        if (ids.length === 2) {
          var a = ptrs[ids[0]], b2 = ptrs[ids[1]];
          var d = Math.hypot(a.x - b2.x, a.y - b2.y);
          if (dist0) {
            var cx = (a.x + b2.x) / 2, cy = (a.y + b2.y) / 2;
            zoomBy((w0 / (d / dist0)) / view.w, cx, cy);
          }
          return;
        }
        if (!last) return;
        if (!host._dragging && Math.hypot(ev.clientX - start.x, ev.clientY - start.y) > 5) {
          host._dragging = true; host._moved = true;
          host.classList.add('dragging');
          try { svg.setPointerCapture(ev.pointerId); } catch (e) {}
        }
        if (host._dragging) {
          var k = layoutOf(svg, view).k;
          view.x -= (ev.clientX - last.x) / k;
          view.y -= (ev.clientY - last.y) / k;
          last = { x: ev.clientX, y: ev.clientY };
          clampView(); applyView();
        }
      });
      function up(ev) {
        delete ptrs[ev.pointerId];
        if (!Object.keys(ptrs).length) {
          host._dragging = false; last = null; dist0 = 0;
          host.classList.remove('dragging');
          /* o clique que acaba um arrasto nao deve abrir municipio nenhum */
          setTimeout(function () { host._moved = false; }, 60);
        }
      }
      svg.addEventListener('pointerup', up);
      svg.addEventListener('pointercancel', up);

      var bar = h('div', { class: 'map-zoom' });
      function btn(label, aria, fn, cls) {
        var b = h('button', { type: 'button', 'aria-label': aria, title: aria, class: cls || null }, label);
        b.addEventListener('click', function (ev) { ev.stopPropagation(); fn(); });
        bar.appendChild(b);
      }
      btn('+', T.zoomIn, function () { zoomBy(0.6); });
      btn('−', T.zoomOut, function () { zoomBy(1 / 0.6); });
      btn('⌂', T.zoomReset, reset, 'home');
      (opts.zoomHost || host.parentNode).appendChild(bar);
    }

    if (tiles) {
      /* o observador tem de ficar guardado: um ResizeObserver sem referencias
         pode ser recolhido antes de chegar a disparar */
      if (window.ResizeObserver) {
        host._ro = new ResizeObserver(function () {
          clearTimeout(host._tt);
          host._tt = setTimeout(function () {
            if (opts.focus && !host._userMoved) focus(opts.focus, opts.pad);
            refreshTiles();
          }, 60);
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
        var sel = state.sel === m.d;
        p.classList.toggle('sel', sel);
        p.classList.toggle('dimmed', !!opts.dim && !!state.sel && !sel);
        if (sel) svg.appendChild(p);          /* o contorno fica por cima dos vizinhos */
      });
    }
    paint();
    host._redraw = function () { paint(); refreshTiles(); };
    host.setAttribute('data-redraw', '1');

    /* enquadramento inicial pedido */
    if (opts.focus) {
      state.sel = opts.focus; paint();
      requestAnimationFrame(function () { focus(opts.focus, opts.pad); });
    }

    return {
      set: function (k, v) { state[k] = v; paint(); },
      state: state,
      scaleName: scaleName,
      repaint: paint,
      refreshTiles: refreshTiles,
      focus: focus,
      reset: reset,
      zoomBy: zoomBy
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
