from openai import OpenAI
from app.config import settings as config
import os

if __name__ == "__main__":
    client = OpenAI(api_key=config.openai_api_key)

    audio_path = os.path.expanduser("~/Downloads/extracted_audio/Video by higherupwellness.mp3")
    audio_file= open(audio_path, "rb")

    # Step 1: Transcribe audio to text
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",  
        file=audio_file,
    )

    print("Transcript:")
    print(transcription.text)
    print("\n" + "="*50 + "\n")

    # Step 2: Summarize the transcript
    transcript_length = len(transcription.text.split())
    dynamic_max_tokens = min(750, max(200, transcript_length // 2))  # Increased upper bound for max_tokens
    print(f"Dynamic max_tokens set to: {dynamic_max_tokens}")
    summary = client.chat.completions.create(
        model="gpt-4o-mini",  # Using mini for cost efficiency
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes content for young adults interested in personal finance, entrepreneurship, and self-improvement. Create concise summaries. Follow Notion formatting guidelines."},
            {"role": "user", "content": f"Please summarize this transcript focusing on key takeaways:\n\n{transcription.text}"}
        ],
        max_tokens= dynamic_max_tokens,
        temperature=0.3
    )

    print("Summary:")
    print(summary.choices[0].message.content)

