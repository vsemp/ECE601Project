import ConfigParser
import gridfs
import time
import logging
import os
import sys
from pymongo import MongoClient
from datetime import datetime, timedelta


DEFAULT_LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
DEFAULT_LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL = 'INFO'

logging.basicConfig(format=DEFAULT_LOG_FORMAT,
                    datefmt=DEFAULT_LOG_DATEFORMAT,
                    level=DEFAULT_LOG_LEVEL)

PATH_CURRENT = os.path.realpath('.')
PATH_TRUNK = PATH_CURRENT[:PATH_CURRENT.rfind('/news')]
if sys.argv[1] == 'asia_pacific':
    CONFIG_NEWS = '%s/news/config/news_tw.conf' % PATH_TRUNK
elif sys.argv[1] == 'usa':
    CONFIG_NEWS = '%s/news/config/news_es.conf' % PATH_TRUNK
elif sys.argv[1] == 'europe':
    CONFIG_NEWS = '%s/news/config/news_eu.conf' % PATH_TRUNK
elif sys.argv[1] == 'gct':
    CONFIG_NEWS = '%s/news/conf/news_gct.conf' % PATH_TRUNK
else:
    raise Exception('region error:' + str(sys.argv[1]))
parser_config = ConfigParser.ConfigParser()
parser_config.read(CONFIG_NEWS)

mongodb_server = parser_config.get('Settings', 'MONGODB_SERVER')
mongodb_db = parser_config.get('Settings', 'MONGODB_DB')
mongodb_collection = parser_config.get(
    'Settings', 'MONGODB_COLLECTION')
mongodb_data_collection = parser_config.get(
    'Settings', 'MONGODB_DATA_COLLECTION')
mongo_client = MongoClient(mongodb_server)
mongo_db = mongo_client[mongodb_db]
mongo_collection = mongo_db[mongodb_collection]
mongo_fs = gridfs.GridFS(mongo_db)


if __name__ == '__main__':
    #mongo_collection.remove({'time': {'$lt': '2017-03-01 00:00:00'}})
    cursor = mongo_collection.find()
    count = 0
    begin_time = int(time.time())
    for item in cursor:
        #if int(time.time()) - begin_time > 5 * 3600:
        #    logging.info('time is up, will exit')
        #    sys.exit(0)
        item_time = item['publish_time']
        crawl_time = item['crawl_time']
        pub_time = datetime.strptime(item_time, '%Y-%m-%d %H:%M:%S')
        delete_time = datetime.now() - timedelta(days = 30)
        if pub_time < delete_time:
            count += 1
            mongo_collection.delete_one({'_id': item['_id']})
            time.sleep(0.02)
            logging.info('count %s, delete %s in mongo' % (count, item['_id']))
