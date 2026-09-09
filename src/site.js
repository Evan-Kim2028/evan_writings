// Site behaviour: theme toggle, reading progress, scroll reveal, sortable
// tables, active TOC link, code copy, lazy Plotly charts. No dependencies.
(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Theme
  var toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
      document.dispatchEvent(new CustomEvent('themechange'));
    });
  }

  // Reading progress
  var bar = document.getElementById('progress');
  if (bar) {
    addEventListener('scroll', function () {
      var h = root.scrollHeight - root.clientHeight;
      bar.style.width = (h > 0 ? root.scrollTop / h * 100 : 0) + '%';
    }, { passive: true });
  }

  // Scroll reveal
  var reveals = document.querySelectorAll('.reveal');
  if (reveals.length && 'IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.1 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('in'); });
  }

  // Sortable tables
  function cellValue(td) {
    var t = td.textContent.trim();
    var m = t.replace(/[,$%*]/g, '').match(/-?\d+(\.\d+)?/);
    return m ? parseFloat(m[0]) : NaN;
  }
  document.querySelectorAll('table.sortable').forEach(function (table) {
    var ths = table.querySelectorAll('thead th');
    ths.forEach(function (th, idx) {
      var dir = document.createElement('span'); dir.className = 'dir'; dir.textContent = '↕';
      th.appendChild(dir);
      th.addEventListener('click', function () {
        var tbody = table.tBodies[0]; if (!tbody) return;
        var rows = Array.prototype.slice.call(tbody.rows);
        var numeric = rows.every(function (r) { return r.cells[idx] && !isNaN(cellValue(r.cells[idx])); });
        var asc = !(th.classList.contains('sorted') && th.dataset.dir === 'asc');
        ths.forEach(function (t) { t.classList.remove('sorted'); t.querySelector('.dir').textContent = '↕'; });
        th.classList.add('sorted'); th.dataset.dir = asc ? 'asc' : 'desc'; dir.textContent = asc ? '↑' : '↓';
        rows.sort(function (a, b) {
          var x = numeric ? cellValue(a.cells[idx]) : a.cells[idx].textContent.trim().toLowerCase();
          var y = numeric ? cellValue(b.cells[idx]) : b.cells[idx].textContent.trim().toLowerCase();
          return (x > y ? 1 : x < y ? -1 : 0) * (asc ? 1 : -1);
        });
        rows.forEach(function (r) { tbody.appendChild(r); });
      });
    });
  });

  // Active TOC link
  var links = Array.prototype.slice.call(document.querySelectorAll('.rail .toc-link'));
  var heads = document.querySelectorAll('.writing-body h2[id], .writing-body h3[id]');
  if (links.length && heads.length && 'IntersectionObserver' in window) {
    var hio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (l) { l.classList.toggle('active', l.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-15% 0px -75% 0px' });
    heads.forEach(function (h) { hio.observe(h); });
  }

  // Copy button on code blocks
  document.querySelectorAll('.writing-body pre').forEach(function (pre) {
    var b = document.createElement('button'); b.className = 'copy'; b.type = 'button'; b.textContent = 'copy';
    b.addEventListener('click', function () {
      var code = pre.querySelector('code');
      navigator.clipboard.writeText((code || pre).innerText).then(function () {
        b.textContent = 'copied'; setTimeout(function () { b.textContent = 'copy'; }, 1500);
      });
    });
    pre.appendChild(b);
  });

  // Lazy Plotly charts: <div class="chart" data-src="assets/charts/x.json">
  var charts = document.querySelectorAll('.chart[data-src]');
  if (charts.length) {
    var base = document.body.dataset.base || '/';
    function css(k) { return getComputedStyle(root).getPropertyValue(k).trim(); }
    function themed(layout) {
      var l = Object.assign({}, layout);
      l.paper_bgcolor = 'rgba(0,0,0,0)'; l.plot_bgcolor = 'rgba(0,0,0,0)';
      l.font = Object.assign({ family: css('--font-sans'), size: 12 }, l.font || {}, { color: css('--text-2') });
      ['xaxis', 'yaxis'].forEach(function (ax) {
        l[ax] = Object.assign({}, l[ax] || {}, { gridcolor: css('--line'), zeroline: false, linecolor: css('--line') });
      });
      l.hoverlabel = { bgcolor: css('--bg-2'), bordercolor: css('--line'), font: { color: css('--text') } };
      l.margin = l.margin || { l: 60, r: 20, t: 20, b: 50 };
      return l;
    }
    function themedData(data) {
      return data.map(function (tr) {
        var t = JSON.parse(JSON.stringify(tr));
        t.marker = t.marker || {};
        if (!t.marker.color) t.marker.color = css('--accent');
        if (t.marker.line && !t.marker.line.color) t.marker.line.color = css('--bg');
        if (t.textfont && !t.textfont.color) t.textfont.color = css('--text-2');
        if (t.line && !t.line.color) t.line.color = css('--accent');
        return t;
      });
    }
    function draw(el, spec) {
      window.Plotly.react(el, themedData(spec.data || []), themed(spec.layout || {}), { displayModeBar: false, responsive: true });
    }
    function load(cb) {
      if (window.Plotly) return cb();
      var s = document.createElement('script');
      s.src = 'https://cdn.plot.ly/plotly-2.35.2.min.js'; s.onload = cb; document.head.appendChild(s);
    }
    var specs = new Map();
    load(function () {
      charts.forEach(function (el) {
        var src = el.dataset.src.replace(/^\//, '');
        fetch(base + src).then(function (r) { return r.json(); }).then(function (spec) {
          specs.set(el, spec);
          draw(el, spec);
        }).catch(function (err) { el.textContent = 'Chart failed to load: ' + err.message; });
      });
      document.addEventListener('themechange', function () {
        specs.forEach(function (spec, el) { draw(el, spec); });
      });
    });
  }
})();
