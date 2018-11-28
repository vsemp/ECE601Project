from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_in_ID'
    region = REGION_ASIA
    locale = LOCALE_INDONESIA_INDONESIAN
    locale_full_name = 'Indonesia'
    input_type = INPUT_TYPE_CRAWL

