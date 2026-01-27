import asyncio

from fastapi import FastAPI, HTTPException
from api.schemas import SessionRequest, SessionResponse
from api.session_service import create_session, get_session, list_sessions_for_user, replay_session
from api.streaming import router as streaming_router
from fastapi.middleware.cors import CORSMiddleware




# Global shutdown event for SSE cancellation
shutdown_event = asyncio.Event()
app = FastAPI(title="Reflecto API", version="1.0")


# --- In-memory event queue for demo ---
import threading
import queue
event_queues = {}

# POST /session/start: minimal session start endpoint for frontend
@app.post("/session/start")
async def start_session():
    # For demo, always use 'demo' as session_id
    session_id = 'demo'
    # Create a queue for this session if not exists
    if session_id not in event_queues:
        event_queues[session_id] = queue.Queue()
    # Immediately emit presence event
    event_queues[session_id].put({"event": "presence", "data": {"state": "AWAKE"}})
    return {"status": "started"}

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



# --- Custom SSE endpoint for demo ---
# --- Custom SSE endpoint for demo ---

# (Removed legacy /stream/{session_id} endpoint; use streaming router)

app.include_router(streaming_router)

# Register FastAPI shutdown handler to set shutdown_event
@app.on_event("shutdown")
async def on_shutdown():
    shutdown_event.set()

# POST /avatar/render: generate avatar image for user
from fastapi import Request
from reflecto.avatar import generator
from fastapi.responses import JSONResponse

@app.post("/avatar/render")
async def render_avatar(request: Request):
    # Accept any presence payload, always return stub
    try:
        _ = await request.json()
    except Exception:
        pass
    return JSONResponse(content={"status": "ok", "image_path": None})

# POST /session: run and persist session
@app.post("/session")
def post_session(req: SessionRequest):
    # user_id must be in req
    if not hasattr(req, 'user_id') or not req.user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    # input_data is the dict passed to run_session
    input_data = {
        "user_state": req.user_state,
        "history": req.history,
        "flow_context": req.flow_context,
        "raw_response": req.raw_response
    }
    result = create_session(req.user_id, input_data)
    return result

# GET /session/{id}: retrieve session by id
@app.get("/session/{session_id}")
def get_session_api(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# GET /sessions/{user_id}: list sessions for user
@app.get("/sessions/{user_id}")
def list_sessions_api(user_id: str):
    return list_sessions_for_user(user_id)


# Phase 12B: Session Replay (Audit Mode)
@app.get("/session/{session_id}/replay")
def replay_session_api(session_id: str):
    result = replay_session(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result
