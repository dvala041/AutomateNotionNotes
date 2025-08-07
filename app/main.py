from fastapi import FastAPI
# from app.routers import notes, auth
# from app.config import settings

# Create FastAPI instance
app = FastAPI(
    title="Automate Notion Notes API",
    description="API for automating Notion note creation and management",
    version="1.0.0"
)

# Include routers
# app.include_router(notes.router, prefix="/api/v1/notes", tags=["notes"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {"message": "Welcome to Automate Notion Notes API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
