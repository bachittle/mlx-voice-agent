import base64
import json
import os
import re
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
LLM_SERVER = 'http://localhost:8001'
DEFAULT_VOICE = 'morgan-freeman'
DEFAULT_TTS_MODEL = 'qwen3-tts'
DEFAULT_LLM_MODEL = 'qwen3-8b'

SYSTEM_PROMPT = "You are a helpful voice assistant. Keep responses short and conversational — one to three sentences max. No markdown, no lists, no formatting. Speak naturally."

# Conversation history per session
conversations = {}


def llm_generate(text, session_id):
    """Send text to local MLX LLM and get a response."""
    if session_id not in conversations:
        conversations[session_id] = []

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    messages.extend(conversations[session_id])
    messages.append({'role': 'user', 'content': text})

    payload = json.dumps({
        'model': DEFAULT_LLM_MODEL,
        'messages': messages,
        'max_tokens': 256,
        'temperature': 0.7,
    }).encode()
    req = urllib.request.Request(
        f'{LLM_SERVER}/v1/chat/completions',
        data=payload,
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    content = data['choices'][0]['message']['content']
    # Strip Qwen thinking tags
    content = re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL)
    content = content.strip()

    # Save to history
    conversations[session_id].append({'role': 'user', 'content': text})
    conversations[session_id].append({'role': 'assistant', 'content': content})

    return content


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    text = data.get('text', '')
    voice = data.get('voice', DEFAULT_VOICE)
    session_id = data.get('session_id', 'default')

    # LLM
    try:
        response_text = llm_generate(text, session_id)
    except Exception as e:
        app.logger.error(f'LLM failed: {e}')
        response_text = text  # fallback to parrot

    # Generate TTS
    try:
        payload = json.dumps({
            'model': DEFAULT_TTS_MODEL,
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


@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.get_json() or {}
    session_id = data.get('session_id', 'default')
    conversations.pop(session_id, None)
    return jsonify({'status': 'ok'})


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
