from instagram_base import InstagramBase
from ...spider_const import *


class InstagramSpider(InstagramBase):
    name = 'instagram_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL

