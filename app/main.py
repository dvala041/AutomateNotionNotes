from fastapi import FastAPI
from app.routers import audio


# Create FastAPI instance
app = FastAPI(
    title="Automate Notion Notes API",
    description="API for automating Notion note creation and management",
    version="1.0.0"
)

# Include routers
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
# app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
# app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {"message": "Welcome to Automate Notion Notes API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
