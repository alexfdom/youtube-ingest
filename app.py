from fasthtml.common import fast_app, serve
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    RequestBlocked,
    AgeRestricted,
    VideoUnplayable,
)
from starlette.responses import HTMLResponse
from starlette.requests import Request
from audio_transcript import audio_transcript
from ytb_utils import extract_video_id, get_description
from jinja2 import Environment, FileSystemLoader
import os

env = Environment(loader=FileSystemLoader("templates"))

app, rt = fast_app()


def fetch_preferred_transcript(video_id: str, languages=("en", "fr", "es", "it")):
    api = YouTubeTranscriptApi()
    try:
        transcript_list = api.list(video_id)
        transcript = transcript_list.find_transcript(list(languages))
        return transcript.fetch()
    except (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
        RequestBlocked,
        AgeRestricted,
        VideoUnplayable,
    ):
        raise
    except Exception as exc:
        raise RuntimeError(f"Transcript fetch failed: {exc}") from exc


def get_video_transcript(video_id, preferred_languages=None):
    """Return a FetchedTranscript (library v1.1.0) or None if not available."""
    api = YouTubeTranscriptApi()
    try:
        languages = preferred_languages or ["en"]
        transcript_list = api.list(video_id)
        transcript = transcript_list.find_transcript(languages)
        fetched = transcript.fetch()
    except NoTranscriptFound:
        return f"No transcripts found for languages {preferred_languages or ['en']}."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except VideoUnavailable:
        return "Video is unavailable or unplayable."
    except AgeRestricted:
        return "Transcript cannot be retrieved (video is age-restricted)."
    except RequestBlocked:
        return "Transcript request was blocked by YouTube (IP may be rate-limited or banned)."
    except VideoUnplayable as e:
        return f"Video cannot be played or transcribed: {e}"
    except Exception as e:
        return f"An error occurred while fetching transcript: {e}"
    return fetched


def build_transcript_html(fetched):
    """Bucket transcript snippets into 30‑second intervals and return HTML."""
    transcript_by_30s = {}
    for snippet in fetched:
        interval = int(snippet.start // 30)
        transcript_by_30s.setdefault(interval, []).append(snippet.text)

    html_parts = []
    for interval in sorted(transcript_by_30s.keys()):
        start = interval * 30
        end = start + 30
        start_min, start_sec = divmod(start, 60)
        end_min, end_sec = divmod(end, 60)
        time_label = f"{start_min:02d}:{start_sec:02d} – {end_min:02d}:{end_sec:02d}"
        interval_text = " ".join(transcript_by_30s[interval])
        html_parts.append(f"<strong>{time_label}:</strong> {interval_text}")

    return "<br>".join(html_parts)


@rt("/", methods=["GET", "POST"])
async def index(request: Request):
    transcript_html = ""
    error_message = ""
    description_content = ""
    html_content = ""

    if request.method == "POST":
        form = await request.form()
        video_url = form.get("video_url")
        # include_description = form.get('include_description') == 'on'
        video_id = extract_video_id(video_url)

        try:
            description_content = get_description(video_url)
        except Exception:
            description_content = "No description available."

        if not video_id:
            try:
                description_content = get_description(video_url)
                transcript_html = audio_transcript(video_url)

            except Exception:
                error_message = "Invalid YouTube URL."
        else:
            fetched = fetch_preferred_transcript(video_id)
            transcript_html = build_transcript_html(fetched)

    template = env.get_template("template.html")
    html_content = template.render(
        error_message=error_message,
        transcript_html=transcript_html,
        description_content=description_content,
    )

    return HTMLResponse(html_content)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    serve(port=port)

# Local development
# http://127.0.0.1:5001
