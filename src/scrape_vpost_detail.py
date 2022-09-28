"""VTuber Post の各個人ページをスクレイピング
- [VTuber Post の個人ページ](https://vtuber-post.com/database/detail.php?id=vtuber_id)

`scrape_vpost_list.py` で取得した id から各ページに飛んでスクレイピングする.
"""

from vpost.scraper import VTuberDetailScraper

scraper = VTuberDetailScraper("vpost_data")
scraper.scrape_youtube_datum()
