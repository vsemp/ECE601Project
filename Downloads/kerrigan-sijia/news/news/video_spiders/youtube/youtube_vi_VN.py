from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_vi_VN'
    region = REGION_ASIA
    locale = LOCALE_VIETNAM_VIETNAMESE
    locale_full_name = 'Vietnam'
    input_type = INPUT_TYPE_CRAWL

