# youtube-script-reader

[한국어](README.ko.md) | [日本語](README.ja.md)

Extract YouTube video transcripts and save them as text files.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Read URLs from a file
python youtube_transcript.py urls.txt

# Pass URLs directly
python youtube_transcript.py https://youtube.com/watch?v=xxx

# Mix files and URLs
python youtube_transcript.py urls.txt https://youtube.com/watch?v=yyy

# With options
python youtube_transcript.py urls.txt -l ko,en -d 3.0 -o outputs -c cookies.txt
```

| Option | Description | Default |
|--------|-------------|---------|
| `-l, --lang` | Transcript language priority (comma-separated) | `ko,en` |
| `-d, --delay` | Delay between requests (seconds) | `3.0` |
| `-o, --output` | Output directory | `outputs` |
| `-c, --cookies` | Cookie file for yt-dlp | - |

Defaults can also be set via `.env` file (`LANGUAGES`, `DELAY`, `COOKIES_FILE`).

Previously exported videos are automatically skipped, so you can re-run after an IP block.

## Working Around IP Blocks

If YouTube blocks your IP, export Chrome cookies and pass them in:

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
python youtube_transcript.py urls.txt -c cookies.txt
```

## Output

Each video is saved in three formats under the `outputs/` directory:

- `.txt` -- human-readable text with timestamps
- `.json` -- structured data with full text
- `.csv` -- single CSV file with all results (`url`, `video_id`, `title`, `channel`, `script`)

The CSV is Excel-compatible (UTF-8 BOM encoded).

Duplicate URLs are automatically deduplicated.
