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

app = Flask(__name__)
CORS(app)  # Enable CORS for iOS app

# Initialize Gemini client
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not set!")
    sys.exit(1)

gemini_client = GeminiHazardClient(
    api_key=api_key,
    model_name="gemini-2.5-flash",
    temperature=0.2,
    top_p=0.8,
    rpm_limit=0  # No rate limiting for demo
)

# Initialize TTS (Coqui VITS)
try:
    from TTS.api import TTS
    tts_model = TTS("tts_models/en/ljspeech/vits")
    print("✅ Coqui VITS loaded successfully")
except Exception as e:
    print(f"⚠️  Warning: Coqui TTS not available: {e}")
    tts_model = None

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

# User profile path (iOS app saves to Documents directory)
# For demo, we'll check if profile exists and load it
USER_PROFILE_PATH = "/Users/prabhavsingh/Library/Containers/com.navaid.app/Data/Documents/user_profile.json"

def load_user_profile():
    """Load user profile if exists, otherwise return placeholder."""
    if os.path.exists(USER_PROFILE_PATH):
        try:
            with open(USER_PROFILE_PATH, 'r') as f:
                profile = json.load(f)

            # Format profile as markdown for prompt injection
            profile_text = f"""
- Name: {profile.get('name', 'N/A')}
- Age: {profile.get('age', 'N/A')}
- Vision Problems: {profile.get('visionProblems', 'N/A')}
- Assistive Devices: {profile.get('assistiveDevices', 'N/A')}
- Other Vision Defects: {profile.get('otherVisionDefects', 'N/A')}
- Primary Environments: {profile.get('primaryNavigationEnvironments', 'N/A')}
- Navigation Challenges: {profile.get('navigationChallenges', 'N/A')}
"""
            print("✅ User profile loaded")
            return profile_text
        except Exception as e:
            print(f"⚠️  Failed to load user profile: {e}")
            return "No user profile available."
    else:
        print("ℹ️  No user profile found (first-time user or not yet configured)")
        return "No user profile available."

# Load user profile once at startup
user_profile_text = load_user_profile()

def inject_user_profile(prompt):
    """Replace {USER_PROFILE_PLACEHOLDER} with actual profile data."""
    return prompt.replace("{USER_PROFILE_PLACEHOLDER}", user_profile_text)


# MARK: - API Endpoints

@app.route('/api/hazard-detection', methods=['POST'])
def hazard_detection():
    """
    Endpoint for hazard detection.

    Request: {"image_path": "/path/to/image.jpg"}
    Response: HazardResponse JSON (v3.0 with haptics + traffic lights)
    """
    try:
        data = request.json
        image_path = data.get('image_path')

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🔍 Analyzing hazards: {os.path.basename(image_path)}")

        # Call Gemini API with user profile injected
        final_prompt = inject_user_profile(hazard_prompt)
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

    Request: {"image_path": "/path/to/image.jpg"}
    Response: SceneUnderstandingResponse JSON
    """
    try:
        data = request.json
        image_path = data.get('image_path')

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🏙️  Analyzing scene: {os.path.basename(image_path)}")

        # Use Gemini 2.5 (more capable) for scene understanding
        scene_client = GeminiHazardClient(
            api_key=api_key,
            model_name="gemini-2.5-flash",
            temperature=0.3,
            top_p=0.9,
            rpm_limit=0
        )

        # Call Gemini API with user profile injected
        final_prompt = inject_user_profile(scene_prompt)
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

    Request: {"image_path": "/path/to/image.jpg"}
    Response: DeepAnalyzeTrafficResponse JSON
    """
    try:
        data = request.json
        image_path = data.get('image_path')

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🚦 Analyzing traffic light: {os.path.basename(image_path)}")

        # Use Gemini 2.0 Flash (fast for time-critical)
        traffic_client = GeminiHazardClient(
            api_key=api_key,
            model_name="gemini-2.0-flash",
            temperature=0.1,
            top_p=0.8,
            rpm_limit=0
        )

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
        "image_path": "/path/to/image.jpg"
    }
    Response: NavigationGuidanceResponse JSON
    """
    try:
        data = request.json
        navigation_instruction = data.get('navigation_instruction')
        image_path = data.get('image_path')

        if not navigation_instruction:
            return jsonify({"error": "No navigation instruction provided"}), 400

        if not image_path or not os.path.exists(image_path):
            return jsonify({"error": "Invalid image path"}), 400

        print(f"🗺️  Navigation guidance: {navigation_instruction[:50]}... + {os.path.basename(image_path)}")

        # Build combined prompt with navigation instruction
        base_prompt_with_profile = inject_user_profile(navigation_guidance_prompt)
        combined_prompt = f"""
{base_prompt_with_profile}

---

## Current Navigation Instruction from Google Maps:
{navigation_instruction}

## Your Task:
Analyze the photo and provide combined guidance following the schema above.
"""

        # Call Gemini API with combined prompt
        raw_dict, raw_text = gemini_client.analyze(Path(image_path), combined_prompt)

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

    Request: {"text": "Hello world"}
    Response: WAV audio file (binary)
    """
    try:
        if tts_model is None:
            return jsonify({"error": "TTS model not available"}), 503

        data = request.json
        text = data.get('text')

        if not text:
            return jsonify({"error": "No text provided"}), 400

        print(f"🔊 Generating TTS: {text[:50]}...")

        # Generate audio
        wav = tts_model.tts(text)

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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "gemini_available": True,
        "tts_available": tts_model is not None,
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
