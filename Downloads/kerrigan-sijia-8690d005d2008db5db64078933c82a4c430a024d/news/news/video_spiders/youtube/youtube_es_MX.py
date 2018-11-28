from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_es_MX'
    region = REGION_AMERICA
    locale = LOCALE_MEXICO_SPAISH
    locale_full_name = 'Mexico'
    input_type = INPUT_TYPE_CRAWL
