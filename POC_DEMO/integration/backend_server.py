#!/usr/bin/env python3
"""
backend_server.py - Python backend for NavAid iOS app

Provides REST API endpoints for:
1. Hazard detection (Gemini 2.5 Flash + v3 prompt)
2. Scene understanding (Gemini 2.5 + scene prompt)
3. Deep analyze traffic (Gemini 2.0 Flash + traffic prompt)
4. TTS audio generation (Coqui VITS)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from pathlib import Path
import io
import json
import uuid
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "MILESTONE1" / "GUIDANCE_METRICS"))

from gemini_api.gemini_client import GeminiHazardClient
from gemini_api.hazard_schema import HazardOutput
from gemini_api.navigation_guidance_schema import NavigationGuidanceOutput

# Google Maps API
try:
    import googlemaps
    gmaps_api_key = ""
    if gmaps_api_key:
        gmaps_client = googlemaps.Client(key=gmaps_api_key)
        print("✅ Google Maps API client initialized")
    else:
        print("⚠️  Warning: GOOGLE_API_KEY not set for Maps API")
        gmaps_client = None
except ImportError:
    print("⚠️  Warning: googlemaps library not installed. Install with: pip install googlemaps")
    gmaps_client = None
except Exception as e:
    print(f"⚠️  Warning: Google Maps API initialization failed: {e}")
    gmaps_client = None

app = Flask(__name__)
CORS(app)  # Enable CORS for iOS app

# Initialize Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not set!")
    sys.exit(1)

# Default Gemini client (for mobile app)
gemini_client = GeminiHazardClient(
    api_key=api_key,
    model_name="gemini-2.5-flash",
    temperature=0.2,
    top_p=0.8,
    rpm_limit=0  # No rate limiting for demo
)

def get_gemini_client(model_name="gemini-2.5-flash", temperature=0.2, top_p=0.8):
    """Create a Gemini client with specified model. Supports web demo model selection."""
    return GeminiHazardClient(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        top_p=top_p,
        rpm_limit=0
    )

# Initialize TTS (Coqui VITS default)
try:
    from TTS.api import TTS
    tts_model = TTS("tts_models/en/ljspeech/vits")
    print("✅ Coqui VITS (LJSpeech) loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Coqui TTS not available: {e}")
    tts_model = None

# TTS model mapping for web demo
TTS_MODEL_MAP = {
    "coqui_vits_ljspeech": "tts_models/en/ljspeech/vits",
    "coqui_vits_vctk": "tts_models/en/vctk/vits",
    "coqui_tacotron2": "tts_models/en/ljspeech/tacotron2-DDC",
    "espeak": "espeak"  # Special case, not a Coqui model
}

def get_tts_model(model_id="coqui_vits_ljspeech"):
    """Get TTS model instance. Supports web demo model selection."""
    if model_id == "espeak":
        # eSpeak not implemented in this backend, return default
        print(f"⚠️  eSpeak requested but not implemented, using default VITS")
        return tts_model, None

    model_path = TTS_MODEL_MAP.get(model_id, "tts_models/en/ljspeech/vits")

    # Return cached model if it's the default
    if model_id == "coqui_vits_ljspeech" and tts_model is not None:
        return tts_model, None

    # Check if this is VCTK (multi-speaker model)
    speaker_id = "p226" if model_id == "coqui_vits_vctk" else None

    # Otherwise load the requested model
    try:
        return TTS(model_path), speaker_id
    except Exception as e:
        print(f"⚠️  Failed to load {model_id}, using default: {e}")
        return tts_model, None

# Load prompts
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(filename):
    """Load prompt from file."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text()

hazard_prompt = load_prompt("hazard_detection_v3.md")
scene_prompt = load_prompt("scene_understanding.md")
traffic_prompt = load_prompt("deep_analyze_traffic.md")
navigation_guidance_prompt = load_prompt("navigation_guidance_v3.md")

print("✅ All prompts loaded")

# Simple uploads directory for web demo
UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# User profile paths (check multiple locations)
# 1. iOS app path
IOS_PROFILE_PATH = "/Users/prabhavsingh/Library/Containers/com.navaid.app/Data/Documents/user_profile.json"
# 2. Integration folder (for web demo)
INTEGRATION_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profile_template.json")

