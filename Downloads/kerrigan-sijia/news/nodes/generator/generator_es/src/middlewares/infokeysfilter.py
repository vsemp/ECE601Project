# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import re
import time


class InfoKeysFilter(FilterMiddleware):
    def __init__(self, *a, **kw):
        super(InfoKeysFilter, self).__init__(*a, **kw)
        self.time_range = self.settings['TIME_RANGE']
        self.test_mode = self.settings.get('TEST_MODE', False)

    def process(self, item):
        return self.TargetUrlChecker(item) and \
               self.SubtitleChecker(item) and \
               self.SourceUrlChecker(item) and \
               self.TimeChecker(item) and \
               self.CrawlTimeChecker(item) and \
               self.SmallImgChecker(item) and \
               self.LargeImgChecker(item) and \
               self.AlbumImgChecker(item) and \
               self.AccountChecker(item) and \
               self.TitleChecker(item) and \
               self.ContentChecker(item) and \
               self.LocationChecker(item) and \
               self.HitCountChecker(item) and \
               self.CommentCountChecker(item) and \
               self.TagsChecker(item) and \
               self.RawTagsChecker(item)
        # and \
        # self.BreakingNewsChecker(item)

    def print_check_result(self, method_name, item, error_info):
        self.filter_standard_log(item, item['account'], method_name + ',' + error_info)
        '''
        self.logger.info('%(method_name)s,%(account)s,%(dedup_key)s,%(error_info)s'
                          % {
                              'method_name': method_name,
                              'account': item['account'],
                              'dedup_key': item['dedup_key'],
                              'error_info': error_info
                          })
        '''

    def TargetUrlChecker(self, item):
        value = item['target_url']
        formater = re.match('http://data-news\.cdn\.cootekservice\.com'
                            '/news/\d{4}-\d{2}-\d{2}/[1|2|3|4|5|6|9]\d+-.+\.',
                            value)
        if not formater:
            self.print_check_result('TargetUrlChecker', item,
                                    'wrong target url format: %s' % value)
            return False
        else:
            return True

    def SubtitleChecker(self, item):
        if item.get('is_jump2src', False):
            return True
        else:
            if len(item['subtitle']) < 2 or \
                            len(item['subtitle']) > 15:
                # TODO self.subtitle?
                self.print_check_result('SubtitleChecker', item,
                                        'wrong subtitle len: %s' % item['subtitle'].encode('utf8'))
                return False
            else:
                return True

    def SourceUrlChecker(self, item):
        if not item['source_url'].strip():
            self.print_check_result('SourceUrlChecker', item, 'null source url')
            return False
        else:
            return True

    def TimeChecker(self, item):
        if item.get('video'):
            return True
        else:
            formater = re.match('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                                item['time'])
            if not formater or \
                            len(formater.group(0)) != len(item['time']):
                self.print_check_result('TimeChecker', item, 'wrong time format')
                return False
            if item.get('target_news'):
                return True
            time_stamp = time.mktime(time.strptime(item['time'],
                                                   '%Y-%m-%d %X'))
            now_time = item.get('_latest_filetime', time.time())
            if time_stamp >= now_time or time_stamp <= now_time - self.time_range:
                self.print_check_result('TimeChecker', item, 'wrong time range')
                return False
            else:
                return True

    def CrawlTimeChecker(self, item):
        self.time_range = self.settings['TIME_RANGE']
        formater = re.match('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                            item['crawl_time'])
        if not formater or \
                        len(formater.group(0)) != len(item['crawl_time']):
            self.print_check_result('CrawlTimeChecker', item, 'wrong time format')
            return False
        else:
            return True

    def SmallImgChecker(self, item):
        value = item['small_img_url']
        if not value.strip():
            return True
        else:
            formater = re.match('http://data-news\.cdn\.cootekservice'
                                '\.com/news/\d{4}-\d{2}-\d{2}/img/'
                                '[1|2|3|4|5|6|9]\d+-.+@[\d+\-\d+\-\d+\-\d+a|]'
                                '*\d+w_\d+h_90Q',
                                value)
            if not formater or \
                            len(formater.group(0)) != len(value):
                self.print_check_result('SmallImgChecker', item, 'wrong image url format: %s' % value)
                return False
            else:
                return True

    def LargeImgChecker(self, item):
        value = item['large_img_url']
        if not value.strip():
            return True
        else:
            formater = re.match('http://data-news\.cdn\.cootekservice'
                                '\.com/news/\d{4}-\d{2}-\d{2}/img/'
                                '[1|2|3|4|5|6|9]\d+-.+@[\d+\-\d+\-\d+\-\d+a|]'
                                '*\d+w_\d+h_\d{2}Q',
                                # '*\d+w_\d+h_90Q',
                                value)
            if not formater or \
                            len(formater.group(0)) != len(value):
                self.print_check_result('LargeImgChecker', item, 'wrong image url format: %s' % value)
                return False
            else:
                return True

    def AlbumImgChecker(self, item):
        if not item.get('album_img_url'):
            return True
        else:
            if not isinstance(item['album_img_url'], list) \
                    or len(item['album_img_url']) != 3:
                self.print_check_result('AlbumImgChecker', item, 'wrong album image length')
                return False
            elif len(set(item['album_img_url'])) != len(item['album_img_url']):
                self.print_check_result('AlbumImgChecker', item, 'dup album image')
                return False
            else:
                for img_url in item['album_img_url']:
                    formater = re.match('http://data-news\.cdn\.cootekservice'
                                        '\.com/news/\d{4}-\d{2}-\d{2}/img/'
                                        '[1|2|3|5|6|9].+-.+(\.[a-zA-Z]+|)@\d+w_\d+h_90Q',
                                        img_url)
                    if not formater or len(formater.group(0)) != len(img_url):
                        self.print_check_result('AlbumImgChecker', item, 'wrong image url format')
                        return False
                return True

    def AccountChecker(self, item):
        formater = re.match('[1|2|3|4|5|6|9].+-.+',
                            item['account'])
        if not formater or \
                        len(formater.group(0)) != len(item['account']):
            self.print_check_result('AccountChecker', item, 'wrong page id format')
            return False
        else:
            return True

    def TitleChecker(self, item):
        illegal_word = [u'三级片', u'三级电影']
        cn_title = re.findall(ur'[\u4e00-\u9fa5]+', item['title'])
        if len(item['title'].strip()) <= 4 or \
                        sum([len(x) for x in cn_title]) <= len(item['title']) / 5:
            self.print_check_result('TitleChecker', item, 'wrong title length')
            return False
        elif illegal_word and \
                re.findall('|'.join(illegal_word), item['title']):
            self.print_check_result('TitleChecker', item, 'illegal content')
            return False
        else:
            return True

    def ContentChecker(self, item):
        illegal_word = []
        if item.get('is_jump2src', False):
            return True
        elif len(item['content'].strip()) == 0:
            if not (item['count_image'] or item.get('video', False)):
                self.print_check_result('ContentChecker', item, 'wrong content length')
                return False
        # del item['count_image']
        if illegal_word and \
                re.findall('|'.join(illegal_word), item['content']):
            self.print_check_result('ContentChecker', item, 'illegal content')
            return False
        else:
            return True

    def LocationChecker(self, item):
        if not isinstance(item['location'], unicode) or \
                        len(item['location']) < 1:
            self.print_check_result('LocationChecker', item, 'wrong location')
            return False
        else:
            return True

    def HitCountChecker(self, item):
        if not isinstance(item['hit_count'], int) or \
                        item['hit_count'] < 0:
            self.print_check_result('HitCountChecker', item, 'wrong hit_count')
            return False
        else:
            return True

    def CommentCountChecker(self, item):
        if not isinstance(item['comment_count'], int) or \
                        item['comment_count'] < 0:
            self.print_check_result('CommentCountChecker', item, 'wrong comment_count')
            return False
        else:
            return True

    def TagsChecker(self, item):
        key_name = 'tags'
        # Do NOT modify tag_all directly!
        # Modify resource/tag_classification first, then execute 'python tool/tag_translator.py'
        # Initialize tag_all
        tag_all = {
            u'财经',
            u'育儿',
            u'科技',
            u'社会',
            u'游戏',
            u'汽车',
            u'星座',
            u'时尚',
            u'文化',
            u'数码',
            u'教育',
            u'家居',
            u'娱乐',
            u'国际',
            u'军事',
            u'健康',
            u'体育',
            u'艺术',
            u'美食',
            u'旅游',
            u'搞笑',
            u'房产',
            u'宠物',
            u'漫画',
            u'彩票',
            u'婚姻',
            u'动漫',
            u'酒香',
            u'科学',
            u'足球',
            u'篮球',
            u'NBA',
            u'CBA',
            u'欧冠',
            u'中超',
            u'英超',
            u'西甲',
            u'意甲',
            u'德甲',
            u'排球',
            u'乒羽',
            u'网球',
            u'高尔夫',
            u'田径',
            u'游泳',
            u'赛车',
            u'养生',
            u'健身',
            u'中医',
            u'瑜伽',
            u'减肥',
            u'保健',
            u'海军',
            u'陆军',
            u'空军',
            u'军情',
            u'武器装备',
            u'影视',
            u'音乐',
            u'明星',
            u'八卦',
            u'综艺',
            u'家电',
            u'家具',
            u'装修',
            u'植物',
            u'厨卫',
            u'高考',
            u'中考',
            u'考研',
            u'资格考试',
            u'手机',
            u'电脑',
            u'历史',
            u'国学',
            u'读书',
            u'收藏',
            u'文物',
            u'国内游',
            u'港澳台',
            u'境外旅游',
            u'美体',
            u'时装',
            u'奢侈品',
            u'珠宝',
            u'手表',
            u'生肖',
            u'风水',
            u'命理',
            u'新车',
            u'SUV',
            u'汽车导购',
            u'汽车保养',
            u'手游',
            u'网游',
            u'电玩',
            u'电竞',
            u'cosplay',
            u'桌游',
            u'政务',
            u'法制',
            u'医患',
            u'反腐',
            u'天文',
            u'地理',
            u'生命',
            u'互联网',
            u'通信',
            u'软件',
            u'菜谱',
            u'烹饪',
            u'亲子',
            u'孕期',
            u'设计',
            u'摄影',
            u'书法',
            u'绘画',
            u'证券',
            u'外汇',
            u'理财',
            u'投资',
            u'基金',
            u'期货',
            u'创业',
            u'经济',
            u'能源',
            u'图集',
            u'视频',
            u'热门',
            u'触宝_美图',
            u'美女',
        }

        if self.test_mode:
            tag_all.add(u'测试标签')
        if not isinstance(item['tags'], list):
            self.print_check_result('TagsChecker', item, 'tags should be a list')
            return False
        else:
            for tag in item['tags']:
                if not isinstance(tag, list):
                    self.print_check_result('TagsChecker', item, 'tag should be a list')
                    return False
                else:
                    tag_name, tag_prob = tag
                    if len(tag_name) < 2:
                        self.print_check_result('TagsChecker', item, 'tag name is too short')
                        return False
                    elif tag_name not in tag_all:
                        self.print_check_result('TagsChecker', item, 'invalid tag name: ' + tag_name)
                        return False
                    elif not isinstance(tag_prob, float):
                        self.print_check_result('TagsChecker', item, 'invalid tag prob type')
                        return False
        tags = [x[0] for x in item['tags']]
        if len(set(tags)) != len(tags):
            self.print_check_result('TagsChecker', item, 'dup tag')
            return False
        else:
            return True

    def RawTagsChecker(self, item):
        if len(set(item['raw_tags'])) != len(item['raw_tags']):
            self.print_check_result('RawTagsChecker', item, 'dup tags')
            return False
        else:
            return True
