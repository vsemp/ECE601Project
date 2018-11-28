MIDDLEWARES = {
    # pre_filter
    'src.middlewares.loads2dict.Loads2Dict': 5,
    'src.middlewares.timefilter.TimeFilter': 10,
    'src.middlewares.crawltimefilter.CrawlTimeFilter': 15,
    'src.middlewares.deduptitlefilter.DedupTitleFilter': 20,
    'src.middlewares.titlefilter.TitleFilter': 25,

    # maker&middle_filter
    'src.middlewares.accountmaker.AccountMaker': 40,
    'src.middlewares.jumpermaker.JumperMaker': 45,
    # 'src.middlewares.sourcefilter.SourceFilter': 30,
    'src.middlewares.videomaker.VideoMaker': 50,
    'src.middlewares.commentmaker.CommentMaker': 51,
    'src.middlewares.targetnewsmaker.TargetNewsMaker': 52,
    'src.middlewares.titlemaker.TitleMaker': 56,
    'src.middlewares.subtitlemaker.SubTitleMaker': 57,
    'src.middlewares.rawtagsmaker.RawTagsMaker': 60,
    'src.middlewares.tagsmaker.TagsMaker': 65,
    'src.middlewares.tagsfilter.TagsFilter': 70,
    'src.middlewares.contentmaker.ContentMaker': 80,
    'src.middlewares.contentfilter.ContentFilter': 90,
    'src.middlewares.descmaker.DescMaker': 91,
    'src.middlewares.updatetypemaker.UpdatetypeMaker': 110,
    'src.middlewares.dedupkeymaker.DedupKeyMaker': 130,
    'src.middlewares.timemaker.TimeMaker': 140,
    #'src.middlewares.topnewsmaker.TopNewsMaker': 145,
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
    'src.middlewares.qualitymaker.QualityMaker': 283,
    'src.middlewares.localemaker.LocaleMaker': 288,

    # post filter
    'src.middlewares.deduplshfilter.DedupLshFilter': 3000,
    'src.middlewares.dupefilter.DupeFilter': 3010,
    'src.middlewares.realtimefilter.RealTimeFilter': 3020,
    'src.middlewares.chinesefilter.ChineseFilter': 3030,
    'src.middlewares.infokeysfilter.InfoKeysFilter': 3040,

    # final
    'src.middlewares.testmode.TestMode': 4010,
    'src.middlewares.extracleaner.ExtraCleaner': 4020,
}

ALIYUN_SERVER = 'http://data-news.cdn.cootekservice.com'
TIME_RANGE = 3 * 24 * 3600
VIDEO_TIME_RANGE = 3 * 30 * 24 * 3600

BROKERS = 'data-kafka01:9092,data-kafka02:9092,data-kafka03:9092'
SRC_TOPIC = 'feedsgenerator'
DST_TOPIC = 'feedsuploader'
DST_TEST_TOPIC = 'feedsuploader_test'
SRC_TOPIC_GROUP_ID = 'feedsgenerator_executor'
SRC_TOPIC_TEST_GROUP_ID = 'feedsgenerator_executor_test'
REDIS_SERVER = 'matrix03'
REDIS_PORT = 7664
REDIS_DB = 4
REDIS_DB_NEWS = 5

DEDUPKEY_LOOK_TABLE = 'feeds_dedupkey'
ACCOUNT_LOOK_TABLE = 'feeds_account'
TITLE_LOOK_TABLE = 'feeds_title'
LSH_LOOK_TABLE = 'feeds_lsh'
IMAGE_LOOK_TABLE = 'feeds_image'
BREAKING_NEWS_ACCOUNT_LOOK_TABLE = 'feeds_breaking_news_account'
TOP_NEWS_INFO = 'feeds_top_news_info'
TARGET_NEWS = 'target_news'

PATH_RESOURCE = '/pixdata/data/news/resource'

VERSION = '20150302'
DEFAULT_SHARE_ICON = 'http://data-news.cdn.cootekservice.com/news/img/tiantiantoutiao_icon.png@200w_200h'
