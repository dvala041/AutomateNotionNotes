from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import Optional
import tempfile
import os
import shutil
from openai import OpenAI
from app.services.extractAudio import AudioExtractor
from app.config import settings as config

router = APIRouter()

class AudioExtractionRequest(BaseModel):
    url: HttpUrl
    audio_format: Optional[str] = "mp3"
    quality: Optional[str] = "best"

class AudioExtractionResponse(BaseModel):
    success: bool
    title: Optional[str] = None
    duration: Optional[float] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None

@router.post("/extract", response_model=AudioExtractionResponse)
async def extract_audio_from_url(request: AudioExtractionRequest):
    """
    Extract audio from a video URL, transcribe it, and provide a summary
    """
    # Create temporary directory for audio file
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract audio to temporary directory
        extractor = AudioExtractor(output_dir=temp_dir)
        result = extractor.extract_audio_from_url(
            url=str(request.url),
            audio_format=request.audio_format,
            quality=request.quality
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=config.openai_api_key)
        
        # Step 1: Transcribe audio to text
        with open(result['file_path'], "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",  
                file=audio_file,
            )
        
        # Step 2: Summarize the transcript
        transcript_length = len(transcription.text.split())
        # More generous token calculation: at least 300, up to 1000 tokens
        dynamic_max_tokens = min(1000, max(300, transcript_length))
        
        summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes content for a 20 year old male interested in personal finance, Computer Science, entrepreneurship, and self-improvement. Create concise summaries - no filler. Follow Notion formatting guidelines."},
                {"role": "user", "content": f"Please summarize this transcript focusing on key takeaways:\n\n{transcription.text}"}
            ],
            max_tokens=dynamic_max_tokens,
            temperature=0.3
        )
        
        return AudioExtractionResponse(
            success=True,
            title=result['title'],
            duration=result['duration'],
            transcript=transcription.text,
            summary=summary.choices[0].message.content
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

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
