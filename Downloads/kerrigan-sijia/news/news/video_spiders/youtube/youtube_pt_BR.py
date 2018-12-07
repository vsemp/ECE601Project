from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_pt_BR'
    region = REGION_AMERICA
    locale = LOCALE_BRAZIL_PORTUGUES
    locale_full_name = 'Brazil'
    input_type = INPUT_TYPE_CRAWL

