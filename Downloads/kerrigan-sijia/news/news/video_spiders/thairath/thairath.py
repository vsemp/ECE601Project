import copy
import json
import re
import requests
from pydispatch import dispatcher
from scrapy import signals, Request, Selector
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider

class thairath(BaseSpider):
    name = 'thairath'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    channel_list = [

        {'url': 'https://www.thairath.co.th/multimedia/video?cat=sport', 'tags': 'sport'},
        {'url': 'https://www.thairath.co.th/multimedia/video?cat=ent', 'tags': 'ent'}
    ]
    content_list = []
    result = []
    browse_times = 0
    browse_limit = 2


    def __init__(self, *a, **kw):
        super(thairath, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            self.logger.warning('content_list p'
                                'op ed')
            rq = Request(
                raw['source_url'],
                headers=self.hd_page,
                meta=raw,
                dont_filter=True,
                callback=self.parse_page
            )
            self.crawler.engine.crawl(rq, self)

        elif self.channel_list:
            self.browse_times = 0
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        cur = self.channel_list.pop(0)
        channel_url = cur['url']
        raw = dict()
        raw['tags'] = cur['tags']
        raw['inlinks'] = [channel_url]

        yield Request(
            channel_url+'&p=1',
            #'https://www.thairath.co.th/clip/140703',
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        self.browse_times += 1
        sel = Selector(response)
        raw = dict()
        raw.update(response.meta)
        High_light = sel.xpath('//div[@class="col-xs-12 col-sm-12 col-md-9 col-lg-9"]//a//@href').extract()[0]
        raw['source_url'] = 'https://www.thairath.co.th'+ High_light
        self.content_list.append(copy.deepcopy(raw))
        for i in sel.xpath('//div[@class="col-xs-6 col-sm-6 col-md-4 col-lg-4"]'):
                sourse_url = i.xpath('.//div[@class="media"]//a[@class="hasCaption"]//@href').extract()
                if(len(sourse_url)>0):
                    raw['source_url'] = 'https://www.thairath.co.th'+ sourse_url[0]
                    self.content_list.append(copy.deepcopy(raw))

        #print (self.content_list)
        if self.browse_times<self.browse_limit:
            next_link=sel.xpath('//li[@class="control"]//a//@href').extract()

            for link in next_link:
                next_page = 0
                for index in range(len(link) - 1, -1, -1):
                    if link[index]=='=':
                        next_page=int(link[index+1:])
                        break
                cur_page=0
                for index in range(len(response.url) - 1, -1, -1):
                    if response.url[index] == '=':
                        cur_page = int(response.url[index + 1:])
                        break

                if(cur_page<next_page):
                    yield Request(
                        'https://www.thairath.co.th'+link,
                        meta=raw,
                        headers=self.hd_page,
                        dont_filter=True,
                        callback=self.parse_list
                    )
                break

    def parse_page(self,response):
        raw = dict()
        print (response.url)
        raw.update(response.meta)
        sel = Selector(response)
        #duration = sel.xpath('//div[@class="vjs-duration vjs-time-control vjs-control"]').extract()###
        #print (duration)
        raw['title'] = re.findall('<meta property="og:title" content="(.*?)">', response.body)[0]
        # print (raw['title'])
        raw['thumbnail'] = re.findall('<meta property="og:image" content="(.*?)">', response.body)[0]
        raw['created time'] = re.findall('<meta property="og:article:published_time" content="(.*?)">', response.body)[0]
        raw['last_modified_time'] = re.findall('<meta http-equiv="last-modified" content="(.*?)">', response.body)[0]
        # print (raw['created time'])
        raw['keywords'] = re.findall('<meta name="keywords" content="(.*?)">', response.body)[0]
        vedio = sel.xpath('//source[@type="application/x-mpegURL"]//@src').extract()[0]
        raw['video'] = vedio.replace("hls_index","hls480")
        print (raw['video'])
        self.result.append(copy.deepcopy(raw))




process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(thairath)
process.start()
#print (thairath.content_list)
#print (len(thairath.content_list))
for i in thairath.result:
    print (i)