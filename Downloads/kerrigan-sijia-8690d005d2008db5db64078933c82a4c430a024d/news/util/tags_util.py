# -*- coding: utf-8 -*-
import jieba.posseg
import ConfigParser
import base64
import redis
import json
import time
import sys
import os
from thrift.transport import TTransport, TSocket
from thrift.protocol import TCompactProtocol
sys.path.append('tags/src')
sys.path.append('tool')
from rpcservice import TagRPCService
from mail_sender import send_mail


PATH_CURRENT = os.path.realpath('.')
PATH_TRUNK = PATH_CURRENT[:PATH_CURRENT.rfind('/cn')]
CONFIG_NEWS = '%s/cn/config/news.conf' % PATH_TRUNK
parser_config = ConfigParser.ConfigParser()
parser_config.read(CONFIG_NEWS)
REDIS_SERVER = parser_config.get('Settings', 'REDIS_SERVER')
REDIS_PORT = int(parser_config.get('Settings', 'REDIS_PORT'))
REDIS_DB = int(parser_config.get('Settings', 'REDIS_DB'))
REDIS_DB_NEWS = int(parser_config.get('Settings', 'REDIS_DB_NEWS'))
REDIS_CLIENT = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_DB)
REDIS_CLIENT_NEWS = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_DB_NEWS)
TAGS_MODEL_VERSION = parser_config.get('Settings', 'TAGS_MODEL_VERSION')


class TagsClient:

    def __init__(self, server, port, retry_times, retry_interval):
        transport = TSocket.TSocket(server, port)
        self.tags_transport = TTransport.TBufferedTransport(transport)
        protocol = TCompactProtocol.TCompactProtocol(self.tags_transport)
        self.tags_client = TagRPCService.Client(protocol)
        self.tags_retry_times = retry_times
        self.tags_retry_interval = retry_interval

    def get_tags_from_news(self, news_info):
        tags, model_version = self.get_tags_from_redis(news_info['account'])
        if tags is not None:
            return tags, model_version
        contents = ''.join([content['text'] for content in news_info['content'] if 'text' in content])
        info = {
            'account': news_info['account'],
            'content_tokens': self.split_words(contents),
            'title_tokens': self.split_words(news_info['title']),
            'source': news_info['subtitle'],
            'subtitle': news_info['subtitle'],
        }
        info_json = json.dumps(info, ensure_ascii=False, sort_keys=True).encode('utf8')
        for times in range(self.tags_retry_times):
            try:
                tags_result = json.loads(self.get_tags_from_server(info_json))
            except TTransport.TTransportException:
                time.sleep(self.tags_retry_interval)
                continue
            if tags_result['status'] == 200:
                tags = []
                for tags_info in tags_result['tags']:
                    tags.append(tags_info[0])
                return tags, tags_result['model_version']
            else:
                subject = '{Matrix}{feeds}{tags client error}'
                message = 'Invalid Return Code %s' % tags_result['status']
                send_mail(subject, message)
                return None, ''
        subject = '{Matrix}{feeds}{lost tags server}'
        message = 'Server Lost\nSpider Name: %s\nRetry Times: %s\nRetry Interval: %s\n' % \
                  ('breaking_news', self.tags_retry_times, self.tags_retry_interval)
        send_mail(subject, message)
        return None, ''

    @staticmethod
    def get_tags_from_redis(account):
        model_version = REDIS_CLIENT.get(TAGS_MODEL_VERSION)
        raw = REDIS_CLIENT_NEWS.get(account)
        if not raw:
            return None, ''
        news_info = json.loads(base64.b64decode(raw))
        if not news_info.get('model_version', '') == model_version:
            return None, model_version
        return news_info.get('tags'), news_info.get('model_version', '')

    def get_tags_from_server(self, info_json):
        self.tags_transport.open()
        tags_result = self.tags_client.gen_tags(info_json)
        self.tags_transport.close()
        return tags_result

    @staticmethod
    def split_words(text):
        return [unicode(word) for word in jieba.posseg.cut(text)]
