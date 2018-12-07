# -*- coding: utf-8 -*-
import scrapy
import copy
import re
import time
import json
import copy
import scrapy
from scrapy import signals
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import requests
import lxml
from lxml import etree
import traceback
import pprint
import logging
from ..out_link_news import OutLinkNews
from ....spider_const import *
import random


# 有两个地方需要加 self.paw(raw)
class YahooSpider(OutLinkNews):
    name = 'yahoo'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'yahoo'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 1
    page_times = 0
    page_limit = 1
    content_list = []
    channel_list = [
        'https://www.yahoo.com/news/',
    ]

    def __init__(self, *a, **kw):
        super(YahooSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        # print(etree.tostring(selector))
        headers_1 = {
            'authority': 'www.yahoo.com',
            'method': 'GET',
            'path': '/news/_td/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=news;ssEP=;useSlingstoneLcp=true;uuids=%5B%224d996d2a-a927-30e9-926f-aa6138b57b23%22%2C%22b1cc9488-6268-3c64-a0f7-38645d08274d%22%2C%2285d74428-93d5-36f2-ae46-0fa9a93bc976%22%2C%22bd01f757-52d0-3d4f-9592-800bd0746f69%22%2C%223bd2544c-1530-3008-b2ac-3b23184f2a8b%22%2C%22ccea589c-bc29-3487-8f54-3b7eff8ad61f%22%2C%227c52b952-04dd-373b-9ad2-cd7c63372448%22%2C%22cbb32b27-3e34-34d2-803d-167c4e076041%22%2C%226681c1e3-3190-3d01-bcff-720e7b1c1645%22%2C%225a52596b-937a-319f-ac65-ab15352f70b4%22%2C%225d17c4b4-e472-33c1-ae85-6e55ab7863b7%22%2C%224808e873-1edb-3f7a-9f00-f1691d8ce1e5%22%2C%22df4473fd-3e35-3747-9279-84d01f9b24aa%22%2C%224301b752-c2b5-3756-9780-a0b8bda89272%22%2C%22d0c6d1b7-53ae-3fe2-a437-2c827e04bf8b%22%2C%222200bb5c-4d72-3d1b-b9ec-f1f0703b03a9%22%2C%22SS-f28118b9-343e-372b-bb64-c4c2d467de8e%22%2C%22SS-6e282f26-b6d1-38f7-b46d-095805aa2ac6%22%2C%22SS-674c6e5f-8c9f-394e-ab3b-ca6767b3312f%22%2C%22SS-7ad6f5f6-a188-3291-a15c-85464973acdf%22%5D?bkt=fp-US-en-US-def&device=desktop&feature=cacheContentCanvas%2CenableGuceJs%2CenableGuceJsOverlay%2CvideoDocking%2CnewContentAttribution%2Clivecoverage%2CenableGDPRFooter%2CenableCMP%2CenableConsentData%2CdeferModalCluster%2CcanvassOffnet%2CnewLayout%2CntkFilmstrip%2Csidepic%2CautoNotif%2CfauxdalNewLayout%2CcacheContentCanvasAds&intl=us&lang=en-US&partner=none&prid=03lgvk5dkcgu2&region=US&site=fp&tz=America%2FLos_Angeles&ver=2.0.16039&returnMeta=true',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cookie': 'B=4j433q5djkpmq&b=3&s=8k; flash_enabled=1; GUC=AQEBAQFbRppcFkIbWgRm&s=AQAAAHr4gHRP&g=W0VRbA; cmp=t=1531330949&j=0; apeaf=td-applet-stream=%7B%22tmpl%22%3A%22items%22%2C%22lv%22%3A1531332841717%7D; ucs=lnct=1531269473&bnpt=1531269481&spt=1531331053; yvapF=%7B%22vl%22%3A14.680475000000003%2C%22rvl%22%3A14.680475000000003%2C%22cc%22%3A1%2C%22rcc%22%3A1%7D',
            'device-memory': '8',
            'dpr': '2',
            'referer': 'https://www.yahoo.com/news/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'viewport-width': '764',
            'x-requested-with': 'XMLHttpRequest', }

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

        new_url = "https://www.yahoo.com/news/_td/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=news;ssEP=;useSlingstoneLcp=true;uuids=%5B%224d996d2a-a927-30e9-926f-aa6138b57b23%22%2C%22b1cc9488-6268-3c64-a0f7-38645d08274d%22%2C%2285d74428-93d5-36f2-ae46-0fa9a93bc976%22%2C%22bd01f757-52d0-3d4f-9592-800bd0746f69%22%2C%223bd2544c-1530-3008-b2ac-3b23184f2a8b%22%2C%22ccea589c-bc29-3487-8f54-3b7eff8ad61f%22%2C%227c52b952-04dd-373b-9ad2-cd7c63372448%22%2C%22cbb32b27-3e34-34d2-803d-167c4e076041%22%2C%226681c1e3-3190-3d01-bcff-720e7b1c1645%22%2C%225a52596b-937a-319f-ac65-ab15352f70b4%22%2C%225d17c4b4-e472-33c1-ae85-6e55ab7863b7%22%2C%224808e873-1edb-3f7a-9f00-f1691d8ce1e5%22%2C%22df4473fd-3e35-3747-9279-84d01f9b24aa%22%2C%224301b752-c2b5-3756-9780-a0b8bda89272%22%2C%22d0c6d1b7-53ae-3fe2-a437-2c827e04bf8b%22%2C%222200bb5c-4d72-3d1b-b9ec-f1f0703b03a9%22%2C%22SS-f28118b9-343e-372b-bb64-c4c2d467de8e%22%2C%22SS-6e282f26-b6d1-38f7-b46d-095805aa2ac6%22%2C%22SS-674c6e5f-8c9f-394e-ab3b-ca6767b3312f%22%2C%22SS-7ad6f5f6-a188-3291-a15c-85464973acdf%22%5D?bkt=fp-US-en-US-def&device=desktop&feature=cacheContentCanvas%2CenableGuceJs%2CenableGuceJsOverlay%2CvideoDocking%2CnewContentAttribution%2Clivecoverage%2CenableGDPRFooter%2CenableCMP%2CenableConsentData%2CdeferModalCluster%2CcanvassOffnet%2CnewLayout%2CntkFilmstrip%2Csidepic%2CautoNotif%2CfauxdalNewLayout%2CcacheContentCanvasAds&intl=us&lang=en-US&partner=none&prid=03lgvk5dkcgu2&region=US&site=fp&tz=America%2FLos_Angeles&ver=2.0.16039&returnMeta=true"
        body = requests.get(new_url, proxies=proxies, headers=headers_1).json()

        for item in body['data']['items']:
            if item['thumbnail']['url'] != []:
                if item['author'] != [] and item['author'] != None:
                    raw['author'] = item['author']['name']

                else:
                    raw['author'] = ''
                if self.is_source_url_exist(self.input_type, item['url']):
                    self.logger.info('source_url exists: ' + item['url'])
                else:
                    raw['source_url'] = item['url']

                    raw['title'] = item['title']

                    raw['thumbnails'] = [item['thumbnail']['url']]

                    if item['tags'] != [] or item['tags'] != None:
                        raw['tags'] = item['tags']

                    else:
                        raw['tags'] = []

                    new_string = item['publishDateStr'].split(',')[1]
                    month = self.month_transfer(item['publishDateStr'].split(',')[0].split()[0])
                    date = item['publishDateStr'].split(',')[0].split()[1]
                    if len(date) == 2:
                        new_string += '-' + month + '-' + date
                    else:
                        new_string += '-' + month + '-' + '0' + date

                    raw['time'] = new_string
                    raw['publisher'] = 'yahoo'
                    raw['subtitle'] = ''
                    raw['keywords'] = []
                    self.parse_raw(raw)

        headers_2 = {
            'authority': 'www.yahoo.com',
            'method': 'GET',
            'path': '/news/_td/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=news;ssEP=;useSlingstoneLcp=true;uuids=%5B%22SS-fac79539-231b-3a82-9486-dbf0edf3a604%22%2C%2254fcde2b-bb87-3b6e-af1d-cb1573336ed5%22%2C%22fd6db8e1-dda6-399f-b533-08c24eb24147%22%2C%22SS-8d1b9b98-9dd1-3a06-ae5d-1a2984b9b693%22%2C%229cb596d2-a989-39bd-ae5d-2853b64d5c91%22%2C%22SS-78a54d37-6e03-3754-b035-29cfb43acaf0%22%2C%228ec00035-a462-3a6b-99ee-10c0c0c07cac%22%2C%2211c4c7da-15d6-38a4-8381-697a22ef49f7%22%2C%2233696352-3487-358d-8bb9-42fc7358768d%22%2C%229762209d-1950-327c-822b-c13e54dd7c91%22%2C%22SS-ac68ae2b-9d29-3aa3-9db9-f011fb36bb41%22%2C%22SS-b47dd327-e0ee-3e4a-ad43-5b851df0de06%22%2C%22SS-737581df-d314-3337-9e61-4cb7f1677d0a%22%2C%22ff377be1-b4cf-3eda-8312-065604b883d5%22%2C%22SS-1ba59c75-fcb6-3aad-985f-0ef12f0e235e%22%2C%2274734403-06de-3246-b55c-e5c619480fec%22%5D?bkt=fp-US-en-US-def&device=desktop&feature=cacheContentCanvas%2CenableGuceJs%2CenableGuceJsOverlay%2CvideoDocking%2CnewContentAttribution%2Clivecoverage%2CenableGDPRFooter%2CenableCMP%2CenableConsentData%2CdeferModalCluster%2CcanvassOffnet%2CnewLayout%2CntkFilmstrip%2Csidepic%2CautoNotif%2CfauxdalNewLayout%2CcacheContentCanvasAds&intl=us&lang=en-US&partner=none&prid=03lgvk5dkcgu2&region=US&site=fp&tz=America%2FLos_Angeles&ver=2.0.16039&returnMeta=true',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'cookie': 'B=4j433q5djkpmq&b=3&s=8k; flash_enabled=1; GUC=AQEBAQFbRppcFkIbWgRm&s=AQAAAHr4gHRP&g=W0VRbA; cmp=t=1531330949&j=0; apeaf=td-applet-stream=%7B%22tmpl%22%3A%22items%22%2C%22lv%22%3A1531332841717%7D; ucs=lnct=1531269473&bnpt=1531269481&spt=1531331053; yvapF=%7B%22vl%22%3A14.680475000000003%2C%22rvl%22%3A14.680475000000003%2C%22cc%22%3A1%2C%22rcc%22%3A1%7D',
            'device-memory': '8',
            'dpr': '2',
            'referer': 'https://www.yahoo.com/news/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'viewport-width': '764',
            'x-requested-with': 'XMLHttpRequest', }

        new_url = "https://www.yahoo.com/news/_td/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=news;ssEP=;useSlingstoneLcp=true;uuids=%5B%22SS-fac79539-231b-3a82-9486-dbf0edf3a604%22%2C%2254fcde2b-bb87-3b6e-af1d-cb1573336ed5%22%2C%22fd6db8e1-dda6-399f-b533-08c24eb24147%22%2C%22SS-8d1b9b98-9dd1-3a06-ae5d-1a2984b9b693%22%2C%229cb596d2-a989-39bd-ae5d-2853b64d5c91%22%2C%22SS-78a54d37-6e03-3754-b035-29cfb43acaf0%22%2C%228ec00035-a462-3a6b-99ee-10c0c0c07cac%22%2C%2211c4c7da-15d6-38a4-8381-697a22ef49f7%22%2C%2233696352-3487-358d-8bb9-42fc7358768d%22%2C%229762209d-1950-327c-822b-c13e54dd7c91%22%2C%22SS-ac68ae2b-9d29-3aa3-9db9-f011fb36bb41%22%2C%22SS-b47dd327-e0ee-3e4a-ad43-5b851df0de06%22%2C%22SS-737581df-d314-3337-9e61-4cb7f1677d0a%22%2C%22ff377be1-b4cf-3eda-8312-065604b883d5%22%2C%22SS-1ba59c75-fcb6-3aad-985f-0ef12f0e235e%22%2C%2274734403-06de-3246-b55c-e5c619480fec%22%5D?bkt=fp-US-en-US-def&device=desktop&feature=cacheContentCanvas%2CenableGuceJs%2CenableGuceJsOverlay%2CvideoDocking%2CnewContentAttribution%2Clivecoverage%2CenableGDPRFooter%2CenableCMP%2CenableConsentData%2CdeferModalCluster%2CcanvassOffnet%2CnewLayout%2CntkFilmstrip%2Csidepic%2CautoNotif%2CfauxdalNewLayout%2CcacheContentCanvasAds&intl=us&lang=en-US&partner=none&prid=03lgvk5dkcgu2&region=US&site=fp&tz=America%2FLos_Angeles&ver=2.0.16039&returnMeta=true"
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
        body = requests.get(new_url, proxies=proxies, headers=headers_2).json()
        count = 0
        for item in body['data']['items']:
            if item['thumbnail']['url'] != []:
                if item['author'] != [] and item['author'] != None:
                    raw['author'] = item['author']['name']

                else:
                    raw['author'] = ''

                raw['source_url'] = item['url']
                if self.is_source_url_exist(self.input_type, item['url']):
                    self.logger.info('source_url exists: ' + item['url'])
                else:

                    raw['title'] = item['title']

                    raw['thumbnails'] = [item['thumbnail']['url']]

                    if item['tags'] != [] or item['tags'] != None:
                        raw['tags'] = item['tags']

                    else:
                        raw['tags'] = []

                    new_string = item['publishDateStr'].split(',')[1]
                    month = self.month_transfer(item['publishDateStr'].split(',')[0].split()[0])
                    date = item['publishDateStr'].split(',')[0].split()[1]
                    if len(date) == 2:
                        new_string += '-' + month + '-' + date
                    else:
                        new_string += '-' + month + '-' + '0' + date

                    raw['time'] = new_string

                    count += 1
                    raw['publisher'] = 'yahoo'
                    raw['subtitle'] = ''
                    raw['keywords'] = []
                    self.parse_raw(raw)

    def month_transfer(self, month):
        if month == 'Jan.' or month == 'January':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY':
            return '02'
        elif month == 'Mar.' or month == 'MARCH':
            return '03'
        elif month == 'Apr.' or month == 'APRIL':
            return '04'
        elif month == 'May' or month == 'MAY':
            return '05'
        elif month == 'June' or month == 'JUNE':
            return '06'
        elif month == 'July' or month == 'JULY':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER':
            return '12'
        else:
            logging.error('month parser failed')
