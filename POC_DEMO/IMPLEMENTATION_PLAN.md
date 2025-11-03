# Implementation Plan - Combined Navigation + Hazard System

## Status: IN PROGRESS

### ✅ COMPLETED:
1. Created `navigation_guidance_schema.py` - Pydantic model for combined response
2. Created `navigation_guidance_prompt.md` - Gemini prompt for combined system
3. Created `NavigationGuidanceResponse` Swift model
4. Added `getNavigationGuidance()` to GeminiAPIService.swift
5. Verified 5 instructions in simulated_directions.json

### 🔄 TODO:

#### 1. Update TripViewModel.swift
**Remove:**
- `photoAnalysisTimer`
- `startPhotoAnalysisLoop()`
- `analyzeNextPhoto()`
- `handleHazardResponse()`

**Modify `playNextNavigationInstruction()`:**
```swift
private func playNextNavigationInstruction() {
    guard let directions = simulatedDirections,
          currentStepIndex < directions.instructions.count else {
        stopTrip()
        return
    }

    let instruction = directions.instructions[currentStepIndex]

    // Get corresponding photo
    guard let photoPath = photoLoader.getTripPhoto(index: currentStepIndex) else {
        // No photo - just speak navigation instruction
        speak(instruction.ttsText)
        currentStepIndex += 1
        return
    }

    // Call combined API
    Task { @MainActor in
        do {
            let response = try await geminiService.getNavigationGuidance(
                navigationInstruction: instruction.ttsText,
                imagePath: photoPath
            )

            // Handle traffic light detection
            if response.trafficLightDetected {
                if let trafficInfo = response.trafficLightInfo {
                    let message = "Traffic light crossing in \(trafficInfo.approximateDistanceMeters) meters. Use Deep Analyze when you reach it."
                    speak(message)
                    playHaptic(.trafficLight)
                    cachedInstruction.cache(mapsInstruction: nil, geminiInstruction: message)
                    currentStepIndex += 1
                    return
                }
            }

            // Speak hazard first (if detected)
            if response.hazardDetected && !response.hazardGuidance.isEmpty {
                speak(response.hazardGuidance) { [weak self] in
                    // After hazard audio finishes, play haptic and speak navigation
                    let haptic = self?.getHapticPattern(from: response.hapticRecommendation) ?? .none
                    self?.playHaptic(haptic)

                    // Small delay, then speak navigation instruction
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                        self?.speak(response.navigationInstruction) { [weak self] in
                            // After navigation audio finishes, wait 20 seconds
                            print("⏱️ Audio complete. Waiting 20 seconds...")
                            DispatchQueue.main.asyncAfter(deadline: .now() + 20) {
                                print("✅ 20-second delay complete")
                            }
                        }
                    }
                }

                // Cache both
                cachedInstruction.cache(
                    mapsInstruction: response.navigationInstruction,
                    geminiInstruction: response.hazardGuidance
                )
            } else {
                // No hazard - just speak navigation
                speak(response.navigationInstruction) { [weak self] in
                    // Wait 20 seconds after audio
                    DispatchQueue.main.asyncAfter(deadline: .now() + 20) {
                        print("✅ 20-second delay complete")
                    }
                }

                cachedInstruction.cache(mapsInstruction: response.navigationInstruction, geminiInstruction: nil)
            }

            currentStepIndex += 1

        } catch {
            print("❌ Navigation guidance error: \(error)")
            // Fallback - just speak original instruction
            speak(instruction.ttsText)
            currentStepIndex += 1
        }
    }
}
```

**Modify `startNavigationLoop()`:**
```swift
private func startNavigationLoop() {
    // Don't start photo timer - photos are now handled inline

    // Play first instruction immediately
    playNextNavigationInstruction()

    // Timer for subsequent instructions (wait longer since we have 20s delay)
    navigationTimer = Timer.scheduledTimer(withTimeInterval: 50, repeats: true) { [weak self] _ in
        self?.playNextNavigationInstruction()
    }
}
```

---

#### 2. Redesign HapticFeedbackView.swift

