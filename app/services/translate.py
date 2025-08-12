from openai import OpenAI

if __name__ == "__main__":
    client = OpenAI()
    audio_file= open("~/Downloads/extracted_audio/Video by productplaybook_.mp3", "rb")

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file,
        prompt="I am a 20 year old interested in personal finance, entrepreneurship, and self-improvement. I want to learn more about these topics. Please summarize the audio content in a way that is engaging and informative for someone with my interests."
    )

    print(transcription.text)