import logging
import sys
from typing import Callable
from promo_scheduling.settings import APP_NAME

log_format = logging.Formatter(
    '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(log_format)
logger.addHandler(consoleHandler)


def log_io(func: Callable):
    def wrapper(*args, **kwargs):
        logger.debug(f'Input {func.__name__}: {args} {kwargs}')
        ret = func(*args, **kwargs)
        logger.debug(f'Output {func.__name__}: {ret}')
        return ret
    return wrapper
