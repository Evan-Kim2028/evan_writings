// theme
document.getElementById('theme').onclick = () => { const h = document.documentElement; h.dataset.theme = h.dataset.theme === 'dark' ? 'light' : 'dark'; localStorage.setItem('theme', h.dataset.theme); };
// grid overlay (press G)
const ov = document.createElement('div'); ov.id = 'grid-overlay';
ov.innerHTML = '<div class="rows"></div><div class="cols">' + '<i></i>'.repeat(12) + '</div>';
document.body.appendChild(ov);
const hint = document.createElement('div'); hint.id = 'grid-hint'; hint.textContent = 'G · grid'; document.body.appendChild(hint);
addEventListener('keydown', e => { if (e.key.toLowerCase() === 'g' && !e.metaKey && !e.ctrlKey) document.body.classList.toggle('show-grid'); });
// reveal
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .1 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
