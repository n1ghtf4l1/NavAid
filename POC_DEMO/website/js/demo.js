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
    const b = el('div', {class:'banner warn'}, [
      el('div', {class:'icon'}, '⚠️'),
      el('div', {}, [el('strong', {}, 'Error'), document.createTextNode(` — ${data.error}`)])
    ]);
    out.appendChild(b);
    return;
  }

  if (mode === 'trip'){
    // Navigation mode - comprehensive display
    const instr = el('div', {class:'panel'}, [
      el('div', {class:'panel-title'}, '🗺️ Navigation Instruction'),
      el('div', {class:'big'}, asText(data.navigation_instruction || 'No instruction provided')),
      el('div', {class:'chips'}, [
        el('div', {class:'chip info'}, `📊 Confidence: ${Math.round((data.confidence || 0)*100)}%`),
        data.notes ? el('div', {class:'chip'}, `📝 Has notes`) : null,
      ].filter(Boolean))
    ]);
    out.appendChild(instr);

    // Hazard section
    if (data.hazard_detected){
      const hazardDetails = el('div', {class:'detail-list'});
      if (data.hazard_guidance) {
        hazardDetails.appendChild(el('div', {class:'detail-item'}, [
          el('strong', {}, 'Guidance: '),
          document.createTextNode(asText(data.hazard_guidance))
        ]));
      }
      if (data.haptic_recommendation) {
        hazardDetails.appendChild(el('div', {class:'detail-item'}, [
          el('strong', {}, 'Haptic: '),
          document.createTextNode(asText(data.haptic_recommendation))
        ]));
      }

      const banner = el('div', {class:'banner warn'}, [
        el('div', {class:'icon'}, '🚧'),
        el('div', {style:'flex:1;'}, [
          el('div', {style:'font-weight:700; margin-bottom:8px; font-size:16px;'}, 'Hazard Detected'),
          hazardDetails
        ])
      ]);
      out.appendChild(banner);
    } else {
      const banner = el('div', {class:'banner ok'}, [
        el('div', {class:'icon'}, '✅'),
        el('div', {}, 'No immediate hazards detected.')
      ]);
      out.appendChild(banner);
    }

    // Traffic light section
    const tlDetails = [];
    if (data.traffic_light_detected && data.traffic_light_info){
      tlDetails.push(el('div', {class:'detail-item'}, [
        el('strong', {}, 'State: '),
        document.createTextNode(data.traffic_light_info.description || 'Unknown')
      ]));
      tlDetails.push(el('div', {class:'detail-item'}, [
        el('strong', {}, 'Distance: '),
        document.createTextNode(`~${data.traffic_light_info.approximate_distance_meters || '?'}m`)
      ]));
    }

    const tl = el('div', {class:'panel'}, [
      el('div', {class:'panel-title'}, '🚦 Traffic Signal'),
      el('div', {class:'big'}, data.traffic_light_detected ? '✅ Signal detected' : '❌ No signal detected'),
      ...(tlDetails.length ? [el('div', {class:'detail-list', style:'margin-top:12px;'}, tlDetails)] : [])
    ]);
    out.appendChild(tl);

    // Show all other fields
    renderAllFields(data, out, ['navigation_instruction', 'confidence', 'hazard_detected', 'hazard_guidance', 'haptic_recommendation', 'traffic_light_detected', 'traffic_light_info']);
    return;
  }

  if (mode === 'deep'){
    // Deep analyze mode
    const panel = el('div', {class:'panel'}, [
      el('div', {class:'panel-title'}, '🚦 Traffic Light Analysis'),
    ]);

    const mainText = data.recommendation || data.description || '';
    if (mainText) panel.appendChild(el('div', {class:'big'}, asText(mainText)));

    const chips = [];
    if ('safe_to_cross' in data) chips.push(el('div', {class: data.safe_to_cross ? 'chip ok':'chip warn'}, data.safe_to_cross ? '✅ Safe to cross' : '❌ Do not cross'));
    if ('countdown_seconds' in data && data.countdown_seconds!=null) chips.push(el('div', {class:'chip info'}, `⏱️ ${data.countdown_seconds}s`));
    if (chips.length) panel.appendChild(el('div', {class:'chips'}, chips));

    out.appendChild(panel);

    // Show all fields
    renderAllFields(data, out, ['recommendation', 'description', 'safe_to_cross', 'countdown_seconds']);
    return;
  }

  // Scene understanding
  const panel = el('div', {class:'panel'}, [
    el('div', {class:'panel-title'}, '🧭 Scene Understanding'),
  ]);

  const mainText = data.summary || data.description || '';
  if (mainText) panel.appendChild(el('div', {class:'big'}, asText(mainText)));

  const chips = [];
  if (Array.isArray(data.landmarks) && data.landmarks.length) {
    chips.push(el('div', {class:'chip info'}, `📍 ${data.landmarks.length} landmark(s)`));
    // Show landmarks
    const landmarksList = el('div', {class:'detail-list', style:'margin-top:12px;'});
    data.landmarks.forEach((lm, i) => {
      landmarksList.appendChild(el('div', {class:'detail-item'}, [
        el('strong', {}, `${i+1}. `),
        document.createTextNode(asText(lm))
      ]));
    });
    panel.appendChild(landmarksList);
  }
  if (data.environment) chips.push(el('div', {class:'chip'}, `🏙️ ${data.environment}`));
  if (chips.length) panel.appendChild(el('div', {class:'chips'}, chips));

  out.appendChild(panel);

  // Show all other fields
  renderAllFields(data, out, ['summary', 'description', 'landmarks', 'environment']);
}

function renderAllFields(data, container, excludeKeys){
  const keys = Object.keys(data || {}).filter(k => !excludeKeys.includes(k));
  if (keys.length === 0) return;

  const panel = el('div', {class:'panel expandable', style:'margin-top:12px; cursor:pointer;'}, [
    el('div', {class:'panel-title', style:'display:flex; justify-content:space-between; align-items:center;'}, [
      document.createTextNode('🔍 Additional Fields'),
      el('span', {style:'font-size:12px; opacity:0.7;'}, '(click to expand)')
    ]),
    el('div', {class:'expand-content', style:'display:none; margin-top:12px;'},
      keys.map(k => el('div', {class:'detail-item', style:'margin-bottom:8px;'}, [
        el('strong', {style:'color:var(--primary);'}, k.replaceAll('_', ' ') + ': '),
        document.createTextNode(asText(data[k]))
      ]))
    )
  ]);

  panel.addEventListener('click', () => {
    const content = panel.querySelector('.expand-content');
    const isExpanded = content.style.display !== 'none';
    content.style.display = isExpanded ? 'none' : 'block';
    panel.querySelector('.panel-title span').textContent = isExpanded ? '(click to expand)' : '(click to collapse)';
  });

  container.appendChild(panel);
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
