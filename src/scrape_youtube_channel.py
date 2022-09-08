import os

from dotenv import load_dotenv

from youtube.scraper import YouTubeChannelScraper

load_dotenv()

API_KEY = os.getenv('API_KEY')

scraper = YouTubeChannelScraper("yt_data", API_KEY, "vpost_data/detail_data.json")
scraper.scrape()
