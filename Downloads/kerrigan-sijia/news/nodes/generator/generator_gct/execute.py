from __future__ import print_function
from src.util import load_settings
from src.util.middleware import Middleware
from src.util.exception import IgnoreMessage
import json
import logging
import sys
import os
from kafka import KafkaConsumer, KafkaProducer
import base64
import time

resource_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, os.path.join(resource_path, './../..'))
sys.path.append(os.path.join(resource_path, './../../..'))

from news.spider_logger import *

# regions
REGION_CHINA = 'china'
REGION_ASIA = 'asia'
REGION_AMERICA = 'america'
REGION_EUROPE = 'europe'
REGION_GCT = 'gct'


class Generator(object):
    def __init__(self, settings, test_dir=None):
        if settings is None:
            self.settings = load_settings('settings')
            self.settings['TEST_MODE'] = True
            if test_dir:
                self.settings['TEST_DIR'] = test_dir
        else:
            self.settings = settings
        self.mw = Middleware.from_settings(self.settings)

    def map(self, mw, message):
        return mw.process(message)

    def filter(self, mw, message):
        if mw.process(message):
            return message

        raise IgnoreMessage('message filtered')

    def mapPartitions(self, mw, message):
        return mw.process([message])[0]

    def process_throughout(self, message):
        for middleware in self.mw.middlewares:
            api = middleware.api
            handler = getattr(self, api)
            try:
                message = handler(middleware, message)
            except IgnoreMessage:
                return

        logger = logging.getLogger(self.__class__.__name__)
        logger.info('%s Success' % json.loads(message)['account'])
        return message


def send2kafka(producer, dst_topic, message):
    # # msg_raw = json.dumps(
    # #     message,
    # #     ensure_ascii=False,
    # #     encoding='utf8',
    # #     sort_keys=True).encode('utf8')
    # base64msg = base64.b64encode(message)

    producer.send(dst_topic, message)
    pubdate = json.loads(message)['pubdate']
    with open('/pixdata/data/news/uploader_%s' % pubdate, 'a') as f:
        f.write(message + '\n')


if __name__ == '__main__':
    settings = load_settings('settings')
    generator = Generator(settings)
    consumer = KafkaConsumer(settings['SRC_TOPIC'],
                             bootstrap_servers=settings['BROKERS'],
                             group_id=(settings['SRC_TOPIC_GROUP_ID']))
    producer = KafkaProducer(bootstrap_servers=settings['BROKERS'])
    for index, msg in enumerate(consumer):
        processed_msg = generator.process_throughout(msg.value)

        if processed_msg:
            if json.loads(processed_msg)['region'] == REGION_ASIA:
                send2kafka(producer, settings['DST_TOPIC_AP'], processed_msg)
                logging.info('%s sent' % settings['DST_TOPIC_AP'])
            elif json.loads(processed_msg)['region'] == REGION_AMERICA:
                send2kafka(producer, settings['DST_TOPIC_USA'], processed_msg)
                logging.info('%s sent' % settings['DST_TOPIC_USA'])
            elif json.loads(processed_msg)['region'] == REGION_EUROPE:
                send2kafka(producer, settings['DST_TOPIC_EU'], processed_msg)
                logging.info('%s sent' % settings['DST_TOPIC_EU'])
            SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(processed_msg)['crawl_id']).info(
                source_url=json.loads(processed_msg)['source_url'],
                custom_info='generator sended')

    if index % 100:
        producer.flush()
