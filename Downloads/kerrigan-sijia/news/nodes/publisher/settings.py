LOG_ENABLED = True
LOG_LEVEL = 'INFO'

MIDDLEWARES = {
}

BROKERS = 'localhost:9092'
SRC_TOPIC = 'feedspublisher'
DST_TOPIC = 'newsfeeds'
ELK_TOPIC = 'news_content'

REDIS_SERVER = '127.0.0.1'
REDIS_PORT = 7664
REDIS_DB = 4
REDIS_DB_NEWS = 5
REDIS_EXPIRATION = 14 * 86400

DEDUPKEY_LOOK_TABLE = 'feeds_dedupkey'
ACCOUNT_LOOK_TABLE = 'feeds_account'
IMAGE_LOOK_TABLE = 'feeds_image'
TITLE_LOOK_TABLE = 'feeds_title'
SOURCE_URL_TABLE = 'feeds_crawled_source_url'

LSH_LOOK_TABLE = 'feeds_lsh'

HTML_DATA_REDIS_SERVER = 'data-cache003'
HTML_DATA_REDIS_PORT = 6379
HTML_DATA_REDIS_PRE = 'news_html_data_zh_CN_'
EXPIRE_SPAN = 14 * 24 * 60 * 60
VIDEO_EXPIRE_SPAN = 3 * 33 * 24 * 60 * 60
COOTEK_EXPIRE_SPAN = 1000 * 24 * 60 * 60

COMMENT_REDIS_SERVER = 'guldan://guldan.corp.cootek.com/bigdata/redis/news_comments'
