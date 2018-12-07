from facebook_base import FacebookSpiderBase
from ...spider_const import *


class YoutubeSpider(FacebookSpiderBase):
    name = 'facebook_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL

