from openai import OpenAI

if __name__ == "__main__":
    client = OpenAI()
    audio_file= open("~/Downloads/extracted_audio/Video by productplaybook_.mp3", "rb")

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file
    )

    print(transcription.text)