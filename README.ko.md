# youtube-script-reader

[English](README.md) | [日本語](README.ja.md)

YouTube 영상의 자막(transcript)을 추출하여 텍스트 파일로 저장하는 도구입니다.

## 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 사용법

```bash
# 파일에서 URL 목록 읽기
python youtube_transcript.py urls.txt

# URL 직접 입력
python youtube_transcript.py https://youtube.com/watch?v=xxx

# 파일 + URL 혼합
python youtube_transcript.py urls.txt https://youtube.com/watch?v=yyy

# 옵션
python youtube_transcript.py urls.txt -l ko,en -d 3.0 -o outputs -c cookies.txt
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-l, --lang` | 자막 언어 우선순위 (쉼표 구분) | `ko,en` |
| `-d, --delay` | 요청 간 대기 시간 (초) | `3.0` |
| `-o, --output` | 출력 디렉토리 | `outputs` |
| `-c, --cookies` | yt-dlp용 쿠키 파일 | - |

`.env` 파일로도 기본값 설정 가능 (`LANGUAGES`, `DELAY`, `COOKIES_FILE`).

이미 다운로드한 영상은 자동으로 건너뛰므로, IP 차단 시 나중에 다시 실행하면 됩니다.

## IP 차단 해결

YouTube가 IP를 차단할 경우 Chrome 쿠키를 추출하여 사용:

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
python youtube_transcript.py urls.txt -c cookies.txt
```

## 출력

`outputs/` 디렉토리에 각 영상마다 세 가지 포맷으로 저장됩니다:

- `.txt` -- 타임스탬프가 포함된 읽기 쉬운 텍스트
- `.json` -- 구조화된 데이터 (전체 텍스트 포함)
- `.csv` -- 전체 결과를 하나의 CSV 파일로 (`url`, `video_id`, `title`, `channel`, `script`)

CSV는 엑셀에서 바로 열 수 있습니다 (UTF-8 BOM 인코딩).

중복 URL은 자동으로 제거됩니다.
