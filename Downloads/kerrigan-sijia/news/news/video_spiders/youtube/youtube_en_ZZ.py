from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_en_ZZ'
    locale = LOCALE_GLOBAL_ENGLISH
    locale_full_name = 'Global'
    input_type = INPUT_TYPE_CRAWL
