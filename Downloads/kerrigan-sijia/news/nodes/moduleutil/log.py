import sys
import logging
from logging.config import dictConfig


DEFAULT_LOG_ENABLED = True
DEFAULT_LOG_ENCODING = 'utf-8'
DEFAULT_LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
DEFAULT_LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_STDOUT = False
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_LOG_FILE = None

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}


class StreamLogger(object):

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def configure_logging(settings={}):
    dictConfig(DEFAULT_LOGGING)
    if settings.get('LOG_STDOUT',DEFAULT_LOG_STDOUT):
        sys.stdout = StreamLogger(logging.getLogger('stdout'))
    logging.root.setLevel(logging.NOTSET)
    handler = _get_handler(settings)
    logging.root.handlers = []
    logging.root.addHandler(handler)


def _get_handler(settings):
    """ Return a log handler object according to settings """
    filename = settings.get('LOG_FILE', DEFAULT_LOG_FILE)
    if filename:
        encoding = settings.get('LOG_ENCODING', DEFAULT_LOG_ENCODING)
        handler = logging.FileHandler(filename, encoding=encoding)
    elif settings.get('LOG_ENABLED', DEFAULT_LOG_ENABLED):
        handler = logging.StreamHandler()
    else:
        handler = logging.NullHandler()

    formatter = logging.Formatter(
        fmt=settings.get('LOG_FORMAT', DEFAULT_LOG_FORMAT),
        datefmt=settings.get('LOG_DATEFORMAT', DEFAULT_LOG_DATEFORMAT)
    )
    handler.setFormatter(formatter)
    handler.setLevel(settings.get('LOG_LEVEL', DEFAULT_LOG_LEVEL))
    return handler
