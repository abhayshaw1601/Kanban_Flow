from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, users, boards, members, tasks, companies, ai, analytics

app = FastAPI(
    title="KanbanFlow API",
    description="A Kanban-style project management application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
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

@app.get("/")
def read_root():
    return {"message": "KanbanFlow API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
