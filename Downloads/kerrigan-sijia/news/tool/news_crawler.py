# /usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import commands
import psutil
import time
from datetime import datetime
import sys
import os
from subprocess import Popen
from mail import MailSender


PATH_CURRENT = os.path.realpath('.')
PATH_TRUNK = PATH_CURRENT[:PATH_CURRENT.rfind('/cn')]
CONFIG_NEWS = '%s/cn/config/news.conf' % PATH_TRUNK
parser_config = ConfigParser.ConfigParser()
parser_config.read(CONFIG_NEWS)
PATH_LOG = parser_config.get('Paths', 'path_log')
PATH_RESOURCE = parser_config.get('Paths', 'path_resource')

# run every 5 minutes
LIST0 = [
    'breaking_news_baidu',
    'breaking_news_xinhuanet',
    #'toutiao_stream',
    #'toutiao_lite',
    #'yidianzixun_wap',
]

# run every 30 minutes
LIST1 = [
    # 'aiweibang',
    #'toutiao_user',
    'analyze_toutiao',  # temp solution
    'sogou',
    'jiemian',
    'thepaper',
    #'thecover',
    'cctv',
    'chinadaily',
    'eastday',
    'eastday_video',
]

# run every 15 minutes(at minute 5\20\35\50 of each hour)
LIST2 = [
    'chinanews',
    'xinhuanet',
    'jinghua',
    'people',
    'huanqiu',
    'fawan',
    'morningpost',
    'xdkb',
    'sohu',
    'news163',
    #'ifeng',
    'sina',
    'news36kr',
    'huxiu',
    'quanminxingtan',
    'guokr',
    'news163local',
    #'toutiao',
    'toutiao_rolling',
]

# run every 15 minutes(at minute 10\25\40\55 of each hour)
LIST3 = [
    'analyze_news163',
    'analyze_baidu',
    #'toutiao_category',
    #'yidianzixun_more',
]

# run at 18:30 of every day
LIST4 = [
    #'sogou_account',
    #'miaopai',
    #'pocomm',
    #'pocomm_meitu',
    #'sougoumm',
]

# run every 15 minutes(at minute 12\27\42\57 of each hour)
LIST5 = [
    #'tencent_rolling',
    'news163_rolling',
    #'autohome',
    'haiwainet',
    #'youth',
    'sina_rolling',
    'sohu_rolling',
    #'ifeng_rolling',
    #'tencent',
    'cankaoxiaoxi',
]
# run at 0:10 of every day
LIST6 = [
    'ku6',
    'jandan',
    'zhihuribao',
    #'miaopai',
]
# run every 1 hour(at minutes 00 of each hour)
LIST7 = [
    #'weibo_video',
    'bjnews',
    'myzaker',
    'cyol',
    'gmw',
    'yangguang',
    'btime',
    'uctoutiao',
]
# run every 2 hour(at minutes 00 of each even hour)
LIST8 = [
    #'yidianzixun',
    #'tencent_open',
    'zaobao',
]
# run every 4 hour(at minutes 00 of hour which mod 4 equals 0)
LIST9 = [
    'weibo',
    'inewsweek',
    #'baidu_baijia',
]
# run every 6 hour(at minutes 00 of hour which mod 6 equals 0)
LIST10 = [
    #'toutiao_video',
    #'pealvideo',
]
# run every 8 hour(at minutes 00 of hour which mod 8 equals 0)
LIST11 = [
    #'anyv',
    'xinwenge',
]
# run every 12 hour(at minutes 00 of hour which mod 12 equals 0)
LIST12 = [
    #'mm131',
    #'meitu4493',
    #'news163_meinv',
    'kaiyanvideo',
]

MEMORY_LIMIT = 1024 * 1024 * 1024 * 4


def start_spiders(crawler_type):
    sub_pro = []
    if 0 <= int(crawler_type) <= 12:
        source_list = eval('LIST%d' % int(crawler_type))
    else:
        return
    for source_name in source_list:
        spider_search = 'ps aux|grep -E "scrapy crawl %s$|%s "|'\
            'grep -v grep' % (source_name, source_name)
        spider_processes = commands.getstatusoutput(spider_search)
        for spider_process in spider_processes[-1].splitlines():
            process_id = spider_process.split(' ', 1)[1].lstrip().split(' ')[0]
            Popen('kill -9 %s' % process_id, shell=True)
    for source_name in source_list:
        start_time = datetime.now().strftime('%Y-%m-%d_%X')
        cmd = 'scrapy crawl %s 2>%s/news_%s_%s' % (
            source_name, PATH_LOG, source_name, start_time)
        p = Popen(cmd, shell=True)
        sub_pro.append(p)
    loop_flag = True
    while loop_flag:
        loop_flag = False
        for p in sub_pro:
            status = p.poll()
            if status is None:
                children_info = psutil.Process(p.pid).children()
                if children_info:
                    process_info = children_info[0]
                    memory_info = process_info.memory_info()
                    spider_name = process_info.cmdline()[-1]
                    if memory_info.rss > MEMORY_LIMIT:
                        process_info.kill()
                        subject = '{Matrix}{feeds}Spider Memory Limit Exceed'
                        body = spider_name
                        to = [
                            'hongjun.liu@cootek.cn',
                            'zhongzhou.dai@cootek.cn',
                            'tengchuan.wang@cootek.cn',
                        ]
                        MailSender('matrix04').send(to, subject, body)
                loop_flag = True
                time.sleep(5)
                break


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print 'Usage: python news_crawler.py crawler_type'
        sys.exit(-1)
    start_spiders(sys.argv[1])

