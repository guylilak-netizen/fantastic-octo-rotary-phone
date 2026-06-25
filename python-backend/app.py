from typing import Optional, Dict
from pydantic import BaseModel
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from life import Life

app = FastAPI(title="Life Simulator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, Life] = {}

class CreateRequest(BaseModel):
    name: str = "Player"
    seed: Optional[int] = None

class CreateResponse(BaseModel):
    session_id: str
    state: dict

class ActionRequest(BaseModel):
    session_id: str
    choice: Optional[str] = None

class ActionResponse(BaseModel):
    state: dict
    event: str

@app.post("/create", response_model=CreateResponse)
def create(req: CreateRequest):
    session_id = str(uuid4())
    life = Life(name=req.name, seed=req.seed)
    sessions[session_id] = life
    return {"session_id": session_id, "state": life.to_dict()}

@app.post("/action", response_model=ActionResponse)
def action(req: ActionRequest):
    sid = req.session_id
    if sid not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    life = sessions[sid]
    if not life.alive:
        return {"state": life.to_dict(), "event": "Character is deceased."}
    event = life.tick_with_choice(req.choice)
    return {"state": life.to_dict(), "event": event}

@app.get("/status")
def status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id].to_dict()
