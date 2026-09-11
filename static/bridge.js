/* BRIDGE shared page behavior: signal line, nav, reveal, outline spy, cards, buttons */

/* ===== scroll signal line + nav ===== */
const line = document.getElementById('signal-line'), nav = document.getElementById('nav');
addEventListener('scroll', () => {
  const h = document.documentElement;
  line.style.width = (h.scrollTop / (h.scrollHeight - h.clientHeight) * 100) + '%';
  nav.classList.toggle('scrolled', scrollY > 40);
}, { passive: true });

/* ===== cursor glow ===== */
const glow = document.getElementById('cursor-glow');
if (glow) addEventListener('pointermove', e => {
  glow.style.left = e.clientX + 'px'; glow.style.top = e.clientY + 'px';
}, { passive: true });

/* ===== reveal on scroll ===== */
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), { threshold: .16 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

/* ===== outline scroll-spy ===== */
const outlineLinks = document.querySelectorAll('.outline a');
if (outlineLinks.length) {
  const targets = [...outlineLinks].map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
  const spy = new IntersectionObserver(es => {
    es.forEach(e => {
      if (!e.isIntersecting) return;
      outlineLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id));
    });
  }, { rootMargin: '-20% 0px -65% 0px' });
  targets.forEach(t => spy.observe(t));
}

/* ===== animated counters ===== */
const cio = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return; cio.unobserve(e.target);
  const el = e.target, t = +el.dataset.target, suf = el.dataset.suffix || '';
  const t0 = performance.now(), dur = 1600;
  (function step(now) {
    const k = Math.min(1, (now - t0) / dur), ease = 1 - Math.pow(1 - k, 3);
    el.textContent = Math.round(t * ease) + suf;
    if (k < 1) requestAnimationFrame(step);
  })(t0);
}), { threshold: .6 });
document.querySelectorAll('.stat .num, .stat-band .big[data-target]').forEach(el => cio.observe(el));

/* ===== card tilt + spotlight ===== */
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('pointermove', e => {
    const r = card.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
    card.style.setProperty('--mx', x * 100 + '%'); card.style.setProperty('--my', y * 100 + '%');
    card.style.transform = `perspective(800px) rotateY(${(x - .5) * 10}deg) rotateX(${(.5 - y) * 8}deg) translateY(-4px)`;
  });
  card.addEventListener('pointerleave', () => { card.style.transform = ''; });
});

/* ===== magnetic buttons ===== */
document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('pointermove', e => {
    const r = btn.getBoundingClientRect();
    btn.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .18}px,${(e.clientY - r.top - r.height / 2) * .28}px)`;
  });
  btn.addEventListener('pointerleave', () => { btn.style.transform = ''; });
});
