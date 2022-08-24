from lib.scraper import VTuberListScraper

scraper = VTuberListScraper("vpost_data")
scraper.ready_scraper()
scraper.scrape_vtuber_list()
