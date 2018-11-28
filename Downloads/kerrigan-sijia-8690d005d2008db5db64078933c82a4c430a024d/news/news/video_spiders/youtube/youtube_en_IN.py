from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_en_IN'
    region = REGION_ASIA
    locale = LOCALE_INDIA_ENGLISH
    locale_full_name = 'India(English)'
    input_type = INPUT_TYPE_CRAWL

