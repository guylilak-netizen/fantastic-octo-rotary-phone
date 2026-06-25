# Kotlin frontend (Compose Desktop)

This folder contains a Compose Desktop app that talks to the Python FastAPI backend.

Usage (requires Gradle installed):

1. Start the backend:
   cd python-backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8000

2. Run the Kotlin app from the kotlin-frontend directory:
   ./gradlew run

The UI uses a retro 2015-ish aesthetic: monospace font, green-on-dark theme, and scanline overlay.
