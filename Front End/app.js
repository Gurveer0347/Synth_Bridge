gsap.registerPlugin(ScrollTrigger, TextPlugin);

// ==================== CUSTOM CURSOR ====================
const cursorDot = document.querySelector('.cursor-dot');
const cursorRing = document.querySelector('.cursor-ring');
if (cursorDot && cursorRing) {
  const dotX = gsap.quickTo(cursorDot, 'left', { duration: 0.15, ease: 'power2' });
  const dotY = gsap.quickTo(cursorDot, 'top', { duration: 0.15, ease: 'power2' });
  const ringX = gsap.quickTo(cursorRing, 'left', { duration: 0.4, ease: 'power2' });
  const ringY = gsap.quickTo(cursorRing, 'top', { duration: 0.4, ease: 'power2' });
  window.addEventListener('mousemove', e => { dotX(e.clientX); dotY(e.clientY); ringX(e.clientX); ringY(e.clientY); });
}

// ==================== PAGE NAVIGATION ====================
function navigateTo(pageId, pushHistory = true) {
  const current = document.querySelector('.page.active');
  const next = document.getElementById(pageId);
  if (!next || current === next) return;
  if (pushHistory) history.pushState({ page: pageId }, '', '#' + pageId);
  if (current) {
    gsap.to(current, { opacity: 0, duration: 0.3, ease: 'power2.inOut', onComplete: () => {
      current.classList.remove('active'); current.style.display = 'none';
      next.style.display = 'block'; next.classList.add('active'); next.scrollTop = 0;
      gsap.fromTo(next, { opacity: 0 }, { opacity: 1, duration: 0.3, ease: 'power2.inOut', onComplete: () => { if (pageId === 'page-landing') initLanding(); if (pageId === 'page-tool') initTool(); }});
    }});
  } else { next.style.display = 'block'; next.classList.add('active'); gsap.fromTo(next, { opacity: 0 }, { opacity: 1, duration: 0.3 }); }
}
window.addEventListener('popstate', e => { navigateTo((e.state && e.state.page) ? e.state.page : 'page-landing', false); });

// ==================== NAVBAR SCROLL ====================
function initNavScroll() {
  const page = document.getElementById('page-landing');
  const nav = document.getElementById('main-nav');
  if (!page || !nav) return;
  page.addEventListener('scroll', () => { nav.classList.toggle('scrolled', page.scrollTop > 60); });
}

// ==================== TSPARTICLES ====================
function initParticles(id) {
  tsParticles.load(id, {
    fullScreen: { enable: false }, background: { color: { value: 'transparent' } }, fpsLimit: 60,
    interactivity: { events: { onHover: { enable: true, mode: 'grab' } }, modes: { grab: { distance: 140, links: { opacity: 0.3 } } } },
    particles: {
      color: { value: '#6366F1' }, links: { color: '#C7D2FE', distance: 130, enable: true, opacity: 0.3, width: 1 },
      move: { enable: true, speed: 0.8, outModes: { default: 'bounce' } },
      number: { density: { enable: true, area: 1000 }, value: 50 },
      opacity: { value: 0.3 }, size: { value: { min: 1, max: 2 } }
    }
  });
}

// ==================== LANDING INIT ====================
let landingInit = false;
function initLanding() {
  if (landingInit) return; landingInit = true;
  initParticles('tsparticles'); initNavScroll();
  const page = document.getElementById('page-landing');

  // Hero text reveal
  const h = document.querySelector('.hero h1');
  if (h) { Splitting({ target: h, by: 'words' }); gsap.fromTo(h.querySelectorAll('.word'), { y: 60, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.08, duration: 0.6, ease: 'power4.out', delay: 0.3 }); }

  // Hero elements stagger
  gsap.fromTo('.hero-logo-row', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.7, ease: 'power3.out', delay: 0.1 });
  gsap.fromTo('.hero-btns', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, delay: 1.0 });
  gsap.fromTo('.hero-stats', { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, delay: 1.2 });

  // Typed.js
  new Typed('#typed-text', {
    strings: ['ALI reads your API docs and builds the bridge automatically.', 'Drop two files. Describe what you want. Done.', 'Your tools. Connected. No engineer needed.', 'From documentation to deployment in under 2 minutes.'],
    typeSpeed: 40, backSpeed: 25, backDelay: 2000, loop: true
  });

  // Button hovers
  document.querySelectorAll('.btn-primary, .btn-ghost').forEach(b => {
    b.addEventListener('mouseenter', () => gsap.to(b, { scale: 1.03, duration: 0.25, ease: 'back.out(1.7)' }));
    b.addEventListener('mouseleave', () => gsap.to(b, { scale: 1, duration: 0.25 }));
  });

  // Scroll reveals - steps
  document.querySelectorAll('.step-card').forEach((c, i) => {
    gsap.fromTo(c, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, delay: i * 0.15, ease: 'power3.out', scrollTrigger: { trigger: c, scroller: page, start: 'top 88%' } });
  });

  // Scroll reveals - bento cards
  document.querySelectorAll('.bento-card').forEach((c, i) => {
    gsap.fromTo(c, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, delay: i * 0.08, ease: 'power3.out', scrollTrigger: { trigger: c, scroller: page, start: 'top 90%' } });
  });

  // Stats
  document.querySelectorAll('.stat-block').forEach(b => {
    gsap.fromTo(b, { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: 'power3.out', scrollTrigger: { trigger: b, scroller: page, start: 'top 92%' } });
  });

  // Who cards
  document.querySelectorAll('.who-card').forEach((c, i) => {
    gsap.fromTo(c, { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, delay: i * 0.12, ease: 'power3.out', scrollTrigger: { trigger: c, scroller: page, start: 'top 88%' } });
  });

  // Section titles
  document.querySelectorAll('.section-title, .section-label, .section-sub').forEach(el => {
    gsap.fromTo(el, { y: 25, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: 'power3.out', scrollTrigger: { trigger: el, scroller: page, start: 'top 90%' } });
  });

  // CTA
  const cta = document.querySelector('.cta-card');
  if (cta) gsap.fromTo(cta, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'power3.out', scrollTrigger: { trigger: cta, scroller: page, start: 'top 85%' } });
}

