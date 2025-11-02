# NavAid PoC Demo - Master Plan
**Project**: Navigation Assistant for Visually Impaired
**Target**: Professional demo with iPhone simulator + website
**Date**: October 31, 2025
**Status**: Planning Phase

---

## 🎯 Project Mission
Build a proof-of-concept demonstration of NavAid - an AI-powered navigation assistant specifically designed for people with Retinitis Pigmentosa and similar visual impairments. This demo showcases real-time hazard detection, audio guidance, and traffic light crossing assistance.

**Core Principle**: Audio-first, safety-critical design with zero compromise on user safety.

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      WEBSITE (HTML/CSS/JS)                   │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐          │
│  │  Features  │  │    Docs    │  │ Demo (Video/ │          │
│  │   & About  │  │   GitHub   │  │  Simulator)  │          │
│  └────────────┘  └────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              iOS APP (Swift + XCode Simulator)               │
│                                                              │
│  HOME SCREEN              IN-TRIP SCREEN                     │
│  ┌──────────────┐        ┌───────────┬───────────┐         │
│  │  Settings    │        │  Repeat   │   Stop    │         │
│  │   (Top 20%)  │        │ (Top-L)   │ (Top-R)   │         │
│  └──────────────┘        └───────────┴───────────┘         │
│  ┌──────────────┐        ┌──────────────────────┐         │
│  │ Logo + Name  │        │  NavAid (Middle 20%) │         │
│  │  (Mid 20%)   │        └──────────────────────┘         │
│  └──────────────┘        ┌───────────┬───────────┐         │
│  ┌──────┬───────┐        │   Deep    │   Scene   │         │
│  │Start │ Scene │        │  Analyze  │  Understand│         │
│  │ Trip │Descr. │        │(Bottom-L) │(Bottom-R) │         │
│  └──────┴───────┘        └───────────┴───────────┘         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI BACKEND (Gemini API)                   │
│                                                              │
│  Hazard Detection     Scene Understanding   Traffic Lights  │
│  (Gemini 2.5 Flash)   (Gemini 2.5)         (Gemini 2.0)    │
│  + Haptics           + Landmarks            + Timing Logic   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  AUDIO OUTPUT (Coqui VITS)                   │
│              + HAPTIC FEEDBACK (Simulated)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Directory Structure

```
/Users/prabhavsingh/Documents/CLASSES/Fall2025/NAVAID/POC_DEMO/
├── MASTER_PLAN.md (this file)
├── TECHNICAL_SPEC.md (detailed tech specs)
├── IMPLEMENTATION_CHECKLIST.md (task tracking)
│
├── website/
│   ├── index.html (main landing page)
│   ├── css/
│   │   ├── styles.css (main styles)
│   │   ├── animations.css (smooth transitions)
│   │   └── responsive.css (mobile responsive)
│   ├── js/
│   │   ├── main.js (interactions)
│   │   └── animations.js (scroll effects, etc.)
│   ├── assets/
│   │   ├── images/
│   │   │   ├── logo.svg (NavAid logo)
│   │   │   ├── hero-bg.jpg
│   │   │   └── feature-icons/
│   │   ├── videos/
│   │   │   └── demo-walkthrough.mp4 (optional)
│   │   └── fonts/ (if custom fonts)
│   └── docs/
│       └── documentation.html
│
├── prompts/
│   ├── hazard_detection_v3.md (UPDATED with haptics + traffic lights)
│   ├── scene_understanding.md (NEW - for scene description)
│   └── deep_analyze_traffic.md (NEW - for crosswalk analysis)
│
├── demo_data/
│   ├── simulated_directions.json (20 Google Maps-style instructions)
│   ├── photos/
│   │   ├── trip_sequence/ (20 photos, numbered 01-20)
│   │   ├── scene_understanding/ (5-10 example scenes)
│   │   └── traffic_lights/ (5-10 crosswalk examples)
│   ├── audio_cache/ (cached TTS outputs)
│   └── test_outputs/ (Gemini responses for testing)
│
└── integration/
    ├── gemini_client.py (enhanced client with new prompts)
    ├── tts_engine.py (Coqui VITS wrapper)
    ├── haptic_simulator.py (haptic pattern definitions)
    └── demo_controller.py (orchestrates demo flow)

/Users/prabhavsingh/Documents/CLASSES/Fall2025/NAVAID/NavAid/ (Swift iOS App)
├── NavAid.xcodeproj
├── NavAid/
│   ├── Models/
│   │   ├── TripState.swift
│   │   ├── HazardResponse.swift
│   │   └── DirectionInstruction.swift
│   ├── Views/
│   │   ├── HomeView.swift
│   │   ├── InTripView.swift
│   │   └── Components/
│   │       ├── LargeButton.swift (accessible button component)
│   │       └── HapticFeedbackView.swift
│   ├── ViewModels/
│   │   ├── TripViewModel.swift
│   │   └── HazardDetectionViewModel.swift
│   ├── Services/
│   │   ├── GeminiAPIService.swift
│   │   ├── TTSService.swift
│   │   ├── HapticService.swift
│   │   └── PhotoLoader.swift (loads from demo_data)
│   ├── Utilities/
│   │   ├── AudioManager.swift
│   │   └── Constants.swift (colors, strings)
│   └── Resources/
│       ├── Assets.xcassets (logo, colors)
│       └── Info.plist
└── DemoData/ (symlink to POC_DEMO/demo_data)
```

