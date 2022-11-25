import logging

def get_logger(modname: str, loglevel=logging.DEBUG) -> logging.Logger:
    logger  = logging.getLogger(modname)
    handler = logging.StreamHandler()
    handler.setLevel(loglevel)
    logger.setLevel(loglevel)
    logger.addHandler(handler)
    logger.propagate = False

    file_handler = logging.FileHandler(filename="vtuber-scraper.log", encoding="utf-8")
    file_handler.setLevel(loglevel)
    logger.addHandler(file_handler)

    return logger
