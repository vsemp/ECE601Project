from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_hi_IN'
    region = REGION_ASIA
    locale = LOCALE_INDIA_HINDI
    locale_full_name = 'India(Hindi)'
    input_type = INPUT_TYPE_CRAWL

