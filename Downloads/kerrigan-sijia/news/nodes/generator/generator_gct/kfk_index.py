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
    # msg_raw = json.dumps(
    #     message,
    #     ensure_ascii=False,
    #     encoding='utf8',
    #     sort_keys=True).encode('utf8')
    logging.info(message)
    base64msg = base64.b64encode(message)
    logging.info(base64msg)
    producer.send(dst_topic, base64msg)
    pubdate = json.loads(message)['pubdate']
    with open('/pixdata/data/news/uploader_%s' % pubdate, 'a') as f:
        f.write(message + '\n')


if __name__ == '__main__':
    settings = load_settings('settings')
    generator = Generator(settings)
    consumer = KafkaConsumer("newsindexer",
                             bootstrap_servers=settings['BROKERS'],
                             group_id=(settings['SRC_TOPIC_GROUP_ID']))
    producer = KafkaProducer(bootstrap_servers=settings['BROKERS'])
    for index, msg in enumerate(consumer):
        logging.info(msg)
        if index % 100:
            producer.flush()
