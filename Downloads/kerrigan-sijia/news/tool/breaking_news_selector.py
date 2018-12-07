#! /usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import commands
import base64
import psutil
import jieba
import redis
import copy
import json
import time
import sys
import os
import re
import pickle
import logging

from kafka import KafkaClient, SimpleProducer
from readability import Document
from pymongo import MongoClient
from bs4 import BeautifulSoup
from gensim import corpora

from util.tags_util import TagsClient
sys.path.append('feeds/generator/src/util')
from breaking_news_util import BreakingNewsDetector, \
    add_duration, detect_keywords
sys.path.append('tags/src')
from rpcservice import TagRPCService

DEFAULT_LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
DEFAULT_LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL = 'INFO'
logging.basicConfig(format=DEFAULT_LOG_FORMAT,
                    datefmt=DEFAULT_LOG_DATEFORMAT,
                    level=DEFAULT_LOG_LEVEL)
logging.getLogger('kafka').setLevel(logging.ERROR)
logging.getLogger('gensim').setLevel(logging.ERROR)
logging.getLogger('readability').setLevel(logging.WARNING)
logging.getLogger('jieba').setLevel(logging.INFO)


PATH_CURRENT = os.path.realpath('.')
PATH_TRUNK = PATH_CURRENT[:PATH_CURRENT.rfind('/cn')]
CONFIG_NEWS = '%s/cn/config/news.conf' % PATH_TRUNK
parser_config = ConfigParser.ConfigParser()
parser_config.read(CONFIG_NEWS)
PATH_RESOURCE = parser_config.get('Paths', 'path_resource')
REDIS_SERVER = parser_config.get('Settings', 'REDIS_SERVER')
REDIS_PORT = int(parser_config.get('Settings', 'REDIS_PORT'))
REDIS_DB = int(parser_config.get('Settings', 'REDIS_DB'))
REDIS_DB_NEWS = int(parser_config.get('Settings', 'REDIS_DB_NEWS'))
REDIS_CLIENT = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_DB)
REDIS_CLIENT_NEWS = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_DB_NEWS)
HASHES_BREAKING_NEWS = parser_config.get(
    'Settings', 'BREAKING_NEWS_LOOK_TABLE')
HASHES_BREAKING_NEWS_ACCOUNT = parser_config.get(
    'Settings', 'BREAKING_NEWS_ACCOUNT_LOOK_TABLE')
RESULT_BREAKING_NEWS = parser_config.get(
    'Settings', 'RESULT_BREAKING_NEWS_TABLE')
BROKER = parser_config.get('Settings', 'BROKER')
MONGODB_SERVER = parser_config.get('Settings', 'MONGODB_SERVER')
MONGODB_DB = parser_config.get('Settings', 'MONGODB_DB')
MONGODB_COLLECTION = parser_config.get('Settings', 'MONGODB_COLLECTION')
TAGS_SERVER = parser_config.get('Settings', 'TAGS_SERVER')
TAGS_PORT = int(parser_config.get('Settings', 'TAGS_PORT'))
TAGS_RETRY_TIMES = int(parser_config.get('Settings', 'TAGS_RETRY_TIMES'))
TAGS_RETRY_INTERVAL = int(parser_config.get('Settings', 'TAGS_RETRY_INTERVAL'))
TAGS_CLIENT = TagsClient(
    TAGS_SERVER, TAGS_PORT, TAGS_RETRY_TIMES, TAGS_RETRY_INTERVAL)


def init_corpora():
    words_info = {}
    timestamp = int(time.time())
    for breaking_news in REDIS_CLIENT.hkeys(HASHES_BREAKING_NEWS):
        data = json.loads(
            REDIS_CLIENT.hget(HASHES_BREAKING_NEWS, breaking_news))
        if data['duration'] < timestamp:
            REDIS_CLIENT.hdel(HASHES_BREAKING_NEWS, breaking_news)
            continue
        document = Document(base64.b64decode(data['content']))
        soup = BeautifulSoup(document.summary(), 'lxml')
        raw = ''.join(soup.stripped_strings)
        words = filter(lambda segments: re.findall(ur'[\u4e00-\u9fa5]{2,}',
                                                   segments), jieba.cut(raw))
        for location in data['location']:
            words_info.setdefault(location, []).append(words)
    corpora_result = {}
    for location in words_info:
        if len(words_info[location]) <= 1:
            continue
        dictionary = corpora.Dictionary(words_info[location])
        corpus = [dictionary.doc2bow(words) for words in words_info[location]]
        corpora_result['dict_%s' % location] = pickle.dumps(dictionary)
        corpora_result['mm_%s' % location] = pickle.dumps(corpus)
    REDIS_CLIENT.set(RESULT_BREAKING_NEWS, json.dumps(corpora_result))


