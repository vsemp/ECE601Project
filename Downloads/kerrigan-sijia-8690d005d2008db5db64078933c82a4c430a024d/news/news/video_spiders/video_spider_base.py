# -*- coding: utf-8 -*-
from ..common_spider_base import *
from ..spider_const import *
import requests
import random
import base64
from util import image_util
import hashlib


class VideoSpider(CommonSpiderBase):
    video_format = 'mp4'
    data_source_type = DATA_SOURCE_TYPE_VIDEO
    custom_settings = {
        'DOWNLOAD_WARNSIZE': 104857600 * 5,
    }
    video_info_keys = ['comment_count', 'like_count', 'duration', 'publisher_icon', 'video_id',
                       'video', 'video_height',
                       'video_width', 'video_type', 'view_count']
    article_info_keys = CommonSpiderBase.article_info_keys + video_info_keys

    def __init__(self, *a, **kw):
        super(VideoSpider, self).__init__(*a, **kw)

    def generate_message(self, article_info):
        message = super(VideoSpider, self).generate_message(article_info)
        message['comment_count'] = article_info.get('comment_count', -1)
        message['view_count'] = article_info.get('view_count', -1)
        message['like_count'] = article_info.get('like_count', -1)

        publisher_icon = self.normalize_publisher_icon(article_info)
        if not publisher_icon:
            self.spider_logger.error(source_url=article_info['source_url'],
                                     custom_info='generator (publisher_icon) message failed')
        message['publisher_icon'] = publisher_icon
        # TODO(xinyu.du@cootek.cn) hard code
        message['page_type'] = 'video'
        # message['content_type'] = 'video'

        video_info = self.normalize_video(article_info)
        if not video_info:
            self.spider_logger.error(source_url=article_info['source_url'],
                                     custom_info='generator (video) message error')
            return None
        message['video'] = video_info
        target_url = 'news/video/%s' % message['video']['norm_name']
        message['url'] = {
            'source_url': article_info['source_url'],
            'target_url': target_url
        }
        return message

    def normalize_content(self, article_info):
        return article_info['content']

    def normalize_publisher_icon(self, article_info):
        account = article_info['account']
        icon_url = article_info['publisher_icon'][0]
        self.logger.warning(icon_url)

        icon_cache = self.download_images(icon_url)

        if not icon_cache:
            self.logger.warning("icon_cache fetch error")
            return None
        file_md5 = self.get_md5(icon_cache)
        icon_info = image_util.get_image_info_with_io(file_md5, icon_cache)
        norm_name = '%s.%s' % (file_md5, icon_info['format'].lower())
        new_icon = self.generate_image_package(norm_name, thumbnail_cache=icon_cache, thumbnail_info=icon_info,
                                               file_md5=file_md5)
        new_icon['image_info']['norm_name'] = '%s.%s' % (file_md5, new_icon['image_info']['format'].lower())
        new_icon['image_info'].pop('name')
        new_icon['image_info']['md5'] = file_md5
        new_icon['norm_name'] = norm_name

        return new_icon

    def normalize_thumbnails(self, article_info):
        account = article_info['account']
        thumbnails_new = []
        thumbnail_url = article_info['thumbnails'][0]
        thumbnail_cache = self.download_images(thumbnail_url)
        if not thumbnail_cache:
            return None
        for name in ['large', 'small', 'share']:
            file_md5 = self.get_md5(thumbnail_cache)
            icon_info = image_util.get_image_info_with_io(file_md5, thumbnail_cache)
            norm_name = '%s_%s.%s' % (file_md5, name, icon_info['format'].lower())
            new_thumb = self.generate_image_package(norm_name, thumbnail_cache=thumbnail_cache,
                                                    thumbnail_info=icon_info, file_md5=file_md5)
            new_thumb['image_info'].pop('name')
            new_thumb['image_info']['md5'] = file_md5
            new_thumb['image_info']['norm_name'] = norm_name
            thumbnails_new.append(new_thumb)
        return thumbnails_new

    def generate_image_package(self, norm_name, thumbnail_cache, thumbnail_info, file_md5):
        image_data = base64.b64encode(thumbnail_cache)
        result = {'norm_name': norm_name,
                  'image_info': thumbnail_info}
        # image_package = {'timestamp': int(time.time()),
        #                  'image_data': image_data}
        # self.redis.hset(self.image_data_table,
        #                 norm_name,
        #                 json.dumps(image_package, sort_keys=True))

        mongo_kw = {'_id': file_md5,
                    'timestamp': int(time.time())}
        try:
            self.mongo_fs.put(thumbnail_cache, **mongo_kw)
        except Exception, e:
            self.logger.warning(e)

        if self.process_mode == PROCESS_MODE_TEST:
            with open(os.path.join(self.img_test_dir, norm_name), 'w') as f:
                f.write(thumbnail_cache)
        return result

    def download_images(self, image_url):
        hd = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'pragma': 'no-cache',
            'cache-control': 'no-cache'
        }
        ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
              '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
              '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
              '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
              '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
              '198.23.195.104:13228', '198.23.195.47:13228',
              '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228']
        tp = random.choice(ta)
        proxies = {
            'http': 'http://{}'.format(tp),
            'https': 'http://{}'.format(tp)
        }

        try:
            image_cache = requests.get(image_url, headers=hd, proxies=proxies).content
        except  Exception, e:
            self.logger.warning(e)
            return None

        return image_cache

    def normalize_video(self, article_info):
        account = article_info['account']
        video_info = dict()
        video_info['video_url'] = article_info['video']
        video_info['video_width'] = article_info.get('video_width', 0)
        video_info['video_height'] = article_info.get('video_height', 0)
        video_info['video_id'] = article_info.get('video_id', 0)
        video_info['duration'] = article_info.get('duration', -1)
        video_info['video_type'] = article_info.get('video_type', -1)
        video_cache = self.download_video(video_info['video_url'])
        if not video_cache or len(video_cache) <= 1024 * 1024 * 0.1:
            self.spider_logger.error(source_url=article_info['source_url'], custom_info='video size smaller than 0.1MB',
                                     source_state='error')
            self.logger.warning('video size smaller than 0.1MB' + '(' + str(article_info['source_url'] + ')'))
            # 记录不可用视频
            input_source_url = "%s_%s" % (self.input_type, article_info['source_url'])
            self.record_invalid_source_url(input_source_url, "video size smaller than 0.1MB")
            self.logger.info('reset source_url_table with : ' + str(input_source_url))

            return None
        video_info['size'] = len(video_cache)
        video_info['md5'] = self.get_md5(video_cache)
        video_info['norm_name'] = '%s.%s' % (video_info['md5'], self.video_format)
        if self.process_mode == PROCESS_MODE_TEST:
            with open(os.path.join(self.test_dir, video_info['norm_name']), 'w') as f:
                f.write(video_cache)
        else:
            mongo_kw = {'_id': video_info['md5'],
                        'timestamp': int(time.time())}
            try:
                self.mongo_fs.put(video_cache, **mongo_kw)
            except Exception, e:
                self.logger.warning(e)
        video_info['video_format'] = self.video_format
        return video_info

    def download_video(self, video_url):
        hd = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'pragma': 'no-cache',
            'cache-control': 'no-cache'
        }
        ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
              '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
              '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
              '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
              '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
              '198.23.195.104:13228', '198.23.195.47:13228',
              '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228']
        tp = random.choice(ta)
        proxies = {
            'http': 'http://{}'.format(tp),
            'https': 'http://{}'.format(tp)
        }

        try:
            video_cache = requests.get(video_url, headers=hd, proxies=proxies).content
        except  Exception, e:
            self.logger.warning(e)
            return None

        return video_cache

    def get_md5(self, file_cache):
        md5_obj = hashlib.md5()
        md5_obj.update(file_cache)
        hash_code = md5_obj.hexdigest()
        md5 = str(hash_code).lower()
        return md5

    def get_view_count_from_raw(self, raw):
        return -1

    def get_like_count_from_raw(self, raw):
        return -1

    def get_comment_count_from_raw(self, raw):
        return -1

    def get_share_count_from_raw(self, raw):
        return -1

    @abstractmethod
    def get_duration_from_raw(self, raw):
        return raw['duration']

    @abstractmethod
    def get_video_id_from_raw(self, raw):
        return raw['video_id']

    @abstractmethod
    def get_video_from_raw(self, raw):
        return raw['video']

    @abstractmethod
    def get_video_type_from_raw(self, raw):
        return ""

    @abstractmethod
    def get_thumbnails_from_raw(self, raw):
        return raw['get_thumbnails']

    @abstractmethod
    def get_publisher_icon_from_raw(self, raw):
        return raw['publisher_icon']

    def get_article_class_from_raw(self, raw):
        return self.data_source_type
