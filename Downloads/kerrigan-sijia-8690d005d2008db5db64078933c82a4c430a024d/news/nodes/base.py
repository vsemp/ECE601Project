import sys
sys.path.append('.')
from moduleutil.stream import NewsFeedsStream
from moduleutil import load_settings
from moduleutil.log import configure_logging
import logging
import os


class BaseObject(object):

    def __init__(self, *a, **kw):
        self.settings = load_settings('settings')
        configure_logging(self.settings)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stream = NewsFeedsStream(self.settings, self)

    def main(self):
        pass

    def open(self):
        self.stream.open()

    def close(self):
        self.stream.close()
