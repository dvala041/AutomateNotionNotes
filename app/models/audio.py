from pydantic import BaseModel, HttpUrl
from typing import Optional

class AudioExtractionRequest(BaseModel):
    url: HttpUrl
    audio_format: Optional[str] = "mp3"
    quality: Optional[str] = "best"
    notion_database_id: Optional[str] = None  # Optional: specific database ID
    notion_page_title: Optional[str] = None   # Optional: custom title for the page

class AudioExtractionResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    duration: Optional[float] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    notion_page_id: Optional[str] = None
    notion_page_url: Optional[str] = None
    error: Optional[str] = None