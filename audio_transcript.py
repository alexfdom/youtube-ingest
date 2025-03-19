import yt_dlp
import os
import whisper


def audio_transcript(video_url):
    transcript_text = ""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'video_audio.%(ext)s',
        # 'ffmpeg_location': '/usr/local/bin/ffmpeg',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Download audio using yt-dlp
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("Audio downloaded successfully!")
    except Exception as e:
        print(f"An error occurred while downloading audio: {e}")

    # Use the downloaded audio file for transcription
    audio_file = "video_audio.mp3"
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        transcript_text = result["text"]
        print("Transcript:")
        print(transcript_text)
    except Exception as e:
        print(f"An error occurred during transcription: {e}")

    # Clean up the audio file
    if os.path.exists(audio_file):
        os.remove(audio_file)
    return transcript_text


