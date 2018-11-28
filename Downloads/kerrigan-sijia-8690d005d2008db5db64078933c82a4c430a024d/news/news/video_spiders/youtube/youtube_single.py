from youtube_base import YoutubeSpiderBase
from ...spider_const import *
from pymongo import MongoClient
from scrapy.conf import settings
import hashlib
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import requests
import lxml
import re
from lxml import etree


class YoutubeSpider(YoutubeSpiderBase):
    name = 'youtube_single_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL
    duration_limit = 60 * 60

    channel_list = [
        {'source_url_id': -1, 'tags': ['listicle', 'animal', 'life', 'comedy'], 'create_date': u'2018-06-22',
         'state': 1, 'source_url': 'https://www.youtube.com/watch?v=dnn-4goA7j8'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=avQ4q0B041Y'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=JVWt4cQVFTU'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=CDg44RkisuE'},
        {'source_url_id': -1, 'tags': ['comedy', 'fashion'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=9fA3hxJvSAY'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=8r5XUWouBq8'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=XcPJstywc0I'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=8js6wrd26Pc'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=H5To68iVK50'},
        {'source_url_id': -1, 'tags': [''], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=n-pDT6yjFm8'},
        {'source_url_id': -1, 'tags': ['interest', 'health'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=20bEecBRgFU'},
        {'source_url_id': -1, 'tags': ['listicle', 'life'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=55K5vu5uNIA'},
        {'source_url_id': -1, 'tags': ['entertainment'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=6QdcKetf9mE'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=blwc4bZwvog'},
        {'source_url_id': -1, 'tags': ['howto', 'baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=m8ft15cTCIk'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=QaVybn1NFZ8'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=QyMxN3vWgsY'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=W2ttCLcv6_g'},
        {'source_url_id': -1, 'tags': ['animal', 'interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=yYJitRb2Ltg'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=yciv6WiYD9o'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=ln17o9dA9Uo'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=dmdvxX3wHyM'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=yeazOxy0SvQ'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=ZtZDILvJI_o'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=C9kvCKbD9Ks'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=cRRW4DX2YCo'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=h-02MvlBFbQ'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=uS8pI8kOfiE'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=UVZVfRDAUpM'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=HaghZ6hpUFE'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=_OxbzVThMuE'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=w0qVciN4lTs'},

        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=TfPa5iRVdGI'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=gXttUA5S-hs'},
        {'source_url_id': -1, 'tags': ['dance'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=yonGLO18jNA'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=f_CsC-oQ7uE'},
        {'source_url_id': -1, 'tags': ['dance'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=KXCiLub8DZg'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=kyNseWYM3vU'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=FbXx2Zv7BEg'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=GDqqjjZ9AyU'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=_GZZ8s5bTkM'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=LPmVHBZDkPE'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=Vf-mKcH4OY8'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=Kfin_IF5eWM'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=OLMaWgmRi6E'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=JN0Ws8eDcX4'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=6797WH6sYNM'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=Bsp_JTtE3-w'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=ZtUPKekDY7M'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=iZ1dgmoihoM'},
        {'source_url_id': -1, 'tags': ['dance', 'interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=SiaG_4OMZ14'},
        {'source_url_id': -1, 'tags': ['comedy', 'baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=rmLk96gNW9g'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=Bl-QY84hojs'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=-SY-aeSplco'},
        {'source_url_id': -1, 'tags': ['food'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=sDIK0893iEg'},
        {'source_url_id': -1, 'tags': ['life'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=QBSrdw19k8M'},
        {'source_url_id': -1, 'tags': ['technolgoy', 'life'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=YF7mkyd-Wm4'},
        {'source_url_id': -1, 'tags': ['entertainment'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=1XrJ_04FZQI'},
        {'source_url_id': -1, 'tags': ['society'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=L7mlTf0Aff4'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=d6kjZXwdyJs'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=8c4CqtYFi7Q'},
        {'source_url_id': -1, 'tags': ['dance'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=XgP_S9NiVnc'},
        {'source_url_id': -1, 'tags': ['dance'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=Ioum3RLkdvU'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=FqJdzYY_Fas'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=b-xScLIevw0'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=DzlH5SDGoyA'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=WkfA7dpoUMM'},
        {'source_url_id': -1, 'tags': ['comedy', 'vehicle'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=UY99HZR8m4c'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=V9uPs5l2asw'},
        {'source_url_id': -1, 'tags': ['society'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=ak-k1rTvfoo'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=4Slcq0Jj4RM'},
        {'source_url_id': -1, 'tags': ['sport', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=2DqNP675u6Y'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=ON5ebMnMgCM'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=NAughowAfgY'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=Cq850P1R4JU'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=lHPzYoIDzSs'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=rm_5tTJ9WkY'},
        {'source_url_id': -1, 'tags': ['sport', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=T-EAOeflFJM'},
        {'source_url_id': -1, 'tags': ['sport', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=NsaSG-0U4mU'},
        {'source_url_id': -1, 'tags': ['society'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=oVuQ6Ggfg4g'},
        {'source_url_id': -1, 'tags': ['life', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.youtube.com/watch?v=zhf1pIl007o'},
    ]

    def __init__(self, *a, **kw):
        super(YoutubeSpiderBase, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        source_dict = self.channel_list.pop(0)
        if self.is_source_url_exist(self.input_type, source_dict['source_url']):
            self.logger.info('source_url exists: ' + str(source_dict['source_url']))
            self.spider_idle()
        else:
            source_url = source_dict['source_url']
            source_url_id = source_dict['source_url_id']
            tags = source_dict['tags']
            state = source_dict['state']
            raw = dict()
            raw['tags'] = tags
            raw['inlinks'] = []
            raw['source_url'] = source_url
            raw['source_url_id'] = source_url_id
            yield Request(
                raw['source_url'],
                headers=self.hd_page,
                meta=raw,
                callback=self.parse_page
            )

    def generate_message(self, article_info):
        message = super(YoutubeSpiderBase, self).generate_message(article_info)
        return message

    def get_extra_from_raw(self, raw):
        extra = super(YoutubeSpiderBase, self).get_extra_from_raw(raw)
        extra['score'] = 10
        return extra
