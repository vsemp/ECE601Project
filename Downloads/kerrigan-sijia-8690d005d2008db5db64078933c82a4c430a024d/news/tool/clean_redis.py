import redis
import time
import logging
import json
import os
import ConfigParser
import sys


DEFAULT_LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
DEFAULT_LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_LOG_LEVEL = 'INFO'

logging.basicConfig(format=DEFAULT_LOG_FORMAT,
                    datefmt=DEFAULT_LOG_DATEFORMAT,
                    level=DEFAULT_LOG_LEVEL)

PATH_CURRENT = os.path.realpath('.')
PATH_TRUNK = PATH_CURRENT[:PATH_CURRENT.rfind('/gct')]
if sys.argv[1] == 'asia_pacific':
    CONFIG_NEWS = '%s/cn/config/news_tw.conf' % PATH_TRUNK
elif sys.argv[1] == 'usa':
    CONFIG_NEWS = '%s/cn/config/news_es.conf' % PATH_TRUNK
elif sys.argv[1] == 'europe':
    CONFIG_NEWS = '%s/cn/config/news_eu.conf' % PATH_TRUNK
elif sys.argv[1] == 'gct':
    CONFIG_NEWS = '%s/news/conf/news_gct.conf' % PATH_TRUNK

else:
    raise Exception('region error:' + str(sys.argv[1]))

parser_config = ConfigParser.ConfigParser()
parser_config.read(CONFIG_NEWS)

REDIS_SERVER = "localhost"
REDIS_PORT = 7664
REDIS_DB = 4


expire_field = 86400 * 7
expire_data = 60 * 4
data_check_interval = 60
table_check_interval = 86400
table_list = [
    'feeds_account',
    'feeds_dedupkey',
    'feeds_image',
    'feeds_crawled_account',
    'feeds_tittle',
    'feeds_lsh',
]
data_list = [
    'image_data',
    'video_data',
]


def deleteHash(tablename):
    now = int(time.time())
    t_keys = myredis.hkeys(tablename)
    tablename_ts = tablename + '_ts'
    ts_keys = myredis.hkeys(tablename_ts)
    ts_keys = set(ts_keys)
    for key in t_keys:
        if key not in ts_keys:
            myredis.hdel(tablename, key)
            logging.info('old key: ' + key)
        else:
            ts = int(myredis.hget(tablename_ts, key))
            if now - ts > expire_field:
                myredis.hdel(tablename, key)
                myredis.hdel(tablename_ts, key)
                logging.info('expired key: ' + key)


def deleteOldData(tablename):
    now = int(time.time())
    keys = myredis.hkeys(tablename)
    for key in keys:
        image_package = myredis.hget(tablename, key)
        if image_package:
            image_package = json.loads(image_package)
            ts = int(image_package['timestamp'])
            if now - ts > expire_data:
                logging.info('expired data: ' + key)
                myredis.hdel(tablename, key)

if __name__ == '__main__':
    myredis = redis.Redis(REDIS_SERVER, REDIS_PORT, REDIS_DB)
    now = int(time.time())
    table_checkpoint = 0
    img_checkpoint = 0
    while True:
        now = int(time.time())
        if now - img_checkpoint > data_check_interval:
            for data_table in data_list:
                logging.info('Checking ' + data_table)
                deleteOldData(data_table)
                logging.info('Clean %s Done' % data_table)
            img_checkpoint = now
        if now - table_checkpoint > table_check_interval:
            for tablename in table_list:
                logging.info('Checking ' + tablename)
                deleteHash(tablename)
            table_checkpoint = now
        time.sleep(5)
