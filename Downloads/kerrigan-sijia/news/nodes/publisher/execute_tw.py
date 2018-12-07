import hashlib
import sys
sys.path.append('.')
from base import *
import json
import redis
import base64
from kafka import KafkaClient, SimpleProducer, KafkaConsumer
from kafka import errors as kafka_errors
import time
import copy
from html_data_pb2 import *
from datetime import datetime
from xedis_shard import shard

sys.path.append('..')
from news.feeds_back_utils import *
from news.spider_logger import *
class Publisher(BaseObject):
    def __init__(self, *a, **kw):
        super(Publisher, self).__init__(*a, **kw)
        THIS_MACHINE = 'ap-crawler01.southeast.cootek.com'
        self.settings['BROKERS'] = 'ap-data01.southeast.cootek.com:9092,ap-rainbow02.southeast.cootek.com:9092'
        self.settings['REDIS_SERVER'] = THIS_MACHINE
        self.settings['HTML_DATA_REDIS_SERVER'] = 'awsap-elc-data01.jvshxl.ng.0001.apse1.cache.amazonaws.com'
        self.settings['HTML_DATA_REDIS_PORT'] = 6379
        self.settings['MONGODB_SERVER'] = THIS_MACHINE
        self.settings['HTML_DATA_REDIS_PRE'] = 'news_html_data_zh_TW_'
        self.cloud_resource_prefix = 'http://news.ap.cdn.cootekservice.com'

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
        #self.redis_comment = shard.GuldanRedisShardAPI.instance(guldan_uri=comment_redis_server)
        self.redis_expiration = int(self.settings['REDIS_EXPIRATION'])
        self.account_look_table = self.settings['ACCOUNT_LOOK_TABLE']
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
        dstClient = KafkaClient(self.broker)
        self.producer = SimpleProducer(dstClient, async=True)

    def video_up_write_redis(self, pubdate, account, ts_cootek, video):
        videoup_source = '47'
        source, videoup_id = account.split('-')
        if source == videoup_source:
            videoup_table = 'videoup'
            url = self.cloud_resource_prefix + '/news/%s/%s' % (pubdate, video['norm_name'])
            self.html_data_redis.hset(videoup_table, videoup_id, url)
            self.html_data_redis.hset(videoup_table + '_ts', videoup_id, int(ts_cootek))
            self.logger.info('videoup_id:' + str(videoup_id) + '  url: ' + str(url))

    def main(self):
        cnt = 0
        for message in self.consumer:
            cnt += 1
            item = json.loads(message.value)
            locales = item['locales']
            account = item['account']
            pubdate = item['pubdate']
            dedup_key = item['dedup_key']
            score = item['score']
            fingerprint = item['fingerprint']
            recall = item.pop('recall', None)
            subtitle = item.get('subtitle', 'Unknown-Unknown')
            locale = item.get('locale', 'unknown')
            if subtitle.startswith('ugc'):
                uid = subtitle.split('-')[-1].strip()
                url = item.get('source_url', 'Unknown')
                if item['process_mode'] != 'sim_mode':
                    self.ugc_proc(uid, url, 0)
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
            if 'html_data' in item and item['html_data']:
                ctid = item['dedup_key']
                # key = self.html_data_redis_pre + ctid
                key = 'news_html_data_%s_' % locale + ctid
                html_proto = NewsHtmlData()
                html_data = item['html_data']
                type_dict = {
                    'article': 1,
                    'album': 2,
                    'video': 3,
                    'tencent_open': 4,
                    'href_article': 5,
                    'fall_video': 6
                }
                html_proto.hint_type = type_dict[html_data['type']]
                html_proto.title = html_data.get('title', '')
                html_proto.share_icon = html_data.get('share_icon', '')
                html_proto.subtitle = html_data.get('subtitle', '')
                html_proto.published = html_data.get('published', '')
                html_proto.content = html_data.get('content', '')
                html_proto.source_url = html_data.get('source_url', '')
                html_proto.thumbnail = html_data.get('thumbnail', '')
                html_proto.video_type = html_data.get('video_type', '')
                html_proto.target_url = html_data.get('target_url', '')
                html_proto.image_zoom = html_data.get('image_zoom', '')
                for _locale in locales:
                    key = 'news_html_data_%s_' % _locale + ctid
                    self.html_data_redis.set(key, html_proto.SerializeToString())
                    expire_span = 30 * 24 * 60 * 60
                    if html_data['type'] == 'video':
                        expire_span = self.video_expire_span
                    if account.startswith('9'):
                        expire_span = self.cootek_expire_span
                    # expire_time = expire_span - int((datetime.now() - publish_time).total_seconds())
                    expire_time = expire_span + 86400 * 2
                    self.html_data_redis.expire(key, expire_time)

                    html_json = {}
                    html_json[ctid] = html_data
                    html_str = json.dumps(html_json, ensure_ascii=False, encoding='utf-8').encode('utf-8')
                    try:
                        self.logger.info('Set redis account: %s, key: %s' % (account, key))
                        open('/pixdata/data/news/newshtml/newshtml_%s' %
                             pubdate, 'a').write(html_str + '\n')
                    except:
                        pass

            item.pop('images', None)
            item.pop('html', None)
            item.pop('html_data', None)
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
            item.pop('score')
            item.pop('model_version')
            item.pop('video', None)

            try:
                """
                if tmp_flag:
                    self.html_data_redis.set(tmp_key, tmp_string)
                    self.html_data_redis.expire(tmp_key, tmp_expire)
                    self.logger.info(
                        'account: %s, dedup_key: %s html_key:%s html_proto_ok' %
                        (account, dedup_key, tmp_key))
                """

                for _locale in locales:
                    item['locale'] = _locale
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
                            self.producer.send_messages('biu_test', base64msg)
                        else:
                            self.producer.send_messages(self.dst_topic, base64msg)
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
                    if set_source_url_crawled(item['source_url_id']):
                        self.logger.info('update remote source_url state success')
                    else:
                        self.logger.error('update remote source_url state failed')
                    item.pop('source_url_id')

                    self.redis.hset(self.account_look_table, account, fingerprint)
                    self.redis.hset(self.account_look_table + '_ts', account, ts_cootek)
                    self.redis.hset(self.dedupkey_look_table, dedup_key, score)
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

    def ugc_proc(self, uid, url, filter_type):
        ugc_redis = redis.Redis('data-cache003')
        ugc_uid_name = 'ugc:%s' % uid
        try:
            ugc_record = json.loads(ugc_redis.hget(ugc_uid_name, url))
            ugc_record.update({'type': filter_type})
            ugc_redis.hset(ugc_uid_name, url, json.dumps(ugc_record))
        except:
            self.logger.error('ugc process failed')


if __name__ == '__main__':
    publisher = Publisher()
    publisher.main()