**New Siri-Style Glow Effect:**
```swift
import SwiftUI

struct HapticFeedbackView: View {
    let pattern: HapticPattern

    @State private var glowOpacity: Double = 0.0
    @State private var glowScale: CGFloat = 1.0

    var body: some View {
        ZStack {
            // Background blur
            Color.black.opacity(0.3)
                .edgesIgnoringSafeArea(.all)

            // Siri-style glow effect
            RoundedRectangle(cornerRadius: 40)
                .strokeBorder(
                    LinearGradient(
                        colors: glowColors(),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 8
                )
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .padding(20)
                .opacity(glowOpacity)
                .scaleEffect(glowScale)
                .blur(radius: 4)
                .shadow(color: glowColors().first?.opacity(0.6) ?? .clear, radius: 20)

            // Direction indicator text
            VStack {
                Spacer()

                Text(patternDescription())
                    .font(.system(size: 24, weight: .medium, design: .rounded))
                    .foregroundColor(.white)
                    .padding()
                    .background(
                        Capsule()
                            .fill(Color.black.opacity(0.7))
                    )
                    .opacity(glowOpacity)

                Spacer()
                    .frame(height: 100)
            }
        }
        .onAppear {
            startGlowAnimation()
        }
    }

    private func glowColors() -> [Color] {
        switch pattern {
        case .leftObstacle:
            return [Color.yellow, Color.orange]
        case .rightObstacle:
            return [Color.yellow, Color.orange]
        case .frontObstacle:
            return [Color.red, Color.orange]
        case .trafficLight, .doNotCross:
            return [Color.red, Color.pink]
        case .safeToCross:
            return [Color.green, Color.mint]
        case .navigationTurn:
            return [Color.blue, Color.cyan]
        case .none:
            return [Color.gray]
        }
    }

    private func patternDescription() -> String {
        switch pattern {
        case .leftObstacle:
            return "← Obstacle on Left"
        case .rightObstacle:
            return "Obstacle on Right →"
        case .frontObstacle:
            return "⚠️ Obstacle Ahead"
        case .trafficLight:
            return "🚦 Traffic Light"
        case .safeToCross:
            return "✅ Safe to Cross"
        case .doNotCross:
            return "🛑 Do Not Cross"
        case .navigationTurn:
            return "→ Turn"
        case .none:
            return ""
        }
    }

    private func startGlowAnimation() {
        // Pulse animation - stays visible longer
        withAnimation(.easeInOut(duration: 0.5)) {
            glowOpacity = 1.0
        }

        // Gentle scale pulse
        withAnimation(.easeInOut(duration: 1.5).repeatCount(getPulseCount(), autoreverses: true)) {
            glowScale = 1.05
        }

        // Fade out after duration
        let duration = getVisibilityDuration()
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            withAnimation(.easeOut(duration: 0.8)) {
                glowOpacity = 0.0
            }
        }
    }

    private func getVisibilityDuration() -> Double {
        switch pattern {
        case .leftObstacle, .rightObstacle:
            return 3.0  // 3 seconds - LONGER
        case .frontObstacle, .trafficLight, .doNotCross:
            return 4.0  // 4 seconds - LONGER
        case .safeToCross:
            return 2.5
        case .navigationTurn:
            return 2.0
        case .none:
            return 0
        }
    }

    private func getPulseCount() -> Int {
        switch pattern {
        case .leftObstacle, .rightObstacle:
            return 2
        case .frontObstacle, .trafficLight, .doNotCross:
            return 3
        case .safeToCross:
            return 2
        case .navigationTurn:
            return 1
        case .none:
            return 0
        }
    }
}
```

---

#### 3. Backend API Endpoint

**Create:** `/Users/prabhavsingh/Documents/CLASSES/Fall2025/NAVAID/POC_DEMO/integration/backend_server.py`

**Add new route:**
```python
@app.post("/api/navigation-guidance")
async def navigation_guidance(request: Request):
    data = await request.json()
    navigation_instruction = data["navigation_instruction"]
    image_path = data["image_path"]

    # Load navigation_guidance_prompt.md and navigation_guidance_schema.py
    # Call Gemini with combined prompt
    # Return NavigationGuidanceOutput JSON

    # (Implementation similar to /api/hazard-detection but with navigation instruction added to prompt)
```

---

### 🎯 EXPECTED FLOW:

```
Timer fires (every 50s)
  ↓
playNextNavigationInstruction()
  ↓
Get instruction #1: "Head straight 50m"
Get photo #1: trip_photo_01.png
  ↓
Call API: getNavigationGuidance(instruction, photo)
  ↓
Gemini analyzes BOTH
  ↓
Returns: {
  hazard_detected: true,
  hazard_guidance: "Pole on right, move left",
  navigation_instruction: "Head straight for 50 meters on the left side"
}
  ↓
IF hazard:
  1. Speak: "Pole on right, move left" [audio 3s]
  2. Play haptic + show BEAUTIFUL GLOW [3-4s]
  3. Speak: "Head straight for 50 meters on the left side" [audio 4s]
  4. Wait 20 seconds
  5. Timer fires → next instruction
ELSE:
  1. Speak: "Head straight for 50 meters on the left side"
  2. Wait 20 seconds
  3. Timer fires → next instruction
```

**NO MORE OVERLAPPING AUDIO!** ✅
