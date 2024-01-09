# VTuberScraper
VTuber に関する情報をスクレピングするスクリプトたち

# installation
環境構築は poetry で
```bash
poetry install
```

## 環境変数
`.env`: `vtuber-scraper` 直下にの `.env` ファイルに `YOUTUBE_API_KEY=hogehoge` の形で、YouTube API のキーを配置すること。

# 各フォルダの説明
## `src`

直下の Python ファイル`src/*.py`: 実行スクリプト \
```bash
python src/scrape_vpost_list.py
```
のように実行. 詳細は各ファイルのコメント参照.

`src/*/*.py` はすべてライブラリ

### 各スクリプトの説明
- `build_dataset.py`: `vpost_data` と `yt_data` を統合して `dataset/uploads` と `dataset/merged.json` を吐き出す。その後、適当なフィルタリングをして、`dataset/dataset.json` を吐き出す。
- `download_youtube_videos.py`: `dataset/dataset.json` を読み込んで、自己紹介動画をダウンロードする。
- `scrape_vpost_detail.py`: vpost の各 VTuber の個人ページをスクレイピング
- `scrape_vpost_list.py`: vpost の VTuber 一覧ページをスクレイピング
- `scrape_youtube_channel.py`: YouTube の channel id からチャンネルの詳細情報を取得
- `scrape_youtube_search.py`: YouTube の動画検索から VTuber を探す

## `test`, `temp`
- `test`: pytest によるテストコードを置くところ
- `temp`: pytest 等で生成される一時データ。消して良い。

## 各種データ
データの類は容量がでかいので、gitignore している

- `vpost_data`: https://vtuber-post.com/ からスクレイピングしたデータ (VTuber の YouTube と Twitter のアカウントリスト)
- `yt_data`: YouTube API でスクレイピングしたデータ
- `dataset`:
  - `videos`: youtube-dlp で収集した youtube の動画ファイル
  - `uploads`: 各 YouTube チャンネルの投稿動画リスト。YouTube API の relatedPlaylist/uploads で収集。
  - `dataset.json`: web フォームにぶちこむように整形されたデータ。
  - `merged.json`: 動画データと投稿動画リスト以外の集めたデータを1つにまとめたやつ。
