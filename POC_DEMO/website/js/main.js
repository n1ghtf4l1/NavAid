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

