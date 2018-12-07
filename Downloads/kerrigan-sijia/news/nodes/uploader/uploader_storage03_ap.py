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


class Uploader(Uploader):
    def __init__(self, *a, **kw):
        super(Uploader, self).__init__(*a, **kw)
        THIS_MACHINE = '127.0.0.1'
        self.settings['BROKERS'] = "stream01.uscasv2.cootek.com:9092,stream02.uscasv2.cootek.com:9092,stream03.uscasv2.cootek.com:9092"
        self.settings['REDIS_SERVER'] = THIS_MACHINE
        self.settings['MONGODB_SERVER'] = "localhost:27016"
        self.settings['BUCKET'] = 'cootek.news.ap'
        self.settings['SRC_TOPIC'] = 'gct_feedsuploader_ap'
        self.settings['DST_TOPIC'] = 'gct_feedspublisher'
        self.aliyun_server = 'http://news.ap.cdn.cootekservice.com'
        self.init_mongo()

if __name__ == '__main__':
    uploader = Uploader()
    uploader.main()
