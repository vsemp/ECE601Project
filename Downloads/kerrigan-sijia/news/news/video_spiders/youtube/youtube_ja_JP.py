from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_ja_JP'
    region = REGION_AMERICA
    locale = LOCALE_JAPAN_JAPANESE
    locale_full_name = 'Japan'
    input_type = INPUT_TYPE_CRAWL

