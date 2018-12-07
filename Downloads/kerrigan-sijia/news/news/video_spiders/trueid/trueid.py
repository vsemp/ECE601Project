import copy
import json
import re
import requests
from pydispatch import dispatcher
from scrapy import signals, Request, Selector
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider

class trueid(BaseSpider):
    name = 'mathai'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    category_list = [

        {'url': 'http://clip.trueid.net/funny/', 'tag': 'funny'},
        #{'url': 'http://clip.trueid.net/enjoyeating/', 'tag': 'enjoy'},
        #{'url':'http://clip.trueid.net/lifestyle/','tag':'character'},#
       # {'url':'http://clip.trueid.net/diy/', 'tag':'create'},
       # {'url': 'http://clip.trueid.net/kids/', 'tag': 'kids'},



    ]
    content_list = []
    result = []
    browse_times = 0
    browse_limit = 2
    result = []

    def __init__(self, *a, **kw):
        super(trueid, self).__init__(*a, **kw)
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

        elif self.category_list:
            self.browse_times = 0
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)
    def start_requests(self):
        cur = self.category_list.pop(0)
        category_url = cur['url']+'1'
        raw = dict()
        raw['tags'] = cur['tag']
        raw['inlinks'] = [category_url]

        yield Request(
            category_url,
            #'http://clip.trueid.net/detail/44243',
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        sel = Selector(response)
        self.browse_times+=1
        for i in sel.xpath('//ul[@class="row list-unstyled mb-0 w-100"]//li[@class="col-6 col-sm-3 col-lg-3 mb-2 d-flex"]'):
            sourse_url = i.xpath('.//a//@href').extract()[0]

            time = i.xpath('.//small[@class="times-duration"]//text()').extract()
            if len(time)>0 and any(char.isdigit() for char in time[0]):


                minute = int(time[0].split(":")[0])
                second = int(time[0].split(":")[1])
                duration = minute * 60 + second
                if duration<=120:
                    raw['source_url'] = sourse_url
                    raw['duration'] = duration
                    self.content_list.append(copy.deepcopy(raw))
        if self.browse_times<self.browse_limit:
            current_page =int(re.search(r'\d+', response.url).group())
            next_page = "http://clip.trueid.net/funny/"+str((current_page+1))
            yield Request(
                next_page,
                meta=raw,
                headers=self.hd_page,
                dont_filter=True,
                callback=self.parse_list
            )

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        sel = Selector(response)
        raw['title'] = re.findall('<title>(.*?)</title>',response.body)[0]
        raw['description'] = re.findall('<meta property="og:description" content="([\s\S]*?)"/>',response.body)[0]
        raw['publisher'] = re.findall('<meta property="article:publisher" content="(.*?)" />',response.body)[0]
        raw['thumbnail'] = re.findall('<meta property="og:image" content="(.*?)" />', response.body)[0]
        raw['keyword'] = re.findall('<meta name="keywords" content="(.*?)" />', response.body)[0]
        raw['video'] = sel.xpath('//div[@class="embed-responsive padding-box"]//iframe//@src').extract()[0]
        raw['created time'] = sel.xpath('//div[@class="article-info pull-right"]//small//text()').extract()[0]
        raw['view_count'] = sel.xpath('//div[@class="article-info pull-right"]//small//text()').extract()[1]
        self.result.append(copy.deepcopy(raw))
        print (raw)



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(trueid)
process.start()
print (trueid.result)