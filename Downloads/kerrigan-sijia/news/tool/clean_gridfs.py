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
CONFIG_NEWS = '%s/news/conf/news_gct.conf' % PATH_TRUNK
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
    cursor = mongo_fs.find()
    count = 0
    begin_time = int(time.time())
    for item in cursor:
        #if int(time.time()) - begin_time > 2 * 3600:
        #    logging.info('time is up, will exit')
        #    sys.exit(0)
        if int(time.time()) - item.timestamp > 1000:
            mongo_fs.delete(item._id)
            time.sleep(0.1)
            logging.info('delete %s in mongo' % item._id)
