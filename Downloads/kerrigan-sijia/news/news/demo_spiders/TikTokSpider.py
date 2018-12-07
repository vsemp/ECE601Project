# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import signals
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher

from ..feeds_back_utils import *
import pprint

class TikTokSpider(scrapy.Spider):
    name = 'tiktok'
    # allowed_domains = ['http://www.alarabiya.net']
    # start_urls = ['http://http://www.bbc.com/arabic/middleeast/']
    download_delay = 0
    hd = {
        'build': '1516788764802',
        'language': 'zh_CN',
        'X-Request-Info5': 'eyJvcyI6ImFuZHJvaWQgNy4xLjEiLCJ2ZXJzaW9uIjoiNi41LjAiLCJzbGlkZXItc2hvdy1jb29raWUiOiJibDgyTlRFMk16azJNemN4TWpNek1qRTFOVEF6T2tOa1NGSTBjWEpaU0d4M2IxbFZkV3R3VEdVeWVXYzlQVHBoTUdabE1tUTVNbVkwTURRMFpEQmxaV0l6WmpFMU56TTVaRFEwTUdNek5EbzJOVEUyTXprMk16Y3hNak16TWpFMU5UQXoiLCJYLVJlcXVlc3QtSUQiOiI1Y2Y3ODgzYS04MDE4LTRlZDgtOWQ3NC04MDRlZjIwMjE3ZGMiLCJtZXRob2QiOiJHRVQiLCJ1cmwiOiJodHRwczpcL1wvYXBpLm11c2ljYWwubHlcL3Jlc3RcL3VzZXJcLzI2NDg5ODAzNTk4ODUyMDk2MD91c2VyX3ZvX3JlbGF0aW9ucz1hbGwiLCJvc3R5cGUiOiJhbmRyb2lkIiwiZGV2aWNlaWQiOiJhMGQ3MGU5ZDExYjk1OTQ2NmE5NDI0MmY5NjA4NmVhZGM3NTU0OSIsInRpbWVzdGFtcCI6MTUxNzIxODM1NjgyMH0=',
        'X-Request-Sign5': '01a6d89754cd16765203fc8e5d98967c26d8509e6b5e',
        'Authorization': 'M-TOKEN "hash"="NWNhYTdjZTkwMDAxMDAwZmUwNGRiNTcxNmIwMDE0MGYyZDM4ZmRjNTBkMDM0MGZlYzA1N2Q5ZWIxYjkzMzBiMTZiNDcxYTNlMWU4MmVlOGEzMjJlMmZmZWU1ZjIzYjVjNjIwYTkwYmUwM2IxYmNlMzYwNTA1NmRjZTJlNDU2YzkwYWZlZDVmYTczNDYyMzJkYmRlMTExYTQyODkyYmExMzc0OWE0YTRjMzkwYWRjMDM1NGJiNDQzYzI4OThhZGFkMWYwYzBkODY0ZTA3ZmM5M2IzYjAzZmRmODU0NTcxNzBmYzhiYzhhZTgzMGFmMjQyNGJjMTlmMzkxNmE0YzliNDJmZTZlM2EzOWJhMGI4NWJhMWE3ZDY4OTcyYjQ1NmQ1ZDI2ZGEzNGQ5YWVjOGE4ZTZmM2QyNzVmYmQ3ZmJiMTU5MDAzYTAwOThmNjU1M2JiODY4NDdmYmUwMjBhNDNlYWQ3ZGZlZjU5MmNhZDQwNjU3MjMwZjQ1OWY4NDdjMDkxZGIxYmViNDU1MTRlZGFmOA=="',
    }
    page = 0
    max_count = 20
    # channel_list = get_channel_list('like', 'Thailand')
    channel_list = [
        'https://t.tiktok.com/i18n/share/user/6544541372165133327/',

    ]

    def __init__(self, *a, **kw):
        super(TikTokSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.channel_list:
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        # url = 'https://api.musical.ly/rest/user/%s' % (re.findall('([0-9]+)', self.channel_list.pop())[-1])
        url = 'https://api.tiktokv.com/aweme/v1/aweme/post/?user_id=%s&count=%s&aid=1180&app_language=en' % (
            re.findall('user/([0-9]+)/', self.channel_list.pop())[0], self.max_count)
        r = requests.get(url, headers=self.hd, verify=False)
        json_data = r.json()
        for each in json_data['aweme_list']:
            raw = dict()
            raw['video'] = each['video']['play_addr']['url_list'][0]
            raw['video_width'] = each['video']['width']
            raw['video_height'] = each['video']['height']
            raw['uid'] = str(each['author_user_id'])
            raw['thumbnails'] = each['video']['cover']['url_list'][0]
            raw['duration'] = int(each['video']['duration']) / 1000
            raw['keywords'] = each['video_labels']
            raw['publisher_icon'] = each['author']['avatar_thumb']['url_list'][0]

            raw['like_count'] = 0
            raw['comment_count'] = 0
            raw['share_count'] = 0
            raw['view_count'] = 0




            # raw['source_url'] = each['videoUri']
            # raw['publisher'] = each['author']['nickName']
            # raw['doc_id'] = str(each['musicalId'])
            # # 生成唯一title
            # raw['title'] = each['author']['nickName'] + '_' + raw['doc_id']
            #
            print raw
        yield Request(
            'https://www.baidu.com/',
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
        pass

        # print url
        # yield requests.get(
        #     url,
        #     headers=self.hd,
        #     dont_filter=True,
        #     callback=self.parse_list
        # )

        # yield Request(
        #     url,
        #     headers=self.hd,
        #     dont_filter=True,
        #     callback=self.parse_list
        # )

        # def parse_list(self, response):
        #     json_data = json.loads(response.body)
        #     if json_data['success'] == True:
        #         video_list = json_data['result']['list']
        #         for each in video_list:
        #             raw = {}
        #             raw['source_url'] = each['videoUri']
        #             raw['uid'] = str(each['author']['userId'])
        #             raw['publisher'] = each['author']['nickName']
        #             raw['publisher_icon'] = each['author']['icon']
        #             raw['doc_id'] = str(each['musicalId'])
        #             # 生成唯一title
        #             raw['title'] = each['caption'] + '_' + raw['doc_id']
        #             raw['video'] = each['videoUri']
        #             raw['thumbnails'] = each['thumbnailUri']
        #             raw['video_width'] = each['width']
        #             raw['video_height'] = each['height']
        #             raw['duration'] = int(each['duration']) / 1000
        #             raw['likedNum'] = int(each['likedNum'])
        #             raw['commentNum'] = int(each['commentNum'])
        #             raw['shareNum'] = int(each['shareNum'])

        # raw['publisher_icon'] = json_data['result']['icon']


        # print raw
        # for category in categories:
        #     url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
        #     yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
        #                   callback=self.page)  # simulate login request

        # for category in categories:
        #     url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
        #     yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
        #                   callback=self.page)  # simulate login request

        # url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category, 1)
        #     yield Request(url, meta={'tag': categories[category], 'category_name': category, 'index': 1},
        #                   callback=self.page)  # simulate login request

        # test_url = 'http://www.alarabiya.net/ar/medicine-and-health/2017/11/26/%D9%87%D9%84-%D9%8A%D8%AA%D8%B3%D8%A8%D8%A8-%D8%AA%D8%B1%D9%85%D8%A8-%D9%81%D9%8A-%D8%B2%D9%8A%D8%A7%D8%AF%D8%A9-%D8%A3%D8%B9%D8%AF%D8%A7%D8%AF-%D8%A7%D9%84%D9%85%D8%B5%D8%A7%D8%A8%D9%8A%D9%86-%D8%A8%D8%A7%D9%84%D9%85%D9%84%D8%A7%D8%B1%D9%8A%D8%A7%D8%9F.html'
        # yield Request(test_url, callback=self.article)  # simulate login request
        pass

        # def parse_list(self, response):
        #     raw = {}
        #     raw['publisher'] = re.findall('"nick_name":"(.*?)"', response.body_as_unicode())[0]
        #     raw['uid'] = re.findall('"uid":"(.*?)"', response.body_as_unicode())[0]
        #
        #     post_url = 'https://like.video/bg_ci_index.php/live/share/getUserPost?u=%s&count=%s' \
        #                % (raw['uid'], self.max_request_video_count)
        #     post_list = requests.get(post_url).json()['post_list']
        #     for each in post_list:
        #         raw['source_url'] = each['share_url']
        #         yield Request(
        #             raw['source_url'],
        #             headers=self.hd,
        #             dont_filter=True,
        #             meta=raw,
        #             callback=self.parse_article
        #         )
        #         # print raw
        #
        # def parse_article(self, response):
        #     soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #     # try:
        #     #     subtitle = soup.find('div', attrs={'id': 'microformat'}).get_text().replace(' - YouTube', '').strip()
        #     # except Exception, e:
        #     #     self.logger.warning(e)
        #     #     self.logger.warning('no subtitle!')
        #     #     return
        #     #     time.sleep(5)
        #     #     yield Request(
        #     #         response.url,
        #     #         headers=self.hd,
        #     #         dont_filter=True,
        #     #         callback=self.parse_list
        #     #     )
        #     #     return
        #
        #     raw = response.meta
        #     raw['doc_id'] = str(response.url).split('/')[-1]
        #     # 生成唯一title
        #     raw['title'] = "%s(%s)" % (re.findall('<title>(.*?)</title>', response.body_as_unicode())[0], raw['doc_id'])
        #     raw['video'] = re.findall('(.*?)\?crc', soup.find('video', attrs={'id': 'videoPlayer'}).attrs['src'])[0]
        #     raw['image'] = soup.find('div', attrs={'class': 'video'}).find('div').find('img').get('src')
        #     raw['video_width'] = soup.find('video', attrs={'id': 'videoPlayer'}).attrs['width']
        #     raw['video_height'] = soup.find('video', attrs={'id': 'videoPlayer'}).attrs['height']
        #     raw['duration'] = 15
        #
        #     # raw['image'] = re.findall('(.*?)\?wmk_sdk', soup.find('div', attrs={'class': 'host clearfix'}).div.div.img.attrs['src'])[0]
        #     # raw['video'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)\?crc=', body)[0]
        #     # raw['video'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)\?crc=', body)[0]
        #     # raw['image'] = re.findall('<video id="videoPlayer" class="video-js" src="(.*?)?crc=', response.body_as_unicode())[0]
        #     print raw
        #
        # # print(raw)
        # # print response.body_as_unicode()
        # # has_more = tjson['has_more']
        # # max_cursor = tjson['max_cursor']
        # # if has_more:
        # #     url = 'https://www.douyin.com/aweme/v1/aweme/post/?user_id=%s&count=21&max_cursor=%d' % (
        # #     self.uid, int(max_cursor))
        # #     yield Request(
        # #         url,
        # #         headers=self.hd,
        # #         dont_filter=True,
        # #         callback=self.parse_list
        # #     )
        #
        # def page(self, response):
        #     bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #     items = bs.find_all("div", class_="item")
        #     if len(items) == 0:
        #         print("item == empty")
        #         return
        #     for item in items:
        #         title = item.find('a', class_='highline').text
        #         # subtitle = item.find('p', class_='eagle-item__summary').text
        #         create_time = item.find('div', class_='date').text
        #         page_url = self.base_url + item.find('a')['href']
        #         doc_id = (hashlib.md5(page_url.encode("utf8")).hexdigest())
        #         tag = response.meta['tag']
        #         meta = {'doc_id': doc_id,
        #                 'title': title,
        #                 'tag': tag,
        #                 # 'subtitle': subtitle,
        #                 'page_url': page_url,
        #                 'create_time': create_time}
        #         yield Request(page_url, meta=meta, callback=self.article)  # simulate login request
        #
        #     category_name = response.meta['category_name']
        #     index = response.meta['index']
        #     print("index:", index)
        #     if index > 2:
        #         return
        #     url = 'http://www.alarabiya.net/%s/archive.news.html?currentPage=%d' % (category_name, index + 1)
        #     yield Request(url, meta={'category_name': category_name, 'tag': tag, 'index': index + 1},
        #                   callback=self.page)  # simulate login request
        #
        # def article(self, response):
        #     raw = {}
        #     bs = BeautifulSoup(response.body_as_unicode(), 'lxml')
        #     #
        #     content_field = bs.find("article", class_="multi_articles")
        #     if content_field is None or len(content_field.find_all('video')) != 0:
        #         print(u"发现player视频页面!!!!!!")
        #         print(response.url)
        #         print('')
        #         return
        #
        #     if len(content_field.find_all("div", class_="article-default-image is-video")) != 0:
        #         print(u"发现youtube视频页面!!!!!!")
        #         print(response.url)
        #         print('')
        #         return
        #
        #     raw['title'] = response.meta['title']
        #     # raw['html'] = response.body
        #     raw['source_url'] = response.url
        #     raw['subtitle'] = 'alarabiya'
        #     raw['raw_tags'] = [response.meta['tag']]
        #     raw['doc_id'] = response.meta['doc_id']
        #     date_str = re.findall("(\d{4}/\d{1,2}/\d{1,2})", response.url)[0]
        #     raw['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date_str, '%Y/%m/%d'))
        #     raw['content'] = []
        #
        #     # 先存第一张图
        #     title_img = content_field.find('div', class_='article_img')
        #     image = title_img.find('img')
        #     if image:
        #         image_content = {'text': '', 'image': image['src']};
        #         if image_content not in raw['content']:
        #             raw['content'].append(image_content)
        #             # print({'text': '', 'image': image['src']})
        #
        #     content_ps = content_field.find('div', class_='article-body').find_all({'p', 'figure'})
        #     for p in content_ps:
        #         image = p.find('img')
        #         if image:
        #             image_content = {'text': '', 'image': image['src']};
        #             if image_content not in raw['content']:
        #                 raw['content'].append(image_content)
        #                 # print({'text': '', 'image': image['src']})
        #
        #         else:
        #             raw['content'].append(
        #                 {'text': p.text.replace(u'\xa0', '').replace(u'\u3000', '').replace(u'\u200e', '')})
        #             # print({'text': p.text.replace('\xa0', '').replace('\u3000', '').replace('\u200e', '')})
        #
        #     print(raw['title'])
        #     # print(raw['source_url'])
        #     print(raw['subtitle'])
        #     print(raw['raw_tags'])
        #     print(raw['doc_id'])
        #     print(raw['time'])
        #     print(raw['content'])
        #     with open('bbc_message_extra.txt', 'a') as f:
        #         f.write(json.dumps(raw) + '\n')
        #

        #     pass
