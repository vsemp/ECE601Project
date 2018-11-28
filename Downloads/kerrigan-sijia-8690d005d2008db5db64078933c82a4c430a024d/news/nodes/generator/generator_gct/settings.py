TEST_MODE = False
LOG_ENABLED = True
LOG_LEVEL = 'INFO'

MIDDLEWARES = {
    # pre_filter
    'src.middlewares.loads2dict.Loads2Dict': 5,
    'src.middlewares.processmodemaker.ProcessModeMaker': 6,
    'src.middlewares.loggermaker.LoggerMaker': 7,
    'src.middlewares.timefilter.TimeFilter': 10,
    'src.middlewares.crawltimefilter.CrawlTimeFilter': 15,
    'src.middlewares.contenttypemaker.ContentTypeMaker': 20,

    # maker&middle_filter
    'src.middlewares.nonefilter.NoneFilter': 30,

    'src.middlewares.accountmaker.AccountMaker': 40,
    # 'src.middlewares.sourcefilter.SourceFilter': 30,
    'src.middlewares.videomaker.VideoMaker': 50,
    'src.middlewares.targetnewsmaker.TargetNewsMaker': 52,
    'src.middlewares.titlemaker.TitleMaker': 56,
    'src.middlewares.tagsmaker.TagsMaker': 65,
    'src.middlewares.tagsfilter.TagsFilter': 70,
    'src.middlewares.contentmaker.ContentMaker': 80,
    'src.middlewares.contentfilter.ContentFilter': 90,
    'src.middlewares.updatetypemaker.UpdatetypeMaker': 110,
    'src.middlewares.dedupkeymaker.DedupKeyMaker': 130,
    'src.middlewares.timemaker.TimeMaker': 140,
    'src.middlewares.localemaker.LocaleMaker': 141,
    'src.middlewares.localefilter.LocaleFilter': 142,
    # 'src.middlewares.topnewsmaker.TopNewsMaker': 145,
    'src.middlewares.imagesmaker.ImagesMaker': 150,
    'src.middlewares.imagesnormalizer.ImagesNormalizer': 160,
    'src.middlewares.imagesnonefilter.ImagesNoneFilter': 163,
    'src.middlewares.imagesrecall.ImagesRecall': 165,
    'src.middlewares.infocountmaker.InfoCountMaker': 190,
    'src.middlewares.targeturlmaker.TargetUrlMaker': 230,
    'src.middlewares.sourceurlmaker.SourceUrlMaker': 240,
    'src.middlewares.crawltimemaker.CrawlTimeMaker': 250,
    'src.middlewares.keywordsmaker.KeywordsMaker': 270,
    'src.middlewares.pagetypemaker.PageTypeMaker': 276,
    'src.middlewares.pagetypefilter.PageTypeFilter': 277,
    'src.middlewares.shareiconmaker.ShareIconMaker': 278,
    'src.middlewares.publishermaker.PublisherMaker': 279,

    # 'src.middlewares.transformer.Transformer': 280,
    # 'src.middlewares.qualitymaker.QualityMaker': 283,
    'src.middlewares.extrainfomaker.ExtraInfoMaker': 300,

    # post filter
    # 'src.middlewares.dupefilter.DupeFilter': 3010,
    # 'src.middlewares.realtimefilter.RealTimeFilter': 3020,
    # 'src.middlewares.infokeysfilter.InfoKeysFilter': 3040,

    # final
    'src.middlewares.simmode.SimMode': 4000,
    'src.middlewares.testmode.TestMode': 4010,
    'src.middlewares.extracleaner.ExtraCleaner': 4020,
}

# ALIYUN_SERVER = 'http://data-news.cdn.cootekservice.com'
# ALIYUN_SERVER = 'http://news.ap.cdn.cootekservice.com'
ALIYUN_SERVER = 'http://news.usa.cdn.cootekservice.com'
TIME_RANGE = 3 * 24 * 3600
VIDEO_TIME_RANGE = 100 * 365 * 24 * 3600

BROKERS = 'localhost:9092'
SRC_TOPIC = 'feedsgenerator'
DST_TOPIC = 'feedsuploader'

DST_TOPIC_AP = 'feedsuploader_ap'
DST_TOPIC_EU = 'feedsuploader_eu'
DST_TOPIC_USA = 'feedsuploader_usa'

DST_TEST_TOPIC = 'feedsuploader_test'
SRC_TOPIC_GROUP_ID = 'feedsgenerator_executor'
SRC_TOPIC_TEST_GROUP_ID = 'feedsgenerator_executor_test'
REDIS_SERVER = 'localhost'
REDIS_PORT = 7664
REDIS_DB = 4
REDIS_DB_NEWS = 5

DEDUPKEY_LOOK_TABLE = 'feeds_dedupkey'
ACCOUNT_LOOK_TABLE = 'feeds_account'
TITLE_LOOK_TABLE = 'feeds_title'
IMAGE_LOOK_TABLE = 'feeds_image'
BREAKING_NEWS_ACCOUNT_LOOK_TABLE = 'feeds_breaking_news_account'
TOP_NEWS_INFO = 'feeds_top_news_info'
TARGET_NEWS = 'target_news'

PATH_RESOURCE = '/pixdata/data/news/resource'

VERSION = '20150302'
DEFAULT_SHARE_ICON = 'http://data-news.cdn.cootekservice.com/news/img/tiantiantoutiao_icon.png@200w_200h'
