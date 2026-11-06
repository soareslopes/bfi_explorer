/* ============================================================
   BFI · utilitarios partilhados
   ============================================================ */
(function () {
  'use strict';

  /* ---------- tema ---------- */
  var KEY = 'bfi-theme';
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  var t = stored();
  if (t) document.documentElement.setAttribute('data-theme', t);

  window.toggleTheme = function () {
    var cur = document.documentElement.getAttribute('data-theme');
    if (!cur) cur = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    save(next);
    document.dispatchEvent(new CustomEvent('bfi:theme', { detail: next }));
  };

  /* ---------- lingua ---------- */
  var LANG = window.LANG || document.documentElement.lang.slice(0, 2) || 'pt';
  window.LANG = LANG;
  var T = window.T = (window.STRINGS || {})[LANG] || (window.STRINGS || {}).pt || {};
  var LOCALE = T.locale || 'pt-PT';
  /* resolve {pt:..., en:...} para a lingua activa */
  function tr(v) {
    if (v && typeof v === 'object' && !Array.isArray(v) && (v.pt !== undefined || v.en !== undefined)) {
      return v[LANG] !== undefined ? v[LANG] : v.pt;
    }
    return v;
  }
  window.tr = tr;

  /* ---------- formatacao ---------- */
  var F = window.F = {
    n: function (v, d) {
      if (v === null || v === undefined || isNaN(v)) return '—'.replace('—', '-');
      d = d === undefined ? 2 : d;
      return Number(v).toLocaleString(LOCALE, { minimumFractionDigits: d, maximumFractionDigits: d });
    },
    i: function (v) {
      if (v === null || v === undefined || isNaN(v)) return '-';
      return Number(v).toLocaleString(LOCALE, { maximumFractionDigits: 0 });
    },
    eur: function (v) {
      if (!v) return '0 €';
      if (v >= 1e6) return F.n(v / 1e6, 1) + ' M€';
      if (v >= 1e3) return F.i(Math.round(v / 1e3)) + (LANG === 'pt' ? ' mil €' : 'k €');
      return F.i(v) + ' €';
    },
    pct: function (v, d) { return F.n(v * 100, d === undefined ? 1 : d) + '%'; },
    sign: function (v, d) {
      var s = F.n(Math.abs(v), d === undefined ? 2 : d);
      return (v > 0 ? '+' : v < 0 ? '-' : '') + s;
    }
  };

  /* ---------- escalas de cor ---------- */
  function cssvar(n) {
    return getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  }
  var SEQ = ['--seq-100', '--seq-200', '--seq-300', '--seq-400', '--seq-550', '--seq-650', '--seq-700'];
  var DIV = ['--div-neg-3', '--div-neg-2', '--div-neg-1', '--div-mid', '--div-pos-1', '--div-pos-2', '--div-pos-3'];

  var SCALES = window.SCALES = {
    /* BFI 0-10, 7 classes fixas para que os anos sejam comparaveis */
    bfi: {
      breaks: [1, 1.5, 2, 2.5, 3, 4],
      labels: T.scaleBFI || [],
      vars: SEQ
    },
    /* dimensoes 0-10 */
    dim: {
      breaks: [1, 2, 3, 4, 6, 8],
      labels: T.scaleDim || [],
      vars: SEQ
    },
    /* variacao, divergente. negativo = piorou */
    delta: {
      breaks: [-1, -0.5, -0.1, 0.1, 0.5, 1],
      labels: T.scaleDelta || [],
      vars: ['--div-pos-3', '--div-pos-2', '--div-pos-1', '--div-mid', '--div-neg-1', '--div-neg-2', '--div-neg-3']
    }
  };

  window.classOf = function (scale, v) {
    if (v === null || v === undefined || isNaN(v)) return -1;
    var b = SCALES[scale].breaks, i = 0;
    while (i < b.length && v >= b[i]) i++;
    return i;
  };
  window.colorOf = function (scale, v) {
    var c = window.classOf(scale, v);
    if (c < 0) return cssvar('--surface-3');
    return cssvar(SCALES[scale].vars[c]);
  };
  window.rampColors = function (scale) { return SCALES[scale].vars.map(cssvar); };

  /* ---------- dados ---------- */
  var D = window.BFI || {};
  var byCode = {};
  (D.municipios || []).forEach(function (m) { byCode[m.d] = m; });
  window.M = {
    all: D.municipios || [],
    get: function (code) { return byCode[code]; },
    bySlug: function (s) { return (D.municipios || []).filter(function (m) { return m.slug === s; })[0]; },
    dims: (D.dims || []).map(function (d) {
      return { k: d.k, cod: d.cod, peso: d.peso,
               nome: tr(d.nome), curto: tr(d.curto), desc: tr(d.desc) };
    }),
    ind: (D.ind || []).map(function (x) {
      return { k: x.k, dim: x.dim, peso: x.peso, nome: tr(x.nome), un: tr(x.un), fmt: x.fmt };
    }),
    nac: D.nacional || {},
    distritos: D.distritos || []
  };
  /* media nacional por serie, para os graficos de referencia */
  window.MEDIA = (function () {
    var s = M.nac.series || {};
    function pack(o, bfi) {
      return { c1: o.c1_declive, c2: o.c2_ambcon, c3: o.c3_infraest,
               c4: o.c4_compolit, c5: o.c5_utiliza, bfi: bfi };
    }
    return {
      s25: pack(s['2025'] || {}, (s['2025'] || {}).bfi_media),
      s18: pack(s['2018_original'] || {}, (s['2018_original'] || {}).bfi_media),
      s18c: pack(s['2018_metodo2025'] || {}, (s['2018_metodo2025'] || {}).bfi_media)
    };
  })();

  /* ---------- svg helpers ---------- */
  var NS = 'http://www.w3.org/2000/svg';
  window.el = function (name, attrs, text) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) if (attrs[k] !== null && attrs[k] !== undefined) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  };
  window.h = function (name, attrs, html) {
    var e = document.createElement(name);
    for (var k in attrs || {}) {
      if (k === 'class') e.className = attrs[k];
      else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), attrs[k]);
      else if (attrs[k] !== null && attrs[k] !== undefined) e.setAttribute(k, attrs[k]);
    }
    if (html !== undefined) e.innerHTML = html;
    return e;
  };
  window.esc = function (s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  };

  /* ---------- navegacao movel ---------- */
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-nav-toggle]');
    if (b) document.querySelector('.nav-links').classList.toggle('open');
  });

  /* ---------- avisos em popover ---------- */
  function closeAlerts(except) {
    document.querySelectorAll('.alertpop[aria-expanded="true"]').forEach(function (x) {
      if (x !== except) x.setAttribute('aria-expanded', 'false');
    });
  }
  document.addEventListener('click', function (ev) {
    if (ev.target.closest('.alertpop .pop')) return;   /* clicar dentro mantem aberto */
    var b = ev.target.closest('.alertpop');
    closeAlerts(b);
    if (b) b.setAttribute('aria-expanded', b.getAttribute('aria-expanded') === 'true' ? 'false' : 'true');
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape') closeAlerts(null);
  });

  /* ---------- voltar para onde o visitante estava ---------- */
  window.bfiBack = function (fallback) {
    var ref = document.referrer;
    if (ref && history.length > 1) {
      try {
        if (new URL(ref, location.href).origin === location.origin) { history.back(); return; }
      } catch (e) {}
    }
    location.href = fallback;
  };

  /* ---------- download CSV ---------- */
  window.downloadCSV = function (filename, rows) {
    var csv = rows.map(function (r) {
      return r.map(function (c) {
        c = c === null || c === undefined ? '' : String(c);
        return /[",;\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c;
      }).join(',');
    }).join('\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }));
    a.download = filename;
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
  };
})();
