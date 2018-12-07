from youtube_base import YoutubeSpiderBase
from ...spider_const import *


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_fix_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'youtube_fix'
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL
