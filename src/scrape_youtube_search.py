"""YouTube の動画検索から VTuber のアカウント情報を集める
"""

import os

from dotenv import load_dotenv

from youtube.scraper import YouTubeSearchScraper

load_dotenv()

API_KEY = os.getenv('API_KEY')

ng_words = [
    "short", "shorts",
]
yt_scraper = YouTubeSearchScraper("yt_data", API_KEY, ng_words)

# VTuber自己紹介動画
yt_scraper.search("VTuber自己紹介", order="rating")
yt_scraper.search("VTuber自己紹介", order="date")
yt_scraper.search("VTuber自己紹介", order="relevance")


# 新人VTuber
yt_scraper.search("新人VTuber", order="rating")
yt_scraper.search("新人VTuber", order="date")
yt_scraper.search("新人VTuber", order="relevance")
