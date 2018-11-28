from ...spider_const import *
from pymongo import MongoClient
from scrapy.conf import settings
import hashlib
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from facebook_base import FacebookSpiderBase
import re

class FacebookSpider(FacebookSpiderBase):
    name = 'facebook_single_en_US'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    locale_full_name = 'United States of America'
    input_type = INPUT_TYPE_CRAWL
    duration_limit = 60 * 60

    channel_list = [
        {'source_url_id': -1, 'tags': ['baby', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/MaBabyLovePMH/videos/168865033834941'},
        {'source_url_id': -1, 'tags': ['life', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/FilterCopy/videos/1771894882857457'},
        {'source_url_id': -1, 'tags': ['baby', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/154109934947338/videos/515960892095572'},
        {'source_url_id': -1, 'tags': ['comedy', 'animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/trynottolaughpets/videos/1991998867717487'},
        {'source_url_id': -1, 'tags': ['comedy', 'animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/thepetcollective/videos/2038972069450921'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/BelieveItUp/videos/1735463986510175'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/MaBabyLovePMH/videos/163490041039107'},
        {'source_url_id': -1, 'tags': ['relationship', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/AmUpset/videos/1965733633658737'},
        {'source_url_id': -1, 'tags': ['baby', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/BabyGotLaughs/videos/1568201049914728'},
        {'source_url_id': -1, 'tags': ['listicle', 'relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/BET/videos/1964768243776669'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/Cosmopolitan/videos/10155794453167708'},
        {'source_url_id': -1, 'tags': ['listicle', 'relationship', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/failarmy/videos/1702480989849056'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/failarmy/videos/545193179197907'},
        {'source_url_id': -1, 'tags': ['food'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/FoodNetworkFinds/videos/560841397631030'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/FunniestFamilyMoments/videos/2200728846883271'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/funnySeriousJokes/videos/1821723007842913'},
        {'source_url_id': -1, 'tags': ['relationship', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/HashtagRelationshipGoals/videos/1312724865539406'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/JayShettyIW/videos/1988736198107502'},
        {'source_url_id': -1, 'tags': ['interest'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/JukinVideo/videos/1745969402157989'},
        {'source_url_id': -1, 'tags': ['baby', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/KidsAreJustTheCutest/videos/1686242318139384'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/MaBabyLovePMH/videos/172608120127299'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/superfunvid/videos/1813555728701473'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/weirdhdtv/videos/1954111988206097'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/JugglingTheJenkinsBlog/videos/563458904033785'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/lifewithpetsshow/videos/198418514026979'},
        {'source_url_id': -1, 'tags': ['listicle', 'relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/SOML/videos/1390449201099490'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/OfficialMonstah/videos/1076358745831452'},
        {'source_url_id': -1, 'tags': ['food'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/EpicMealTime/videos/1691051674291460'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/R1Lmedia/videos/2682254085130308'},
        {'source_url_id': -1, 'tags': ['comedy', 'relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/shulerking/videos/1903170996567598'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/seen.everything/videos/1600603063377558'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/imgeorgejanko/videos/952106761553912'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/SugeeBlog/videos/944607472365710'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/ShutUpCartoons/videos/10154755170826765'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/funnyordie/videos/10156213932858851'},
        {'source_url_id': -1, 'tags': ['fashion'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/glamour/videos/10155781474025479'},
        {'source_url_id': -1, 'tags': ['food'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/VIX.Yum/videos/252081328529212'},
        {'source_url_id': -1, 'tags': ['baby'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/NTDFunniest/videos/2144837105805779'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/Brotality.me/videos/1983144468586810'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/TRNDVideos/videos/1252662324837457'},
        {'source_url_id': -1, 'tags': ['baby', 'relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/NTDFunniest/videos/2117356651887158'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/JaNinaWorld/videos/1703446302999867'},
        {'source_url_id': -1, 'tags': ['listicle', 'life'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/CaresOneNo/videos/2567232280183419'},
        {'source_url_id': -1, 'tags': ['listicle', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/markianb/videos/965506313574663'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/R1Lmedia/videos/2657603964261987'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/mymgag/videos/1840001072738977'},
        {'source_url_id': -1, 'tags': ['interest', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/juliojanpierre/videos/1991685404479881'},
        {'source_url_id': -1, 'tags': ['relationship', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/R1Lmedia/videos/2662271120461938'},
        {'source_url_id': -1, 'tags': ['baby', 'comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/R1Lmedia/videos/2906909635998084'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/spideypostsblog/videos/413511145755828'},
        {'source_url_id': -1, 'tags': ['relationship'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/lifenlesson/videos/2034497136820098'},
        {'source_url_id': -1, 'tags': ['animal'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/viralmotion/videos/1747142385415201'},
        {'source_url_id': -1, 'tags': ['comedy'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/videohebohlucu/videos/352255898601006'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/moses.ayala.9/videos/10212307676954944'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/viral.sauce/videos/467588533687511'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/funny.funny247/videos/1316739121790151'},
        {'source_url_id': -1, 'tags': [], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/HarpersBazaar/videos/10155491404422562'},
        {'source_url_id': -1, 'tags': ['entertainment'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/viral.sauce/videos/491316924648005'},
        {'source_url_id': -1, 'tags': ['comedy', 'life'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/viral.sauce/videos/472450336534664'},
        {'source_url_id': -1, 'tags': ['comedy', 'life'], 'create_date': u'2018-06-22', 'state': 1,
         'source_url': 'https://www.facebook.com/viral.sauce/videos/459124074533957'},
    ]

    def __init__(self, *a, **kw):
        super(FacebookSpiderBase, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        source_dict = self.channel_list.pop(0)
        source_url = source_dict['source_url']
        source_url_id = source_dict['source_url_id']
        tags = source_dict['tags']
        state = source_dict['state']
        raw = dict()
        raw['tags'] = tags
        raw['inlinks'] = []
        raw['source_url'] = source_url
        raw['source_url_id'] = source_url_id
        raw['publisher'] = re.findall('com/(.*?)/videos', source_url)[0]
        raw['publisher_icon'] = [self.get_icon_url(raw['publisher'])]

        yield Request(
            raw['source_url'],
            headers=self.hd_page,
            meta=raw,
            dont_filter=True,
            callback=self.parse_page
        )

    def get_extra_from_raw(self, raw):
        extra = super(FacebookSpiderBase, self).get_extra_from_raw(raw)
        extra['score'] = 10
        return extra
