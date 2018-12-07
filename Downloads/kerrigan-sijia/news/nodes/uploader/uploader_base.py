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
import traceback
sys.path.append('../..')
from news.spider_logger import *

# regions
REGION_CHINA = 'china'
REGION_ASIA = 'asia'
REGION_AMERICA = 'america'
REGION_EUROPE = 'europe'
REGION_GCT = 'gct'


class Uploader(BaseObject):
    def __init__(self, *a, **kw):
        super(Uploader, self).__init__(*a, **kw)

    def init_mongo(self):
        mongo_client = MongoClient(self.settings['MONGODB_SERVER'])
        mongo_db = mongo_client[self.settings['MONGODB_DB']]
        self.mongo_fs = gridfs.GridFS(mongo_db)

    def renew_bucket(self, bucket_name):
        now = int(time.time())
        if now - self._bucket_last_ts > 600:
            self._bucket_last_ts = now
            s3 = boto3.resource('s3')
            self.bucket = s3.Bucket(bucket_name)
        return self.bucket

    def main(self):
        self.broker = self.settings['BROKERS']
        self.src_topic = self.settings['SRC_TOPIC']
        self.dst_topic = self.settings['DST_TOPIC']
        self.bucket_name = self.settings['BUCKET']
        self._bucket_last_ts = 0
        redis_server = self.settings['REDIS_SERVER']
        redis_port = self.settings['REDIS_PORT']
        redis_db = self.settings['REDIS_DB']
        self.redis = redis.Redis(redis_server, redis_port, redis_db)
        self.image_data_table = self.settings['IMAGE_DATA_TABLE']
        self.consumer = KafkaConsumer(self.src_topic,
                                      group_id='uploader',
                                      bootstrap_servers=self.broker,
                                      )
        dstClient = KafkaClient(self.broker)
        self.producer = SimpleProducer(dstClient, async=True)
        cnt = 0
        up_cnt = 0
        pass_cnt = 0
        fail_cnt = 0
        for message in self.consumer:

            cnt += 1
            value = message.value
            try:
                item = json.loads(value)
            except:
                self.logger.info('json.loads error and continue')
                continue

            SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).info(
                source_url=item['source_url'],
                custom_info='uploader received')

            bucket = self.renew_bucket(self.bucket_name)

            pubdate = item['pubdate']
            account = item['account']
            crawl_time = item['crawl_time']
            self.logger.info(
                'Try to upload %s (%s crawled)' % (account, crawl_time))
            success = True
            need_upload = False
            if item.get('video'):
                norm_name = item['video']['norm_name']
                md5 = item['video']['md5']
                video_format = str(item['video']['video_format']).lower()
                vidInOss = 'news/video/%s' % norm_name
                if item['process_mode'] == 'sim_mode':
                    vidInOss = vidInOss.replace('news/', 'news/sim_mode/')
                    self.logger.info(
                        'process_mode url is %s' % vidInOss)
                true_path = "%s/%s" % (self.aliyun_server, vidInOss)
                if not self.check2(self.bucket_name, vidInOss):
                    if self.mongo_fs.exists(md5):
                        try:
                            grid_out = self.mongo_fs.get(md5)
                            video_data = grid_out.read()
                            bucket.upload_fileobj(StringIO(video_data), vidInOss,
                                                  ExtraArgs={'ContentType': 'video/%s' % video_format})
                            self.logger.info('Uploaded video from mongodb %s' % true_path)
                            self.mongo_fs.delete(md5)
                        except Exception, e:
                            self.logger.info(' except Exception, e:!!!!!!')
                            traceback.print_exc()
                            SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).error(
                                source_url=item['source_url'],
                                custom_info=e.message)
                            success = False
                            continue
                    else:
                        self.logger.info('Video mongo_fs not exists !!!')
                        SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).error(
                            source_url=item['source_url'],
                            custom_info='video is dropped in redis')
                        continue
            if item['images']:
                need_upload = True
                image_md5s = set()
                for image_package in item['images']:
                    norm_name = image_package['image_info']['norm_name']
                    imgInOss = 'news/img/%s' % norm_name
                    image_format = str(image_package['image_info']['format']).lower()
                    true_path = "%s/%s" % (self.aliyun_server, imgInOss)
                    if item['process_mode'] == 'sim_mode':
                        imgInOss = imgInOss.replace('news/', 'news/sim_mode/')
                    md5 = image_package['image_info']['md5']
                    if self.mongo_fs.exists(md5):
                        try:
                            grid_out = self.mongo_fs.get(md5)
                            image_data = grid_out.read()
                            bucket.upload_fileobj(StringIO(image_data), imgInOss,
                                                  ExtraArgs={'ContentType': 'image/%s' % image_format})
                            self.logger.info('Uploaded images from mongodb %s' % true_path)
                            image_md5s.add(md5)
                        except Exception, e:
                            self.logger.info(' except Exception, e:!!!!!!')
                            self.logger.error(e)
                            SpiderLogger.create_spider_logger_by_crawl_id(
                                crawl_id=json.loads(value)['crawl_id']).error(
                                source_url=item['source_url'],
                                custom_info=e.message)
                            success = False
                            continue
                    else:
                        self.logger.info('Image mongo_fs not exists !!!')
                        SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).error(
                            source_url=item['source_url'],
                            custom_info='video is dropped in redis')
                        continue
                [self.mongo_fs.delete(each) for each in image_md5s]

            if item['publisher_icon'] and len(item['publisher_icon']) != 0:
                need_upload = True
                if item.get('publisher_icon'):
                    norm_name = item['publisher_icon']['norm_name']
                    md5 = item['publisher_icon']['image_info']['md5']
                    imgInOss = 'news/icon/%s' % norm_name
                    if item['process_mode'] == 'sim_mode':
                        imgInOss = imgInOss.replace('news/', 'news/sim_mode/')
                        self.logger.info(
                            'process_mode url is %s' % imgInOss)
                    true_path = "%s/%s" % (self.aliyun_server, imgInOss)
                    if not self.check2(self.bucket_name, imgInOss):
                        if self.mongo_fs.exists(md5):
                            try:
                                grid_out = self.mongo_fs.get(md5)
                                image_data = grid_out.read()
                                bucket.upload_fileobj(StringIO(image_data), imgInOss,
                                                      ExtraArgs={'ContentType': 'image/jpeg'})
                                self.logger.info('Uploaded icon from mongodb %s' % true_path)
                                self.mongo_fs.delete(md5)
                            except Exception, e:
                                self.logger.info(' except Exception, e:!!!!!!')
                                self.logger.error(e)
                                SpiderLogger.create_spider_logger_by_crawl_id(
                                    crawl_id=json.loads(value)['crawl_id']).error(
                                    source_url=item['source_url'],
                                    custom_info=e.message)
                                success = False
                                continue
                        else:
                            self.logger.info('publish_icon mongo_fs not exists !!!')
                            SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).error(
                                source_url=item['source_url'],
                                custom_info='publish_icon is dropped in redis')
                            continue
            if success:
                try:
                    if need_upload:
                        up_cnt += 1
                        self.logger.info(
                            '[%d(p: %d, u: %d, f: %d)] %s uploaded' %
                            (cnt, pass_cnt, up_cnt, fail_cnt, account))
                    else:
                        pass_cnt += 1
                        self.logger.info(
                            '[%d(p: %d, u: %d, f: %d)] %s passed' %
                            (cnt, pass_cnt, up_cnt, fail_cnt, account))
                    open('/pixdata/data/news/checker_%s' %
                         pubdate, 'a').write(value + '\n')
                    try:
                        self.logger.info('self.producer.send_messages!!!!!')
                        self.producer.send_messages(self.dst_topic, value)
                        self.logger.info(json.loads(value)['crawl_id'])
                        SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).info(
                            source_url=item['source_url'],
                            custom_info='uploader sended')
                    except kafka_errors.FailedPayloadsError:
                        self.logger.info('self.producer.send_messages  error!!!!!!!!!')
                        SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=json.loads(value)['crawl_id']).error(
                            source_url=item['source_url'],
                            custom_info='uploader kafka FailedPayloadsError')

                except:
                    pass
            else:
                fail_cnt += 1
                self.logger.info(
                    '[%d(p: %d, u: %d, f: %d)] %s failed' %
                    (cnt, pass_cnt, up_cnt, fail_cnt, account))

    def s3_check_exist(self, bucket, key):
        try:
            s3 = boto3.client('s3')
            s3.head_object(Bucket=bucket, Key=key)
            self.logger
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True

    def check2(self, bucket, key):
        try:
            s3 = boto3.resource(service_name='s3')
            s3.Object(bucket, key).load()
            self.logger.info('s3 file exist')
        except ClientError as e:
            self.logger.info('s3 file not exist')
            return False
        self.logger.info('s3 file return True')
        return True


if __name__ == '__main__':
    uploader = Uploader()
    uploader.main()