def load_user_profile():
    """Load user profile if exists, otherwise return placeholder."""

    # Search for iOS app profile in simulator OR container
    profile_path = None

    # Try container path first (real device)
    if os.path.exists(IOS_PROFILE_PATH):
        profile_path = IOS_PROFILE_PATH
        print(f"📱 Using iOS container profile")
    else:
        # Search simulator devices
        simulator_base = os.path.expanduser("~/Library/Developer/CoreSimulator/Devices")
        if os.path.exists(simulator_base):
            for root, dirs, files in os.walk(simulator_base):
                if 'user_profile.json' in files and '/Documents/' in root:
                    profile_path = os.path.join(root, 'user_profile.json')
                    print(f"📱 Found iOS simulator profile")
                    break

    # Fallback to integration template
    if not profile_path:
        profile_path = INTEGRATION_PROFILE_PATH
        print(f"📋 Using demo template")

    if profile_path and os.path.exists(profile_path):
        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)

            # Handle new nested format (user_profile key)
            if 'user_profile' in data:
                profile = data['user_profile']

                # Extract mobility aids
                mobility_aids = profile.get('mobility_aids', {})
                aids_list = []
                if mobility_aids.get('white_cane'): aids_list.append('white cane')
                if mobility_aids.get('walking_stick'): aids_list.append('walking stick')
                if mobility_aids.get('guide_dog'): aids_list.append('guide dog')
                if mobility_aids.get('other'): aids_list.append(mobility_aids['other'])

                # Format profile as markdown for prompt injection
                vision_condition = profile.get('vision_condition', {})
                profile_text = f"""
**User Profile:**
- **Vision Condition:** {vision_condition.get('type', 'N/A')} - {vision_condition.get('description', '')}
- **Field of View:** {vision_condition.get('field_of_view_degrees', 'N/A')}° (peripheral vision loss)
- **Mobility Aids:** {', '.join(aids_list) if aids_list else 'None'}
- **Notes:** {vision_condition.get('notes', '')}
- **Additional:** {profile.get('additional_notes', '')}
"""
            else:
                # Handle old flat format (iOS app)
                profile = data
                profile_text = f"""
- Name: {profile.get('name', 'N/A')}
- Age: {profile.get('age', 'N/A')}
- Vision Problems: {profile.get('visionProblems', 'N/A')}
- Assistive Devices: {profile.get('assistiveDevices', 'N/A')}
- Other Vision Defects: {profile.get('otherVisionDefects', 'N/A')}
- Primary Environments: {profile.get('primaryNavigationEnvironments', 'N/A')}
- Navigation Challenges: {profile.get('navigationChallenges', 'N/A')}
"""

            print(f"✅ User profile loaded from {os.path.basename(profile_path)}")
            return profile_text
        except Exception as e:
            print(f"⚠️  Failed to load user profile: {e}")
            import traceback
            traceback.print_exc()
            return "No user profile available."
    else:
        print("ℹ️  No user profile found (first-time user or not yet configured)")
        return "No user profile available."

def inject_user_profile(prompt, personalization_enabled=True):
    """
    Replace {USER_PROFILE_PLACEHOLDER} with actual profile data or empty string.
    Reloads profile on each call to pick up changes after survey completion.

    Args:
        prompt: The prompt template with placeholder
        personalization_enabled: If False, replaces with "No personalization enabled"
    """
    if personalization_enabled:
        # Reload profile on each call to pick up changes
        current_profile = load_user_profile()
        return prompt.replace("{USER_PROFILE_PLACEHOLDER}", current_profile)
    else:
        return prompt.replace("{USER_PROFILE_PLACEHOLDER}", "No personalization enabled. Use generic guidance for all users.")


# MARK: - API Endpoints

