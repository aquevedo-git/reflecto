import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from api.schemas import SessionRequest, SessionResponse
from application.services.session_service import create_session, get_session, list_sessions_for_user, replay_session, verify_event_chain
from api.routes.streaming import router as streaming_router
from fastapi.middleware.cors import CORSMiddleware

from api.routes.write import router as write_router
from api.routes import daily



# Global shutdown event for SSE cancellation
shutdown_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    shutdown_event.set()


app = FastAPI(title="Reflecto API", version="1.0", lifespan=lifespan)



app.include_router(daily.router)

app.include_router(write_router)

# Register session_action router
from api.routes.session_action import router as session_action_router
app.include_router(session_action_router)

# Import and include the new session_start router
from api.routes.session_start import router as session_start_router
app.include_router(session_start_router)

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

# POST /avatar/render: generate avatar image for user
from fastapi import Request
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

# Phase 12C: Event Chain Verification (Audit Mode)
@app.get("/session/{session_id}/verify")
def verify_session_events(session_id: str):
    return verify_event_chain(session_id)
