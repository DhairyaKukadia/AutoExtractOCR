import logging
from logging.handlers import RotatingFileHandler

from app.config.settings import APP_LOG_FILE


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    fh = RotatingFileHandler(APP_LOG_FILE, maxBytes=2_000_000, backupCount=3)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
