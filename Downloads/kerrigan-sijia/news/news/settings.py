# -*- coding: utf-8 -*-

# Scrapy settings for news project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#


# CONCURRENT_REQUESTS = 32

BOT_NAME = 'news'
COOKIES_ENABLED = True

SPIDER_MODULES = ['news.video_spiders','news.news_spiders','news.demo_spiders']
NEWSPIDER_MODULE = 'news.video_vspiders'

DOWNLOAD_HANDLERS = {'s3': None}

DOWNLOADER_MIDDLEWARES = {
    'news.middlewares.InitHeaders': 50,
    'news.middlewares.DomainDelay': 60,
    'news.middlewares.InvalidHttpstatusDeal': 70,
    'news.middlewares.ProxyMiddleware': 80,
    'news.middlewares.JavaScriptMiddleware': 90,
}

MAIL_HOST = 'rainbow01'
MAIL_PORT = 9100
MAIL_TO = [
    'zhongzhou.dai@cootek.cn',
    'tengchuan.wang@cootek.cn',
    'lu.xia@cootek.cn',
    'xinyu.du@cootek.cn',
    'bo.wang@cootek.cn',
    'darbra.chen@cootek.cn',
]


# Crawl responsibly by identifying yourself (and your website) on the
# user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
