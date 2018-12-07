import hashlib
import sys

sys.path.append('..')
from base import *
import json
import redis
import base64
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from kafka import errors as kafka_errors
import time
import copy
from datetime import datetime

sys.path.append('../..')

from news.feeds_back_utils import *
from news.spider_logger import *


# from xedis_shard import shard

class Publisher(BaseObject):
    def __init__(self, *a, **kw):
        super(Publisher, self).__init__(*a, **kw)
        THIS_MACHINE = '127.0.0.1'
        self.settings['BROKERS'] = '127.0.0.1:9092'
        self.settings['REDIS_SERVER'] = THIS_MACHINE
        self.settings['HTML_DATA_REDIS_SERVER'] = 'awseu-elc-data01-001.5waxog.0001.euc1.cache.amazonaws.com'
        self.settings['HTML_DATA_REDIS_PORT'] = 6379
        self.settings['MONGODB_SERVER'] = "localhost:27016"
        self.settings['HTML_DATA_REDIS_PRE'] = 'news_html_data_zh_TW_'
        self.settings['SRC_TOPIC'] = 'feedspublisher'
        self.settings['DST_TOPIC'] = 'gct_newsfeeds'

        redis_server = self.settings['REDIS_SERVER']
        redis_port = self.settings['REDIS_PORT']
        redis_db = self.settings['REDIS_DB']
        redis_db_news = self.settings['REDIS_DB_NEWS']
        html_redis_server = self.settings['HTML_DATA_REDIS_SERVER']
        html_redis_port = self.settings['HTML_DATA_REDIS_PORT']
        comment_redis_server = self.settings['COMMENT_REDIS_SERVER']
        self.html_data_redis_pre = self.settings['HTML_DATA_REDIS_PRE']
        self.html_data_redis = redis.Redis(html_redis_server, html_redis_port)
        self.expire_span = self.settings['EXPIRE_SPAN']
        self.cootek_expire_span = self.settings['COOTEK_EXPIRE_SPAN']
        self.video_expire_span = self.settings['VIDEO_EXPIRE_SPAN']
        self.redis = redis.Redis(redis_server, redis_port, redis_db)
        self.redis_news = redis.Redis(redis_server, redis_port, redis_db_news)
        # self.redis_comment = shard.GuldanRedisShardAPI.instance(guldan_uri=comment_redis_server)
        self.redis_expiration = int(self.settings['REDIS_EXPIRATION'])
        self.account_look_table = self.settings['ACCOUNT_LOOK_TABLE']
        self.feeds_crawled_source_url = self.settings['SOURCE_URL_TABLE']
        self.dedupkey_look_table = self.settings['DEDUPKEY_LOOK_TABLE']
        self.image_look_table = self.settings['IMAGE_LOOK_TABLE']
        self.title_look_table = self.settings['TITLE_LOOK_TABLE']
        self.broker = self.settings['BROKERS']
        self.src_topic = self.settings['SRC_TOPIC']
        self.consumer = KafkaConsumer(
            self.src_topic,
            group_id='publisher',
            bootstrap_servers=self.broker,
        )

        self.dst_topic = self.settings['DST_TOPIC']
        self.elk_topic = self.settings['ELK_TOPIC']
        dstClient = KafkaClient(
            "stream01.uscasv2.cootek.com:9092,stream02.uscasv2.cootek.com:9092,stream03.uscasv2.cootek.com:9092")

        self.producer = SimpleProducer(dstClient, async=True)

    def main(self):
        cnt = 0
        for message in self.consumer:
            cnt += 1
            item = json.loads(message.value)
            account = item['account']
            pubdate = item['pubdate']
            dedup_key = item['dedup_key']
            fingerprint = item['fingerprint']
            recall = item.pop('recall', None)
            locale = item.get('locale', 'unknown')
            input_type = item.get('input_type', 'crawl')
            source_url = item['source_url']
            """
            tmp_flag = False
            tmp_key = None
            tmp_string = None
            tmp_expire = None
            if 'html_proto' in item and item['html_proto']:
                tmp_key = item['html_proto']['key']
                tmp_string = item['html_proto']['string']
                tmp_expire = item['html_proto']['expire_time']
                item.pop('html_proto', None)
                tmp_flag = True
            """
            item.pop('fingerprint')
            comment = item.pop('comment', None)
            ts = int(time.time())
            item['timestamp'] = ts
            if 'raw' in item:
                item['raw'].pop('html', None)
            msg_raw = json.dumps(
                item,
                ensure_ascii=False,
                encoding='utf8',
                sort_keys=True).encode('utf8')
            base64msg_raw = base64.b64encode(msg_raw)
            item.pop('raw', None)
            item.pop('images', None)
            item.pop('page_type', None)

            if "content_type" in item and item['content_type'] == "default":
                item.pop('content_type', None)

            try:
                """
                if tmp_flag:
                    self.html_data_redis.set(tmp_key, tmp_string)
                    self.html_data_redis.expire(tmp_key, tmp_expire)
                    self.logger.info(
                        'account: %s, dedup_key: %s html_key:%s html_proto_ok' %
                        (account, dedup_key, tmp_key))
                """

                msg = json.dumps(
                    item,
                    ensure_ascii=False,
                    encoding='utf8',
                    sort_keys=True).encode('utf8')
                elk_item = copy.deepcopy(item)
                elk_msg = json.dumps(
                    elk_item,
                    ensure_ascii=False,
                    encoding='utf8',
                    sort_keys=True).encode('utf8')
                base64msg = base64.b64encode(msg)
                # kafka may failed to send message
                try:
                    if item['process_mode'] == 'sim_mode':
                        self.producer.send_messages("newsfeeds", base64msg)
                        self.logger.info(msg)
                    else:
                        self.producer.send_messages(self.dst_topic, base64msg)
                        self.logger.info(msg)

                    SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=item['crawl_id']).info(
                        source_url=item['source_url'],
                        custom_info='publisher sended',
                        source_state='finished')
                    SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=item['crawl_id']).save_item(
                        item=item)

                except kafka_errors.FailedPayloadsError:
                    SpiderLogger.create_spider_logger_by_crawl_id(crawl_id=item['crawl_id']).error(
                        source_url=item['source_url'],
                        custom_info='publisher kafka FailedPayloadsError')
                self.logger.info(
                    '[%d] account: %s, dedup_key: %s published' %
                    (cnt, account, dedup_key))
                open('/pixdata/data/news/newsfeeds_%s' %
                     pubdate, 'a').write(msg + '\n')
                ts_cootek = ts + 3600 * 24 * 1000 if account.startswith('9') else ts
                if item['process_mode'] != 'sim_mode':
                    if 'source_url_id' in item:
                        if item['inlinks'] == []:
                            if set_source_url_crawled(item['source_url_id']):
                                self.logger.info('update remote source_url state success')
                            else:
                                self.logger.error('update remote source_url state failed')
                        item.pop('source_url_id')

                    self.redis.hset(self.account_look_table, account, fingerprint)
                    self.redis.hset(self.account_look_table + '_ts', account, ts_cootek)

                    input_source_url = "%s_%s" % (input_type, source_url)

                    self.redis.hset(self.feeds_crawled_source_url, input_source_url, fingerprint)
                    self.redis.hset(self.dedupkey_look_table, dedup_key, -1)
                    self.redis.hset(
                        self.dedupkey_look_table + '_ts', dedup_key, ts_cootek)
                    if recall:
                        self.redis.hset(self.image_look_table, account, recall)
                        self.redis.hset(self.image_look_table + '_ts', account, ts)

                    title_md5 = hashlib.md5(item['title'].encode("utf-8")).hexdigest()
                    self.redis.hset(self.title_look_table, title_md5, 1)
                    self.redis.hset(self.title_look_table + '_ts', title_md5, int(ts_cootek))

                    self.redis_news.set(item['account'], base64msg_raw)
                    self.redis_news.expire(item['account'], self.redis_expiration)
                    if comment:
                        # self.redis_comment.set('comment_'+dedup_key, json.dumps(comment, ensure_ascii=False))
                        self.logger.info('comment generated dedup_key: %s account_id: %s' % (dedup_key, account))
            except:
                self.logger.error(
                    'Message %s cannot be sent to %s' % (account, self.broker))


if __name__ == '__main__':
    publisher = Publisher()
    publisher.main()