---

## 🎨 UI/UX Specifications

### Color Palette
**Primary**: #0061FF (NavAid Blue - Official)
**Variants**:
- Light: #3384FF (hover states)
- Dark: #004ACC (pressed states)
- Ultra Dark: #00368F (backgrounds)

**Accessibility Colors** (high contrast for visual impairments):
- Success/Safe: #00C853 (bright green)
- Warning: #FFB300 (amber)
- Danger: #E53935 (red)
- Text on Dark: #FFFFFF
- Background: #000000 (pure black for OLED)

### Typography (iOS App)
**Primary Font**: SF Pro (iOS system font)
**Sizes**:
- Title: 48pt (bold)
- Button Label: 28pt (semibold)
- Body: 20pt (regular)
- Caption: 16pt (light)

**Accessibility**:
- Minimum 28pt for tap targets
- Dynamic Type support
- VoiceOver labels on all interactive elements

### Button Layout (Precise Specifications)

**Home Screen:**
```
┌─────────────────────────────────────┐ ← Top (0%)
│         SETTINGS (Disabled)         │
│           Top 20%                   │
├─────────────────────────────────────┤ ← 20%
│                                     │
│     [Logo] NavAid                   │
│         Middle 20%                  │
│                                     │
├─────────────────────────────────────┤ ← 40%
│                                     │
│   START TRIP  │  SCENE DESCRIBE    │
│               │                     │
│   Bottom 60%  │  (split 50/50)     │
│               │                     │
│               │                     │
└─────────────────────────────────────┘ ← 100%
```

**In-Trip Screen:**
```
┌─────────────────────────────────────┐ ← Top (0%)
│   REPEAT    │      STOP            │
│  Last Inst  │      Trip            │
│             │                       │
│   Top 40%   │  (split 50/50)       │
├─────────────────────────────────────┤ ← 40%
│                                     │
│         NavAid                      │
│       Middle 20%                    │
│                                     │
├─────────────────────────────────────┤ ← 60%
│    DEEP      │     SCENE            │
│   ANALYZE    │   UNDERSTANDING      │
│  (Traffic)   │                      │
│             │                       │
│  Bottom 40% │  (split 50/50)       │
│             │                       │
└─────────────────────────────────────┘ ← 100%
```

---

## 🔧 Technical Implementation

### Option 1: Swift iOS App with XCode Simulator (RECOMMENDED)

**Pros:**
✅ Professional, realistic demo
✅ Actual iOS simulator experience
✅ Can simulate haptics properly
✅ Real camera integration (even with preset photos)
✅ Better for future development
✅ Native audio/speech APIs

**Cons:**
❌ Requires XCode proficiency
❌ Cannot embed live in website (need video recording)

**Decision**: Use Swift app, record demo video for website

