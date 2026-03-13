from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, users, boards, members, tasks, companies, ai, analytics, comments
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KanbanFlow API",
    description="A Kanban-style project management application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(boards.router)
app.include_router(members.router)
app.include_router(tasks.router)
app.include_router(companies.router)
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(analytics.router, prefix="", tags=["Analytics"])
app.include_router(comments.router, prefix="", tags=["Comments"])

@app.get("/")
def read_root():
    return {"message": "KanbanFlow API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# WebSocket endpoint to handle any connection attempts
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Basic WebSocket endpoint to handle connection attempts.
    Currently not used for real-time features but prevents 403 errors.
    """
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for any message
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data}")
                
                # Echo back a simple response
                await websocket.send_text(f"Echo: {data}")
                
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1000)
