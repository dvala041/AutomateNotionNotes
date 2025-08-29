from fastapi import APIRouter, HTTPException, status
from app.models.audio import AudioExtractionRequest, AudioExtractionResponse
import tempfile
import os
import shutil
import json
import re
from openai import OpenAI
from app.services.extractAudio import AudioExtractor
from app.services.notion import NotionService
from app.config import settings as config


def clean_markdown(text: str) -> str:
    """Remove markdown formatting from text"""
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic formatting  
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove horizontal lines
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


router = APIRouter()

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
        
        # Step 2: Summarize the transcript and extract metadata
        transcript_length = len(transcription.text.split())
        # More generous token calculation: at least 300, up to 1000 tokens
        dynamic_max_tokens = min(1000, max(300, transcript_length))
        
        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a helpful assistant that summarizes content from short form videos like reels.

CRITICAL: You must return ONLY a JSON object. Do NOT use any markdown formatting in the summary field.

Return a JSON object with this EXACT structure:
{
  "title": "A concise title",
  "category": "If fitness related categorize by body part. Otherwise categorize by topic.",
  "summary": "Plain text summary with proper line breaks. Use numbered lists and bullet points as shown below."
}


REQUIRED formatting (with line breaks):
1. First main point

• Sub-point under first point
• Another sub-point

2. Second main point

• Sub-point under second point
• Final sub-point

Each numbered item should be on its own line. Each bullet point should be on its own line. Use actual line breaks (\\n) between sections.

Focus on key takeaways and actionable insights. No filler content or sponsorship mentions."""},
                {"role": "user", "content": f"Please analyze and summarize this transcript:\n\n{transcription.text}"}
            ],
            max_tokens=dynamic_max_tokens,
            temperature=0.3
        )
        
        # Parse the JSON response
        try:
            summary_data = json.loads(summary_response.choices[0].message.content)
            # Clean any remaining markdown from the summary
            summary_data['summary'] = clean_markdown(summary_data['summary'])
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            summary_data = {
                "title": f"Summary: {result['title']}" if result.get('title') else "Video Summary",
                "category": "Other",
                "author": "Unknown",
                "summary": summary_response.choices[0].message.content
            }
        
        # Optional: Save to Notion if database_id is provided
        notion_page_id = None
        notion_page_url = None

        print("Config Notion Database ID:", config.notion_database_id)

        if request.notion_database_id or config.notion_database_id:
            print("Saving to Notion...")
            try:
                notion_service = NotionService()
                database_id = request.notion_database_id or config.notion_database_id
                
                # Get author information - use uploader from video info or fallback
                author = "Unknown"
                try:
                    video_info = extractor.get_video_info(str(request.url))
                    if video_info.get('success') and video_info.get('uploader'):
                        author = video_info['title'].split("Video by")[1].rstrip()
                except Exception as e:
                    print(f"Could not get video uploader info: {e}")
                
                page_title = summary_data['title']
                
                notion_result = notion_service.create_page_in_database(
                    database_id=database_id,
                    title=page_title,
                    category=summary_data['category'],
                    author=author,
                    summary=summary_data['summary'],
                    transcript=transcription.text,
                    video_url=str(request.url),
                    duration=result['duration'],
                    video_title=result['title']
                )
                
                print(f"Notion result: {notion_result}")
                
                if notion_result['success']:
                    notion_page_id = notion_result['page_id']
                    notion_page_url = notion_result['page_url']
                    print(f"Successfully created Notion page: {notion_page_url}")
                else:
                    print(f"Failed to create Notion page: {notion_result.get('error', 'Unknown error')}")
                    
            except Exception as notion_error:
                # Don't fail the whole request if Notion fails
                print(f"Failed to save to Notion: {str(notion_error)}")
                print(f"Notion error type: {type(notion_error)}")
                import traceback
                print(f"Notion error traceback: {traceback.format_exc()}")
                pass
        
        return AudioExtractionResponse(
            success=True,
            title=summary_data['title'],
            duration=result['duration'],
            transcript=transcription.text,
            summary=summary_data['summary'],
            notion_page_id=notion_page_id,
            notion_page_url=notion_page_url
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

@router.get("/notion/databases")
async def list_notion_databases():
    """
    List all Notion databases available to the integration
    """
    try:
        notion_service = NotionService()
        result = notion_service.list_databases()
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Notion databases: {str(e)}"
        )

@router.get("/notion/database/{database_id}/properties")
async def get_database_properties(database_id: str):
    """
    Get the properties schema of a specific Notion database
    """
    try:
        notion_service = NotionService()
        result = notion_service.get_database_properties(database_id)
        
        if result['success']:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database properties: {str(e)}"
        )
