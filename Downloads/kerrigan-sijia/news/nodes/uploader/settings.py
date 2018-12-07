LOG_ENABLED = True
LOG_LEVEL = 'INFO'

MIDDLEWARES = {
}

ACCESSID = 'vtum99z0ySLlf8Yg'
ACCESSKEY = 'OAsidmqnTd5hxrrVtpVNMqwWZJSQxT'
OSS_PREFIX = 'oss://data-news/news'
ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
BUCKET = 'data-news'

BROKERS = '127.0.0.1:9092'
SRC_TOPIC = 'feedsuploader'
SRC_TOPIC_AP = 'feedsuploader_ap'
SRC_TOPIC_USA = 'feedsuploader_usa'
SRC_TOPIC_EU = 'feedsuploader_eu'
DST_TOPIC = 'feedspublisher'
BUCKET = 'data-news'

REDIS_SERVER = '127.0.0.1'
REDIS_PORT = 7664
REDIS_DB = 4
IMAGE_DATA_TABLE = 'image_data'
VIDEO_DATA_TABLE = 'video_data'

HTML_DATA_REDIS_SERVER = 'data-cache003'
HTML_DATA_REDIS_PORT = 6379
HTML_DATA_REDIS_PRE = 'news_html_data_zh_CN_'
EXPIRE_SPAN = 14 * 24 * 60 * 60
VIDEO_EXPIRE_SPAN = 3 * 33 * 24 * 60 * 60
COOTEK_EXPIRE_SPAN = 1000 * 24 * 60 * 60

MONGODB_SERVER = 'localhost:27017'
MONGODB_DB = 'news'

MAIL_HOST = 'rainbow01'
MAIL_PORT = 9100
MAIL_TO = [
    'tengchuan.wang@cootek.cn',
    'bo.wang@cootek.cn',
    'yongchao.zhou@cootek.cn',
    'lu.xia@cootek.cn',
    'dabra.chen@cootek.cn',
    'xinyu.du@cootek.cn',
]
