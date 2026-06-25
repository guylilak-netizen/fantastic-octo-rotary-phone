# Python backend for Life simulator

This small FastAPI backend wraps the existing life simulator logic so a frontend can create named characters and advance their life year-by-year.

Run (recommended in a virtualenv):

pip install -r requirements.txt
uvicorn app:app --reload --port 8000

Endpoints:
- POST /create {"name": "Alice", "seed": 42} -> {"session_id": "...", state: {...}}
- POST /action {"session_id": "...", "choice": "Work"} -> {state: {...}, event: "..."}
- GET /status?session_id=... -> {state: {...}}

This backend keeps sessions in memory for simplicity.
