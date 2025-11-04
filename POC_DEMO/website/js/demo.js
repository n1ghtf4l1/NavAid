import { $, el, DEFAULT_API_BASE } from './main.js';

function getApiBase(){
  return DEFAULT_API_BASE;
}

function mapEndpoint(mode){
  switch(mode){
    case 'scene': return '/api/scene-understanding';
    case 'deep': return '/api/deep-analyze-traffic';
    case 'trip': return '/api/navigation-guidance';
    default: return '/api/scene-understanding';
  }
}

// Global state
let selectedImages = [];
let navInstructions = {}; // Map of image_index -> instruction
let results = []; // Array of {image, data, mode, imageIndex}
let currentResultIndex = 0;

function showPreviewGrid(files){
  const holder = $('#previewGrid');
  const count = $('#imageCount');

  holder.innerHTML = '';
  count.textContent = files.length;

  if (files.length === 0){
    holder.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--muted); padding: 20px;">No images selected</div>';
    return;
  }

  files.forEach((file, index) => {
    const wrapper = el('div', {style: 'position: relative; border-radius: 8px; overflow: hidden; aspect-ratio: 1; border: 2px solid var(--card-border);'});
    const img = new Image();
    img.alt = `preview ${index+1}`;
    img.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';
    img.onload = () => wrapper.appendChild(img);
    img.src = URL.createObjectURL(file);

    const badge = el('div', {style: 'position: absolute; top: 4px; right: 4px; background: rgba(108, 92, 231, 0.9); color: white; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600;'}, `${index + 1}`);
    wrapper.appendChild(badge);
    holder.appendChild(wrapper);
  });
}

function setLoading(on){
  $('#runBtn').disabled = on;
  $('#runBtn').textContent = on ? 'Analyzing…' : '▶️ Run Analysis';
}

function asText(v){
  if (v == null) return '—';
  if (Array.isArray(v)) return v.join(', ');
  if (typeof v === 'object') return JSON.stringify(v, null, 2);
  return String(v);
}

