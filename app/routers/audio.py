from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import Optional
import tempfile
import os
from app.services.extractAudio import AudioExtractor

router = APIRouter()

class AudioExtractionRequest(BaseModel):
    url: HttpUrl
    audio_format: Optional[str] = "mp3"
    quality: Optional[str] = "best"

class AudioExtractionResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    duration: Optional[float] = None
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None

@router.post("/extract", response_model=AudioExtractionResponse)
async def extract_audio_from_url(request: AudioExtractionRequest):
    """
    Extract audio from a video URL (Instagram Reel, YouTube, TikTok, etc.)
    """
    try:
        extractor = AudioExtractor()
        result = extractor.extract_audio_from_url(
            url=str(request.url),
            audio_format=request.audio_format,
            quality=request.quality
        )
        
        if result['success']:
            return AudioExtractionResponse(
                success=True,
                title=result['title'],
                duration=result['duration'],
                file_path=result['file_path'],
                download_url=f"/api/v1/audio/download/{os.path.basename(result['file_path'])}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio extraction failed: {str(e)}"
        )

@router.get("/info")
async def get_video_info(url: str):
    """
    Get video information without downloading
    """
    try:
        extractor = AudioExtractor()
        result = extractor.get_video_info(url)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get video info: {str(e)}"
        )
