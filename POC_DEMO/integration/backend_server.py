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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "MILESTONE1" / "GUIDANCE_METRICS"))

from gemini_api.gemini_client import GeminiHazardClient
from gemini_api.hazard_schema import HazardOutput

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

print("✅ All prompts loaded")


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

        # Call Gemini API
        raw_dict, raw_text = gemini_client.analyze(Path(image_path), hazard_prompt)

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

        # Call Gemini API
        raw_dict, raw_text = scene_client.analyze(Path(image_path), scene_prompt)

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

        # Call Gemini API
        raw_dict, raw_text = traffic_client.analyze(Path(image_path), traffic_prompt)

        # Return as JSON
        return jsonify(raw_dict)

    except Exception as e:
        print(f"❌ Traffic light analysis error: {e}")
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
