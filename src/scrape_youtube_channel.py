"""YouTube の channel id からチャンネルの詳細情報を取得

`scrape_youtube_search.py` で取得した id から各チャンネルの情報を取得する.
"""

import os

from dotenv import load_dotenv

from youtube.scraper import YouTubeChannelScraper

load_dotenv()

API_KEY = os.getenv('API_KEY')

scraper = YouTubeChannelScraper("yt_data", API_KEY, "vpost_data/detail_data.json")
scraper.scrape()
