import copy
import json
import re
import requests
from pydispatch import dispatcher
from scrapy import signals, Request, Selector
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider

class mathai(BaseSpider):
    name = 'mathai'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    category_list = [

        {'url': 'https://video.sanook.com/channel/newsplusth/clip/category/normal/', 'tag': 'newsplusth'},
        #{'url': 'https://video.sanook.com/channel/cloud9_creation/clip/category/travel', 'tag': 'cloud9_creation'},
      #  {'url':'https://video.sanook.com/channel/kuichawshow/clip/category/normal','tag':'kuichawshow'}
    ]
    content_list = []
    result = []
    browse_times = 0
    browse_limit = 2

    def __init__(self, *a, **kw):
        super(mathai, self).__init__(*a, **kw)
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
        category_url = cur['url']
        raw = dict()
        raw['tags'] = cur['tag']
        raw['inlinks'] = [category_url]

        yield Request(
            category_url,
            #"https://video.sanook.com/player/1339665/",
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):

        raw = dict()
        raw.update(response.meta)

        sel = Selector(response)

        for i in sel.xpath('//div[@class="archive__article-wrap post-display four-col"]//article'):
            url = i.xpath('.//a[@title]//@href').extract()[0]
            raw['source_url'] = url
            time = i.xpath('.//time[@class="clip-time"]//text()').extract()
            if(len(time)>0):
                t = time[0]
            minute = int(t.split(":")[0])
            second = int(t.split(":")[1])
            duration = minute * 60 + second
            if duration<=120:
                raw['duration'] = duration
                id =url[-8:-1]
                raw['video'] = 'https://video.sanook.com/liveplay/{}.m3u8'.format(id)
                r = requests.get(raw['video'])

                #link = re.findall('https:(.*?)index', r.content)[0]#
                #link = "https:" + link[:-1]#
                #raw['link'] = link
                raw['views'] = i.xpath('.//span[@class="sukhumvitreg"]//text()').extract()[1]
                self.content_list.append(copy.deepcopy(raw))
        if self.browse_times < self.browse_limit:
            self.browse_times += 1
            if sel.xpath('//a[@rel="next"]'):

                next_page ='https://video.sanook.com/'+sel.xpath('//a[@rel="next"]//@href').extract()[0]


                yield Request(
                    next_page,
                    meta=raw,
                    headers=self.hd_page,
                    dont_filter=True,
                    callback=self.parse_list
                )

    def parse_page(self, response):
        print (444)
        raw = dict()
        raw.update(response.meta)

        sel = Selector(response)
        raw['like'] = sel.xpath('//span[@id="total_vote_good"]//text()').extract()[0]
        raw['not like'] = sel.xpath('//span[@id="total_vote_bad"]//text()').extract()[0]

        raw['title'] = re.findall('<meta property="og:title" content="(.*?)">', response.body)[0]
        #print (raw['title'])
        raw['thumbnail'] = re.findall('<meta property="og:image" content="(.*?)">',response.body)[0]
        raw['thumbnail']
        raw['created time']=re.findall('<meta name="SParse:publishtime" content="(.*?)"/>',response.body)[0]
        #print (raw['created time'])
        raw['keywords'] = re.findall('<meta name="SParse:keyword" content="(.*?)"/>',response.body)[0]
        #print (raw['keywords'])
        raw['editor'] = re.findall('<meta name="SParse:editor" content="(.*?)"/>',response.body)[0]
        #print (raw['editor'])


        self.result.append(copy.deepcopy(raw))




process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(mathai)
process.start()
print (mathai.result)
