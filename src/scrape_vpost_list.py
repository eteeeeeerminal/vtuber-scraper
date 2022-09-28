"""VTuber Post の個人データベースをスクレイピング
- [VTuber Post の個人データベース](https://vtuber-post.com/database/index.php)
"""

from vpost.scraper import VTuberListScraper

scraper = VTuberListScraper("vpost_data")
scraper.ready_scraper()
scraper.scrape_vtuber_list()
