import re
from scrapy import Selector, Request
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider


class mathai_channel(BaseSpider):
    name = 'mathai_channel'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    host_url = 'https://video.sanook.com/channel/recommend/'
    category_list = []#list of dict
    channel_list = []
    dedup = set()

    def start_requests(self):
        for page in range(1,3):
            yield Request(
                self.host_url+'page/'+str(page),
                headers=self.hd_page,
                dont_filter=True,
                callback=self.parse_channel
            )

    def parse_channel(self, response):
        sel = Selector(response)
        for i in sel.xpath('//div[@id="recommendedarchive_tab"]//article'):
            channel = dict()
            channel['url'] = i.xpath('.//a//@href').extract()[0]+ 'clip/'
            channel['channel'] = i.xpath('.//a//@title').extract()[0]
            self.channel_list.append(channel)
        print (len(mathai_channel.channel_list))
        for ch in self.channel_list:
            url = ch['url']
            if url not in self.dedup:
                self.dedup.add(url)
                yield Request(
                    url,
                    meta = ch,
                    headers=self.hd_page,
                    dont_filter=True,
                    callback=self.parse_category
                )

    def parse_category(self, response):
        #print (response.url)
        #print (111)
        raw = dict()
        raw.update(response.meta)
        tag = raw['channel']
        sel = Selector(response)
        for i in sel.xpath('//div[@class="col span-2"]//option//@value').extract()[1:]:
            content = dict()
            content['url'] = 'https://video.sanook.com'+i
            content['tag'] =tag
            self.category_list.append(content)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(mathai_channel)
process.start()
print (len(mathai_channel.category_list))

for m in mathai_channel.category_list:
   print (m)
   print ('\n')