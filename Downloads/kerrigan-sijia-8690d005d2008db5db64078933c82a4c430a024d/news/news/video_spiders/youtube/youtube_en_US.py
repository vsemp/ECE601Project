from youtube_base import YoutubeSpiderBase
from ...spider_const import *
from pymongo import MongoClient
from scrapy.conf import settings
import hashlib
from scrapy.http import Request


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL

