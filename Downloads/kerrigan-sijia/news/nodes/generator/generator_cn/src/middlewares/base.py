import logging
import redis
import os

FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
DATEFORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT, level=logging.INFO)
logging.getLogger('gensim').setLevel(logging.ERROR)
logging.getLogger('summa').setLevel(logging.ERROR)


class BaseMiddleware(object):
    def __init__(self, *a, **kw):
        self.settings = kw['settings']
        self.redis_cli = redis.Redis(self.settings['REDIS_SERVER'],
                                     self.settings['REDIS_PORT'],
                                     self.settings['REDIS_DB'])
        self.redis_news_cli = redis.Redis(self.settings['REDIS_SERVER'],
                                          self.settings['REDIS_PORT'],
                                          self.settings['REDIS_DB_NEWS'])
        self.title_look_table = self.settings['TITLE_LOOK_TABLE']
        self.lsh_look_table = self.settings['LSH_LOOK_TABLE']
        self.dedupkey_look_table = self.settings['DEDUPKEY_LOOK_TABLE']


    @classmethod
    def from_settings(cls, settings):
        return cls(settings=settings)

    @property
    def logger(self):
        logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT, level=logging.DEBUG)
        return logging.getLogger(self.__class__.__name__)

    def get_resource_file_path(self, file_name):
        resource_path = "feeds/generator/generator_cn/resources/" \
            if self.settings.get('TEST_MODE', False) else "resources/"
        return os.path.join(resource_path, file_name)


class MapMiddleware(BaseMiddleware):
    api = 'map'


class FilterMiddleware(BaseMiddleware):
    api = 'filter'

    def filter_standard_log(self, account_id, info=''):
        if type(info) == str:
            info = info.decode('utf-8')
        log_content = account_id + ' ' + info
        self.logger.info(log_content)


class MapPartitionsMiddleware(BaseMiddleware):
    api = 'mapPartitions'
