from youtube_base import YoutubeSpiderBase
from ...spider_const import *
from pymongo import MongoClient
from scrapy.conf import settings
import hashlib
from scrapy.http import Request
import lxml
import re
from ...feeds_back_utils import *
from ...spider_const import *
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_hifit_pt_BR'
    region = REGION_AMERICA
    locale = LOCALE_BRAZIL_PORTUGUES
    source_name = 'youtube'
    input_type = INPUT_TYPE_CRAWL

    def __init__(self, *a, **kw):
        super(YoutubeSpiderBase, self).__init__(*a, **kw)
        channel_list = get_channel_list_with_other_keys('youtube_hifit', 'Brazil')
        self.channel_list = self.channel_list_filter(channel_list)
        dispatcher.connect(self.spider_idle, signals.spider_idle)
