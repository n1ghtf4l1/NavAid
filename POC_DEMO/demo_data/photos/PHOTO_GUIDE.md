# NavAid Demo Photo Guide

This guide explains exactly what photos you need to capture for the demo.

---

## 📸 Overview

You need **THREE sets of photos**:
1. **Trip Sequence**: 20 photos showing a walking route
2. **Scene Understanding**: 5-10 photos of different environments
3. **Traffic Lights**: 5-10 photos of pedestrian crossings

---

## 1. Trip Sequence Photos (20 photos)

### Purpose
Simulate a blind user walking a route with the app analyzing the path every 5 seconds.

### Requirements
- **Total**: 20 photos
- **Timing**: Every 5 seconds (or every ~40 meters of walking)
- **Camera Position**: Chest level, forward-facing (user's perspective)
- **Route**: Follow the path in `simulated_directions.json` (or modify to match your route)

### File Naming
```
trip_photo_01.jpg
trip_photo_02.jpg
trip_photo_03.jpg
...
trip_photo_20.jpg
```

### Suggested Content

#### Clear Path Photos (14 photos)
Photos: 1, 2, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 20

**What to show**:
- Empty sidewalk ahead
- Clear walking path
- Normal urban/residential environment
- Trees, buildings, parked cars (off-path)
- No immediate hazards in walking lane

**Example descriptions**:
- "Straight sidewalk with trees on sides"
- "Clear path, buildings on left, parked cars on right (across curb)"
- "Residential street, no obstacles"

#### Hazard Photos (4 photos)

**Photo 3** - Traffic Cone
- Orange traffic cone partially blocking right side of sidewalk
- Should trigger: `bearing: "right"`, `haptic: "right_haptic"`

**Photo 8** - Person Crossing
- Pedestrian walking across the path ahead
- Should trigger: `bearing: "center"`, `hazard_types: ["person"]`, `haptic: "full_haptic"`

**Photo 11** - Parked Vehicle
- Car or van parked on sidewalk, encroaching on right side
- Should trigger: `bearing: "right"`, `hazard_types: ["vehicle"]`, `haptic: "right_haptic"`

**Photo 17** - Construction Barrier
- Construction barrier or fence on left side
- Should trigger: `bearing: "left"`, `hazard_types: ["barrier"]`, `haptic: "left_haptic"`

#### Traffic Light Photos (2 photos)

**Photo 5** - Traffic Light Ahead (First Crossing)
- Pedestrian crosswalk visible ahead (~15 meters)
- Traffic light pole/signal visible
- Should trigger: `traffic_light_detected: true`
- User will test Deep Analyze here

**Photo 14** - Traffic Light Ahead (Second Crossing)
- Another pedestrian crossing
- Different intersection
- Should trigger: `traffic_light_detected: true`

### Photography Tips
1. **Consistent Angle**: Keep phone at chest level (stomach height)
2. **Landscape Orientation**: Horizontal photos, not vertical
3. **Good Lighting**: Take photos during daytime, avoid direct sun glare
4. **Focus on Path**: Aim camera straight ahead, not down at ground
5. **Context Visible**: Show surrounding environment (buildings, trees, street)
6. **Natural Progression**: Photos should feel like a continuous walk

---

## 2. Scene Understanding Photos (5-10 photos)

### Purpose
Demonstrate the "What's around me?" feature that describes the user's surroundings.

### Requirements
- **Total**: 5-10 photos
- **Variety**: Different environment types
- **Landmarks**: Visible businesses, street signs, notable features

### File Naming
```
scene_01.jpg
scene_02.jpg
scene_03.jpg
...
scene_10.jpg
```

### Suggested Scenarios

**Scene 1: Commercial Street**
- Street with visible storefronts (Starbucks, CVS, restaurants, etc.)
- Business signs clearly readable
- Sidewalk with pedestrians
- Should show: landmarks, street name (if visible)

**Scene 2: Residential Street**
- Houses or apartment buildings
- Tree-lined street
- Quiet neighborhood
- Should show: no major landmarks, natural features

**Scene 3: Shopping Plaza**
- Large stores (Target, Walmart, etc.)
- Parking lot visible
- Multiple businesses
- Should show: major landmarks, shopping area context

**Scene 4: Park or Plaza**
- Open public space
- Trees, benches, grass
- Paths or walkways
- Should show: park features, orientation

**Scene 5: Transit Station**
- Bus stop or metro entrance
- Station signs visible
- Transit infrastructure
- Should show: transit landmarks, direction

**Optional Extras**:
- Intersection (multiple streets meeting)
- University campus
- Alley or narrow passage
- Mixed-use area (residential + commercial)

### Photography Tips
1. **Readable Signs**: Zoom in slightly to ensure business names/signs are clear
2. **Street Signs**: Include street name signs when possible
3. **Orientation Cues**: Show cardinal direction hints if available
4. **Context**: Capture enough of the scene to understand the environment type
5. **Landmarks First**: Prioritize recognizable businesses/features

---

## 3. Traffic Light Photos (5-10 photos)

### Purpose
Demonstrate the Deep Analyze feature for safe pedestrian crossing.

### Requirements
- **Total**: 5-10 photos
- **Variety**: Different signal states (red, green, countdown)
- **Visibility**: Traffic signal and pedestrian crossing must be clear

### File Naming
```
traffic_01.jpg
traffic_02.jpg
traffic_03.jpg
...
traffic_10.jpg
```

### Suggested Scenarios

**Traffic 1: Green Light with Countdown (Safe to Cross)**
- Pedestrian WALK signal (white walking person)
- Countdown timer visible showing 10+ seconds
- Crosswalk stripes visible
- Should return: `safe_to_cross: true`, adjusted time

**Traffic 2: Red Light with Countdown (Do Not Cross)**
- Pedestrian DON'T WALK signal (red hand)
- Countdown showing wait time (e.g., 45 seconds)
- Should return: `safe_to_cross: false`, wait time

**Traffic 3: Green Light, No Countdown**
- WALK signal visible
- No countdown timer shown
- Should return: `safe_to_cross: true`, caution warning

**Traffic 4: Red Light, No Countdown**
- DON'T WALK signal
- No timer visible
- Should return: `safe_to_cross: false`, generic "wait"

**Traffic 5: Flashing/Yellow (Low Countdown)**
- Flashing red hand OR countdown showing 3-5 seconds
- Should return: `safe_to_cross: false`, insufficient time

**Optional Extras**:
- Complex intersection (multiple signals)
- Wide crosswalk (6+ lanes)
- Narrow crosswalk (2 lanes)
- Obscured signal (trees, poor visibility)

### Photography Tips
1. **Signal Clarity**: Ensure the pedestrian signal is in focus and readable
2. **Countdown Visible**: If there's a countdown, make sure numbers are clear
3. **Crosswalk Context**: Show the crossing stripes/zebra pattern
4. **Distance**: Stand ~5-10 meters from the crossing (user approaching)
5. **Lighting**: Avoid backlit photos where signal is hard to see
6. **Pedestrian Signal, Not Vehicle**: Focus on the pedestrian WALK/DON'T WALK signal, not car traffic lights

---

## 📋 Quick Checklist

Before you're done, verify you have:

### Trip Sequence
- [ ] 20 photos total
- [ ] Photos numbered 01-20
- [ ] Chest-level perspective
- [ ] At least 4 hazard scenarios (cone, person, vehicle, barrier)
- [ ] 2 traffic light warnings (photos 5 and 14)
- [ ] Clear path photos for the rest

### Scene Understanding
- [ ] 5-10 photos total
- [ ] At least 3 different environment types (commercial, residential, transit, etc.)
- [ ] Visible landmarks or notable features in most photos
- [ ] Readable business signs when applicable

### Traffic Lights
- [ ] 5-10 photos total
- [ ] At least 1 green with countdown
- [ ] At least 1 red with countdown
- [ ] At least 1 green without countdown
- [ ] Clear pedestrian signals in all photos
- [ ] Crosswalk visible

---

## 🎬 Demo Coordination

When you run the demo:
1. **Trip photos** will load sequentially (01 → 20) every 5 seconds during the navigation
2. **Scene understanding photos** will be loaded when user presses the Scene Understanding button
3. **Traffic light photos** will be loaded when user presses Deep Analyze button

Make sure the photos tell a coherent story!

---

## 💡 Pro Tips

1. **Test Photos First**: Take a few test shots and send them to Gemini API to verify they work
2. **Consistent Lighting**: Try to capture all photos in similar lighting conditions
3. **HD Quality**: Use at least 1080p resolution (phone camera default)
4. **Landscape Mode**: Always horizontal orientation
5. **Real Scenarios**: Capture real street scenes, not staged setups
6. **Safety First**: Be careful when taking photos near traffic!

---

**Questions?** Review the prompts in `/POC_DEMO/prompts/` to understand what the AI looks for in each photo type.

**Good luck with your photo shoot! 📸**