// ==================== FLOATING LABELS ====================
document.querySelectorAll('.form-group input').forEach(input => {
  input.addEventListener('input', () => input.classList.toggle('has-value', input.value.length > 0));
});

// ==================== AUTH SUBMIT ====================
function handleAuthSubmit(btn, targetPage) {
  const t = btn.querySelector('.btn-text'), s = btn.querySelector('.spinner');
  if (t) t.style.display = 'none'; if (s) s.style.display = 'block';
  setTimeout(() => { if (t) t.style.display = 'inline'; if (s) s.style.display = 'none'; navigateTo(targetPage); }, 1200);
}

// ==================== TOOL PAGE ====================
let toolInit = false, filesUploaded = { a: false, b: false };
function checkRunReady() { const b = document.getElementById('btn-run-ali'); if (filesUploaded.a && filesUploaded.b) { b.classList.add('ready'); b.disabled = false; } else { b.classList.remove('ready'); b.disabled = true; } }
function initTool() {
  if (toolInit) return; toolInit = true;
  document.querySelectorAll('.upload-box').forEach(box => {
    const key = box.dataset.tool;
    box.addEventListener('dragover', e => { e.preventDefault(); box.classList.add('dragover'); });
    box.addEventListener('dragleave', () => box.classList.remove('dragover'));
    box.addEventListener('drop', e => { e.preventDefault(); box.classList.remove('dragover'); const f = e.dataTransfer.files[0]; if (!f) return; box.classList.add('uploaded'); box.querySelector('.upload-icon').innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>'; box.querySelector('.sub').textContent = ''; let fn = box.querySelector('.filename'); if (!fn) { fn = document.createElement('div'); fn.className = 'filename'; box.appendChild(fn); } fn.textContent = f.name; filesUploaded[key] = true; checkRunReady(); });
    box.addEventListener('click', () => { const inp = document.createElement('input'); inp.type = 'file'; inp.accept = '.txt,.md,.pdf'; inp.addEventListener('change', () => { if (!inp.files[0]) return; box.classList.add('uploaded'); box.querySelector('.upload-icon').innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>'; box.querySelector('.sub').textContent = ''; let fn = box.querySelector('.filename'); if (!fn) { fn = document.createElement('div'); fn.className = 'filename'; box.appendChild(fn); } fn.textContent = inp.files[0].name; filesUploaded[key] = true; checkRunReady(); }); inp.click(); });
  });
}

// ==================== RUN ALI ====================
function runALI() {
  const btn = document.getElementById('btn-run-ali'); if (!btn.classList.contains('ready')) return;
  const z1 = document.getElementById('zone-upload'), z2 = document.getElementById('zone-pipeline'), z3 = document.getElementById('zone-code'), z4 = document.getElementById('zone-result');
  gsap.to(z1, { opacity: 0.4, duration: 0.4 }); z2.style.display = 'block'; gsap.fromTo(z2, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4 });
  const stages = document.querySelectorAll('.timeline-stage'); let i = 0;
  function go() { if (i >= stages.length) return; const s = stages[i]; s.classList.add('active'); s.style.opacity = '1'; gsap.fromTo(s.querySelector('.stage-title'), { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.3 }); const l = s.querySelector('.stage-line'); if (l) gsap.fromTo(l, { scaleY: 0 }, { scaleY: 1, duration: 0.7, transformOrigin: 'top' });
    setTimeout(() => { s.classList.remove('active'); s.classList.add('done'); s.querySelector('.stage-circle').innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#10B981" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>'; i++;
      if (i === 4) { z3.style.display = 'block'; gsap.fromTo(z3, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.4 }); typeCode(); }
      if (i === 5) { z4.style.display = 'block'; gsap.fromTo(z4, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5, ease: 'back.out(1.7)' }); }
      if (i < stages.length) setTimeout(go, 800); }, 2500); }
  setTimeout(go, 300);
}

// ==================== CODE TYPEWRITER ====================
const codeText = `import requests\nimport os\n\nHUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")\nDISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")\n\ndef get_latest_lead():\n    url = "https://api.hubspot.com/crm/v3/objects/contacts"\n    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}\n    response = requests.get(url, headers=headers)\n    contacts = response.json().get("results", [])\n    return contacts[0] if contacts else None\n\ndef send_discord_alert(lead):\n    name = lead["properties"].get("firstname", "Unknown")\n    company = lead["properties"].get("company", "Unknown")\n    email = lead["properties"].get("email", "Unknown")\n    payload = {\n        "username": "ALI Bridge",\n        "embeds": [{\n            "title": "New Lead Alert",\n            "color": 3447003,\n            "fields": [\n                {"name": "Name", "value": name, "inline": True},\n                {"name": "Company", "value": company, "inline": True},\n                {"name": "Email", "value": email, "inline": False}\n            ]\n        }]\n    }\n    requests.post(DISCORD_WEBHOOK, json=payload)\n\nlead = get_latest_lead()\nif lead:\n    send_discord_alert(lead)\n    print("SUCCESS")`;
function typeCode() { const c = document.getElementById('code-output'), l = document.getElementById('line-numbers'); if (!c) return; let idx = 0; function go() { if (idx >= codeText.length) { c.textContent = codeText; if (typeof Prism !== 'undefined') { c.className = 'language-python'; Prism.highlightElement(c); } l.innerHTML = Array.from({ length: codeText.split('\n').length }, (_, i) => i + 1).join('<br>'); return; } c.textContent += codeText[idx]; l.innerHTML = Array.from({ length: c.textContent.split('\n').length }, (_, i) => i + 1).join('<br>'); idx++; setTimeout(go, idx / codeText.length > 0.8 ? 40 : 18); } go(); }
function copyCode() { navigator.clipboard.writeText(codeText); const b = document.getElementById('btn-copy'); b.textContent = 'Copied!'; setTimeout(() => b.textContent = 'Copy', 1500); }

// ==================== RESET ====================
function resetTool() { const z2 = document.getElementById('zone-pipeline'), z3 = document.getElementById('zone-code'), z4 = document.getElementById('zone-result'); gsap.to([z2, z3, z4], { opacity: 0, duration: 0.3, onComplete: () => { z2.style.display = 'none'; z3.style.display = 'none'; z4.style.display = 'none'; document.querySelectorAll('.timeline-stage').forEach((s, i) => { s.classList.remove('active', 'done'); s.style.opacity = '0.3'; s.querySelector('.stage-circle').innerHTML = `<span class="stage-num">${i+1}</span><span class="mini-spin"></span>`; }); document.querySelectorAll('.upload-box').forEach(box => { box.classList.remove('uploaded', 'dragover'); box.querySelector('.upload-icon').innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/><path d="M12 18v-6"/><path d="M9 15l3-3 3 3"/></svg>'; box.querySelector('.sub').textContent = 'Drop .txt or .md file'; const fn = box.querySelector('.filename'); if (fn) fn.remove(); }); filesUploaded = { a: false, b: false }; checkRunReady(); const c = document.getElementById('code-output'); if (c) { c.textContent = ''; c.className = ''; } const l = document.getElementById('line-numbers'); if (l) l.innerHTML = '1'; gsap.to(document.getElementById('zone-upload'), { opacity: 1, duration: 0.3 }); }}); }

// ==================== SMOOTH SCROLL ====================
function scrollToSection(id) { const p = document.getElementById('page-landing'), t = document.getElementById(id); if (p && t) p.scrollTo({ top: t.offsetTop - 80, behavior: 'smooth' }); }

// ==================== ETHERAL SHADOWS ====================
function initEtheralShadows() {
  [{ inner: 'etheral-hero-inner', hue: 'etherHue1', filter: 'etherFilter1' }, { inner: 'etheral-signup-inner', hue: 'etherHue2', filter: 'etherFilter2' }, { inner: 'etheral-login-inner', hue: 'etherHue3', filter: 'etherFilter3' }].forEach(f => {
    const el = document.getElementById(f.inner), h = document.getElementById(f.hue);
    if (el) el.style.filter = `url(#${f.filter}) blur(4px)`;
    if (h) { let v = 0; (function a() { v = (v + 3.8) % 360; h.setAttribute('values', String(v)); requestAnimationFrame(a); })(); }
  });
}

// ==================== INIT ====================
window.addEventListener('DOMContentLoaded', () => { history.replaceState({ page: 'page-landing' }, '', '#page-landing'); navigateTo('page-landing', false); initLanding(); initTool(); initEtheralShadows(); });
