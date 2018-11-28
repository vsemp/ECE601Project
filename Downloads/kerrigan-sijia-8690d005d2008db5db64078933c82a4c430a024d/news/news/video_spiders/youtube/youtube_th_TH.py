from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_th_TH'
    region = REGION_ASIA
    locale = LOCALE_THAILAND_THAI
    locale_full_name = 'Thailand'
    input_type = INPUT_TYPE_CRAWL

