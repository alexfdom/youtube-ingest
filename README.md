# YouTube Ingest

YouTube Ingest is a web application designed to convert videos from YouTube or other platforms into a text digest tailored for integration with any LLM.

The backend leverages the power of both the `youtube_transcript_api` and `yt_dlp` libraries to fetch video descriptions and transcripts seamlessly. On the frontend, the application is built using FastHTML, with dynamic HTML templates rendered via Jinja2, allowing session-specific content to be presented to users.

For videos where the transcript is not directly available on YouTube, we utilize `whisper` to extract the audio and subsequently obtain its transcription.

