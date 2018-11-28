import copy
import json
import re
from urllib import urlencode

import requests
from pydispatch import dispatcher
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import BaseSpider
from scrapy.http import Request
#from test_news_spider import TestNewsSpider


class reddit(BaseSpider):
    name = 'reddit'

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}
    channel_list = [
        {'url': 'https://www.reddit.com/r/funny/', 'tags': ['funny']},
        # 'https://www.reddit.com/r/worldnews/'
    ]
    after_token = ''
    sort_type = 'hot'

    reddit_channel_params = {
        'after': after_token,
        'sort': sort_type
    }

    browse_times = 0
    browse_limit = 3

    def __init__(self, *a, **kw):
        super(reddit, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.browse_times = 0
                self.reddit_channel_params['after'] = ""
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        channel_dict = self.channel_list.pop(0)
        raw = dict()
        raw['in_links'] = [channel_dict['url']]
        raw['tags'] = channel_dict['tags']
        raw['channel_name'] = re.findall("https://www.reddit.com/r/(.*?)/", channel_dict['url'])[0]
        print (channel_dict['url'])
        print (raw['channel_name'])
        target_url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/' + raw['channel_name'] + '?' + urlencode(
            self.reddit_channel_params)

       # print target_url
       # print raw['in_links'][0]
        yield Request(
            target_url,
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )


    def parse_list(self,response):
        raw = dict()
        raw.update(response.meta)
        print (111)
        print (type(response))
        t_json = json.loads(response.text)
        next_token = t_json['token']

        # first,get channel info
        raw['publisher_id'] = t_json['subreddits'].keys()[0]
        raw['subscriber_count'] = t_json['subreddits'][raw['publisher_id']]['subscribers']
        raw['publisher_icon'] = t_json['subreddits'][raw['publisher_id']]['icon']['url']
        raw['raw_tags'] = t_json['subredditAboutInfo'][raw['publisher_id']]['advertiserCategory']
        for key in t_json['posts'].keys():
            # print key
            item = t_json['posts'][key]
            if item['isLocked']:
               # print 'advertisement, drop!'
                continue
            if 'media' not in item or item['media'] is None:
                #print 'not media'
                continue
            media_type = item['media']['type']
            if media_type not in ['video', 'image', 'gifvideo']:
                continue
            raw['title'] = item['title']
            raw['publish_time'] = item['created'] / 1000
            raw['source_url'] = item['permalink']
            raw['domain'] = item['domain']
            raw['publisher'] = item['author']
            if media_type == 'image':
                raw['doc_id'] = key
                raw['content'] = []
                content_dict = dict()
                raw['thumbnails'] = [item['media']['resolutions'][-1]['url']]
                content_dict['img'] = item['media']['resolutions'][-1]['url']
                content_dict['text'] = ""
                content_dict['rich_content'] = ""
                raw['content'].append(content_dict)
                #print (raw)

        self.browse_times += 1
        if self.browse_times >= self.browse_limit:
            self.logger.info('browse_times is %s ' % self.browse_times)
            return

        self.reddit_channel_params['after'] = next_token
        target_url = 'https://gateway.reddit.com/desktopapi/v1/subreddits/' + raw['channel_name'] + '?' + urlencode(
            self.reddit_channel_params)
      #  print target_url
        yield Request(
            target_url,
            meta=raw,
            headers=self.hd_page,
            dont_filter=True,
            callback=self.parse_list
        )

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0)'
})
process.crawl(reddit)
process.start()


