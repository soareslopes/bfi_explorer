/* ============================================================
   BFI · tabela de ranking ordenavel e filtravel
   ============================================================ */
(function () {
  'use strict';
  var DL = T.dimLabels || [];
  var COLS = [
    { k: 'rank', t: T.colRank, n: true, w: 54, get: function (m, s) { return m[s] ? m[s].rank : null; } },
    { k: 'n',    t: T.colMun,  n: false,       get: function (m) { return m.n; } },
    { k: 'dist', t: T.colDist, n: false,       get: function (m) { return m.dist; } },
    { k: 'bfi',  t: 'BFI',     n: true, bar: 6, get: function (m, s) { return m[s] ? m[s].bfi : null; } },
    { k: 'c1',   t: DL[0], n: true, bar: 10, get: function (m, s) { return m[s] ? m[s].c1 : null; } },
    { k: 'c2',   t: DL[1], n: true, bar: 10, get: function (m, s) { return m[s] ? m[s].c2 : null; } },
    { k: 'c3',   t: DL[2], n: true, bar: 10, get: function (m, s) { return m[s] ? m[s].c3 : null; } },
    { k: 'c4',   t: DL[3], n: true, bar: 10, get: function (m, s) { return m[s] ? m[s].c4 : null; } },
    { k: 'c5',   t: DL[4], n: true, bar: 10, get: function (m, s) { return m[s] ? m[s].c5 : null; } },
    { k: 'pop',  t: T.colPop, n: true,        get: function (m) { return m.pop; } },
    { k: 'cic',  t: T.colCic, n: true,        get: function (m) { return m.cic; } }
  ];

  window.rankingTable = function (host, opts) {
    opts = opts || {};
    var serie = opts.serie || 's25';
    var sort = { k: 'rank', dir: 1 };
    var q = '', dist = '', only = '';

    var wrap = h('div');
    var ctrls = h('div', { class: 'controls' });
    var search = h('input', { type: 'search', placeholder: T.searchPh, 'aria-label': T.searchPh });
    var fs = h('div', { class: 'field' }); fs.appendChild(h('label', {}, T.search)); fs.appendChild(search);
    var selD = h('select', { 'aria-label': T.district });
    selD.appendChild(h('option', { value: '' }, T.all));
    M.distritos.forEach(function (d) { selD.appendChild(h('option', { value: d }, d)); });
    var fd = h('div', { class: 'field' }); fd.appendChild(h('label', {}, T.district)); fd.appendChild(selD);
    var seg = h('div', { class: 'seg' });
    [['', T.all], ['cap', T.capitals], ['bs', T.withBS]].forEach(function (o) {
      var b = h('button', { type: 'button', 'aria-pressed': o[0] === only }, o[1]);
      b.addEventListener('click', function () {
        only = o[0];
        seg.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
        b.setAttribute('aria-pressed', 'true');
        draw();
      });
      seg.appendChild(b);
    });
    var dl = h('button', { class: 'btn ghost', type: 'button', style: 'height:36px;padding:0 14px;font-size:.85rem' }, T.downloadCSV);
    ctrls.appendChild(fs); ctrls.appendChild(fd); ctrls.appendChild(seg); ctrls.appendChild(dl);

    var count = h('div', { class: 'small muted', style: 'margin:-6px 0 12px' });
    var tw = h('div', { class: 'tbl-wrap', style: 'max-height:70vh;overflow-y:auto' });
    var table = h('table', { class: 'tbl' });
    tw.appendChild(table);
    wrap.appendChild(ctrls); wrap.appendChild(count); wrap.appendChild(tw);
    host.innerHTML = ''; host.appendChild(wrap);

    function rows() {
      var out = M.all.filter(function (m) {
        if (!m[serie]) return false;
        if (dist && m.dist !== dist) return false;
        if (only === 'cap' && !m.cap) return false;
        if (only === 'bs' && !m.bs) return false;
        if (q) {
          var s = (m.n + ' ' + m.dist).toLowerCase()
            .normalize('NFD').replace(/[̀-ͯ]/g, '');
          if (s.indexOf(q) < 0) return false;
        }
        return true;
      });
      var col = COLS.filter(function (c) { return c.k === sort.k; })[0];
      out.sort(function (a, b) {
        var va = col.get(a, serie), vb = col.get(b, serie);
        if (va === null) return 1; if (vb === null) return -1;
        if (typeof va === 'string') return va.localeCompare(vb, 'pt') * sort.dir;
        return (va - vb) * sort.dir;
      });
      return out;
    }

    function draw() {
      var data = rows();
      count.textContent = data.length + ' ' + T.of + ' ' + M.all.length + ' ' + T.municipalities;
      table.innerHTML = '';
      var thead = h('thead'), tr = h('tr');
      COLS.forEach(function (c) {
        var th = h('th', { scope: 'col', class: sort.k === c.k ? 'sorted' + (sort.dir > 0 ? ' asc' : '') : '',
                           style: c.w ? 'width:' + c.w + 'px' : null,
                           title: T.sortBy + ' ' + c.t }, c.t);
        th.addEventListener('click', function () {
          if (sort.k === c.k) sort.dir = -sort.dir;
          else { sort.k = c.k; sort.dir = (c.k === 'rank' || c.k === 'n' || c.k === 'dist') ? 1 : -1; }
          draw();
        });
        tr.appendChild(th);
      });
      thead.appendChild(tr); table.appendChild(thead);

      var tb = h('tbody');
      data.forEach(function (m) {
        var r = h('tr');
        COLS.forEach(function (c) {
          var v = c.get(m, serie);
          if (c.k === 'n') {
            r.appendChild(h('td', { class: 'nm' },
              '<a href="' + (opts.base || 'municipio/') + m.slug + '.html">' + esc(m.n) + '</a>' +
              (m.cap ? ' <span class="chip" style="padding:1px 6px;font-size:.66rem">' + T.capital + '</span>' : '')));
          } else if (c.bar && v !== null) {
            var pc = Math.max(2, Math.min(100, v / c.bar * 100));
            r.appendChild(h('td', { class: 'n cellbar' },
              '<i style="width:' + pc.toFixed(0) + '%;background:' + colorOf(c.k === 'bfi' ? 'bfi' : 'dim', v) + '"></i>' +
              '<span>' + F.n(v, 2) + '</span>'));
          } else if (c.n) {
            r.appendChild(h('td', { class: 'n' }, v === null ? '-' : (c.k === 'pop' ? F.i(v) : (c.k === 'rank' ? v : F.n(v, c.k === 'cic' ? 1 : 2)))));
          } else {
            r.appendChild(h('td', {}, esc(v)));
          }
        });
        tb.appendChild(r);
      });
      table.appendChild(tb);
    }

    search.addEventListener('input', function () {
      q = search.value.trim().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
      draw();
    });
    selD.addEventListener('change', function () { dist = selD.value; draw(); });
    dl.addEventListener('click', function () {
      var data = rows();
      var head = ['rank', 'municipality', 'district', 'bfi', 'c1_slope', 'c2_built_environment',
                  'c3_infrastructure', 'c4_political_commitment', 'c5_cycling', 'population_2021', 'cycle_lanes_km'];
      var out = [head].concat(data.map(function (m) {
        var s = m[serie];
        return [s.rank, m.n, m.dist, s.bfi, s.c1, s.c2, s.c3, s.c4, s.c5, m.pop, m.cic];
      }));
      downloadCSV('bfi_' + (serie === 's25' ? '2025' : serie === 's18' ? '2018_original' : '2018_comparable') + '.csv', out);
    });

    draw();
    return { setSerie: function (s) { serie = s; draw(); } };
  };
})();