@app.route('/api/hazard-detection', methods=['POST'])
def hazard_detection():
    """
    Endpoint for hazard detection.

    Request: {"image_path": "/path/to/image.jpg", "personalization_enabled": true/false (optional)}
    Response: HazardResponse JSON (v3.0 with haptics + traffic lights)
    """
    try:
        data = request.json
        image_path = data.get('image_path')
        personalization_enabled = data.get('personalization_enabled', False)  # Default OFF

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🔍 Analyzing hazards: {os.path.basename(image_path)} (personalization: {personalization_enabled})")

        # Call Gemini API with user profile injected (or not)
        final_prompt = inject_user_profile(hazard_prompt, personalization_enabled)
        raw_dict, raw_text = gemini_client.analyze(Path(image_path), final_prompt)

        print(raw_dict)

        # Validate and normalize
        hazard_output = HazardOutput(**raw_dict).normalized()

        # Return as JSON
        return jsonify(hazard_output.model_dump())

    except Exception as e:
        print(f"❌ Hazard detection error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/scene-understanding', methods=['POST'])
def scene_understanding():
    """
    Endpoint for scene understanding.

    Request: {"image_path": "/path/to/image.jpg", "vision_model": "gemini-2.5-flash" (optional), "personalization_enabled": true/false (optional)}
    Response: SceneUnderstandingResponse JSON
    """
    try:
        data = request.json
        image_path = data.get('image_path')
        vision_model = data.get('vision_model', 'gemini-2.5-flash')  # Default for mobile app compatibility
        personalization_enabled = data.get('personalization_enabled', False)  # Default OFF

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🏙️  Analyzing scene: {os.path.basename(image_path)} with {vision_model} (personalization: {personalization_enabled})")

        # Use specified model (web demo) or default (mobile app)
        scene_client = get_gemini_client(model_name=vision_model, temperature=0.3, top_p=0.9)

        # Call Gemini API with user profile injected (or not)
        final_prompt = inject_user_profile(scene_prompt, personalization_enabled)
        raw_dict, raw_text = scene_client.analyze(Path(image_path), final_prompt)

        # Return as JSON (no validation model needed, raw JSON is fine)
        return jsonify(raw_dict)

    except Exception as e:
        print(f"❌ Scene understanding error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/deep-analyze-traffic', methods=['POST'])
def deep_analyze_traffic():
    """
    Endpoint for traffic light analysis.

    Request: {"image_path": "/path/to/image.jpg", "vision_model": "gemini-2.0-flash" (optional)}
    Response: DeepAnalyzeTrafficResponse JSON
    """
    try:
        data = request.json
        image_path = data.get('image_path')
        vision_model = data.get('vision_model', 'gemini-2.5-flash')  # Default for mobile app

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🚦 Analyzing traffic light: {os.path.basename(image_path)} with {vision_model}")

        # Use specified model (web demo) or default (mobile app)
        traffic_client = get_gemini_client(model_name=vision_model, temperature=0.1, top_p=0.8)

        # Call Gemini API with user profile injected
        final_prompt = inject_user_profile(traffic_prompt)
        raw_dict, raw_text = traffic_client.analyze(Path(image_path), final_prompt)

        # Return as JSON
        return jsonify(raw_dict)

    except Exception as e:
        print(f"❌ Traffic light analysis error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/navigation-guidance', methods=['POST'])
def navigation_guidance():
    """
    Endpoint for combined navigation + hazard guidance (v3.0).

    Request: {
        "navigation_instruction": "Head straight for 50 meters",
        "image_path": "/path/to/image.jpg",
        "vision_model": "gemini-2.5-flash" (optional),
        "personalization_enabled": true/false (optional)
    }
    Response: NavigationGuidanceResponse JSON
    """
    try:
        data = request.json
        navigation_instruction = data.get('navigation_instruction')
        image_path = data.get('image_path')
        vision_model = data.get('vision_model', 'gemini-2.5-flash')  # Default for mobile app
        personalization_enabled = data.get('personalization_enabled', False)  # Default OFF

        print(personalization_enabled)

        if not navigation_instruction:
            return jsonify({"error": "No navigation instruction provided"}), 400

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🗺️  Navigation guidance: {navigation_instruction[:50]}... + {os.path.basename(image_path)} with {vision_model} (personalization: {personalization_enabled})")

        # Build combined prompt with navigation instruction
        base_prompt_with_profile = inject_user_profile(navigation_guidance_prompt, personalization_enabled)
        combined_prompt = f"""
{base_prompt_with_profile}

---

## Current Navigation Instruction from Google Maps:
{navigation_instruction}

## Your Task:
Analyze the photo and provide combined guidance following the schema above.
"""

        # Use specified model (web demo) or default (mobile app)
        nav_client = get_gemini_client(model_name=vision_model, temperature=0.2, top_p=0.8)

        # Call Gemini API with combined prompt
        raw_dict, raw_text = nav_client.analyze(Path(image_path), combined_prompt)

        print(f"📤 Response: {raw_dict}")

        # Validate and normalize
        guidance_output = NavigationGuidanceOutput(**raw_dict).normalized()

        # Return as JSON
        return jsonify(guidance_output.model_dump())

    except Exception as e:
        print(f"❌ Navigation guidance error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """
    Endpoint for TTS audio generation.

    Request: {"text": "Hello world", "tts_model": "coqui_vits_ljspeech" (optional)}
    Response: WAV audio file (binary)
    """
    try:
        if tts_model is None:
            return jsonify({"error": "TTS model not available"}), 503

        data = request.json
        text = data.get('text')
        tts_model_id = data.get('tts_model', 'coqui_vits_ljspeech')  # Default for mobile app

        if not text:
            return jsonify({"error": "No text provided"}), 400

        print(f"🔊 Generating TTS with {tts_model_id}: {text[:50]}...")

        # Get the requested TTS model and speaker ID (if multi-speaker)
        selected_tts, speaker_id = get_tts_model(tts_model_id)

        if selected_tts is None:
            return jsonify({"error": "TTS model not available"}), 503

        # Generate audio (with speaker parameter for multi-speaker models)
        if speaker_id:
            print(f"  Using speaker: {speaker_id}")
            wav = selected_tts.tts(text=text, speaker=speaker_id)
        else:
            wav = selected_tts.tts(text=text)

        # Convert to WAV bytes
        import scipy.io.wavfile as wavfile
        import numpy as np

        audio_buffer = io.BytesIO()
        wavfile.write(audio_buffer, 22050, np.array(wav))
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype='audio/wav',
            as_attachment=False,
            download_name='tts.wav'
        )

    except Exception as e:
        print(f"❌ TTS error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """
    Accept an image file upload and return a local filesystem path for downstream endpoints.

    Response: {"image_path": "/absolute/path/to/saved.jpg"}
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided (field 'image')"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        # Sanitize and generate unique filename to avoid collisions
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_name = f"upload_{uuid.uuid4().hex}{ext or '.jpg'}"
        save_path = UPLOADS_DIR / unique_name

        file.save(save_path)
        abs_path = str(save_path.resolve())
        print(f"⬆️  Received upload: {filename} -> {abs_path}")

        return jsonify({"image_path": abs_path})

    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Endpoint for audio transcription using Whisper.

    Request: Multipart form with 'audio' file (WAV, M4A, MP3)
    Response: {"text": "transcribed text"}
    """
    try:
        # Check if audio file is in request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        print(f"🎤 Transcribing audio: {audio_file.filename}")

        # Save temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.filename)[1]) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Use OpenAI Whisper for transcription
            import whisper

            # Load Whisper model (base is good balance of speed/accuracy)
            whisper_model = whisper.load_model("base")

            # Transcribe
            result = whisper_model.transcribe(tmp_path)

            print(f"📝 Transcription: {result['text']}")

            return jsonify({"text": result['text'].strip()})

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-trip', methods=['POST'])
def generate_trip():
    """
    Generate trip JSON from Google Maps Directions API with caching.

    Request: {
        "origin": "Campus Center, Berkeley, CA",
        "destination": "Library, Berkeley, CA",
        "mode": "walking" (optional, default: walking),
        "alternatives": false (optional),
        "avoid": [] (optional, e.g., ["highways", "tolls", "ferries"]),
        "units": "metric" (optional, "metric" or "imperial"),
        "use_cache": true (optional, default: true)
    }
    Response: NavAid trip JSON format
    """
    try:
        if gmaps_client is None:
            return jsonify({"error": "Google Maps API not available"}), 503
        
        demo_mode = 'WEBSITE'

        data = request.json
        origin = data.get('origin')
        destination = data.get('destination')
        mode = data.get('mode', 'walking')  # walking, driving, bicycling, transit
        alternatives = data.get('alternatives', False)
        avoid = data.get('avoid', [])  # List of things to avoid
        units = data.get('units', 'metric')
        use_cache = data.get('use_cache', True)

        if not origin or not destination:
            return jsonify({"error": "Both origin and destination are required"}), 400

        # Generate cache key
        import hashlib
        cache_key = hashlib.md5(
            f"{origin}|{destination}|{mode}|{sorted(avoid)}|{units}".encode()
        ).hexdigest()
        cache_file = UPLOADS_DIR.parent / "cache" / "trips" / f"{cache_key}.json"

        # Check cache
        if use_cache and cache_file.exists():
            print(f"📦 Loading cached trip: {origin} → {destination}")
            with open(cache_file, 'r') as f:
                cached_trip = json.load(f)

            if demo_mode == 'IOS':
                # Convert to iOS format if it's in old nested format
                if "trip_metadata" in cached_trip:
                    meta = cached_trip["trip_metadata"]
                    ios_format = {
                        "origin": meta.get("origin", origin),
                        "destination": meta.get("destination", destination),
                        "distance_meters": meta.get("total_distance_meters", 0),
                        "duration_seconds": int(meta.get("estimated_duration_minutes", 0) * 60),
                        "num_steps": meta.get("num_steps", 0),
                        "steps": cached_trip.get("instructions", []),
                        "from_cache": True
                    }
                    return jsonify(ios_format)
                else:
                    # Already in iOS format
                    cached_trip["from_cache"] = True
                    return jsonify(cached_trip)
            else:
                cached_trip["from_cache"] = True
                return jsonify(cached_trip)

        print(f"🗺️  Generating trip: {origin} → {destination} ({mode}, avoid: {avoid})")

        # Prepare API parameters
        api_params = {
            'origin': origin,
            'destination': destination,
            'mode': mode,
            'alternatives': alternatives,
            'units': units
        }

        # Add avoid parameter if specified
        if avoid:
            api_params['avoid'] = '|'.join(avoid)

        # Call Google Maps Directions API
        directions_result = gmaps_client.directions(**api_params)

        if not directions_result or len(directions_result) == 0:
            return jsonify({"error": "No route found"}), 404

        # Use the first route
        route = directions_result[0]
        legs = route['legs'][0]  # Assuming single-leg trip (no waypoints)

        # Extract trip metadata
        total_distance = legs['distance']['value']  # meters
        total_duration = legs['duration']['value']  # seconds

        # Parse steps into NavAid format with more granularity
        instructions = []
        import re

        for i, step in enumerate(legs['steps'], start=1):
            # Extract maneuver type
            maneuver = step.get('maneuver', 'straight')

            # Clean HTML from instruction text
            instruction_text = re.sub('<[^<]+?>', '', step['html_instructions'])

            # Create TTS-friendly text with more detail
            tts_text = instruction_text
            distance_m = step['distance']['value']
            duration_s = step['duration']['value']

            # Add distance context
            if distance_m > 10:
                if distance_m >= 1000:
                    distance_str = f"{distance_m / 1000:.1f} kilometers"
                elif distance_m >= 100:
                    distance_str = f"{round(distance_m / 10) * 10} meters"  # Round to nearest 10m
                else:
                    distance_str = f"{distance_m} meters"
                tts_text = f"{instruction_text} for {distance_str}"

            # Add time estimate for longer segments
            if duration_s > 60:
                time_str = f"{round(duration_s / 60)} minute" + ("s" if duration_s >= 120 else "")
                tts_text = f"{tts_text} (about {time_str})"

            # Extract additional details from substeps if available
            substeps = []
            if 'steps' in step:
                for substep in step['steps']:
                    substep_text = re.sub('<[^<]+?>', '', substep.get('html_instructions', ''))
                    if substep_text and substep_text != instruction_text:
                        substeps.append(substep_text)

            instructions.append({
                "step_number": i,
                "instruction": instruction_text,
                "distance_meters": distance_m,
                "duration_seconds": duration_s,
                "maneuver": maneuver,
                "tts_text": tts_text,
                "substeps": substeps if substeps else None,
                "start_location": step.get('start_location'),
                "end_location": step.get('end_location')
            })

        # Add final destination step
        instructions.append({
            "step_number": len(instructions) + 1,
            "instruction": f"You have arrived at your destination",
            "distance_meters": 0,
            "duration_seconds": 0,
            "maneuver": "destination",
            "tts_text": f"You have arrived at {destination}"
        })

        # Build NavAid trip JSON
        from datetime import datetime
        # iOS app format (flat structure)
        trip_json = {
            "origin": origin,
            "destination": destination,
            "distance_meters": total_distance,
            "duration_seconds": total_duration,
            "num_steps": len(instructions),
            "steps": instructions,  # iOS expects "steps" not "instructions"
            "from_cache": False
        }

        # Also save full metadata version for web demo
        trip_json_full = {
            "trip_metadata": {
                "origin": origin,
                "destination": destination,
                "total_distance_meters": total_distance,
                "estimated_duration_minutes": round(total_duration / 60, 1),
                "num_steps": len(instructions),
                "mode": mode,
                "avoid": avoid,
                "units": units,
                "generated_at": datetime.now().isoformat(),
                "cache_key": cache_key
            },
            "instructions": instructions,
            "photo_timing": {
                "description": f"Photos needed for each step during the trip",
                "total_photos_needed": len(instructions),
                "photo_naming_convention": f"Upload {len(instructions)} photos corresponding to each navigation step"
            }
        }

        # Save to cache (use full format for web demo compatibility)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(trip_json_full, f, indent=2)
        print(f"💾 Cached trip to {cache_file.name}")

        print(f"✅ Generated trip with {len(instructions)} steps")
        return jsonify(trip_json)

    except Exception as e:
        print(f"❌ Trip generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/trip-history', methods=['GET'])
def trip_history():
    """
    Get list of recent cached trips.

    Response: [
        {
            "origin": "...",
            "destination": "...",
            "num_steps": 5,
            "distance_meters": 450,
            "generated_at": "2025-11-03T22:40:10",
            "cache_key": "abc123..."
        },
        ...
    ]
    """
    try:
        cache_dir = UPLOADS_DIR.parent / "cache" / "trips"
        if not cache_dir.exists():
            return jsonify([])

        trips = []
        for cache_file in sorted(cache_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                with open(cache_file, 'r') as f:
                    trip_data = json.load(f)
                    metadata = trip_data.get('trip_metadata', {})
                    trips.append({
                        "origin": metadata.get('origin'),
                        "destination": metadata.get('destination'),
                        "num_steps": metadata.get('num_steps'),
                        "distance_meters": metadata.get('total_distance_meters'),
                        "generated_at": metadata.get('generated_at'),
                        "cache_key": metadata.get('cache_key')
                    })
            except Exception as e:
                print(f"⚠️  Failed to load cache file {cache_file.name}: {e}")
                continue

        # Return most recent 10 trips
        return jsonify(trips[:10])

    except Exception as e:
        print(f"❌ Trip history error: {e}")
        return jsonify([])


@app.route('/api/generate-color-scheme', methods=['POST'])
def generate_color_scheme():
    """
    Generate personalized color scheme for user based on colorblindness description.

    Request: {"colorblind_description": "I have protanopia (red-green colorblindness)..."}
    Response: {
        "start_button": "#1E88E5",
        "pause_button": "#FFA726",
        "end_button": "#EF5350",
        "scene_button": "#66BB6A",
        "deep_analyze_button": "#66BB6A"
    }
    """
    try:
        data = request.json
        colorblind_desc = data.get('colorblind_description', 'No colorblindness')

        print(f"🎨 Generating color scheme for: {colorblind_desc[:50]}...")

        # Use Gemini 2.0 Flash Lite for color generation (direct API call)
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-2.5-flash")
        gcfg = genai.types.GenerationConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )

        prompt = f"""You are a color accessibility expert. Generate an optimal color scheme for a navigation app designed for blind and visually impaired users.

User's colorblind condition:
{colorblind_desc}

Generate 5 button colors (in hex format) that are:
1. Highly distinguishable from each other for this specific colorblind type
2. High contrast against white/light backgrounds
3. Safe and clear for the user's vision condition

Button purposes:
- start_button: Start navigation (should feel "go/action")
- pause_button: Pause trip (should feel "wait/caution")
- end_button: End trip (should feel "stop/terminate")
- scene_button: Scene understanding (should feel "explore/analyze")
- deep_analyze_button: Deep traffic analysis (SAME as scene_button - used in two places)

Return ONLY a JSON object with these exact keys and hex color values (e.g., #1E88E5):

{{
  "start_button": "#HEXCODE",
  "pause_button": "#HEXCODE",
  "end_button": "#HEXCODE",
  "scene_button": "#HEXCODE",
  "deep_analyze_button": "#HEXCODE"
}}

NO markdown, NO explanation, JUST the JSON object."""

        response = model.generate_content(prompt, generation_config=gcfg)
        raw_dict = json.loads(response.text)

        print(f"✅ Generated color scheme: {raw_dict}")
        return jsonify(raw_dict)

    except Exception as e:
        print(f"❌ Color scheme generation error: {e}")
        import traceback
        traceback.print_exc()
        # Return default fallback colors (purple theme)
        return jsonify({
            "start_button": "#8B5CF6",
            "pause_button": "#F59E0B",
            "end_button": "#EF4444",
            "scene_button": "#10B981",
            "deep_analyze_button": "#10B981"
        })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "gemini_available": True,
        "tts_available": tts_model is not None,
        "gmaps_available": gmaps_client is not None,
        "prompts_loaded": True
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("NavAid Backend Server Starting...")
    print("="*60)
    print(f"Gemini API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"Coqui TTS: {'✅ Available' if tts_model else '⚠️  Not available (will use iOS native)'}")
    print(f"Prompts: ✅ Loaded (hazard v3, scene, traffic)")
    print("="*60)
    print("\nServer running on http://localhost:8000")
    print("Press Ctrl+C to stop\n")

    app.run(host='0.0.0.0', port=8000, debug=True)
