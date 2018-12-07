from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_fr_FR'
    region = REGION_AMERICA
    locale = LOCALE_FRANCE_FRENCH
    locale_full_name = 'France'
    input_type = INPUT_TYPE_CRAWL
