from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_ar_AR'
    region = REGION_ASIA
    locale = LOCALE_ARABIA_ARABIC
    locale_full_name = 'Saudi Arabia'
    input_type = INPUT_TYPE_CRAWL

