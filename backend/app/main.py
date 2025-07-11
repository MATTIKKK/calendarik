from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, calendar, chat, ai, user, speech
from app.core.config import settings

app = FastAPI(
    title="NeChaos API",
    description="Backend API for NeChaos application",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",  
    "https://nechaos.netlify.app"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 