### Tech Stack (iOS App):
- **Language**: Swift 5.9+
- **Framework**: SwiftUI
- **Minimum iOS**: 16.0
- **APIs**:
  - AVFoundation (audio)
  - CoreHaptics (haptic feedback)
  - URLSession (Gemini API calls)
  - Speech (if needed for TTS fallback)

### Tech Stack (Website):
- **Pure HTML5/CSS3/Vanilla JavaScript**
- **Libraries** (minimal):
  - AOS.js (Animate On Scroll) - lightweight animations
  - (Optional) Feather Icons for clean icons
- **Hosting**: GitHub Pages / Netlify (static hosting)

---

## 🤖 AI Integration Details

### 1. Hazard Detection Prompt (v3.0)

**Model**: Gemini 2.5 Flash
**Frequency**: Every 5 seconds during trip
**Timeout**: 3 seconds max

**NEW JSON Schema** (additions in bold):

```json
{
  "hazard_detected": true,
  "num_hazards": 2,
  "hazard_types": ["trafficcone", "person"],
  "one_sentence": "...",
  "evasive_suggestion": "...",
  "bearing": "center",
  "proximity": "near",
  "confidence": 0.88,
  "notes": "...",

  // NEW FIELDS
  "haptic_recommendation": "full_haptic",  // left_haptic | right_haptic | full_haptic | no_haptic

  "traffic_light_detected": true,  // NEW
  "traffic_light_info": {
    "approximate_distance_meters": 15,
    "description": "Pedestrian crossing ahead with traffic signal visible",
    "requires_deep_analyze": true
  }
}
```

**Haptic Logic**:
- `left_haptic`: Dangerous obstacle on left (pole, person, cone near left edge)
- `right_haptic`: Dangerous obstacle on right
- `full_haptic`: Obstacle directly ahead (center bearing + near proximity)
- `no_haptic`: Clear path or distant hazards

**Traffic Light Trigger**:
When `traffic_light_detected = true`:
1. Play STRONG haptic pattern (3 long pulses)
2. Audio: "Traffic light crossing in {distance}. Please use Deep Analyze button once you reach the intersection. DO NOT PROCEED WITHOUT."
3. Highlight Deep Analyze button in UI

---

### 2. Scene Understanding Prompt (NEW)

**Model**: Gemini 2.5 (more capable for scene interpretation)
**Trigger**: User presses Scene Understanding button
**Use Case**: "What's around me? What shops? What street?"

**Prompt Strategy**:
```
You are a scene describer for a blind pedestrian. Analyze this image and provide:

1. Overall Scene Type: (street, plaza, storefront, park, etc.)
2. Prominent Landmarks: Any visible business names, street signs, building names
3. Notable Features: Benches, trees, fountains, statues, etc.
4. Approximate Orientation: If street signs visible, mention direction
5. Safety Notes: Any immediate concerns (construction, crowds, etc.)

Return JSON:
{
  "scene_type": "commercial street",
  "landmarks": ["Starbucks on left", "CVS Pharmacy ahead"],
  "street_name": "Main Street" or null,
  "features": ["bus stop 20m ahead", "bike rack on right"],
  "safety_notes": "crowded sidewalk, stay right",
  "one_sentence_summary": "You're on Main Street facing north. Starbucks on your left, CVS ahead. Sidewalk is crowded."
}
```

**Audio Output**: Read `one_sentence_summary` + key landmarks

---

### 3. Deep Analyze Traffic Light Prompt (NEW)

**Model**: Gemini 2.0 Flash (faster for time-critical task)
**Trigger**: User presses Deep Analyze at intersection
**Use Case**: Determine if safe to cross pedestrian crossing

