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
    'src.middlewares.deduptitlefilter.DedupTitleFilter': 20,

    # maker&middle_filter
    'src.middlewares.accountmaker.AccountMaker': 40,
    # 'src.middlewares.sourcefilter.SourceFilter': 30,
    'src.middlewares.videomaker.VideoMaker': 50,
    'src.middlewares.commentmaker.CommentMaker': 51,
    'src.middlewares.targetnewsmaker.TargetNewsMaker': 52,
    'src.middlewares.videosizemaker.VideoSizeMaker': 55,
    'src.middlewares.titlemaker.TitleMaker': 56,
    'src.middlewares.subtitlemaker.SubTitleMaker': 57,
    'src.middlewares.rawtagsmaker.RawTagsMaker': 60,
    'src.middlewares.publishermaker.PublisherMaker': 63,
    'src.middlewares.genremaker.GenreMaker': 64,
    'src.middlewares.tagsmaker.TagsMaker': 65,
    'src.middlewares.tagsfilter.TagsFilter': 70,
    'src.middlewares.contentmaker.ContentMaker': 80,
    'src.middlewares.contentfilter.ContentFilter': 90,
    'src.middlewares.descmaker.DescMaker': 91,
    'src.middlewares.updatetypemaker.UpdatetypeMaker': 110,
    'src.middlewares.dedupkeymaker.DedupKeyMaker': 130,
    'src.middlewares.timemaker.TimeMaker': 140,
    # 'src.middlewares.topnewsmaker.TopNewsMaker': 145,
    'src.middlewares.imagesmaker.ImagesMaker': 150,
    'src.middlewares.imagesnormalizer.ImagesNormalizer': 160,
    'src.middlewares.imagesnonefilter.ImagesNoneFilter': 163,
    'src.middlewares.imagesrecall.ImagesRecall': 165,
    'src.middlewares.scoremaker.ScoreMaker': 170,
    'src.middlewares.layoutmaker.TargetLayoutMaker': 185,
    'src.middlewares.hitcountmaker.HitCountMaker': 190,
    'src.middlewares.commentcountmaker.CommentCountMaker': 200,
    'src.middlewares.targeturlmaker.TargetUrlMaker': 230,
    'src.middlewares.sourceurlmaker.SourceUrlMaker': 240,
    'src.middlewares.crawltimemaker.CrawlTimeMaker': 250,
    'src.middlewares.locationmaker.LocationMaker': 260,
    'src.middlewares.keywordsmaker.KeywordsMaker': 270,
    'src.middlewares.breakingnewsmaker.BreakingNewsMaker': 275,
    'src.middlewares.pagetypemaker.PageTypeMaker': 276,
    'src.middlewares.pagetypefilter.PageTypeFilter': 277,
    'src.middlewares.shareiconmaker.ShareIconMaker': 278,
    'src.middlewares.transformer.Transformer': 280,
    'src.middlewares.localemaker.LocaleMaker': 288,
    'src.middlewares.extrainfomaker.ExtraInfoMaker': 300,

    # post filter
    'src.middlewares.dupefilter.DupeFilter': 3010,
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

BROKERS = 'kafka001.uscasv2.cootek.com:9092,kafka002.uscasv2.cootek.com:9092,kafka003.uscasv2.cootek.com:9092'
SRC_TOPIC = 'feedsgenerator'
DST_TOPIC = 'feedsuploader'
DST_TEST_TOPIC = 'feedsuploader_test'
SRC_TOPIC_GROUP_ID = 'feedsgenerator_executor'
SRC_TOPIC_TEST_GROUP_ID = 'feedsgenerator_executor_test'
REDIS_SERVER = 'crawler01.uscasv2.cootek.com'
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
