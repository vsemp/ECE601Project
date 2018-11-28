# -*- coding: utf-8 -*-
from base_spider import BaseSpider
from spider_const import *
from abc import ABCMeta, abstractmethod, abstractproperty
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.http import FormRequest, Request
import logging
import time
import sys
from scrapy.conf import settings
from spider_logger import SpiderLogger
import os
from kafka import KafkaClient, SimpleProducer
import ConfigParser
import redis
from pymongo import MongoClient
import gridfs
import hashlib
import json
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from bs4.element import Comment, NavigableString, Tag
import struct


# 当前爬虫运行模式
class CommonSpiderBase(BaseSpider):
    __metaclass__ = ABCMeta
    name = 'comment_spider'
    # 确定国家
    locale = ''
    # 确定服务器位置
    region = ''
    process_mode = 'normal_mode'
    data_source_type = ''
    filter_failed_account = False
    feed_crawled_count = 0
    input_type = INPUT_TYPE_CRAWL

    # --TODO 解析定义
    # doc_id：目标页面唯一ID名，方便后续查找(必须放在最前面)
    # account：用于定义单条新闻爬取ID。
    #
    article_info_keys = ['doc_id', 'account', 'article_class', 'content', 'crawl_id', 'crawl_time', 'extra',
                         'html', 'input_type', 'keywords', 'locale', 'region', 'process_mode', 'publish_time',
                         'publisher',
                         'publisher_id', 'share_count', 'source_name', 'source_url', 'tags', 'thumbnails', 'title']

    table_accountid_files = {
        DATA_SOURCE_TYPE_WEIXIN: 'table_weixin_accountid',
        DATA_SOURCE_TYPE_NEWS: 'table_web_accountid',
        DATA_SOURCE_TYPE_TOUTIAO: 'table_toutiao_accountid',
        DATA_SOURCE_TYPE_VIDEO: 'table_video_accountid',
        DATA_SOURCE_TYPE_WEIBO: 'table_weibo_accountid',
        DATA_SOURCE_TYPE_COOTEK: 'table_cootek_accountid',
    }

    def __init__(self, *a, **kw):
        super(CommonSpiderBase, self).__init__(*a, **kw)
        logging.getLogger('kafka').setLevel(logging.INFO)
        logging.getLogger('PIL').setLevel(logging.INFO)
        self.spider_logger = SpiderLogger(spider_name=self.name)
        self.end_time = time.time()
        self.start_time = self.end_time - self.default_section
        self.logger.info('timestamp from: %s' %
                         time.strftime('%Y-%m-%d %X',
                                       time.localtime(self.start_time)))
        self.logger.info('timestamp to: %s' %
                         time.strftime('%Y-%m-%d %X',
                                       time.localtime(self.end_time)))
        self.load_config()
        self.init_accountid_table()
        self.init_redis()
        self.init_process_mode()
        self.init_mongodb()
        self.init_documents_mongodb()
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        dispatcher.connect(self.spider_error, signals.spider_error)
        if self.process_mode == PROCESS_MODE_TEST:
            self.init_test_mode()
        else:
            self.init_kafka()

    def load_config(self):
        conf = ConfigParser.ConfigParser()
        conf.read(self.get_config_path())
        self.conf = conf
        self.path_resource = conf.get('Paths', 'path_resource')
        self.path_result = conf.get('Paths', 'path_result')

    def get_config_path(self):
        path_current = os.path.realpath('.')
        path_trunk = path_current[:path_current.rfind('/news')]
        if settings.getbool('storage03'):
            config_path = '%s/news/conf/news_storage03.conf' % path_trunk
            return config_path
        config_path = '%s/news/conf/news_gct.conf' % path_trunk

        # if self.region == REGION_AMERICA:
        #     config_path = '%s/news/conf/news_es.conf' % path_trunk
        # elif self.region == REGION_ASIA:
        #     config_path = '%s/news/conf/news_tw.conf' % path_trunk
        # elif self.region == REGION_EUROPE:
        #     config_path = '%s/news/conf/news_eu.conf' % path_trunk
        # elif self.region == REGION_CHINA:
        #     config_path = '%s/news/conf/news_cn.conf' % path_trunk
        # elif self.region == REGION_GCT:
        #     config_path = '%s/news/conf/news_gct.conf' % path_trunk
        return config_path

    def init_accountid_table(self):
        if not self.data_source_type:
            return
        self.file_table_accountid = os.path.join(
            self.path_resource,
            self.table_accountid_files[self.data_source_type])
        self.table_accountid = {}
        for line in open(self.file_table_accountid):
            s = line.strip().split('\t', 1)
            if len(s) != 2:
                continue
            ac_name, ac_id = s
            self.table_accountid[ac_name] = ac_id

    def init_redis(self):
        redis_server = self.conf.get('Settings', 'REDIS_SERVER')
        redis_port = int(self.conf.get('Settings', 'REDIS_PORT'))
        redis_db = int(self.conf.get('Settings', 'REDIS_DB'))
        redis_db_news = int(self.conf.get('Settings', 'REDIS_DB_NEWS'))
        self.redis = redis.Redis(redis_server, redis_port, redis_db)
        self.redis_news = redis.Redis(redis_server, redis_port, redis_db_news)
        self.account_look_table = self.conf.get('Settings', 'ACCOUNT_LOOK_TABLE')
        self.source_url_table = self.conf.get('Settings', 'SOURCE_URL_TABLE')
        self.account_crawled_look_table = self.conf.get('Settings', 'ACCOUNT_CRAWLED_LOOK_TABLE')
        self.image_data_table = self.conf.get('Settings', 'IMAGE_DATA_TABLE')
        self.video_data_table = self.conf.get('Settings', 'VIDEO_DATA_TABLE')
        self.breaking_news_look_table = self.conf.get('Settings',
                                                      'BREAKING_NEWS_LOOK_TABLE')
        self.analyze_news_table = self.conf.get('Settings', 'ANALYZE_NEWS_TABLE')
        self.tags_model_version = self.conf.get('Settings', 'TAGS_MODEL_VERSION')
        self.kafka_topic_generator = self.conf.get('Settings', 'KAFKA_TOPIC_GENERATOR')

    def init_kafka(self):
        broker = self.conf.get('Settings', 'BROKER')
        kclient = KafkaClient(broker)
        self.producer = SimpleProducer(kclient, async=False)

    def init_mongodb(self):
        mongodb_server = self.conf.get('Settings', 'MONGODB_SERVER')
        mongodb_db = self.conf.get('Settings', 'MONGODB_DB')
        mongodb_collection = self.conf.get(
            'Settings', 'MONGODB_COLLECTION')
        mongodb_data_collection = self.conf.get(
            'Settings', 'MONGODB_DATA_COLLECTION')
        mongo_client = MongoClient(mongodb_server)
        mongo_db = mongo_client[mongodb_db]
        self.mongo_collection = mongo_db[mongodb_collection]
        self.mongo_invalid_url_collection = mongo_client['record']['invalid_url']
        self.mongo_fs = gridfs.GridFS(mongo_db)

    def init_documents_mongodb(self):
        conn = MongoClient('192.168.173.130', 27017)
        self.mongo_documents = conn['news']['documents']

    def spider_opened(self):
        self.spider_logger.spider_start(process_mode=self.process_mode)

    def spider_closed(self):
        self.spider_logger.spider_stop()

    def spider_error(self, failure, response, spider):
        self.spider_logger.error(response=response, failure=failure, spider=spider)

    def parse_raw(self, raw):
        logging.warning('parse_raw!!!')
        self.spider_logger.info(source_url=self.get_source_url_from_raw(raw), custom_info='source crawl finished')
        article_info = self.generate_article_info(raw)
        if article_info is None:
            logging.warning('article_info is None!!!')
            return
        account = article_info['account']
        message = self.generate_message(article_info)
        if message is None:
            self.spider_logger.error(source_url=article_info['source_url'], custom_info='generate_message failed')
            logging.error('Message is None: %s' % account)
            return
        else:
            self.send_msg(message)

    def is_source_url_exist(self, input_type, source_url):
        input_source_url = "%s_%s" % (input_type, source_url)
        if self.process_mode == PROCESS_MODE_TEST:
            return False
        elif self.process_mode == PROCESS_MODE_SIM:
            return False
        elif self.process_mode == PROCESS_MODE_UPDATE:
            return False
        else:
            is_exist = self.mongo_documents.find_one(
                {"_id": self.get_doc_id_from_source_url(source_url)}) is not None
            # if not is_exist:
            #     is_exist = bool(self.redis.hget(self.source_url_table, input_source_url))

            if is_exist:
                self.spider_logger.warning(source_url=source_url, custom_info='source_url exists',
                                           source_state='filted')
            return is_exist

    @abstractmethod
    def normalize_content(self, article_info):
        pass

    def generate_message(self, article_info):
        # TODO（xinyu.du@cootek.cn）感觉时间这个地方需要处理一下
        account = article_info['account']
        message = {'account': article_info['account'],
                   'article_class': article_info['article_class'],
                   'content': self.normalize_content(article_info),
                   'crawl_id': self.spider_logger.get_crawl_id(),
                   'crawl_time': article_info['crawl_time'],
                   'extra': article_info['extra'],
                   'html': article_info['html'],
                   'input_type': article_info['input_type'],
                   'keywords': article_info['keywords'],
                   'locale': article_info.get('locale', 'unknown'),
                   'region': article_info.get('region', 'unknown'),
                   'process_mode': article_info['process_mode'],
                   'publish_time': article_info['publish_time'],
                   'publisher': article_info['publisher'],
                   'publisher_id': article_info['publisher_id'],
                   'source_name': article_info['source_name'],
                   'tags': article_info['tags'],
                   'thumbnails': self.normalize_thumbnails(article_info),
                   'title': article_info['title'],
                   }
        message['share_count'] = article_info.get('share_count', -1)
        if not message['thumbnails']:
            self.spider_logger.error(source_url=article_info['source_url'],
                                     custom_info='generator (thumbnails) message error')
            logging.warning('generator (thumbnails) message error')

            return None

        return message

    # 放到子类实现
    @abstractmethod
    def normalize_thumbnails(self, article_info):
        pass

    def send_msg(self, message):
        logging.warning('send_msg!!!!')
        self.feed_crawled_count += 1
        account = message['account']
        self.logger.info('FeedCount: %d, Account: %s' %
                         (self.feed_crawled_count, account))
        message_json = json.dumps(message, ensure_ascii=False, sort_keys=True,
                                  encoding='utf8').encode('utf8')
        message['_id'] = account
        if self.process_mode == PROCESS_MODE_TEST:
            self.generator.process_throughout(message_json)
            return
        try:
            self.producer.send_messages(self.kafka_topic_generator, message_json)
            self.mongo_collection.replace_one({'_id': account}, message, True)
            self.spider_logger.info(source_url=message['url']['source_url'], custom_info='source send message')
            logging.warning(message_json)
        except Exception as e:
            self.spider_logger.error(source_url=message['url']['source_url'], custom_info='Failed to send message')
            self.logger.error(
                'Failed to send message %s: %s' % (account, str(e)))

    def record_account_crawled(self, account):
        self.redis.hset(self.account_crawled_look_table, account, 1)
        self.redis.hset(self.account_crawled_look_table + '_ts', account, int(time.time()))

    def generate_article_info(self, raw):
        article_info = {}
        for key in self.article_info_keys:
            article_info[key] = getattr(self, 'get_%s_from_raw' % key)(raw)
            if article_info[key] is None:
                logging.info('%s is None' % key)
                self.spider_logger.error(source_url=raw['source_url'], custom_info='article_info key %s is None' % key,
                                         )
                return None
            raw[key] = article_info[key]
        article_info['raw'] = raw
        return article_info

    def is_account_exists(self, account):
        if self.process_mode == PROCESS_MODE_TEST:
            return False
        elif self.process_mode == PROCESS_MODE_SIM:
            return False
        elif self.process_mode == PROCESS_MODE_UPDATE:
            return False
        else:
            if self.filter_failed_account:
                return self.is_account_crawled(account)
            else:
                return self.is_account_crawled_succeeded(account)

    def is_account_crawled(self, account):
        return bool(self.redis.hget(self.account_crawled_look_table, account))

    def is_account_crawled_succeeded(self, account):
        return bool(self.redis.hget(self.account_look_table, account))

    def init_process_mode(self):
        if settings.getbool('TEST_MODE'):
            self.process_mode = PROCESS_MODE_TEST
            return
        elif settings.getbool('SIM_MODE'):
            self.process_mode = PROCESS_MODE_SIM
            return
        elif settings.getbool('UPDATE_MODE'):
            self.process_mode = PROCESS_MODE_UPDATE
            return

    def init_test_mode(self):
        sys.path.append(self.get_generator_path())
        from execute import Generator
        # 用于存储测试模式下载的图文或者视频的位置，无参数则放在当前目录
        self.test_dir = settings.get('TEST_DIR', '.')
        self.generator = Generator(None, self.test_dir)
        if not os.path.isdir(self.test_dir):
            os.mkdir(self.test_dir)
        self.img_test_dir = os.path.join(self.test_dir, 'img')
        if not os.path.isdir(self.img_test_dir):
            os.mkdir(self.img_test_dir)

    def get_generator_path(self):
        generator_path = 'nodes/generator/generator_gct'
        # if self.region == REGION_AMERICA:
        #     generator_path = 'nodes/generator/generator_es'
        # elif self.region == REGION_ASIA:
        #     generator_path = 'nodes/generator/generator_tw'
        # elif self.region == REGION_EUROPE:
        #     generator_path = 'nodes/generator/generator_eu'
        # elif self.region == REGION_CHINA:
        #     generator_path = 'nodes/generator/generator_cn'
        # elif self.region == REGION_GCT:
        #     generator_path = 'nodes/generator/generator_gct'
        return generator_path

    def get_account_from_raw(self, raw):
        source = getattr(self, 'source', None) or self.name
        source_id = self._get_source_id(source)
        doc_id = raw['doc_id']
        return '%s%s-%s' % (self.data_source_type, source_id, doc_id)

    def _get_source_id(self, source):
        if isinstance(source, unicode):
            source = source.encode('utf8')
        if source not in self.table_accountid:
            open(self.file_table_accountid, 'a').write(
                source + '\t' + str(len(self.table_accountid)) + '\n')
        source_id = self.table_accountid.setdefault(
            source, str(len(self.table_accountid)))
        return source_id

    def get_content_from_raw(self, raw):
        return []

    def get_crawl_id_from_raw(self, raw):
        return self.spider_logger.get_crawl_id()

    def get_crawl_time_from_raw(self, raw):
        return int(time.time())

    def get_doc_id_from_source_url(self, source_url):
        dedup_key = struct.unpack("<Q", hashlib.md5(source_url.encode('utf8')).digest()[:8])[0]
        return str(dedup_key)

    def record_invalid_source_url(self, source_url, invalid_info):
        doc_id = self.get_doc_id_from_source_url(source_url)
        record = dict()
        record['_id'] = doc_id
        record['source_url'] = source_url
        record['invalid_info'] = invalid_info
        self.logger.warning("record_invalid_source_url %s:%s" % (source_url, invalid_info))
        self.mongo_invalid_url_collection.replace_one({'_id': record['_id']}, record, True)

    def is_source_url_invalid(self, source_url):
        if self.process_mode == PROCESS_MODE_TEST:
            return False
        elif self.process_mode == PROCESS_MODE_SIM:
            return False
        elif self.process_mode == PROCESS_MODE_UPDATE:
            return False
        else:
            self.logger.info('check_is_source_url %s:%s' % (source_url, self.get_doc_id_from_source_url(source_url)))
            item = self.mongo_invalid_url_collection.find_one(
                {"_id": self.get_doc_id_from_source_url(source_url)})
            self.logger.info(item)
            if item is not None:
                self.spider_logger.warning(source_url=source_url,
                                           custom_info='source_url invalid (%s)' % item['invalid_info'],
                                           source_state='filted')
                return True
            else:
                return False

    @abstractmethod
    def get_doc_id_from_raw(self, raw):
        return raw['doc_id']

    @abstractmethod
    def get_extra_from_raw(self, raw):
        return {}

    def get_html_from_raw(self, raw):
        return raw['response'].body_as_unicode()

    @abstractmethod
    def get_keywords_from_raw(self, raw):
        pass

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_region_from_raw(self, raw):
        return self.region

    def get_process_mode_from_raw(self, raw):
        return self.process_mode

    @abstractmethod
    def get_publish_time_from_raw(self, raw):
        return raw['publish_time']

    @abstractmethod
    def get_publisher_from_raw(self, raw):
        return raw['publisher']

    @abstractmethod
    def get_publisher_id_from_raw(self, raw):
        return raw['publisher_id']

    @abstractmethod
    def get_source_name_from_raw(self, raw):
        return self.source_name

    @abstractmethod
    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    @abstractmethod
    def get_tags_from_raw(self, raw):
        return raw['tags']

    def get_thumbnails_from_raw(self, raw):
        return []

    @abstractmethod
    def get_title_from_raw(self, raw):
        return raw['title']

    @abstractmethod
    def get_article_class_from_raw(self, raw):
        pass

    @abstractmethod
    def get_input_type_from_raw(self, raw):
        pass

    @abstractmethod
    def get_share_count_from_raw(self, raw):
        pass


if __name__ == '__main__':
    spider = CommonSpiderBase()
    spider.init_test_mode()
