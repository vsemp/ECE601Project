# -*- coding: utf-8 -*-
from ..video_spider_base import VideoSpider
from ...spider_const import *


# TODO 有问题，需要修改
class MuseSpider(VideoSpider):
    name = 'muse_base'
    # download_delay = 3
    # download_timeout = 60
    video_type = 'mp4'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'muse'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    download_maxsize = 104857600
    download_warnsize = 104857600
    default_section = 60 * 60 * 24 * 1 * 365