**Prompt Strategy**:
```
You are a traffic light analyzer for a blind pedestrian at a crosswalk.

CRITICAL SAFETY TASK: Analyze this crosswalk image and determine:

1. Traffic Light Status: red, green, yellow, or unknown
2. Countdown Timer: If visible, extract exact number (in seconds)
3. Pedestrian Signal: Walk symbol visible? Don't Walk symbol?

TIMING LOGIC:
- If RED or YELLOW: Do not cross, estimate wait time if visible
- If GREEN:
  - Read countdown timer
  - SUBTRACT 7 seconds for processing delay + crossing time
  - If result < 5 seconds: TOO SHORT, do not cross
  - If result >= 5 seconds: Safe to cross, tell user adjusted time

Return JSON:
{
  "light_status": "green" | "red" | "yellow" | "unknown",
  "countdown_timer_seconds": 15 or null,
  "adjusted_crossing_time": 8,  // countdown - 7 seconds
  "safe_to_cross": true | false,
  "instruction": "Cross now. You have 8 seconds." or "Do not cross. Wait for green light, approximately 45 seconds."
}
```

**Audio Output**: Read `instruction` with appropriate urgency

**Haptic Pattern**:
- Safe to cross: 2 short pulses (go signal)
- Do NOT cross: 3 long pulses (stop signal)

---

## 🎵 Audio System

### TTS Engine: Coqui VITS (LJSpeech)
**Selected From Evaluation**: Best WER (4.95%), RTF 0.24

**Implementation**:
```python
from TTS.api import TTS

tts = TTS("tts_models/en/ljspeech/vits")

def generate_audio(text: str) -> bytes:
    """Generate audio from text, return WAV bytes."""
    wav = tts.tts(text)
    # Save to temp file or stream directly
    return wav_bytes
```

**Caching Strategy**:
1. Cache last Google Maps instruction + last Gemini instruction
2. Pre-generate common phrases:
   - "Traffic light ahead"
   - "Hazard detected"
   - "Path clear"
   - "Analyzing scene..."

**Fallback**: iOS native AVSpeechSynthesizer if Coqui unavailable

---

## 📳 Haptic Feedback System

### Haptic Patterns (iOS CoreHaptics)

```swift
enum HapticPattern {
    case leftObstacle      // 2 sharp taps (left side)
    case rightObstacle     // 2 sharp taps (right side)
    case frontObstacle     // 3 strong pulses (center)
    case trafficLight      // 3 long strong pulses (critical warning)
    case safeToCross       // 2 short gentle pulses (confirmation)
    case doNotCross        // 3 long strong pulses (danger)
    case navigationTurn    // 1 medium pulse (turn cue)
}

// Implementation
func playHaptic(_ pattern: HapticPattern) {
    let engine = CHHapticEngine()
    // Define intensity, sharpness, duration per pattern
    // ...
}
```

**Visual Indicator** (for demo purposes):
Show haptic pattern on screen with pulsing border:
- Left: Blue pulse on left edge
- Right: Blue pulse on right edge
- Full: Entire border pulses
- Traffic: Red border pulse

---

## 📊 Demo Flow

### Pre-Demo Setup:
1. Load 20 simulated Google Maps instructions into JSON
2. Prepare 20 sequential photos (user will provide)
3. Pre-generate TTS audio for instructions (cache)
4. Validate Gemini API connectivity

### Demo Sequence:

#### Phase 1: App Introduction (10 seconds)
1. User opens app → Home screen displayed
2. VoiceOver/TTS announces: "NavAid - Navigation Assistant. Two buttons available: Start Trip on bottom left, Scene Understanding on bottom right. Settings on top."

#### Phase 2: Start Trip (5 seconds)
1. User taps "Start Trip"
2. Screen transitions to In-Trip view
3. TTS announces: "Trip started. Four buttons available. Top left: Repeat Last Instruction. Top right: Stop Trip. Bottom left: Deep Analyze for crosswalks. Bottom right: Scene Understanding. Please keep phone at chest level."

#### Phase 3: Navigation Loop (5 minutes)
**Every 30 seconds**:
1. Play Google Maps instruction (e.g., "Continue straight for 50 meters")
2. Load next photo from sequence
3. Send to Gemini Hazard Detection (v3 prompt)
4. Process response:
   - If hazards: Play evasive instruction + haptic
   - If traffic light detected: Play warning + strong haptic
   - If clear: Continue
5. Cache instruction for Repeat button

**Example Sequence**:
- **00:00**: "In 50 meters, turn right onto Main Street"
- **00:05**: Photo 1 → "Path clear, continue forward" + no haptic
- **00:10**: Photo 2 → "Person crossing ahead, slow down" + full haptic
- **00:30**: "Turn right onto Main Street"
- **00:35**: Photo 3 → "Traffic light detected 15 meters ahead..."

#### Phase 4: Traffic Light Encounter (30 seconds)
1. Gemini detects traffic light
2. Strong haptic + audio warning
3. User reaches intersection
4. User presses "Deep Analyze"
5. Deep Analyze prompt analyzes crossing
6. Returns: "Do not cross. Wait for green light." OR "Cross now, 8 seconds remaining"
7. Appropriate haptic

#### Phase 5: Scene Understanding Test (15 seconds)
1. User presses "Scene Understanding"
2. Camera captures scene (or loads example)
3. Gemini 2.5 analyzes
4. Audio describes: "You're on Main Street. Starbucks on left, CVS ahead..."

#### Phase 6: Repeat Function (5 seconds)
1. User presses "Repeat"
2. Last cached instruction replays

#### Phase 7: Stop Trip (3 seconds)
1. User presses "Stop Trip"
2. Returns to Home screen
3. TTS: "Trip ended. Welcome back."

**Total Demo**: ~7 minutes

---

## 🔌 Google Maps API Integration (Future)

**Current**: Simulated JSON instructions
**Future**: Real-time directions

### Implementation Plan:

```python
import googlemaps

gmaps = googlemaps.Client(key='YOUR_API_KEY')

def get_directions(origin: str, destination: str):
    """Fetch turn-by-turn directions."""
    directions = gmaps.directions(
        origin,
        destination,
        mode="walking",
        alternatives=False
    )

    # Parse steps
    steps = []
    for leg in directions[0]['legs']:
        for step in leg['steps']:
            steps.append({
                'instruction': step['html_instructions'],
                'distance': step['distance']['text'],
                'duration': step['duration']['text'],
                'maneuver': step.get('maneuver', 'straight')
            })

    return steps
```

**Integration Points**:
1. User inputs destination via voice (future: speech-to-text)
2. Fetch directions from current location
3. Parse into NavAid instruction format
4. Feed to TTS at appropriate intervals based on GPS location
5. Trigger photo analysis every 5 seconds regardless of navigation step

**Challenges**:
- GPS accuracy indoors
- Timing instructions based on walking speed
- Handling route deviations

**Mitigation**:
- Use simulated GPS for demo
- Adjust timing based on user profile (walking speed)
- Implement "recalculating" flow if off-route

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Days 1-2)
- [x] Create master plan (this document)
- [ ] Set up directory structure
- [ ] Design website wireframes
- [ ] Create Swift iOS project structure
- [ ] Set up color scheme and assets

### Phase 2: Backend & Prompts (Days 2-3)
- [ ] Write hazard detection prompt v3.0 (with haptics + traffic lights)
- [ ] Write scene understanding prompt
- [ ] Write deep analyze traffic prompt
- [ ] Enhance gemini_client.py with new prompts
- [ ] Create TTS wrapper for Coqui VITS
- [ ] Implement haptic pattern definitions

### Phase 3: iOS App - Core UI (Days 3-4)
- [ ] Build Home screen (SwiftUI)
- [ ] Build In-Trip screen (SwiftUI)
- [ ] Implement large accessible buttons
- [ ] Add haptic feedback simulation
- [ ] Implement audio playback
- [ ] Add screen transitions

### Phase 4: iOS App - Functionality (Days 4-5)
- [ ] Implement Start Trip flow
- [ ] Load simulated directions JSON
- [ ] Photo loader service (from demo_data)
- [ ] Integrate Gemini API calls
- [ ] Implement hazard detection loop (every 5s)
- [ ] Cache system for Repeat button

### Phase 5: iOS App - Special Features (Days 5-6)
- [ ] Scene Understanding button
- [ ] Deep Analyze button (traffic lights)
- [ ] Traffic light detection + warning system
- [ ] Haptic patterns for all scenarios
- [ ] Stop Trip functionality

### Phase 6: Demo Data Preparation (Day 6)
- [ ] Create simulated_directions.json (20 instructions)
- [ ] Organize photo folders (trip, scene, traffic)
- [ ] Pre-generate TTS audio for caching
- [ ] Test Gemini responses with sample photos

