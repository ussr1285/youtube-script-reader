# youtube-script-reader

YouTube 영상의 자막(transcript)을 추출하여 텍스트 파일로 저장하는 도구입니다.

## 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 설정

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 설정을 변경할 수 있습니다:

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `URL_FILE` | YouTube URL 목록 파일 경로 | `ycombinaotr-영상들.txt` |
| `LANGUAGES` | 자막 언어 우선순위 (쉼표 구분) | `ko,en` |
| `DELAY` | 요청 간 대기 시간 (초) | `3.0` |
| `COOKIES_FILE` | yt-dlp용 쿠키 파일 (선택) | `` |

## 실행

```bash
python youtube_transcript.py
```

이미 다운로드한 영상은 자동으로 건너뛰므로, IP 차단 시 나중에 다시 실행하면 됩니다.

## IP 차단 해결

YouTube가 IP를 차단할 경우 Chrome 쿠키를 추출하여 사용할 수 있습니다:

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

그 후 `.env`에 `COOKIES_FILE=cookies.txt`를 설정하면 됩니다.

## 출력

`outputs/` 디렉토리에 각 영상마다 두 가지 포맷으로 저장됩니다:

- `.txt` - 타임스탬프가 포함된 읽기 쉬운 텍스트
- `.json` - 구조화된 데이터 (전체 텍스트 포함)

## URL 파일 형식

한 줄에 하나의 YouTube URL:

```
https://www.youtube.com/watch?v=MGsalg2f9js
https://www.youtube.com/watch?v=4uzGDAoNOZc
```

중복 URL은 자동으로 제거됩니다.
