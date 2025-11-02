# NavAid PoC Demo - README

Welcome to the NavAid Proof-of-Concept Demo!

This directory contains all the resources needed to build and demonstrate the NavAid navigation assistant for visually impaired users.

---

## 📁 Directory Structure

```
POC_DEMO/
├── MASTER_PLAN.md              ⭐ Complete project plan (READ THIS FIRST)
├── README.md                    📖 This file
├── website/                     🌐 Landing page (HTML/CSS/JS)
├── prompts/                     🤖 AI prompts for Gemini
│   ├── hazard_detection_v3.md   ✅ Main hazard detection (with haptics + traffic lights)
│   ├── scene_understanding.md   ✅ Scene description feature
│   └── deep_analyze_traffic.md  ✅ Traffic light crossing analysis
├── demo_data/                   📊 Demo data and photos
│   ├── simulated_directions.json ✅ 20-step navigation route (template)
│   └── photos/                   📷 Demo photos (YOU NEED TO ADD THESE)
│       ├── trip_sequence/        🚶 20 sequential trip photos
│       ├── scene_understanding/  🏙️ 5-10 scene description examples
│       └── traffic_lights/       🚦 5-10 crosswalk examples
└── integration/                 🔌 Python integration scripts (TO BE BUILT)
```

---

## 🚀 Quick Start

### Step 1: Read the Master Plan
Open `MASTER_PLAN.md` for the complete technical specification, architecture, and implementation phases.

### Step 2: Understand the Prompts
Review the three AI prompts in `prompts/`:
1. **hazard_detection_v3.md** - Main hazard detection with new features:
   - Haptic recommendations (left/right/full/none)
   - Traffic light detection
   - Enhanced safety logic

2. **scene_understanding.md** - User asks "What's around me?"
   - Landmarks (Starbucks, CVS, etc.)
   - Street names
   - Orientation (cardinal directions)

3. **deep_analyze_traffic.md** - Safety-critical crosswalk analysis
   - Traffic light status (red/green/yellow)
   - Countdown timer reading
   - Adjusted safe crossing time (countdown - 7 seconds)
   - Clear GO/NO-GO instructions

### Step 3: Prepare Demo Data

#### A. Modify `simulated_directions.json`
The template has 20 navigation steps from "Starbucks, Main Street" to "Library, Oak Avenue". You can:
- Keep the template as-is
- OR modify to match your actual demo route
- Ensure step timing aligns with photo capture (every 5 seconds)

#### B. Capture Demo Photos
You need **THREE sets of photos**:

**1. Trip Sequence (20 photos)**
- Walk the route with phone at chest level
- Take photos every ~5 seconds (or every ~40 meters)
- Name files: `trip_photo_01.jpg` through `trip_photo_20.jpg`
- Include diverse scenarios:
  - Clear sidewalks (photos 1, 2, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 20)
  - Hazards (photos 3, 8, 11, 17): cones, people, vehicles, construction
  - Traffic lights (photos 5, 14): visible crosswalks with traffic signals

**2. Scene Understanding (5-10 photos)**
- Various environments:
  - Commercial street with shops
  - Residential area
  - Plaza or park
  - Transit station
- Name files: `scene_01.jpg`, `scene_02.jpg`, etc.
- Should have visible landmarks, street signs, or notable features

**3. Traffic Lights (5-10 photos)**
- Pedestrian crosswalks with traffic signals
- Include variety:
  - Green light with countdown timer
  - Red light with countdown timer
  - Green light without timer
  - Complex intersection
- Name files: `traffic_01.jpg`, `traffic_02.jpg`, etc.

Place photos in respective folders under `demo_data/photos/`.

---

## 🎨 Website (To Be Built)

The website will be a single-page design with:
- **Hero Section**: NavAid logo, tagline, visual demo
- **Features**: Key features (hazard detection, traffic lights, scene understanding)
- **About**: Mission, target users (RP, visual impairments)
- **Three Buttons**:
  - 📚 Documentation
  - 💻 GitHub Code
  - 🎬 Demo (video or link)

**Color Scheme**: NavAid Blue (#0061FF)

Files to be created:
- `website/index.html`
- `website/css/styles.css`
- `website/js/main.js`

---

## 📱 iOS App (To Be Built)

The Swift iOS app will be created in `/Users/prabhavsingh/Documents/CLASSES/Fall2025/NAVAID/NavAid/`

**App Structure**:
- Home Screen: Start Trip + Scene Understanding buttons
- In-Trip Screen: Repeat, Stop, Deep Analyze, Scene Understanding buttons
- Audio output: Coqui VITS TTS
- Haptic feedback: Visual indicators + CoreHaptics
- API integration: Gemini 2.5 Flash

---

## 🔌 Integration Layer (To Be Built)

Python scripts to connect the iOS app with AI backend:
- `integration/gemini_client.py` - Enhanced Gemini API client
- `integration/tts_engine.py` - Coqui VITS wrapper
- `integration/haptic_simulator.py` - Haptic pattern definitions
- `integration/demo_controller.py` - Demo orchestration

---

## ✅ Current Status

**Completed**:
- ✅ Master plan created
- ✅ Directory structure set up
- ✅ Three AI prompts written (v3.0, scene understanding, deep analyze)
- ✅ Simulated directions JSON template

**In Progress**:
- 🔄 Demo photo preparation (YOU)

**To Do**:
- ⏳ Swift iOS app development
- ⏳ Python integration layer
- ⏳ Website development
- ⏳ Full demo testing

---

## 📝 Next Steps

### For YOU (User):
1. **Read MASTER_PLAN.md** thoroughly
2. **Capture demo photos** (20 trip + 5-10 scene + 5-10 traffic)
3. **Review `simulated_directions.json`** and modify if needed
4. **Decide on demo approach**:
   - Option 1: Swift iOS app with XCode Simulator (recommended)
   - Option 2: Web-based iPhone emulator

### For US (Together):
1. Build Swift iOS app structure
2. Integrate Gemini API with new prompts
3. Implement TTS audio system
4. Create website with NavAid blue theme
5. Test full demo flow
6. Record walkthrough video

---

## 🎯 Demo Flow Summary

**Duration**: ~7 minutes

1. **App Introduction** (10s): TTS explains buttons
2. **Start Trip** (5s): Transition to in-trip screen
3. **Navigation Loop** (5min):
   - Every 30s: Google Maps instruction → Load photo → Gemini analysis → Audio + Haptics
   - Traffic light warnings trigger Deep Analyze
4. **Traffic Light Crossing** (30s): User tests Deep Analyze button
5. **Scene Understanding** (15s): User tests scene description
6. **Repeat Function** (5s): Replay last instruction
7. **Stop Trip** (3s): Return to home screen

---

## 🌟 Key Features to Demonstrate

1. ✅ **Hazard Detection**: Real-time obstacle warnings with haptics
2. ✅ **Traffic Light Safety**: Countdown analysis for safe crossing
3. ✅ **Scene Understanding**: "What's around me?" descriptions
4. ✅ **Audio Guidance**: Natural TTS with Coqui VITS
5. ✅ **Haptic Feedback**: Left/Right/Full patterns for spatial awareness
6. ✅ **Accessible UI**: Large buttons, clear layout, VoiceOver support

---

## 📞 Questions?

Refer to:
- `MASTER_PLAN.md` for detailed technical specs
- `prompts/` for AI behavior documentation
- `demo_data/simulated_directions.json` for navigation structure

---

**Remember**: This is assistive technology for blind users. Every detail matters for their safety. 🦯

*Built with care for people with visual impairments.*

