import copy
import json
import re

import requests
from numpy import split
from pydispatch import dispatcher
from scrapy import signals, Request, Selector
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider

class seeme(BaseSpider):
    name = 'seeme'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    channel_list = [
        {'url': 'https://seeme.me/ch/kaewpremier', 'tags': ['Entertainment']},
        {'url':'https://seeme.me/ch/bioscope','tags':['movie']}

    ]
    content_list = []

    browse_times = 0
    browse_limit = 2
    result = []
    def __init__(self, *a, **kw):
        super(seeme, self).__init__(*a, **kw)
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
            channel_url + '/clips',
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)


        sel = Selector(response)
        for i in sel.xpath('//div[@class="thumbnail-wrap"]'):
            url = i.xpath('.//a//@href').extract()[0]
            #print (url)
            raw['source_url'] = url
            time = str(i.xpath('.//span[@class="duration"]//text()').extract()[0])
            minute = int(time.split(":")[0])
            second = int(time.split(":")[1])
            duration = minute * 60 + second

            if(duration<=120):
                self.content_list.append(copy.deepcopy(raw))
        if self.browse_times<self.browse_limit:
            self.browse_times+=1
            if sel.xpath('//li//a[@rel = "next"]'):
                next_page = sel.xpath('//li//a[@rel="next"]//@href').extract()[0]

                yield Request(
                    next_page,
                    meta=raw,
                    headers=self.hd_page,
                    dont_filter=True,
                    callback=self.parse_list
                )



    def parse_page(self, response):

        r = requests.get(response.url, verify=False)
        target1 = 'playlist:'
        target2 = 'autoplay_countdown'
        start_index = [m.start() for m in re.finditer(target1, r.content)][0] + 11
        end_index = [m.start() for m in re.finditer(target2, r.content)][0] - 6
        infor = '[' + r.content[start_index:end_index] + ']'
        # print ((infor))
        r_json = json.loads(infor)
        raw = dict()
        raw.update(response.meta)
        for i in r_json:

            if i['mediaid'] == response.url:
                raw['duration'] = i['duration']

                # raw['embedurl'] = i['embedurl'] #the link of the another video

                for source in i['sources']:

                    if source['type'] == 'mp4':
                        raw['video'] = source['file']
                        raw['type'] = source['type']
                        raw['label'] = source['label']

        sel = Selector(r)
        context = sel.xpath('//script[@type="application/ld+json"]//text()').extract()[0]
        context = "[" + context + "]"
        context_json = json.loads(context)

        for i in context_json:
            raw['like'] = i['interactionCount']
            raw['created time'] = i['uploadDate']
            raw['thumbnail'] = i['thumbnailUrl']  #
            raw['description'] = i['description']
            raw['logo'] = i['publisher']['logo']['url']
            raw['logo_hight'] = i['publisher']['logo']['height']
            raw['logo_width'] = i['publisher']['logo']['width']
            raw['publisher'] = i['publisher']['name']
            raw['publisher_type'] = i['publisher']['@type']
            raw['title'] = i['name']
            self.result.append(raw)
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(seeme)
process.start()
for item in seeme.result:
    print (item)
    print ('\n')
