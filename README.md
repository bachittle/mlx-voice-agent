# MLX Voice Agent

A fully local voice AI assistant that runs on a MacBook. Phones connect to it over the local network as thin clients — no app install, just open a browser.

Built at the AI Agents Waterloo Voice Hackathon (Feb 2026).

## How It Works

Your MacBook runs everything — STT, LLM, and TTS. Phones and tablets connect via a web frontend and become voice interfaces. The MacBook does the thinking, the phone does the talking.

```
Phone (mic/speaker) → WiFi → MacBook (STT → LLM → TTS) → WiFi → Phone (playback)
```

- **Frontend:** Single HTML file. No build step, no frameworks. Opens on any phone browser.
- **Backend:** Python server running on the MacBook.
- **LLM:** Local models via MLX. No cloud, no API keys, no cost.
- **TTS:** Qwen voice cloning. Celebrity voices included — Morgan Freeman, Scarlett Johansson, David Attenborough, Snoop Dogg, Gordon Ramsay, and more. Swap on the fly.

## Quick Start

```bash
pip install flask flask-cors
python3 server.py
```

Open `http://localhost:5050` on your MacBook, or connect from any device on the same network.

## What It Can Do

- Answer questions using local LLMs
- Control smart home lights (Philips Hue)
- Respond in celebrity voices
- Run fully offline — no internet required after model downloads

## Origin

This app was built by a more capable voice agent — an agentic AI assistant that lives on a MacBook and does everything from writing code to controlling smart home devices to managing daily routines. That system built this one through voice commands. This project is the open source output.

Instead of sharing that more capable voice agent, I'm sharing this one. Bits and pieces of that agent will be open source over time, especially if I see there is any demand for it. 

## Built At

AI Agents Waterloo Voice Hackathon, Feb 2026 — Kitchener, ON
