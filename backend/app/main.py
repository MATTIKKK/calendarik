from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, calendar
from app.core.config import settings

app = FastAPI(
    title="Calendarik API",
    description="Backend API for Calendarik application",
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
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 