def select_breaking_news():
    breaking_news_detector = {}
    dictionary = {}
    corpus = {}
    pickle_dict = json.loads(REDIS_CLIENT.get('feeds_breaking_news_result'))
    for key in pickle_dict:
        if 'dict_' in key:
            dictionary[key.replace('dict_', '')] = pickle.loads(
                pickle_dict[key])
        elif 'mm_' in key:
            corpus[key.replace('mm_', '')] = pickle.loads(pickle_dict[key])
    set_location = set(dictionary.keys()).intersection(set(corpus.keys()))
    for location in set_location:
        breaking_news_detector[location] = BreakingNewsDetector(
            dictionary[location], corpus[location])
    breaking_news_info = []
    time_lowerbound = time.strftime(
        '%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 24 * 60 * 60))
    for account in REDIS_CLIENT_NEWS.keys('*'):
        try:
            news_info = json.loads(
                base64.b64decode(REDIS_CLIENT_NEWS.get(account)))
        except TypeError:
            continue
        if news_info['time'] < time_lowerbound:
            continue
        list_location, duration = detect_keywords(news_info)
        if list_location:
            breaking_news_info.append((news_info, list_location, duration, 1))
            continue
        list_location = []
        m = re.findall(ur'[\u4e00-\u9fa5]+', news_info['content'])
        text = ' '.join(m)
        content = [x for x in jieba.cut(text)]
        for location in set_location:
            content_copy = copy.deepcopy(content)
            if breaking_news_detector[location].judge_similarity(content_copy):
                list_location.append(location)
        if list_location:
            breaking_news_info.append((news_info, list_location, None, 0))
    REDIS_CLIENT.delete(HASHES_BREAKING_NEWS_ACCOUNT)
    for breaking_news in breaking_news_info:
        account_info = {
            'location': breaking_news[1],
            'duration': breaking_news[2],
            'mode': breaking_news[3],
        }
        content = json.dumps(
            account_info, sort_keys=True, encoding='utf-8').encode('utf8')
        REDIS_CLIENT.hset(
            HASHES_BREAKING_NEWS_ACCOUNT, breaking_news[0]['account'], content)
        logging.info(breaking_news[0]['account'])
    for breaking_news in breaking_news_info:
        update_breaking_news(breaking_news[0])


def update_breaking_news(news_info):
    mongo_client = MongoClient(MONGODB_SERVER)
    mongo_db = mongo_client[MONGODB_DB]
    mongo_collection = mongo_db[MONGODB_COLLECTION]
    news_info_mongo = mongo_collection.find_one({'_id': news_info['account']})
    if news_info_mongo is None:
        return
    news_info_mongo['tags'], news_info_mongo[
        'model_version'] = TAGS_CLIENT.get_tags_from_news(news_info_mongo)
    if news_info_mongo['tags'] is None:
        return
    news_json = json.dumps(
        news_info_mongo,
        ensure_ascii=False,
        encoding='utf-8',
        sort_keys=True).encode('utf8')
    kafka_producer = SimpleProducer(KafkaClient(BROKER), async=False)
    kafka_producer.send_messages('feedsgenerator', news_json)


if __name__ == '__main__':
    process_breaking_news = commands.getstatusoutput(
        'ps aux|grep -E "python tool/breaking_news_selector.py$"'
        '|grep -v grep')[-1].splitlines()
    if len(process_breaking_news) > 1:
        for process in process_breaking_news:
            process_id = int(process.split()[1])
            if process_id == psutil.Process().pid:
                continue
            process_info = psutil.Process(process_id)
            if process_info.create_time() + 60 * 50 < int(time.time()):
                process_info.kill()
            else:
                sys.exit(0)
    init_corpora()
    select_breaking_news()
