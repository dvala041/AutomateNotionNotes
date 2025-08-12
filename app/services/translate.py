from openai import OpenAI
from app.config import settings as config
import os

if __name__ == "__main__":
    client = OpenAI(api_key=config.openai_api_key)

    audio_path = os.path.expanduser("~/Downloads/extracted_audio/Video by calltoleap.mp3")
    audio_file= open(audio_path, "rb")

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",  
        file=audio_file,
        # stream=True  # May prove helpful for showing real-time transcription updates
    )

    print(transcription.text)