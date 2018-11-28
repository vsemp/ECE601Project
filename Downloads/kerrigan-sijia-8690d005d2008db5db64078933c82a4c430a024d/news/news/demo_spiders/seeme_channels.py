
import re
from scrapy import Selector, Request
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider


class seeme_channel(BaseSpider):
    name = 'seeme_channel'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    host_url = 'https://seeme.me/'
    category_list = []
    channel_list = []#list of dict
    def start_requests(self):

        yield Request(
            self.host_url,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_category
        )

    def parse_category(self, response):

        sel = Selector(response)
        for i in sel.xpath('//div[@id="mainmenu"]//li'):
            category_url = i.xpath('a//@href').extract()[0]
            self.category_list.append(category_url)

        for link in self.category_list:
            link = link+'/channels'
            yield Request(
                link,
                headers=self.hd_page,
                dont_filter=True,
                callback=self.parse_channel
            )

    def parse_channel(self,response):
        category = re.findall("https://seeme.me/c/(.*?)/channels", response.url)[0]
        sel = Selector(response)
        for i in sel.xpath('//div[@class="row channel-list block-grid-xs-2 block-grid-sm-4 block-grid-md-6"]'):
            channel_link = i.xpath('.//h3//a//@href').extract()
            for element in channel_link:
                raw = dict()
                raw['tags'] = category
                raw['url'] = element
                self.channel_list.append(raw)




process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(seeme_channel)
process.start()
print seeme_channel.channel_list


