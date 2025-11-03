// Shared small helpers
export function $(sel, root = document) { return root.querySelector(sel); }
export function $all(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

export const DEFAULT_API_BASE = 'http://localhost:8000';

export function setActiveNav() {
  const path = location.pathname.split('/').pop() || 'index.html';
  const link = document.querySelector(`.nav a[href$="${path}"]`);
  if (link) link.classList.add('active');
}

export function el(tag, attrs = {}, children = []){
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => {
    if (k === 'class') e.className = v;
    else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  });
  (Array.isArray(children) ? children : [children]).forEach(c => {
    if (typeof c === 'string') e.appendChild(document.createTextNode(c));
    else if (c) e.appendChild(c);
  });
  return e;
}

document.addEventListener('DOMContentLoaded', setActiveNav);

// Simple scroll reveal for elements with .reveal class
document.addEventListener('DOMContentLoaded', () => {
  const els = Array.from(document.querySelectorAll('.reveal'));
  if (!('IntersectionObserver' in window)) {
    els.forEach(el => el.classList.add('in'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });
  els.forEach(el => io.observe(el));
});

// Header shadow on scroll
document.addEventListener('scroll', () => {
  const header = document.querySelector('.site-header');
  if (!header) return;
  if (window.scrollY > 12) header.classList.add('scrolled');
  else header.classList.remove('scrolled');
});

// Gentle parallax for hero image/glow
document.addEventListener('mousemove', (ev) => {
  const frame = document.querySelector('.hero-media .frame');
  const glow = document.querySelector('.hero-media .glow');
  if (!frame || !glow) return;
  const { innerWidth:w, innerHeight:h } = window;
  const dx = (ev.clientX - w/2) / w; // -0.5..0.5
  const dy = (ev.clientY - h/2) / h;
  frame.style.transform = `translate3d(${dx*10}px, ${dy*6}px, 0)`;
  glow.style.transform = `translate3d(${dx*16}px, ${dy*10}px, 0)`;
});
