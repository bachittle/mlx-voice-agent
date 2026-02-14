import base64
import json
import os
import urllib.request
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

TTS_SERVER = 'http://localhost:8000'
DEFAULT_VOICE = 'morgan-freeman'
DEFAULT_MODEL = 'qwen3-tts'


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    text = data.get('text', '')
    voice = data.get('voice', DEFAULT_VOICE)
    # Parrot: echo back for now, swap in LLM later
    response_text = text

    # Generate TTS
    try:
        payload = json.dumps({
            'model': DEFAULT_MODEL,
            'voice': voice,
            'input': response_text,
            'response_format': 'wav',
        }).encode()
        req = urllib.request.Request(
            f'{TTS_SERVER}/v1/audio/speech',
            data=payload,
            headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            wav = resp.read()
        audio_b64 = base64.b64encode(wav).decode('ascii')
        return jsonify({'response': response_text, 'audio': audio_b64})
    except Exception as e:
        app.logger.error(f'TTS failed: {e}')
        return jsonify({'response': response_text, 'audio': None, 'error': str(e)})


@app.route('/api/voices', methods=['GET'])
def voices():
    try:
        req = urllib.request.Request(f'{TTS_SERVER}/v1/voices')
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        return jsonify(data)
    except Exception as e:
        return jsonify({'voices': []}), 502


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
