import json

from scrapy import signals
from scrapy.crawler import CrawlerProcess
import re
import scrapy.spiders
from scrapy.selector import Selector
import requests
from scrapy.xlib.pydispatch import dispatcher

from test_news_spider import TestNewsSpider


class FunnyMesses(TestNewsSpider):
    name = 'FunnyMesses'
    allow_domains = ['funnymemess.com']
    count = 0
    channel_list = ['http://www.funnymemess.com/']
    result = []

    def __init__(self, *a, **kw):
        super(FunnyMesses, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)


    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        channel_url = self.channel_list.pop(0)
        raw = dict()
        raw['inlinks'] = channel_url
        yield scrapy.Request(
            channel_url,
            meta=raw,
           # headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )


    def parse_list(self, response):
        url_list = []

        page_list = ["1","2","3","4","5"]
        for i in page_list:
            post_dict = {
                'action': 'td_ajax_block',
                'td_atts': '{"limit":"","sort":"","post_ids":"","tag_slug":"","autors_id":"","installed_post_types":"",'
                           '"category_id":"","category_ids":"","custom_title":"Latest Post","custom_url":"",'
                           '"show_child_cat":"","sub_cat_ajax":"","ajax_pagination":"next_prev",'
                           '"header_color":"","header_text_color":"","ajax_pagination_infinite_stop":"",'
                           '"td_column_number":3,"td_ajax_preloading":"","td_ajax_filter_type":"",'
                           '"td_ajax_filter_ids":"","td_filter_default_txt":"All","color_preset":"",'
                           '"border_top":"","class":"td_uid_4_5bbc0217ae76e_rand","el_class":"","offset":"",'
                           '"css":"","live_filter":"","live_filter_cur_post_id":"","live_filter_cur_post_author":""',
                'td_block_id': 'td_uid_4_5bbc0217ae76e',
                '3': '3',
                'td_current_page': i,
                'block_type': 'td_block_12',
                'td_filter_value': '',
                'td_user_action': '',
            }

            r = requests.post('https://www.funnymemess.com/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=7.4',
                              data=post_dict, verify=False)
            target = 'td-module-thumb'
            target1 = "bookmark"
            start_index = [m.start() for m in re.finditer(target, r.content)]
            end_index = [m.start() for m in re.finditer(target1, r.content)]

            for i in range(len(start_index)):
                start = start_index[i] + 59 #check later
                end = end_index[2*i]-11
                url = "https://www.funnymemess.com/"+r.content[start:end]
                url_list.append(url)
        for i in url_list:
            url = response.urljoin(i)
           # print (url) #type: string
            items = dict()

            items['in_link'] = url

            yield scrapy.Request(url=url,meta={'items':items}, callback=self.parse_page) # check metas
    print (result)

    def parse_page(self, response):
        current_page = []
        sel = Selector(response)
        items = response.meta['items']

        # category
        link = items['in_link'].encode('ascii', 'ignore')
        category = link[28:-1]

        # image img_title
        if len(sel.xpath('//figure')) != 0:
            for i in sel.xpath('//figure'):
                img_infor = dict()
                img_source = i.xpath('.//img//@src').extract()
                img_title = i.xpath('.//figcaption[@class = "wp-caption-text"]//text()').extract()
                img_infor['in_link'] = items['in_link']
                img_infor['category'] = category
                img_infor['thumbnails'] = img_source
                img_infor['img_title'] = img_title
                current_page.append(img_infor)

        self.count += 1
        print (self.count)
        self.result.append(json.dumps(current_page))




