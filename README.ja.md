# youtube-script-reader

[English](README.md) | [한국어](README.ko.md)

YouTube動画の字幕(トランスクリプト)を抽出してテキストファイルとして保存するツールです。

## インストール

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使い方

```bash
# ファイルからURL一覧を読み込む
python youtube_transcript.py urls.txt

# URLを直接指定
python youtube_transcript.py https://youtube.com/watch?v=xxx

# ファイルとURLを混在
python youtube_transcript.py urls.txt https://youtube.com/watch?v=yyy

# オプション付き
python youtube_transcript.py urls.txt -l ja,en -d 3.0 -o outputs -c cookies.txt
```

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-l, --lang` | 字幕の言語優先順位（カンマ区切り） | `ko,en` |
| `-d, --delay` | リクエスト間の待機時間（秒） | `3.0` |
| `-o, --output` | 出力ディレクトリ | `outputs` |
| `-c, --cookies` | yt-dlp用Cookieファイル | - |

`.env`ファイルでデフォルト値を設定することも可能です（`LANGUAGES`、`DELAY`、`COOKIES_FILE`）。

既にダウンロード済みの動画は自動的にスキップされるため、IPブロック時は後で再実行できます。

## IPブロックの回避

YouTubeがIPをブロックした場合、ChromeのCookieをエクスポートして使用します：

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
python youtube_transcript.py urls.txt -c cookies.txt
```

## 出力

`outputs/`ディレクトリに各動画ごとに3つの形式で保存されます：

- `.txt` -- タイムスタンプ付きの読みやすいテキスト
- `.json` -- 構造化データ（全文テキスト含む）
- `.csv` -- 全結果を1つのCSVファイルに（`url`、`video_id`、`title`、`channel`、`script`）

CSVはExcelで直接開けます（UTF-8 BOMエンコーディング）。

重複URLは自動的に除外されます。
