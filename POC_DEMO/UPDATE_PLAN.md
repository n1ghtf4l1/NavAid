# NavAid App Updates - Session 2

## Changes Requested

### 1. Remove Auto-Repeat Instructions ✅
**Problem:** App reads welcome/start instructions repeatedly in a loop - annoying
**Fix:**
- Remove looping of start instructions
- Only read instructions ONCE when app opens
- Only read trip start instructions ONCE when trip begins
- Repeat button should only work when user presses it manually

**Files to modify:**
- `NAVAID-APP/NAVAID-APP/ViewModels/TripViewModel.swift`
  - Remove auto-repeat in `startTrip()` function
  - Keep manual repeat in `repeatLastInstruction()` function

---

### 2. Redesign Buttons - Pastel Colors & Rounded Style 🎨
**Problem:** Buttons look ugly - need modern, accessible design
**Requirements:**
- **Pastel colors** (soft, easy on eyes)
- **Rounded corners** (not sharp rectangles)
- **Button-like 3D appearance** (shadows, depth)
- **Different color for each button** (visual distinction)

**New Pastel Color Palette:**
```swift
// Pastel Colors
static let pastelBlue = Color(hex: "A8DAFF")      // Start Trip (soft blue)
static let pastelGreen = Color(hex: "B4E7CE")     // Scene Understanding (soft green)
static let pastelOrange = Color(hex: "FFD9A8")    // Repeat (soft orange)
static let pastelRed = Color(hex: "FFB3BA")       // Stop Trip (soft red)
static let pastelPurple = Color(hex: "D4C5F9")    // Deep Analyze (soft purple)
static let pastelYellow = Color(hex: "FFF4A8")    // Alternative
```

**Button Design:**
- Corner radius: 20-25px
- Shadow: soft drop shadow for depth
- Padding: generous internal padding
- Font: Keep large for accessibility (28pt)
- Text color: Dark text on pastel backgrounds for contrast

**Files to modify:**
- `NAVAID-APP/NAVAID-APP/Utilities/Constants.swift` - Add pastel colors
- `NAVAID-APP/NAVAID-APP/Views/Components/LargeButton.swift` - Redesign button style
- `NAVAID-APP/NAVAID-APP/Views/HomeView.swift` - Update button colors
- `NAVAID-APP/NAVAID-APP/Views/InTripView.swift` - Update button colors

---

### 3. Update Demo Data for 5-Step Demo 📸
**Current Photos Available:**
```
trip_sequence/
  - trip_photo_01.jpg
  - trip_photo_02.jpg
  - trip_photo_03.jpg
  - trip_photo_04.jpg
  - trip_photo_05.jpg

scene_understanding/
  - [1 scene photo]

traffic_lights/
  - [1 traffic light photo]
```

**Demo Flow:**
- 5 navigation steps (shortened from 20)
- 5 trip photos (1 per step)
- 1 traffic light test (manual button press)
- 1 scene understanding test (manual button press)

**Files to modify:**
- `NAVAID/POC_DEMO/demo_data/simulated_directions.json`
  - Reduce from 20 steps to 5 steps
  - Update trip metadata (distance, duration, num_steps)
  - Create realistic 5-step route matching photos

**New 5-Step Route:**
1. "Head north on Main Street for 50 meters"
2. "Turn right onto Elm Street"
3. "Continue on Elm Street for 60 meters"
4. "Approach the intersection. Traffic light ahead in 15 meters"
5. "You have arrived at your destination"

**Timings:**
- Navigation instruction interval: 30 seconds (unchanged)
- Photo analysis interval: 5 seconds (unchanged)
- Total trip duration: ~2.5 minutes (5 steps × 30s)

---

## Implementation Order

### Phase 1: Fix Instructions Loop
1. Open `TripViewModel.swift`
2. Modify `startTrip()` - remove welcome message loop
3. Ensure instructions only play once at start
4. Test: Start app → should hear welcome ONCE, not repeatedly

### Phase 2: Redesign Buttons
1. Update `Constants.swift` - add pastel colors
2. Update `LargeButton.swift`:
   - Add rounded corners (`.cornerRadius(20)`)
   - Add shadow (`.shadow(radius: 5)`)
   - Change text color to dark (`.foregroundColor(.black)`)
3. Update `HomeView.swift`:
   - Start Trip → pastelBlue
   - Scene Understanding → pastelGreen
4. Update `InTripView.swift`:
   - Repeat → pastelOrange
   - Stop Trip → pastelRed
   - Deep Analyze → pastelPurple
   - Scene Understanding → pastelGreen
5. Test: Visual appearance in simulator

### Phase 3: Update Demo Data
1. Edit `simulated_directions.json`
2. Reduce to 5 steps matching photo sequence
3. Update metadata (distance, duration)
4. Test: Run trip → should complete in ~2.5 minutes

---

## Testing Checklist

- [ ] App opens → Welcome message plays ONCE only
- [ ] Start Trip → Trip start message plays ONCE only
- [ ] No looping/repeating unless user presses Repeat button
- [ ] All buttons have pastel colors
- [ ] All buttons have rounded corners
- [ ] Buttons look 3D with shadows
- [ ] Text readable on pastel backgrounds
- [ ] Trip completes after 5 steps (~2.5 min)
- [ ] Deep Analyze button works with traffic light photo
- [ ] Scene Understanding button works with scene photo

---

## Notes

- Keep accessibility features (large text, VoiceOver)
- Keep haptic feedback on all buttons
- Keep all existing functionality (Gemini API, TTS, haptics)
- Only changing: UI appearance + demo length + no auto-repeat

---

## Next Session Start Command

When ready to implement, run:
1. Open XCode with NAVAID-APP project
2. Start backend: `cd /Users/prabhavsingh/Documents/CLASSES/Fall2025/NAVAID/POC_DEMO/integration && KMP_DUPLICATE_LIB_OK=TRUE python backend_server.py`
3. Make code changes per this plan
4. Build and test in simulator
