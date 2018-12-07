from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_ko_KR'
    region = REGION_ASIA
    locale = LOCALE_KOREA_KOREAN
    locale_full_name = 'Korea'
    input_type = INPUT_TYPE_CRAWL

