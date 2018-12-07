from scrapy import Selector, Request
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider


class thairath_channel(BaseSpider):
    name = 'thairath_channel'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    host_url = 'https://www.thairath.co.th/multimedia/video'
    category_list = []#list of dict
    channel_list = []
    dedup = set()

    def start_requests(self):
        yield Request(
            self.host_url,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_channel
        )

    def parse_channel(self, response):
        sel = Selector(response)
        for i in sel.xpath('//ul[@class="side-menu multimedia"]//li[@class="side-menu"]'):
            raw = dict()
            channel = 'https://www.thairath.co.th'+i.xpath('.//a//@href').extract()[0]
            if(channel[-3:]!='pol' and channel[-3:]!='eco' and channel[-7:]!='oversea'):
                raw['tags'] = channel.replace("https://www.thairath.co.th/multimedia/video?cat=","")
                raw['url'] = channel
                self.channel_list.append(raw)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(thairath_channel)
process.start()
print (thairath_channel.channel_list)