# YouTube Ingest

YouTube Ingest is a web application designed to convert videos from YouTube or other platforms into a text digest tailored for integration with any LLM.

The backend leverages the power of both the [`youtube_transcript_api`](https://github.com/jdepoix/youtube-transcript-api/tree/master) and [`yt_dlp`](https://github.com/yt-dlp/yt-dlp) libraries to fetch video descriptions and transcripts seamlessly. On the frontend, the application is built using [FastHTML](https://github.com/AnswerDotAI/fasthtml), with dynamic HTML templates rendered via [Jinja2](https://github.com/pallets/jinja/), allowing session-specific content to be presented to users.

For videos where the transcript is not directly available on YouTube, we utilize [`whisper`](https://github.com/openai/whisper) to extract the audio and subsequently obtain its transcription.

## Railway Deployment

This branch enables deployment via Railway's cloud infrastructure.