/* ============================================================
   BFI · graficos em SVG, sem dependencias
   Marcas finas, pontas arredondadas, legenda sempre presente
   para 2 ou mais series, rotulos directos ate 4 series.
   ============================================================ */
(function () {
  'use strict';
  function cv(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  /* nota: varias funcoes usam T como margem superior, por isso o dicionario
     de traducoes e lido por esta funcao e nunca pelo identificador T */
  function TXT() { return window.T || {}; }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  /* tooltip partilhado */
  var tip;
  function tipFor(host) {
    if (!tip) { tip = h('div', { class: 'maptip' }); document.body.appendChild(tip); tip.style.position = 'fixed'; }
    return tip;
  }
  function showTip(host, x, y, html) {
    var t = tipFor(host);
    t.innerHTML = html; t.classList.add('on');
    var r = t.getBoundingClientRect();
    t.style.left = Math.min(Math.max(8, x - r.width / 2), innerWidth - r.width - 8) + 'px';
    t.style.top = Math.max(8, y - r.height - 12) + 'px';
  }
  function hideTip() { if (tip) tip.classList.remove('on'); }
  window.hideChartTip = hideTip;

  /* ---------------------------------------------------------
     RADAR · ate 2 series sobre as 5 dimensoes
     --------------------------------------------------------- */
  window.radar = function (node, series, opts) {
    opts = opts || {};
    var max = opts.max || 10, R = 112, cx = 170, cy = 148, n = 5;
    var labels = opts.labels || TXT().dimLabels || [];
    var keys = ['c1', 'c2', 'c3', 'c4', 'c5'];
    clear(node);
    var svg = el('svg', { viewBox: '0 0 340 300', class: 'chart', role: 'img' });
    svg.appendChild(el('title', {}, opts.title || TXT().profileTitle));

    function pt(i, v) {
      var a = -Math.PI / 2 + i * 2 * Math.PI / n, r = R * Math.min(v / max, 1);
      return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    }
    /* teia */
    var g = el('g', { class: 'grid' });
    [0.25, 0.5, 0.75, 1].forEach(function (f) {
      var p = [];
      for (var i = 0; i < n; i++) { var q = pt(i, max * f); p.push(q[0].toFixed(1) + ',' + q[1].toFixed(1)); }
      g.appendChild(el('polygon', { points: p.join(' '), fill: 'none', stroke: cv('--line'), 'stroke-width': 1 }));
    });
    for (var i = 0; i < n; i++) {
      var q = pt(i, max);
      g.appendChild(el('line', { x1: cx, y1: cy, x2: q[0].toFixed(1), y2: q[1].toFixed(1), stroke: cv('--line'), 'stroke-width': 1 }));
    }
    svg.appendChild(g);

    /* rotulos dos eixos */
    for (var j = 0; j < n; j++) {
      var a = -Math.PI / 2 + j * 2 * Math.PI / n;
      var lx = cx + (R + 26) * Math.cos(a), ly = cy + (R + 26) * Math.sin(a);
      var anchor = Math.abs(Math.cos(a)) < 0.3 ? 'middle' : (Math.cos(a) > 0 ? 'start' : 'end');
      svg.appendChild(el('text', {
        x: lx.toFixed(1), y: (ly + 4).toFixed(1), 'text-anchor': anchor,
        class: 'lbl', 'font-size': 10.5, 'font-weight': 600
      }, labels[j]));
    }

    var colors = [cv('--series-1'), cv('--ink-3')];
    series.forEach(function (s, si) {
      var col = s.color || colors[si] || colors[0];
      var pts = keys.map(function (k, i) { return pt(i, s.v[k] || 0); });
      var poly = pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
      if (si === 0) {
        svg.appendChild(el('polygon', { points: poly, fill: col, 'fill-opacity': .16, stroke: 'none' }));
      }
      svg.appendChild(el('polygon', {
        points: poly, fill: 'none', stroke: col, 'stroke-width': 2,
        'stroke-dasharray': s.dashed ? '5 4' : null,
        'stroke-linejoin': 'round'
      }));
      if (!s.dashed) {
        pts.forEach(function (p, i) {
          var c = el('circle', { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 4.5, fill: col, stroke: cv('--surface-1'), 'stroke-width': 2 });
          var hit = el('circle', { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 13, fill: 'transparent', style: 'cursor:pointer' });
          hit.addEventListener('mousemove', function (ev) {
            showTip(node, ev.clientX, ev.clientY,
              '<b>' + esc(labels[i]) + '</b><span>' + s.name + ': ' + F.n(s.v[keys[i]], 2) + ' / 10</span>');
          });
          hit.addEventListener('mouseleave', hideTip);
          svg.appendChild(c); svg.appendChild(hit);
        });
      }
    });
    node.appendChild(svg);

    if (series.length > 1) {
      var lg = h('div', { class: 'legend-items small', style: 'margin-top:4px;justify-content:center' });
      series.forEach(function (s, si) {
        lg.appendChild(h('span', {}, '<b style="background:' + (s.color || colors[si]) + '"></b>' + esc(s.name)));
      });
      node.appendChild(lg);
    }
  };

  /* ---------------------------------------------------------
     BARRAS AGRUPADAS · poucas categorias, 1 a 3 series
     --------------------------------------------------------- */
  window.groupedBars = function (node, cats, series, opts) {
    opts = opts || {};
    clear(node);
    var W = opts.width || 680, H = opts.height || 300, L = 54, R = 16, T = 14, B = 54;
    var FS = opts.fontSize || 11;
    var max = opts.max || Math.max.apply(null, series.reduce(function (a, s) { return a.concat(s.v); }, [])) * 1.12;
    var iw = W - L - R, ih = H - T - B;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'chart', role: 'img' });
    svg.appendChild(el('title', {}, opts.title || TXT().chartCompare));
    var colors = [cv('--series-1'), cv('--series-2'), cv('--series-3')];

    /* grelha + eixo y */
    var g = el('g', { class: 'grid' });
    var ticks = opts.ticks || 5;
    for (var i = 0; i <= ticks; i++) {
      var v = max * i / ticks, y = T + ih - ih * i / ticks;
      g.appendChild(el('line', { x1: L, y1: y.toFixed(1), x2: W - R, y2: y.toFixed(1), stroke: cv('--line') }));
      g.appendChild(el('text', { x: L - 9, y: (y + 4).toFixed(1), 'text-anchor': 'end',
                                 class: 'val', 'font-size': FS }, F.n(v, max > 20 ? 0 : 1)));
    }
    svg.appendChild(g);

    var bw = iw / cats.length;
    var inner = Math.min(bw * 0.68, 86);
    var sw = (inner - 2 * (series.length - 1)) / series.length; /* 2px de folga entre barras */

    cats.forEach(function (cat, ci) {
      var x0 = L + ci * bw + (bw - inner) / 2;
      series.forEach(function (s, si) {
        var v = s.v[ci] || 0, hgt = Math.max(2, ih * Math.min(v / max, 1));
        var x = x0 + si * (sw + 2), y = T + ih - hgt;
        var col = s.color || colors[si];
        var rect = el('path', {
          d: roundTopRect(x, y, sw, hgt, 4), fill: col
        });
        svg.appendChild(rect);
        var hit = el('rect', { x: x, y: T, width: sw, height: ih, fill: 'transparent', style: 'cursor:pointer' });
        hit.addEventListener('mousemove', function (ev) {
          showTip(node, ev.clientX, ev.clientY, '<b>' + esc(cat) + '</b><span>' + esc(s.name) + ': ' + F.n(v, 2) + '</span>');
        });
        hit.addEventListener('mouseleave', hideTip);
        svg.appendChild(hit);
        if (series.length <= 4 && opts.directLabels !== false) {
          svg.appendChild(el('text', {
            x: (x + sw / 2).toFixed(1), y: (y - 6).toFixed(1), 'text-anchor': 'middle',
            class: 'val', 'font-size': FS, 'font-weight': 600, fill: cv('--ink-2')
          }, F.n(v, 2)));
        }
      });
      /* rotulo da categoria, em duas linhas se precisar */
      var words = cat.split(' '), line1 = words[0], line2 = words.slice(1).join(' ');
      var tx = L + ci * bw + bw / 2;
      svg.appendChild(el('text', { x: tx.toFixed(1), y: T + ih + 20, 'text-anchor': 'middle',
                                   class: 'lbl', 'font-size': FS, 'font-weight': 600 }, line1));
      if (line2) svg.appendChild(el('text', { x: tx.toFixed(1), y: T + ih + 20 + FS * 1.25,
                                   'text-anchor': 'middle', class: 'lbl', 'font-size': FS }, line2));
    });
    svg.appendChild(el('line', { x1: L, y1: T + ih, x2: W - R, y2: T + ih, stroke: cv('--line-strong') }));
    node.appendChild(svg);

    if (series.length > 1) {
      var lg = h('div', { class: 'legend-items small', style: 'margin-top:6px' });
      series.forEach(function (s, si) {
        lg.appendChild(h('span', {}, '<b style="background:' + (s.color || colors[si]) + '"></b>' + esc(s.name)));
      });
      node.appendChild(lg);
    }
  };

  function roundTopRect(x, y, w, hgt, r) {
    r = Math.min(r, w / 2, hgt);
    return 'M' + x + ' ' + (y + hgt) + 'V' + (y + r) + 'a' + r + ' ' + r + ' 0 0 1 ' + r + ' ' + (-r) +
           'h' + (w - 2 * r) + 'a' + r + ' ' + r + ' 0 0 1 ' + r + ' ' + r + 'V' + (y + hgt) + 'Z';
  }

  /* ---------------------------------------------------------
     HISTOGRAMA · distribuicao dos 278 municipios
     --------------------------------------------------------- */
  window.histogram = function (node, values, opts) {
    opts = opts || {};
    clear(node);
    var W = 680, H = opts.height || 320, L = 42, R = 14, T = 12, B = 46;
    var lo = opts.min || 0, hi = opts.max || 6.5, nb = opts.bins || 26;
    var bins = new Array(nb).fill(0), step = (hi - lo) / nb;
    values.forEach(function (v) {
      var i = Math.min(nb - 1, Math.max(0, Math.floor((v - lo) / step)));
      bins[i]++;
    });
    var peak = Math.max.apply(null, bins) * 1.1;
    var iw = W - L - R, ih = H - T - B;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'chart', role: 'img' });
    svg.appendChild(el('title', {}, opts.title || TXT().chartDist));

    var g = el('g', { class: 'grid' });
    for (var i = 0; i <= 4; i++) {
      var y = T + ih - ih * i / 4;
      g.appendChild(el('line', { x1: L, y1: y.toFixed(1), x2: W - R, y2: y.toFixed(1), stroke: cv('--line') }));
      g.appendChild(el('text', { x: L - 8, y: (y + 4).toFixed(1), 'text-anchor': 'end', class: 'val' }, Math.round(peak * i / 4)));
    }
    svg.appendChild(g);

    var bw = iw / nb;
    bins.forEach(function (c, i) {
      var v = lo + (i + 0.5) * step;
      var hgt = Math.max(c ? 2 : 0, ih * c / peak);
      var x = L + i * bw, y = T + ih - hgt;
      if (c) svg.appendChild(el('path', { d: roundTopRect(x + 1, y, bw - 2, hgt, 3), fill: colorOf(opts.scale || 'bfi', v) }));
      var hit = el('rect', { x: x, y: T, width: bw, height: ih, fill: 'transparent', style: 'cursor:pointer' });
      hit.addEventListener('mousemove', function (ev) {
        showTip(node, ev.clientX, ev.clientY,
          '<b>' + F.n(lo + i * step, 1) + ' a ' + F.n(lo + (i + 1) * step, 1) + '</b><span>' + c + ' ' + TXT().municipalities + '</span>');
      });
      hit.addEventListener('mouseleave', hideTip);
      svg.appendChild(hit);
    });

    /* marcas de referencia */
    (opts.marks || []).forEach(function (m) {
      var x = L + iw * (m.v - lo) / (hi - lo);
      svg.appendChild(el('line', { x1: x.toFixed(1), y1: T - 2, x2: x.toFixed(1), y2: T + ih, stroke: m.color || cv('--series-2'), 'stroke-width': 2, 'stroke-dasharray': '4 3' }));
      svg.appendChild(el('text', { x: (x + 5).toFixed(1), y: T + 10, class: 'lbl', 'font-weight': 600, fill: m.color || cv('--series-2') }, m.label));
    });

    for (var k = Math.ceil(lo); k <= hi; k++) {
      var x = L + iw * (k - lo) / (hi - lo);
      svg.appendChild(el('text', { x: x.toFixed(1), y: T + ih + 18, 'text-anchor': 'middle', class: 'lbl' }, k));
    }
    svg.appendChild(el('text', { x: (L + iw / 2).toFixed(1), y: H - 6, 'text-anchor': 'middle', class: 'lbl' }, opts.xlabel || TXT().bfiScale));
    svg.appendChild(el('line', { x1: L, y1: T + ih, x2: W - R, y2: T + ih, stroke: cv('--line-strong') }));
    node.appendChild(svg);
  };

  /* ---------------------------------------------------------
     DISPERSAO · 2018 contra 2025
     --------------------------------------------------------- */
  window.scatter = function (node, pts, opts) {
    opts = opts || {};
    clear(node);
    var W = 660, H = 520, L = 52, R = 18, T = 18, B = 52;
    var mx = opts.max || 6.2, iw = W - L - R, ih = H - T - B;
    var X = function (v) { return L + iw * v / mx; };
    var Y = function (v) { return T + ih - ih * v / mx; };
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'chart', role: 'img' });
    svg.appendChild(el('title', {}, opts.title || TXT().chartScatter));

    var g = el('g', { class: 'grid' });
    for (var i = 0; i <= 6; i++) {
      g.appendChild(el('line', { x1: X(i), y1: T, x2: X(i), y2: T + ih, stroke: cv('--line') }));
      g.appendChild(el('line', { x1: L, y1: Y(i), x2: W - R, y2: Y(i), stroke: cv('--line') }));
      g.appendChild(el('text', { x: X(i), y: T + ih + 17, 'text-anchor': 'middle', class: 'lbl' }, i));
      g.appendChild(el('text', { x: L - 8, y: Y(i) + 4, 'text-anchor': 'end', class: 'lbl' }, i));
    }
    svg.appendChild(g);
    /* diagonal de referencia */
    svg.appendChild(el('line', { x1: X(0), y1: Y(0), x2: X(mx), y2: Y(mx), stroke: cv('--ink-3'), 'stroke-width': 1.5, 'stroke-dasharray': '6 4' }));
    svg.appendChild(el('text', { x: X(mx) - 6, y: Y(mx) + 18, 'text-anchor': 'end', class: 'lbl', 'font-weight': 600 }, TXT().noChange));

    pts.forEach(function (p) {
      var up = p.y >= p.x;
      var col = up ? cv('--series-1') : cv('--series-2');
      var c = el('circle', {
        cx: X(p.x).toFixed(1), cy: Y(p.y).toFixed(1), r: p.hi ? 6 : 4,
        fill: col, 'fill-opacity': p.hi ? 1 : .55,
        stroke: cv('--surface-1'), 'stroke-width': 2, style: 'cursor:pointer'
      });
      c.addEventListener('mousemove', function (ev) {
        showTip(node, ev.clientX, ev.clientY, '<b>' + esc(p.n) + '</b><span>2018: ' + F.n(p.x, 2) +
          '<br>2025: ' + F.n(p.y, 2) + '<br>' + F.sign(p.y - p.x, 2) + '</span>');
      });
      c.addEventListener('mouseleave', hideTip);
      c.addEventListener('click', function () { if (p.href) location.href = p.href; });
      svg.appendChild(c);
      if (p.label) {
        svg.appendChild(el('text', {
          x: (X(p.x) + 9).toFixed(1), y: (Y(p.y) + 4).toFixed(1), class: 'lbl',
          'font-weight': 600, fill: cv('--ink')
        }, p.n));
      }
    });

    svg.appendChild(el('text', { x: (L + iw / 2).toFixed(1), y: H - 6, 'text-anchor': 'middle', class: 'lbl', 'font-weight': 600 }, opts.xlabel || TXT().xScatter));
    svg.appendChild(el('text', { x: 14, y: (T + ih / 2).toFixed(1), 'text-anchor': 'middle', class: 'lbl', 'font-weight': 600, transform: 'rotate(-90 14 ' + (T + ih / 2).toFixed(1) + ')' }, opts.ylabel || TXT().yScatter));
    node.appendChild(svg);

    var lg = h('div', { class: 'legend-items small', style: 'margin-top:6px' });
    lg.appendChild(h('span', {}, '<b style="background:' + cv('--series-1') + '"></b>' + TXT().improved));
    lg.appendChild(h('span', {}, '<b style="background:' + cv('--series-2') + '"></b>' + TXT().worsened));
    node.appendChild(lg);
  };

  /* ---------------------------------------------------------
     SPARK de dimensoes para o cartao
     --------------------------------------------------------- */
  window.sparkDims = function (s) {
    var out = '';
    ['c1', 'c2', 'c3', 'c4', 'c5'].forEach(function (k) {
      var v = s[k] || 0;
      out += '<div style="height:' + Math.max(8, Math.round(v / 10 * 100)) +
             '%;background:' + colorOf('dim', v) + '"></div>';
    });
    return out;
  };

  document.addEventListener('bfi:theme', function () {
    document.querySelectorAll('[data-redraw]').forEach(function (n) {
      if (n._redraw) n._redraw();
    });
  });
})();
