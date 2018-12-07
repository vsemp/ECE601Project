# -*- coding: utf-8 -*-

import logging

from lxml import etree
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..out_link_news import OutLinkNews
from ....spider_const import *


class SmoshSpider(OutLinkNews):
    name = 'smosh'
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'smosh'
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 2
    content_list = []
    channel_list = [
        'http://smosh.com/',
        'http://www.smosh.com/page/2',
        'http://www.smosh.com/page/3',

    ]

    def __init__(self, *a, **kw):
        super(SmoshSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.browse_times <= self.browse_limit and self.channel_list:
            self.browse_times += 1
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        channel_url = self.channel_list.pop()

        raw = dict()
        raw['inlinks'] = [channel_url]
        yield Request(
            url=channel_url,
            meta=raw,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)

        selector = etree.HTML(response.body)
        try:

            urls = selector.xpath('//li[@class="infinite-post"]/a/@href')
            thumbnails = selector.xpath(
                '//li[@class="infinite-post"]/a/div[@class="split-img"]/img/@data-img | //li[@class="infinite-post"]/a/div[@class="split-img"]/img/@src')
            thumbnails = [thumbnail for thumbnail in thumbnails if 'data:image' not in thumbnail]
            authors = selector.xpath('//li[@class="infinite-post"]/a/div/span/span/text()')
            titles = selector.xpath('//li[@class="infinite-post"]/a/div/h2/text()')
            subtitles = selector.xpath('//li[@class="infinite-post"]/a/div/p/text()')
            time = selector.xpath('//li[@class="infinite-post"]/a/div/span/text()')

            for index, url in enumerate(urls):
                if self.is_source_url_exist(self.input_type, url):
                    self.logger.info('source_url exists: ' + url)
                else:
                    raw['source_url'] = url
                    raw['thumbnails'] = [thumbnails[index]]
                    raw['author'] = authors[index]
                    raw['title'] = titles[index]
                    raw['subtitle'] = subtitles[index]
                    raw['time'] = self.month_prepration(time[index][3:])
                    raw['keywords'] = []
                    raw['tags'] = ['comedy']
                    raw['publisher'] = 'smosh'
                    self.parse_raw(raw)
        except:
            logging.error("the article fails to pass")

    def month_prepration(self, time):
        time_string = time.split(',')[1]
        month = self.month_transfer(time.split(',')[0].split()[0])
        date = time.split(',')[0].split()[1]
        if len(date) == 2:
            time_string += '-' + month + '-' + date
        else:
            time_string += '-' + month + '-' + '0' + date
        return time_string

    def month_transfer(self, month):

        if month == 'Jan.' or month == 'January' or month == 'JANUARY':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY' or month == 'February':
            return '02'
        elif month == 'Mar.' or month == 'MARCH' or month == 'March':
            return '03'
        elif month == 'Apr.' or month == 'APRIL' or month == 'April':
            return '04'
        elif month == 'May' or month == 'MAY' or month == 'May':
            return '05'
        elif month == 'June' or month == 'JUNE' or month == 'Jun':
            return '06'
        elif month == 'July' or month == 'JULY' or month == 'Jul':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST' or month == 'August':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER' or month == 'Sep' or month == 'September':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER' or month == 'October':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER' or month == 'November':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER' or month == 'December':
            return '12'
        else:
            logging.error('month parser failed')
