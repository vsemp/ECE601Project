import re

import scrapy
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from ..base_spider import BaseSpider
import re
from ..feeds_back_utils import *
import pprint


class TikTokSpider(BaseSpider):
    name = 'tiktok_base'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    download_delay = 0
    hd = {
        'build': '1516788764802',
        'language': 'zh_CN',
        'X-Request-Info5': 'eyJvcyI6ImFuZHJvaWQgNy4xLjEiLCJ2ZXJzaW9uIjoiNi41LjAiLCJzbGlkZXItc2hvdy1jb29raWUiOiJibDgyTlRFMk16azJNemN4TWpNek1qRTFOVEF6T2tOa1NGSTBjWEpaU0d4M2IxbFZkV3R3VEdVeWVXYzlQVHBoTUdabE1tUTVNbVkwTURRMFpEQmxaV0l6WmpFMU56TTVaRFEwTUdNek5EbzJOVEUyTXprMk16Y3hNak16TWpFMU5UQXoiLCJYLVJlcXVlc3QtSUQiOiI1Y2Y3ODgzYS04MDE4LTRlZDgtOWQ3NC04MDRlZjIwMjE3ZGMiLCJtZXRob2QiOiJHRVQiLCJ1cmwiOiJodHRwczpcL1wvYXBpLm11c2ljYWwubHlcL3Jlc3RcL3VzZXJcLzI2NDg5ODAzNTk4ODUyMDk2MD91c2VyX3ZvX3JlbGF0aW9ucz1hbGwiLCJvc3R5cGUiOiJhbmRyb2lkIiwiZGV2aWNlaWQiOiJhMGQ3MGU5ZDExYjk1OTQ2NmE5NDI0MmY5NjA4NmVhZGM3NTU0OSIsInRpbWVzdGFtcCI6MTUxNzIxODM1NjgyMH0=',
        'X-Request-Sign5': '01a6d89754cd16765203fc8e5d98967c26d8509e6b5e',
        'Authorization': 'M-TOKEN "hash"="NWNhYTdjZTkwMDAxMDAwZmUwNGRiNTcxNmIwMDE0MGYyZDM4ZmRjNTBkMDM0MGZlYzA1N2Q5ZWIxYjkzMzBiMTZiNDcxYTNlMWU4MmVlOGEzMjJlMmZmZWU1ZjIzYjVjNjIwYTkwYmUwM2IxYmNlMzYwNTA1NmRjZTJlNDU2YzkwYWZlZDVmYTczNDYyMzJkYmRlMTExYTQyODkyYmExMzc0OWE0YTRjMzkwYWRjMDM1NGJiNDQzYzI4OThhZGFkMWYwYzBkODY0ZTA3ZmM5M2IzYjAzZmRmODU0NTcxNzBmYzhiYzhhZTgzMGFmMjQyNGJjMTlmMzkxNmE0YzliNDJmZTZlM2EzOWJhMGI4NWJhMWE3ZDY4OTcyYjQ1NmQ1ZDI2ZGEzNGQ5YWVjOGE4ZTZmM2QyNzVmYmQ3ZmJiMTU5MDAzYTAwOThmNjU1M2JiODY4NDdmYmUwMjBhNDNlYWQ3ZGZlZjU5MmNhZDQwNjU3MjMwZjQ1OWY4NDdjMDkxZGIxYmViNDU1MTRlZGFmOA=="',
    }
    page = 0
    max_count = 20
    # channel_list = get_channel_list('like', 'Thailand')
    channel_list = [
        # {'url': 'https://m.tiktok.com/v/6569929131457252614.html', 'tags': ['life']},
        {'url': 'https://m.tiktok.com/v/6599472724823772418.html', 'tags': ['life']},
        # {'url': 'https://m.tiktok.com/v/6586657878122188037.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6589974705418013957.html', 'tags': ['animal', 'girl']},
        # {'url': 'https://m.tiktok.com/v/6589628452918267142.html', 'tags': ['girl']},
        # {'url': 'https://m.tiktok.com/v/6592659156853853446.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/6592413940108496134.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/6590401312242797830.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/6589317852266761478.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6592542249010072838.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6590644809306737925.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6589407416947838213.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/6577022746847350022.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/6588585770485812485.html', 'tags': ['food', 'music']},
        # {'url': 'https://m.tiktok.com/v/6587126432370003206.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/6587894636784651526.html', 'tags': ['music', 'animal']},
        # {'url': 'https://m.tiktok.com/v/6581469195865689350.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6587410645128318213.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6584996174967606533.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6585193618909170949.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6534256964296250368.html', 'tags': ['magic']},
        # {'url': 'https://m.tiktok.com/v/6564368825083497733.html', 'tags': ['music', 'interest']},
        # {'url': 'https://m.tiktok.com/v/6562798427183254790.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6585031647479991558.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6582722128745860358.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6586399370566962437.html', 'tags': ['baby', 'interst']},
        # {'url': 'https://m.tiktok.com/v/6591161406316350726.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/6579607426209680645.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6579603215870872838.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6574035297984580870.html', 'tags': ['life']},
        # {'url': 'https://m.tiktok.com/v/6576147027107777797.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6581883974262459653.html', 'tags': ['vehicle']},
        # {'url': 'https://m.tiktok.com/v/6568536071892634885.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6589197338630163713.html', 'tags': ['cartoon']},
        # {'url': 'https://m.tiktok.com/v/6579766683127254278.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6579371089523117317.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6566765988501523718.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6576919993995234565.html', 'tags': ['animal']},
        # {'url': 'https://m.tiktok.com/v/6571144520593837317.html', 'tags': ['music', 'comedy']},
        # {'url': 'https://m.tiktok.com/v/6578507944889945349.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6566954192080997638.html', 'tags': ['life', 'food']},
        # {'url': 'https://m.tiktok.com/v/6585921222117166342.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6583277317362027781.html', 'tags': ['interest', 'beauty']},
        # {'url': 'https://m.tiktok.com/v/6592545802969681158.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6567000243672452358.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6592152994723138822.html', 'tags': ['sport']},
        # {'url': 'https://m.tiktok.com/v/6592228061956017413.html', 'tags': ['fashion']},
        # {'url': 'https://m.tiktok.com/v/6581420248761634053.html', 'tags': ['dance', 'guy']},
        # {'url': 'https://m.tiktok.com/v/6560857100862360837.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6581019235223342341.html', 'tags': ['interst']},
        # {'url': 'https://m.tiktok.com/v/6569184961704758533.html', 'tags': ['fitness']},
        # {'url': 'https://m.tiktok.com/v/6579155737736400134.html', 'tags': ['fitness']},
        # {'url': 'https://m.tiktok.com/v/6579239243925703941.html', 'tags': ['sport']},
        # {'url': 'https://m.tiktok.com/v/6571011342898040070.html', 'tags': ['sport']},
        # {'url': 'https://m.tiktok.com/v/6583244356117859589.html', 'tags': ['sport']},
        # {'url': 'https://m.tiktok.com/v/6588265042519526662.html', 'tags': ['life']},
        # {'url': 'https://m.tiktok.com/v/6575648272386362630.html', 'tags': ['nature']},
        # {'url': 'https://m.tiktok.com/v/6581187986317135110.html', 'tags': ['life']},
        # {'url': 'https://m.tiktok.com/v/188162498372628480.html', 'tags': ['music', 'guy']},
        # {'url': 'https://m.tiktok.com/v/183911473834864640.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/210271140672577536.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/202677941393154048.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/6517751830884127744.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/248957577928073216.html', 'tags': ['dance', 'interest']},
        # {'url': 'https://m.tiktok.com/v/274401412393132032.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6535503875217052672.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/6591092931891825926.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6568889797287349510.html', 'tags': ['guy']},
        # {'url': 'https://m.tiktok.com/v/6568609165319605509.html', 'tags': ['guy']},
        # {'url': 'https://m.tiktok.com/v/260700977911967744.html', 'tags': ['intersest']},
        # {'url': 'https://m.tiktok.com/v/256319757480558592.html', 'tags': ['interest']},
        # {'url': 'https://m.tiktok.com/v/168536242484064256.html', 'tags': ['music', 'guy']},
        # {'url': 'https://m.tiktok.com/v/260042274464849920.html', 'tags': ['music', 'guy']},
        # {'url': 'https://m.tiktok.com/v/248416887464890368.html', 'tags': ['music', 'interest']},
        # {'url': 'https://m.tiktok.com/v/201665145469550592.html', 'tags': ['music', 'interest']},
        # {'url': 'https://m.tiktok.com/v/6553010058043593743.html', 'tags': ['talent', 'music']},
        # {'url': 'https://m.tiktok.com/v/232027772674605056.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/53010275779518465.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/299888749465968640.html', 'tags': ['beauty', 'music']},
        # {'url': 'https://m.tiktok.com/v/284173589204058112.html', 'tags': ['beauty', 'music']},
        # {'url': 'https://m.tiktok.com/v/125168149292883968.html', 'tags': ['music']},
        # {'url': 'https://m.tiktok.com/v/45070660757917696.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/47966776.html', 'tags': ['comedy']},
        # {'url': 'https://m.tiktok.com/v/6548617911324382208.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/209481591864352768.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/219042779904065536.html', 'tags': ['animal', 'beauty']},
        # {'url': 'https://m.tiktok.com/v/316549936257613824.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/283103159877738496.html', 'tags': ['comedy', 'beauty']},
        # {'url': 'https://m.tiktok.com/v/266201596949417984.html', 'tags': ['relationship']},
        # {'url': 'https://m.tiktok.com/v/6552135489070044175.html', 'tags': ['fashion']},
        # {'url': 'https://m.tiktok.com/v/6528822906070242304.html', 'tags': ['dance']},
        # {'url': 'https://m.tiktok.com/v/6527809423232996367.html', 'tags': ['music']},
        # {'url': 'https://m.tiktok.com/v/237108383747723264.html', 'tags': ['music']},
        # {'url': 'https://m.tiktok.com/v/6572982332553170182.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/6558884261695329295.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/6563183362737982725.html', 'tags': ['beauty']},
        # {'url': 'https://m.tiktok.com/v/209805673235103744.html', 'tags': ['beauty', 'dance']},
        # {'url': 'https://m.tiktok.com/v/6572634489799838981.html', 'tags': ['girl', 'interest']},
        # {'url': 'https://m.tiktok.com/v/6539564951084733455.html', 'tags': ['comedy']},
    ]

    tiktok_list = [
        # 'https://t.tiktok.com/i18n/share/video/6580265528428858626/',
        # 'https://t.tiktok.com/i18n/share/video/6573845690898713858/',
        # 'https://t.tiktok.com/i18n/share/video/6579794852060335361/',
        # 'https://t.tiktok.com/i18n/share/video/6587516643545451778/',
        # 'https://t.tiktok.com/i18n/share/video/6573207385538563329/',
        # 'https://t.tiktok.com/i18n/share/video/6563967482669829377/',
        # 'https://t.tiktok.com/i18n/share/video/6586997618235149570/',
        # 'https://t.tiktok.com/i18n/share/video/6588530376761675010/',
        # 'https://t.tiktok.com/i18n/share/video/6587361444499557634/',
        # 'https://t.tiktok.com/i18n/share/video/6585436240890301698/',
        # 'https://t.tiktok.com/i18n/share/video/6573465827125759234/',
        # 'https://t.tiktok.com/i18n/share/video/6532717718234205441/',
        # 'https://t.tiktok.com/i18n/share/video/6516456880494087425/',
        # 'https://t.tiktok.com/i18n/share/video/6562064962489945345/',
        # 'https://t.tiktok.com/i18n/share/video/6591316472268590338/',
        # 'https://t.tiktok.com/i18n/share/video/6590670645711867138/',
        # 'https://t.tiktok.com/i18n/share/video/6590155631162821889/',
        # 'https://t.tiktok.com/i18n/share/video/6587231975981976833/',
        # 'https://t.tiktok.com/i18n/share/video/6573464717296143618/',
        # 'https://t.tiktok.com/i18n/share/video/6574736385675103489/',
        # 'https://t.tiktok.com/i18n/share/video/6591445284083993857/',
        # 'https://t.tiktok.com/i18n/share/video/6590604671033806081/',
        # 'https://t.tiktok.com/i18n/share/video/6580265353861926145/',
        # 'https://t.tiktok.com/i18n/share/video/6590116363400908034/',
        # 'https://t.tiktok.com/i18n/share/video/6573466291833670914/',
        # 'https://t.tiktok.com/i18n/share/video/6562467063074393346/',
        # 'https://t.tiktok.com/i18n/share/video/6590242718163668225/',
        # 'https://t.tiktok.com/i18n/share/video/6565860653947424001/',
        # 'https://t.tiktok.com/i18n/share/video/6571690913511247105/',
        # 'https://t.tiktok.com/i18n/share/video/6587297185799343361/',
        # 'https://t.tiktok.com/i18n/share/video/6573464911857323265/',
        # 'https://t.tiktok.com/i18n/share/video/6576564848610512130/',
        # 'https://t.tiktok.com/i18n/share/video/6580263500533206273/',
        # 'https://t.tiktok.com/i18n/share/video/6573452831271947522/',
        # 'https://t.tiktok.com/i18n/share/video/6576230334411574529/',
        # 'https://t.tiktok.com/i18n/share/video/6591604052671335681/',
        # 'https://t.tiktok.com/i18n/share/video/6587366470269799681/',
        # 'https://t.tiktok.com/i18n/share/video/6579129280947555586/',
        # 'https://t.tiktok.com/i18n/share/video/6574613557961297153/',
        # 'https://t.tiktok.com/i18n/share/video/6586139351439117569/',
        # 'https://t.tiktok.com/i18n/share/video/6590399438496206086/',
        # 'https://t.tiktok.com/i18n/share/video/6589649673454095621/',
        # 'https://t.tiktok.com/i18n/share/video/6591178038078082309/',
        # 'https://t.tiktok.com/i18n/share/video/6589768800332156166/',
        # 'https://t.tiktok.com/i18n/share/video/6591172822687550725/',
        # 'https://t.tiktok.com/i18n/share/video/6589782234834668806/',
        # 'https://t.tiktok.com/i18n/share/video/6585607433782037766/',
        # 'https://t.tiktok.com/i18n/share/video/6591189333305199878/',
        # 'https://t.tiktok.com/i18n/share/video/6591512246629698821/',
        # 'https://t.tiktok.com/i18n/share/video/6590395433695055110/',
        # 'https://t.tiktok.com/i18n/share/video/6587788417633881350/',
        # 'https://t.tiktok.com/i18n/share/video/6576169277739502850/',
        # 'https://t.tiktok.com/i18n/share/video/6590080652022910213/',
        # 'https://t.tiktok.com/i18n/share/video/6590770567178095877/',
        # 'https://t.tiktok.com/i18n/share/video/6589585646178798853/',
        # 'https://t.tiktok.com/i18n/share/video/6589665309110570245/',
        # 'https://t.tiktok.com/i18n/share/video/6589638684000128261/',
        # 'https://t.tiktok.com/i18n/share/video/6589696337363602693/',
        # 'https://t.tiktok.com/i18n/share/video/6589728512750390533/',
        # 'https://t.tiktok.com/i18n/share/video/6591502980506193158/',
        # 'https://t.tiktok.com/i18n/share/video/6589353297176431878/',
        # 'https://t.tiktok.com/i18n/share/video/6588495319548300549/',
        # 'https://t.tiktok.com/i18n/share/video/6591507708736703749/',
        # 'https://t.tiktok.com/i18n/share/video/6589743443176590597/',
        # 'https://t.tiktok.com/i18n/share/video/6590836257880804613/',
        # 'https://t.tiktok.com/i18n/share/video/6591119551201545477/',
        # 'https://t.tiktok.com/i18n/share/video/6589377737545223429/',
        # 'https://t.tiktok.com/i18n/share/video/6589900779887267077/',
        # 'https://t.tiktok.com/i18n/share/video/6586045090374880517/',
        # 'https://t.tiktok.com/i18n/share/video/6590005006408092934/',
        # 'https://t.tiktok.com/i18n/share/video/6588483553229540614/',
        # 'https://t.tiktok.com/i18n/share/video/6590864198824103173/',
        # 'https://t.tiktok.com/i18n/share/video/6590781890557381893/',
        # 'https://t.tiktok.com/i18n/share/video/6574549755358088454/',
        # 'https://t.tiktok.com/i18n/share/video/6589930842565381382/',
    ]

    def __init__(self, *a, **kw):
        super(TikTokSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        raw = dict()
        temp = self.channel_list.pop(0)
        raw['url'] = temp['url']
        raw['tags'] = temp['tags']
        yield Request(
            raw['url'],
            meta=raw,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_page
        )

    def parse_list(self, response):
        pass

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        # print response.body_as_unicode()
        tjson = json.loads(re.findall('var data = (.*?)\};', response.body_as_unicode())[0] + "}")
        print(tjson)
        if tjson['video']['has_watermark']:
            self.logger.warning('watermark warning!!!!!!!!')
        else:
            raw['source_url'] = response.url
            raw['publisher_id'] = tjson['author']['uid']
            raw['publisher'] = tjson['author']['nickname']
            raw['publisher_icon'] = [tjson['author']['avatar_thumb']['url_list'][0]]
            raw['publish_ts'] = tjson['create_time']
            raw['title'] = tjson['desc']
            raw['video'] = "https:" + tjson['video']['play_addr']['url_list'][0]
            raw['thumbnails'] = ["https:" + tjson['video']['cover']['url_list'][0]]
            raw['video_height'] = tjson['video']['height']
            raw['video_width'] = tjson['video']['width']

            raw['like_count'] = tjson['statistics']['digg_count']
            raw['share_count'] = tjson['statistics']['share_count']
            raw['view_count'] = tjson['statistics']['play_count']
            raw['comment_count'] = tjson['statistics']['comment_count']

            raw['keywords'] = []
            for item in tjson['text_extra']:
                raw['keywords'].append(item['hashtag_name'])

            raw['extra_info'] = dict()
            raw['extra_info']['raw_doc_id'] = tjson['aweme_id']
            pprint.pprint(raw)
