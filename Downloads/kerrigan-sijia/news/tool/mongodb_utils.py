from pymongo import MongoClient
import logging
import json
import time


DEFAULT_LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
DEFAULT_LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL = 'INFO'

logging.basicConfig(format=DEFAULT_LOG_FORMAT,
                    datefmt=DEFAULT_LOG_DATEFORMAT,
                    level=DEFAULT_LOG_LEVEL)

mongo_client = MongoClient()
mongo_db = mongo_client.news
mongo_collection = mongo_db.raw


def write_mongodb(raw):
    page_id = raw['account']
    raw['_id'] = page_id
    result = mongo_collection.replace_one({'_id': page_id}, raw, True)


def dump_mongodb(time_range=30*86400):
    now = int(time.time())
    time_start = now - time_range
    time_start_str = time.strftime('%Y-%m-%d %X', time.localtime(time_start))
    result = mongo_collection.find({'time': {'$gte': time_start_str}})
    return result

if __name__ == '__main__':
    result = dump_mongodb()
    print result.count()
    for i in result:
        print i['account']
