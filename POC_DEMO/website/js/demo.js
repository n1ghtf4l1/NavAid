import { $, el, DEFAULT_API_BASE } from './main.js';

function getApiBase(){
  return DEFAULT_API_BASE; // fixed per feedback
}

function mapEndpoint(mode){
  switch(mode){
    case 'scene': return '/api/scene-understanding';
    case 'deep': return '/api/deep-analyze-traffic';
    case 'trip': return '/api/navigation-guidance';
    default: return '/api/scene-understanding';
  }
}

function showPreview(file){
  const holder = $('#preview');
  holder.innerHTML = '';
  const img = new Image();
  img.alt = 'preview';
  img.onload = () => holder.appendChild(img);
  img.src = URL.createObjectURL(file);
}

function setLoading(on){
  $('#runBtn').disabled = on;
  $('#runBtn').textContent = on ? 'Analyzing…' : 'Run Analysis';
}

function renderKV(title, entries){
  const wrap = el('div', {class: 'result'});
  wrap.appendChild(el('h4', {}, title));
  const grid = el('div', {class: 'kv'});
  entries.forEach(([k,v]) => {
    grid.appendChild(el('div', {class: 'k'}, k));
    grid.appendChild(el('div', {class: 'v'}, v));
  });
  wrap.appendChild(grid);
  return wrap;
}

function asText(v){
  if (v == null) return '—';
  if (Array.isArray(v)) return v.join(', ');
  if (typeof v === 'object') return JSON.stringify(v, null, 2);
  return String(v);
}

function renderResult(mode, data){
  const out = $('#output');
  out.innerHTML = '';

  if (data.error){
    out.appendChild(renderKV('Error', [['Message', data.error]]));
    return;
  }

  if (mode === 'trip'){
    // NavigationGuidanceOutput schema
    out.appendChild(renderKV('Navigation + Hazards', [
      ['Instruction', asText(data.navigation_instruction)],
      ['Hazard Detected', data.hazard_detected ? 'Yes' : 'No'],
      ['Hazard Guidance', asText(data.hazard_guidance)],
      ['Haptic', asText(data.haptic_recommendation)],
      ['Traffic Light', data.traffic_light_detected ? 'Detected' : 'Not detected'],
      ['Traffic Light Info', data.traffic_light_info ? `${data.traffic_light_info.description} (~${data.traffic_light_info.approximate_distance_meters}m)` : '—'],
      ['Confidence', asText(data.confidence)],
      ['Notes', asText(data.notes)],
    ]));
    return;
  }

  // Scene understanding / Deep analyze traffic (raw JSON)
  // Try to surface likely fields nicely
  const knownTitle = mode === 'scene' ? 'Scene Understanding' : 'Traffic Light Analysis';
  const pairs = [];
  const keys = Object.keys(data || {});
  if (keys.length === 0){
    out.appendChild(renderKV(knownTitle, [['Result', 'No data']]));
    return;
  }

  const tryKeys = ['summary','description','safety_notes','landmarks','environment','safe_to_cross','countdown_seconds','recommendation','details'];
  for (const k of tryKeys){
    if (k in data){
      pairs.push([k.replaceAll('_',' ').replace(/\b\w/g, c=>c.toUpperCase()), asText(data[k])]);
    }
  }
  // Append remaining keys that are not already shown
  for (const k of keys){
    if (!tryKeys.includes(k)){
      pairs.push([k.replaceAll('_',' ').replace(/\b\w/g, c=>c.toUpperCase()), asText(data[k])]);
    }
  }
  out.appendChild(renderKV(knownTitle, pairs));
}

async function uploadImageIfNeeded(){
  const f = $('#image').files[0];
  if (!f) return null; // maybe sample path chosen

  const apiBase = getApiBase();
  const fd = new FormData();
  fd.append('image', f);
  const res = await fetch(`${apiBase}/api/upload-image`, {
    method: 'POST',
    body: fd,
  });
  if (!res.ok){
    throw new Error(`Upload failed: ${res.status}`);
  }
  const j = await res.json();
  return j.image_path || null;
}

async function run(){
  const mode = document.querySelector('.segmented button.active')?.dataset.mode || 'scene';
  const apiBase = getApiBase();
  const endpoint = mapEndpoint(mode);

  setLoading(true);
  try {
    // Determine image path: uploaded file -> upload endpoint; else sample path; else manual path
    let imagePath = null;
    const sampleActive = document.querySelector('.sample-btn.active');
    const sample = sampleActive?.dataset.path || '';

    if ($('#image').files.length > 0){
      imagePath = await uploadImageIfNeeded();
    } else if (sample) {
      imagePath = sample;
    }

    if (!imagePath){
      renderResult(mode, { error: 'Please select an image (upload, sample, or enter a local path).' });
      return;
    }

    const payload = { image_path: imagePath };
    if (mode === 'trip'){
      payload.navigation_instruction = $('#navInstruction').value.trim() || 'Continue straight for 20 meters';
    }

    const res = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json().catch(() => ({ error: 'Invalid JSON response' }));
    if (!res.ok){
      renderResult(mode, data);
    } else {
      renderResult(mode, data);
    }
  } catch (err){
    renderResult('error', { error: err.message || String(err) });
  } finally {
    setLoading(false);
  }
}

function wire(){
  $('#image').addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) showPreview(f);
  });
  $('#runBtn').addEventListener('click', (e) => { e.preventDefault(); run(); });
  // Segmented control
  document.querySelectorAll('.segmented button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.segmented button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const showNav = btn.dataset.mode === 'trip';
      $('#navField').style.display = showNav ? 'block' : 'none';
    });
  });
  // Sample chips
  document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      $('#image').value = '';
      $('#preview').textContent = 'Sample selected';
    });
  });
}

document.addEventListener('DOMContentLoaded', wire);