### Phase 7: Website Development (Days 7-8)
- [ ] HTML structure for single-page site
- [ ] CSS styling (NavAid blue theme #0061FF)
- [ ] Features section (what NavAid does)
- [ ] About section (mission, target users)
- [ ] Documentation page
- [ ] GitHub link integration
- [ ] Demo section (embedded video or simulator)
- [ ] Responsive design
- [ ] Animations and polish

### Phase 8: Integration & Testing (Day 9)
- [ ] End-to-end test of demo flow
- [ ] Record demo video (7 minutes)
- [ ] Test all button interactions
- [ ] Verify audio output quality
- [ ] Test haptic feedback
- [ ] Validate Gemini API responses

### Phase 9: Polish & Documentation (Day 10)
- [ ] Final UI/UX polish
- [ ] Add accessibility labels (VoiceOver)
- [ ] Write user documentation
- [ ] Create demo script/walkthrough
- [ ] Final testing
- [ ] Deploy website

---

## 📋 File Deliverables

### Website:
- `index.html` - Main landing page
- `css/styles.css` - Styling
- `js/main.js` - Interactions
- Demo video or simulator embed

### iOS App:
- Complete XCode project
- Runnable in iOS Simulator
- All screens functional
- API integration working

### Prompts:
- `hazard_detection_v3.md` (with haptics + traffic)
- `scene_understanding.md`
- `deep_analyze_traffic.md`

### Demo Data:
- `simulated_directions.json`
- 20 sequential trip photos
- 5-10 scene understanding photos
- 5-10 traffic light photos

### Documentation:
- This master plan
- Technical specification
- Implementation checklist
- Demo walkthrough script

---

## 🎯 Success Criteria

### Demo Must:
✅ Run smoothly in iOS Simulator
✅ Show all 6 screens/states (Home, In-Trip, each button function)
✅ Audio guidance works (TTS outputs)
✅ Haptic feedback visible (on-screen indicator)
✅ Gemini API calls complete successfully
✅ Traffic light detection + Deep Analyze works
✅ Scene Understanding provides rich descriptions
✅ Repeat button caches and replays correctly

### Website Must:
✅ Look professional and beautiful
✅ NavAid blue theme (#0061FF) throughout
✅ Clear feature descriptions
✅ Links to docs and GitHub
✅ Demo video embedded or link to simulator
✅ Responsive on desktop and mobile
✅ Fast loading (<2 seconds)

### Code Must:
✅ Clean, documented Swift code
✅ Modular architecture (MVVM pattern)
✅ Error handling for API failures
✅ Accessible UI (VoiceOver support)
✅ Reusable components

---

## 🔮 Future Enhancements (Post-POC)

1. **Real Google Maps Integration**
   - Live GPS tracking
   - Turn-by-turn with location awareness
   - Route recalculation

2. **Advanced Features**
   - Indoor navigation (AR Kit)
   - Public transit integration
   - Crowdsourced hazard reporting
   - Multi-language support

3. **ML Improvements**
   - On-device hazard detection (Core ML)
   - Temporal consistency (video stream vs. photos)
   - Personalized obstacle preferences

4. **Hardware Integration**
   - Smart glasses (Meta Ray-Ban, etc.)
   - Bone conduction audio
   - Wearable haptics (vest, wristband)

5. **Community Features**
   - Route sharing
   - Accessibility ratings (routes, venues)
   - Emergency contact integration

---

## 📞 Contact & Collaboration

**GitHub**: [Link to repository]
**Documentation**: [Link to docs]
**Demo**: [Link to live demo]

---

## 🙏 Acknowledgments

This project is built with the goal of improving independence and safety for people with visual impairments. Special thanks to:
- Retinitis Pigmentosa community for feedback
- Accessibility advocates
- Open-source contributors (Coqui TTS, Gemini API)

**Remember**: Every feature we build could prevent an accident or enable someone to navigate independently. We build with care.

---

*End of Master Plan v1.0*
*Next Steps: Execute Phase 1 - Foundation*
