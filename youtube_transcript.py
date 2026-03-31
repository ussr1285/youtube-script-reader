import os
import json
import time
import glob
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import IpBlocked

load_dotenv()

URL_FILE = os.getenv("URL_FILE", "ycombinaotr-영상들.txt")
LANGUAGES = os.getenv("LANGUAGES", "ko,en").split(",")
DELAY = float(os.getenv("DELAY", "3.0"))
COOKIES_FILE = os.getenv("COOKIES_FILE", "")
OUTPUT_DIR = "outputs"

ytt_api = YouTubeTranscriptApi()


def load_urls(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    unique = list(dict.fromkeys(lines))
    print(f"Loaded {len(lines)} lines -> {len(unique)} unique URLs")
    return unique


def extract_video_id(url):
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")

    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            return qs.get("v", [None])[0]
        if parsed.path.startswith(("/embed/", "/shorts/")):
            return parsed.path.split("/")[2]

    return None


def is_already_exported(video_id):
    return len(glob.glob(os.path.join(OUTPUT_DIR, f"yt_{video_id}_*.json"))) > 0


def fetch_metadata(url):
    try:
        resp = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": url, "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return {"title": data.get("title", "Unknown"), "author_name": data.get("author_name", "Unknown")}
    except Exception:
        return {"title": "Unknown", "author_name": "Unknown"}


def fetch_transcript_api(video_id):
    """Primary: youtube-transcript-api (fast, no cookies needed)"""
    result = ytt_api.fetch(video_id, languages=LANGUAGES)
    return [{"text": s.text, "start": s.start, "duration": s.duration} for s in result]


def fetch_transcript_ytdlp(video_id, url):
    """Fallback: yt-dlp with cookies (slower, bypasses IP blocks)"""
    import yt_dlp

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": LANGUAGES,
        "quiet": True,
    }
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        subs = info.get("subtitles", {})
        auto_subs = info.get("automatic_captions", {})

        # Find best subtitle source
        sub_url = None
        for lang in LANGUAGES:
            for source in [subs, auto_subs]:
                if lang in source:
                    for fmt in source[lang]:
                        if fmt["ext"] == "json3":
                            sub_url = fmt["url"]
                            break
                if sub_url:
                    break
            if sub_url:
                break

        if not sub_url:
            return None

        resp = requests.get(sub_url, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        segments = []
        for event in data.get("events", []):
            if "segs" in event:
                text = "".join(s.get("utf8", "") for s in event["segs"]).strip()
                if text and text != "\n":
                    segments.append({
                        "text": text,
                        "start": event.get("tStartMs", 0) / 1000.0,
                        "duration": event.get("dDurationMs", 0) / 1000.0,
                    })

        return segments if segments else None


def fetch_transcript(video_id, url):
    """Try youtube-transcript-api first, then yt-dlp as fallback"""
    try:
        return fetch_transcript_api(video_id), "api"
    except IpBlocked:
        raise
    except Exception:
        pass

    try:
        result = fetch_transcript_ytdlp(video_id, url)
        if result:
            return result, "yt-dlp"
    except Exception:
        pass

    return None, None


def format_timestamp(seconds):
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def save_outputs(video_id, url, metadata, transcript, timestamp_str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    base = f"yt_{video_id}_{timestamp_str}"

    # TXT output
    txt_path = os.path.join(OUTPUT_DIR, f"{base}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"Title: {metadata['title']}\n")
        f.write(f"Channel: {metadata['author_name']}\n")
        f.write(f"Video: {url}\n")
        f.write(f"Exported at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        for segment in transcript:
            ts = format_timestamp(segment["start"])
            f.write(f"[{ts}] {segment['text']}\n")

    # JSON output
    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")
    full_text = " ".join(seg["text"] for seg in transcript)
    data = {
        "video_id": video_id,
        "url": url,
        "title": metadata["title"],
        "channel": metadata["author_name"],
        "exported_at": datetime.now().isoformat(),
        "languages": LANGUAGES,
        "transcript": transcript,
        "full_text": full_text,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return txt_path, json_path


def main():
    print("=" * 60)
    print("YouTube Transcript Exporter")
    print("=" * 60)
    print()

    urls = load_urls(URL_FILE)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    success = 0
    skipped = 0
    already = 0
    ip_blocked_count = 0

    for i, url in enumerate(urls, 1):
        video_id = extract_video_id(url)
        if not video_id:
            print(f"[{i}/{len(urls)}] [!] Invalid URL: {url}")
            skipped += 1
            continue

        if is_already_exported(video_id):
            print(f"[{i}/{len(urls)}] EXIST: {video_id}")
            already += 1
            continue

        print(f"[{i}/{len(urls)}] Processing: {video_id} ... ", end="", flush=True)

        metadata = fetch_metadata(url)

        try:
            transcript, method = fetch_transcript(video_id, url)
            if transcript:
                save_outputs(video_id, url, metadata, transcript, timestamp_str)
                print(f"OK ({method}) - {metadata['title'][:45]}")
                success += 1
                ip_blocked_count = 0
            else:
                print(f"SKIP (no transcript)")
                skipped += 1
        except IpBlocked:
            ip_blocked_count += 1
            if ip_blocked_count >= 3:
                print(f"IP BLOCKED ({ip_blocked_count}x)")
                print(f"\n[!] YouTube IP blocked. Re-run later to continue.")
                print(f"    Already exported files will be skipped automatically.")
                skipped += len(urls) - i
                break
            wait = 120 * ip_blocked_count
            print(f"IP BLOCKED - waiting {wait}s ... ", end="", flush=True)
            time.sleep(wait)
            try:
                transcript, method = fetch_transcript(video_id, url)
                if transcript:
                    save_outputs(video_id, url, metadata, transcript, timestamp_str)
                    print(f"OK ({method}) - {metadata['title'][:45]}")
                    success += 1
                    ip_blocked_count = 0
                else:
                    print(f"SKIP")
                    skipped += 1
            except Exception:
                print(f"SKIP")
                skipped += 1
        except Exception as e:
            print(f"SKIP ({type(e).__name__})")
            skipped += 1

        if i < len(urls):
            time.sleep(DELAY)

    print()
    print("=" * 60)
    print(f"Done: {success} exported, {skipped} skipped, {already} already existed")
    print(f"Output: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
