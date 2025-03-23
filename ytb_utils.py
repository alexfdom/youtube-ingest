from yt_dlp import YoutubeDL


def extract_video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=")[-1]
    return None


def get_description(url):
    options = {
        "quiet": True,
        "skip_download": True,
    }

    with YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get("description", "No description found.")
        except Exception as e:
            raise e


# --- test --- #
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    if "v=" in url:
        video_id = url.split("v=")[-1]
    print(video_id)

    url = "https://www.youtube.com/shorts/ecBizx0OmdA"
    description = get_description(url)
    print(description)