function renderResult(mode, data, container){
  const out = container || $('#modalOutput');
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

async function uploadImage(file){
  const apiBase = getApiBase();
  const fd = new FormData();
  fd.append('image', file);
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

function getSelectedModel(type){
  const activeBtn = document.querySelector(`.model-btn.active[data-model-type="${type}"]`);
  return activeBtn ? activeBtn.dataset.value : null;
}

async function processImage(file, imageIndex, mode, visionModel, ttsModel){
  const apiBase = getApiBase();
  const endpoint = mapEndpoint(mode);

  // Upload image
  const imagePath = await uploadImage(file);

  // Build payload
  const payload = {
    image_path: imagePath,
    vision_model: visionModel,
    tts_model: ttsModel
  };

  // Add navigation instruction if trip mode
  if (mode === 'trip'){
    if (navInstructions[imageIndex]) {
      payload.navigation_instruction = navInstructions[imageIndex];
    } else {
      payload.navigation_instruction = $('#navInstruction').value.trim() || 'Continue straight for 20 meters';
    }
  }

  // Make API call
  const res = await fetch(`${apiBase}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await res.json().catch(() => ({ error: 'Invalid JSON response' }));

  if (!res.ok){
    return { error: data.error || 'Analysis failed' };
  }

  return data;
}

async function run(){
  const mode = document.querySelector('.segmented button.active')?.dataset.mode || 'scene';
  const visionModel = getSelectedModel('vision') || 'gemini-2.5-flash';
  const ttsModel = getSelectedModel('tts') || 'coqui_vits_ljspeech';

  if (selectedImages.length === 0){
    alert('Please upload at least one image to analyze.');
    return;
  }

  // Reset results
  results = [];
  currentResultIndex = 0;

  setLoading(true);

  // Show modal with progress
  showModal();
  $('#progressBar').style.display = 'block';
  $('#progressText').textContent = `0 / ${selectedImages.length}`;
  $('#progressFill').style.width = '0%';
  updateCarouselButtons();

  // Process images sequentially
  for (let i = 0; i < selectedImages.length; i++){
    const file = selectedImages[i];
    const img = new Image();
    const imgUrl = URL.createObjectURL(file);
    img.src = imgUrl;

    try {
      const data = await processImage(file, i, mode, visionModel, ttsModel);

      // Store result
      results.push({
        image: img,
        imageUrl: imgUrl,
        data: data,
        mode: mode,
        imageIndex: i
      });

      // Update progress
      const progress = ((i + 1) / selectedImages.length) * 100;
      $('#progressFill').style.width = `${progress}%`;
      $('#progressText').textContent = `${i + 1} / ${selectedImages.length}`;

      // Show first result immediately
      if (i === 0){
        displayResult(0);
      }

      // Auto-advance to latest result if on last viewed result
      if (currentResultIndex === i - 1){
        currentResultIndex = i;
        displayResult(i);
      }

      updateCarouselButtons();

    } catch (err){
      console.error(`Error processing image ${i}:`, err);
      results.push({
        image: img,
        imageUrl: imgUrl,
        data: { error: err.message || String(err) },
        mode: mode,
        imageIndex: i
      });
    }
  }

  // Hide progress bar after completion
  setTimeout(() => {
    $('#progressBar').style.display = 'none';
  }, 500);

  setLoading(false);
}

function showModal(){
  $('#demoModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}

window.closeDemoModal = function(){
  $('#demoModal').classList.remove('active');
  document.body.style.overflow = '';

  // Clean up object URLs
  results.forEach(r => {
    if (r.imageUrl) URL.revokeObjectURL(r.imageUrl);
  });
};

function displayResult(index){
  if (index < 0 || index >= results.length) return;

  const result = results[index];
  currentResultIndex = index;

  // Update counter
  $('#resultCounter').textContent = `(${index + 1} of ${results.length})`;

  // Show image
  const modalPreview = $('#modalPreview');
  modalPreview.innerHTML = '';
  if (result.image){
    modalPreview.appendChild(result.image.cloneNode(true));
  } else {
    modalPreview.innerHTML = '<div style="padding:40px;text-align:center;color:var(--muted);">No preview available</div>';
  }

  // Render results
  const modalOutput = $('#modalOutput');
  modalOutput.innerHTML = '';
  renderResult(result.mode, result.data, modalOutput);

  updateCarouselButtons();
}

function updateCarouselButtons(){
  const prevBtn = $('#prevBtn');
  const nextBtn = $('#nextBtn');

  if (!prevBtn || !nextBtn) return;

  prevBtn.disabled = currentResultIndex === 0;
  nextBtn.disabled = currentResultIndex >= results.length - 1;

  prevBtn.style.opacity = prevBtn.disabled ? '0.3' : '1';
  nextBtn.style.opacity = nextBtn.disabled ? '0.3' : '1';
}

window.navigateResult = function(direction){
  const newIndex = currentResultIndex + direction;
  if (newIndex >= 0 && newIndex < results.length){
    displayResult(newIndex);
  }
};

function extractAudioText(mode, data){
  if (mode === 'trip'){
    let text = data.navigation_instruction || 'No instruction';
    if (data.hazard_detected && data.hazard_guidance){
      text += '. ' + data.hazard_guidance;
    }
    return text;
  } else if (mode === 'deep'){
    return data.recommendation || data.description || 'No recommendation';
  } else {
    return data.summary || data.description || 'No summary';
  }
}

window.playAudioInstruction = async function(){
  if (results.length === 0 || currentResultIndex >= results.length){
    alert('No audio instruction available');
    return;
  }

  const result = results[currentResultIndex];
  const audioText = extractAudioText(result.mode, result.data);

  if (!audioText){
    alert('No audio instruction available');
    return;
  }

  const btn = document.querySelector('.demo-play-btn');
  const originalText = btn.innerHTML;
  btn.innerHTML = '<span>⏳</span><span>Generating...</span>';
  btn.disabled = true;

  try {
    const ttsModel = getSelectedModel('tts') || 'coqui_vits_ljspeech';
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/api/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: audioText,
        tts_model: ttsModel
      })
    });

    if (!res.ok){
      throw new Error('TTS generation failed');
    }

    // Get audio blob
    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    // Play audio
    const audio = new Audio(audioUrl);
    audio.play();

    // Update button
    btn.innerHTML = '<span>🔊</span><span>Playing...</span>';

    audio.onended = () => {
      btn.innerHTML = originalText;
      btn.disabled = false;
      URL.revokeObjectURL(audioUrl);
    };

    audio.onerror = () => {
      btn.innerHTML = originalText;
      btn.disabled = false;
      alert('Failed to play audio');
    };

  } catch (err){
    btn.innerHTML = originalText;
    btn.disabled = false;
    alert('Failed to generate audio: ' + err.message);
  }
};

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (!$('#demoModal').classList.contains('active')) return;

  if (e.key === 'ArrowLeft'){
    navigateResult(-1);
  } else if (e.key === 'ArrowRight'){
    navigateResult(1);
  } else if (e.key === 'Escape'){
    closeDemoModal();
  }
});

// Close modal on background click
document.addEventListener('DOMContentLoaded', () => {
  $('#demoModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'demoModal'){
      closeDemoModal();
    }
  });
});

function wire(){
  // Images selection
  $('#images').addEventListener('change', (e) => {
    selectedImages = Array.from(e.target.files || []);
    showPreviewGrid(selectedImages);
  });

  // JSON file selection
  $('#navJson')?.addEventListener('change', async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const json = JSON.parse(text);

      navInstructions = {};

      // Support two formats:
      // Format 1: Simple array [{image_index: 0, instruction: "..."}, ...]
      if (Array.isArray(json)){
        json.forEach(item => {
          if (item.image_index != null && item.instruction){
            navInstructions[item.image_index] = item.instruction;
          }
        });
      }
      // Format 2: NavAid trip JSON with nested instructions array
      else if (json.instructions && Array.isArray(json.instructions)){
        json.instructions.forEach((item, index) => {
          // Use step_number - 1 as image_index (0-based), or just use index
          const imageIndex = (item.step_number != null) ? item.step_number - 1 : index;
          const instruction = item.tts_text || item.instruction;
          if (instruction){
            navInstructions[imageIndex] = instruction;
          }
        });
      }

      $('#jsonPreview').style.display = 'block';
      $('#jsonCount').textContent = Object.keys(navInstructions).length;

      if (Object.keys(navInstructions).length === 0){
        alert('No instructions found in JSON. Expected format:\n' +
              '1. Array: [{image_index: 0, instruction: "..."}]\n' +
              '2. Object: {instructions: [{step_number: 1, instruction: "..."}]}');
      }
    } catch (err){
      alert('Failed to parse JSON file: ' + err.message);
    }
  });

  // Run button
  $('#runBtn').addEventListener('click', (e) => {
    e.preventDefault();
    run();
  });

  // Mode segmented control
  document.querySelectorAll('.segmented button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.segmented button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const showNav = btn.dataset.mode === 'trip';
      const navPane = $('#navInstructionsPane');
      const uploadPane = $('#uploadPane');

      if (navPane && uploadPane) {
        if (showNav) {
          // Show nav pane and make upload pane share the row
          navPane.style.display = 'block';
          uploadPane.style.gridColumn = '';
        } else {
          // Hide nav pane and make upload pane full width
          navPane.style.display = 'none';
          uploadPane.style.gridColumn = '1 / -1';
        }
      }
    });
  });

  // Model selection buttons
  document.querySelectorAll('.model-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const modelType = btn.dataset.modelType;
      // Remove active from all buttons of same type
      document.querySelectorAll(`.model-btn[data-model-type="${modelType}"]`).forEach(b => {
        b.classList.remove('active');
      });
      // Add active to clicked button
      btn.classList.add('active');
    });
  });
}

document.addEventListener('DOMContentLoaded', wire);
