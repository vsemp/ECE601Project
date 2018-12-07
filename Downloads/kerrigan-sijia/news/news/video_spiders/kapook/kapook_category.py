from scrapy import Selector, Request
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider


class kapook_category(BaseSpider):
    name = 'kapook_category'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    host_url = 'https://world.kapook.com/clip'
    category_list = []#list of dict

    def start_requests(self):
        yield Request(
            self.host_url,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_category
        )

    def parse_category(self, response):

        sel = Selector(response)
        for i in sel.xpath('//div[@class="category_world"][@id="category_world1"]//a'):
           # print (i)
            raw = dict()
            url = 'https://world.kapook.com'+i.xpath('.//@href')[0].extract()
            tag = url.replace("https://world.kapook.com/clip/","")
            raw['url'] = url
            raw['tag'] = tag
            self.category_list.append(raw)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(kapook_category)
process.start()
print (kapook_category.category_list)