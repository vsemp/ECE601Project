# from youtube_base import YoutubeSpiderBase
# from ...spider_const import *
# from pymongo import MongoClient
# from scrapy.conf import settings
# import hashlib
# from scrapy.http import Request
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy import signals
# from pymongo import MongoClient
# import json
# import lxml
# import re
# from tools.statistic import YoutubeStatistic
# import pymongo
#
#
# class YoutubeSpider(YoutubeSpiderBase):
#     name = 'youtube_fix_view_count'
#     region = REGION_AMERICA
#     locale = LOCALE_USA_ENGLISH
#     locale_full_name = 'United States of America'
#     input_type = INPUT_TYPE_CRAWL
#     duration_limit = 60 * 60
#     # conn = MongoClient(
#     #     'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
#     #     readPreference="primary")
#     conn = 'localhost:27017'
#     db = conn.news
#     my_set = db.documents
#
#     content_list = []
#
#     def __init__(self, *a, **kw):
#         super(YoutubeSpiderBase, self).__init__(*a, **kw)
#         for i in self.my_set.find({"$and": [{"source_name": "youtube"}, {"view_count": {"$exists": False}}]}):
#
#             hash_value = settings.getint("hash_value", default=-1)
#             hash_total = settings.getint("hash_total", default=-1)
#
#             source_hash = int(hashlib.md5(str(i['source_url'])).hexdigest(), 16)
#             if hash_value != -1 and hash_total != -1:
#                 if source_hash % hash_total != hash_value:
#                     continue
#                 else:
#                     pass
#                     # self.logger.warning("hash pick!")
#             self.content_list.append(i['source_url'])
#         self.logger.info("content_list len is %s" % len(self.content_list))
#         dispatcher.connect(self.spider_idle, signals.spider_idle)
#
#     def spider_idle(self):
#         if self.content_list:
#             for rq in self.start_requests():
#                 self.crawler.engine.crawl(rq, self)
#
#     def start_requests(self):
#         source_url = self.content_list.pop(0)
#         raw = dict()
#         raw['source_url'] = source_url
#         yield Request(
#             raw['source_url'],
#             headers=self.hd_page,
#             meta=raw,
#             callback=self.parse_page
#         )
#
#     def parse_page(self, response):
#         # print response.url
#         body_instance = response.body_as_unicode()
#         tree = lxml.html.fromstring(body_instance)
#         raw = dict()
#         raw.update(response.meta)
#
#         display_selector = '//*[@id="watch7-main-container"]/div[@id="watch7-main"]/div[@id="watch7-content"]/meta[@itemprop="interactionCount"]/@content'
#         raw['source_url'] = response.url
#         raw['view_count'] = int(tree.xpath(display_selector)[0].replace(',', ''))
#
#         raw['like_count'] = int(
#             tree.xpath('//*[@id="watch8-sentiment-actions"]/span/span[1]/button/span/text()')[0].replace(',', ''))
#         raw['dislike_count'] = int(
#             tree.xpath('//*[@id="watch8-sentiment-actions"]/span/span[3]/button/span/text()')[0].replace(',', ''))
#
#         raw['extra'] = dict()
#         raw['share_count'] = -1
#         raw['comment_count'] = -1
#         try:
#             video_id = response.url.split('v=')[-1]
#             static_html = YoutubeStatistic.fetch_statistic_page(video_id=video_id)
#             tjson = json.loads(YoutubeStatistic.extract_statistics(static_html.encode('utf8')))[0]
#             raw['share_count'] = int(tjson['shares']['cumulative']['opt']['vAxis']['maxValue'])
#             raw['share_peak'] = tjson['shares']['daily']['opt']['vAxis']['maxValue']
#             # raw['share_array'] = tjson['shares']['daily']['data']
#
#             raw['view_count'] = int(tjson['views']['cumulative']['opt']['vAxis']['maxValue'])
#             raw['view_peak'] = tjson['views']['daily']['opt']['vAxis']['maxValue']
#             # raw['view_array'] = tjson['views']['daily']['data']
#
#             raw['subscriber_count'] = tjson['subscribers']['cumulative']['opt']['vAxis']['maxValue']
#             raw['subscriber_peak'] = tjson['subscribers']['daily']['opt']['vAxis']['maxValue']
#             raw['subscriber_array'] = tjson['subscribers']['daily']['data']
#             watch_time_str = re.findall("<span class=\"menu-metric-value\">(.*?)</span>", static_html)[0]
#             raw['watch_time_arg'] = int(watch_time_str.split(":")[0]) * 60 + int(watch_time_str.split(":")[1])
#             raw['comment_count'] = int(YoutubeStatistic.get_comments_count(video_id))
#
#             raw['extra']['view_peak'] = raw['view_peak']
#             raw['extra']['share_peak'] = raw['share_peak']
#             raw['extra']['subscriber_peak'] = raw['subscriber_peak']
#             raw['extra']['subscriber_count'] = raw['subscriber_count']
#             raw['extra']['watch_time_arg'] = raw['watch_time_arg']
#             raw['extra']['dislike_count'] = raw['dislike_count']
#
#         except Exception, e:
#             pass
#
#         self.my_set.update({"source_url": raw['source_url']}, {'$set': {"view_count": raw['view_count']}}, multi=True)
#         self.my_set.update({"source_url": raw['source_url']}, {'$set': {"comment_count": raw['comment_count']}},
#                            multi=True)
#         self.my_set.update({"source_url": raw['source_url']}, {'$set': {"like_count": raw['like_count']}}, multi=True)
#         self.my_set.update({"source_url": raw['source_url']}, {'$set': {"share_count": raw['share_count']}}, multi=True)
#         self.my_set.update({"source_url": raw['source_url']}, {'$set': {"dislike_count": raw['dislike_count']}},
#                            multi=True)
#         # self.my_set.update({"source_url": raw['source_url']}, {'$set': {"extra": raw['extra']}}, multi=True)
#         self.logger.info("%s_updated,view_count is %s" % (raw['source_url'], raw['view_count']))
