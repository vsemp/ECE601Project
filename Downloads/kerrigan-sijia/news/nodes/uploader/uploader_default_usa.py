import sys

from botocore.exceptions import ClientError

sys.path.append('..')
from base import *
import base64
import json
import redis
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from cStringIO import StringIO
import time
from kafka import errors as kafka_errors
import boto3
from pymongo import MongoClient
import gridfs
sys.path.append('../..')
from news.spider_logger import *
from uploader_base import Uploader
# regions



class Uploader(Uploader):
    def __init__(self, *a, **kw):
        super(Uploader, self).__init__(*a, **kw)
        THIS_MACHINE = '127.0.0.1'
        self.settings['BROKERS'] = "localhost:9092"
        self.settings['REDIS_SERVER'] = THIS_MACHINE
        self.settings['MONGODB_SERVER'] = "localhost:27017"
        self.settings['BUCKET'] = 'cootek.news.usa'
        self.settings['SRC_TOPIC'] = 'feedsuploader_usa'
        self.settings['DST_TOPIC'] = 'feedspublisher'
        self.aliyun_server = 'http://news.usa.cdn.cootekservice.com'
        self.init_mongo()



if __name__ == '__main__':
    uploader = Uploader()
    uploader.main()
