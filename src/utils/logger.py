import logging

def get_logger(modname: str, loglevel=logging.DEBUG) -> logging.Logger:
    logger  = logging.getLogger(modname)
    handler = logging.StreamHandler()
    handler.setLevel(loglevel)
    logger.setLevel(loglevel)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
