from fasthtml.common import fast_app, serve
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from starlette.responses import HTMLResponse
from starlette.requests import Request
import os
from audio_transcript import audio_transcript
from ytb_utils import extract_video_id, get_description
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

app, rt = fast_app()

@rt('/', methods=['GET', 'POST'])
async def index(request: Request):
    transcript_html = ""
    error_message = ""
    description_content = ""
    html_content = ""
    
    if request.method == 'POST':
        form = await request.form()
        video_url = form.get('video_url')
        include_description = form.get('include_description') == 'on'
        video_id = extract_video_id(video_url)
        transcript = None
        transcript_html = None
        description_content = ""
        html_content = ""

        if not video_id:
            try:
                
                description_content = get_description(video_url)
                transcript_html = audio_transcript(video_url)
            except Exception:
                error_message = "Invalid YouTube URL."
        else:
            try:
                if include_description:
                    description_content = get_description(video_url)

                try:
                    if not transcript:
                        description_content = get_description(video_url)
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'fr', 'es', 'it'])
                    else:
                        description_content = get_description(video_url)

                        transcript = audio_transcript(video_url)
        
                    if not transcript_html:
                        transcript_by_30s = {}
                        for item in transcript:
                            interval = int(item["start"] // 30)
                            transcript_by_30s.setdefault(interval, []).append(item["text"])
                        
                        # Build HTML with each 30-second interval labeled by its time range
                        transcript_html = ""
                        for interval in sorted(transcript_by_30s.keys()):
                            start = interval * 30
                            end = start + 30
                            
                            start_min, start_sec = divmod(start, 60)
                            end_min, end_sec = divmod(end, 60)
                            time_label = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"
                            
                            # Combine the transcript text for this interval
                            interval_text = " ".join(transcript_by_30s[interval])
                            transcript_html += f"<strong>{time_label}:</strong> {interval_text}<br>"

                except VideoUnavailable:
                    error_message = "The video is unavailable."
                except TranscriptsDisabled:
                    error_message = "Transcripts are disabled for this video."
                except NoTranscriptFound:
                    error_message = "No transcript found for this video."
                except Exception as e:
                    error_message = f"An error occurred: {e}"
            except Exception as e:
                error_message = f"An error occurred: {e}"

    template = env.get_template('template.html')
    html_content = template.render(
        error_message=error_message,
        transcript_html=transcript_html,
        description_content=description_content
    )

    return HTMLResponse(html_content)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    serve(port=port)

# Local development
# http://127.0.0.1:5001 
