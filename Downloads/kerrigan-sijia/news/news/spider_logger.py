# -*- coding: utf-8 -*-
import datetime
import os
import json


class SpiderLogger():
    enable = True
    spider_name = ''
    crawl_id = ''
    spider_start_ts = ''
    spider_stop_ts = ''
    #home_path = r'/Users/LeonDu/spider/spider_log/'
    home_path = r'/home/xinyu.du/spider_log/'

    logger_path = ''

    def __init__(self, spider_name, crawl_id=''):
        self.spider_name = spider_name
        if not crawl_id:
            self.crawl_id = self.__generate_crawl_id(spider_name)
        else:
            self.crawl_id = crawl_id
        self.logger_path = self.home_path + self.crawl_id + '/'
        if not os.path.exists(self.logger_path):
            os.makedirs(self.logger_path)


    @staticmethod
    def create_spider_logger_by_crawl_id(crawl_id):
        spider_name = crawl_id[:-15]
        spider_logger = SpiderLogger(spider_name, crawl_id)
        return spider_logger

    def __generate_crawl_id(self, spider_name):
        crawl_id = '%s_%s' % (spider_name, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        return crawl_id

    def get_crawl_id(self):
        return self.crawl_id

    def __generate_message(self, spider_name, spider_state='crawling', source_url='', msg_type='info', source_state='',
                           source_info=''):
        raw = dict()
        raw['spider_name'] = self.spider_name
        raw['crawl_id'] = self.crawl_id
        raw['ts'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        raw['crawl_state'] = spider_state
        raw['type'] = msg_type
        raw['source_url'] = source_url
        raw['source_url_state'] = source_state
        return raw

    def spider_start(self, process_mode='normal_mode'):
        self.spider_start_ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = self.logger_path + 'spider_started'
        fp = open(file_path, 'w+')
        fp.write(str(process_mode))

        if process_mode == 'SIM_MODE':
            file_path = self.logger_path + 'sim_mode'
            fp = open(file_path, 'w+')
            fp.write(str(process_mode))

        raw = self.__generate_message(spider_name=self.spider_name, spider_state='start', msg_type='start')
        raw['info'] = 'spider_start'
        sorted(raw.keys())
        self.__message_write(raw)

        pass

    def spider_stop(self):
        self.spider_stop_ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = self.logger_path + 'spider_finished'
        fp = open(file_path, 'w+')
        fp.write(str(self.spider_stop_ts))

        raw = self.__generate_message(spider_name=self.spider_name, spider_state='stop', msg_type='stop')
        sorted(raw.keys())
        raw['info'] = 'spider_stop'
        self.__message_write(raw)
        pass

    def source_url_start(self, source_url, custom_info):
        raw = dict()
        raw = self.__generate_message(spider_name=self.spider_name, spider_state='running', msg_type='info')
        raw['source_url'] = source_url
        raw['info'] = custom_info
        sorted(raw.keys())
        self.__message_write(raw)
        pass

    def __message_write(self, msg, file_name='log'):
        if self.enable:
            file_path = self.logger_path + file_name
            fp = open(file_path, 'a+')
            fp.write(json.dumps(msg) + '\n')

    def source_url_start(self, source_url):
        pass

    def write_file(self):
        pass

    def info(self, source_url='', custom_info='', source_state='running'):
        raw = self.__generate_message(spider_name=self.spider_name, spider_state='running', msg_type='info')
        raw['source_url'] = source_url
        raw['info'] = custom_info
        raw['source_url_state'] = source_state
        sorted(raw.keys())
        self.__message_write(raw)
        pass

    def warning(self, source_url='', custom_info='', source_state='running'):
        raw = dict()
        raw = self.__generate_message(spider_name=self.spider_name, spider_state='running', msg_type='warning')
        raw['source_url'] = source_url
        raw['info'] = custom_info
        raw['source_url_state'] = source_state
        sorted(raw.keys())
        self.__message_write(raw)
        pass

    def error(self, failure='', response='', spider='', custom_info='', source_url='', source_state='error'):
        raw = dict()
        raw = self.__generate_message(spider_name=self.spider_name, spider_state='running',
                                      msg_type='error')
        raw['source_url'] = source_url
        raw['info'] = custom_info
        raw['traceback'] = ''
        if failure:
            raw['info'] = failure.getErrorMessage()
            raw['traceback'] = failure.getTraceback()
            raw['error_url'] = response.url
            if response.meta.get('article_info', ''):
                raw['source_url'] = response.meta.get('article_info', '')['source_url']
        raw['source_url_state'] = source_state
        sorted(raw.keys())
        self.__message_write(raw)
        pass

    def save_item(self, item):
        raw = dict()
        raw['ctid'] = item.get('dedup_key', '')
        raw['title'] = item.get('title', '')
        raw['duration'] = item.get('duration', '')
        raw['tags'] = item.get('raw_tags', '')
        raw['publisher_id'] = item.get('publisher_id', '')
        raw['publisher'] = item.get('publisher', '')
        raw['crawl_id'] = item.get('crawl_id', '')
        if raw['crawl_id'] != '':
            raw['spider_name'] = raw['crawl_id'][:-15]
            raw['ts'] = raw['crawl_id'].split('_')[-1]
        raw['source_url'] = item.get('source_url', '')
        raw['locale'] = item.get('locale', '')
        raw['account'] = item.get('account', '')

        if raw['account'] != '':
            raw['source_id'] = raw['account'].split('-')[0]
        raw['process_mode'] = item.get('process_mode', '')
        sorted(raw.keys())
        self.__message_write(raw, file_name='items')

    def log(self, source_url):
        pass

    def debug(self, source_url):
        pass

    def exception(self, source_url):
        pass
