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
from .....spider_const import *
from ...out_link_news import OutLinkNews


# 两个地方要加 self.pawreferrefer
class BodybuildingSpider(OutLinkNews):
    name = 'bodybuilding'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'bodybuilding'
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
    channel_list = ['https://www.bodybuilding.com/recipes?tag=dropdown',
                    'https://www.bodybuilding.com/category/diet-plans?tag=dropdown',
                    'https://www.bodybuilding.com/category/nutrition-tips?tag=dropdown',
                    'https://www.bodybuilding.com/category/meal-planning?tag=dropdown', ]

    def __init__(self, *a, **kw):
        super(BodybuildingSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def parse_list(self, response):
        raw = dict()
        raw.update(response.meta)
        selector = etree.HTML(response.body)
        # print(etree.tostring(selector))
        if raw['inlinks'][0] != 'https://www.bodybuilding.com/recipes?tag=dropdown':
            urls = selector.xpath('//a[@class="thumb-container"]/@href')
            thumbnails = selector.xpath('//a[@class="thumb-container"]/div/img/@data-srcset')
            for index, url in enumerate(urls):
                raw['thumbnails'] = [thumbnails[index].split(',')[1].strip().split(' ')[0]]
                raw['source_url'] = url
                # print(raw['thumbnails'])
                self.content_list.append(copy.deepcopy(raw))

        else:
            # print(etree.tostring(selector))
            headers_1 = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'Connection': 'keep-alive',
                # 'Cookie': 's_fid=1DF261A9F05FD979-3E006DAC9397C6B6; v62=%5B%5BB%5D%5D; v63=%5B%5BB%5D%5D; v66=%5B%5BB%5D%5D; v13=%5B%5BB%5D%5D; s_nr=1531365433157; s_prop_14=Visit; m=12DE4BA8-E012-4ACF-8164-6946925EFEF2; s_cc=true; s_vi=[CS]v1|2DA3641F05030D26-40001193C0000065[CE]; _ga=GA1.2.45587545.1531365433; _gid=GA1.2.2092358617.1531365433; __qca=P0-1607063844-1531365433357; __gads=ID=def54963fb049b60:T=1531365439:S=ALNI_MYPMuK4didibPen2rxo7_SHkrVOHg; s_lv_s=Less%20than%201%20day; s_vnum=1533957433161%26vn%3D3; s_invisit=true; __insp_wid=2024354313; __insp_nv=true; __insp_targlpu=aHR0cHM6Ly93d3cuYm9keWJ1aWxkaW5nLmNvbS9jYXRlZ29yeS9udXRyaXRpb24tdGlwcz90YWc9ZHJvcGRvd24%3D; __insp_targlpt=TnV0cml0aW9uIFRpcHMgQXJ0aWNsZXMgYW5kIFZpZGVvcyAtIEJvZHlidWlsZGluZy5jb20%3D; __insp_norec_sess=true; gpv_pn=fun%3A%20article%3A%20all%20recipes; __insp_slim=1531431463966; bc_pv_end=undefined; s_lv=1531432184787; s_ppv=0; _gat_UA-55035870-1=1; _dc_gtm_UA-55035870-1=1',
                'Host': 'cms-api.bodybuilding.com',
                # 'If-None-Match': 'W/"3083e-HQilu6dbG8dhRXfEOTCJKSHXmrg"',
                'Origin': 'https://www.bodybuilding.com',
                'Referer': 'https://www.bodybuilding.com/recipes?tag=dropdown',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36', }
            new_url = 'https://cms-api.bodybuilding.com/BbcomRecipe?sort=publishDate&order=desc&limit=300'
            try:
                for body in requests.get(new_url, headers=headers_1).json()['_embedded']['bb-cms:search-results']:
                    raw['title'] = body['name']
                    raw['time'] = body['publishDate'].split('T')[0]
                    raw['author'] = body['schemaOrg']['author']['name']
                    # print(raw['title'], raw['time'],raw['author'])
                    raw['tags'] = ['hifit_matrix']
                    raw['source_name'] = 'bodybuilding'
                    raw['publisher'] = 'bodybuilding'
                    raw['keywords'] = []
                    raw['subtitle'] = ''
            except:
                logging.error('article_recipe fails to parse')

    def parse_page(self, response):
        raw = dict()

        raw.update(response.meta)
        selector = etree.HTML(response.body)
        try:
            if raw['thumbnails'] == []:
                pass
            elif raw['inlinks'][0] != 'https://www.bodybuilding.com/recipes?tag=dropdown':
                raw['title'] = selector.xpath('//h1/text()')[0].strip()
                raw['author'] = selector.xpath('//div[@class="BBCMS__content--author-info"]/a/text()')[0].strip()
                time = selector.xpath('//div[@class="BBCMS__content--author-date"]/text()')[0].strip()
                year = time.split(',')[1]
                date = time.split(',')[0].split(' ')[1]
                month = time.split(',')[0].split(' ')[0]
                # print('22', year, date, month)
                # month = self.month_transfer(month)
                # print('11', year, date, month)
                time_raw = year + '-' + month + '-' + date
                raw['time'] = time_raw.strip()

                # print(raw['time'])
                # print(raw['author'])
                # print(raw['title'])
                raw['tags'] = ['hifit_matrix']
                raw['source_name'] = 'bodybuilding'
                raw['publisher'] = 'bodybuilding'
                raw['keywords'] = []
                raw['subtitle'] = ''
                self.parse_raw(raw)
        except:
            logging.error('article fails to parse')

    def month_transfer(self, month):
        if month == 'Jan.' or month == 'January' or month == 'Jan' or month == 'January':
            return '01'
        elif month == 'Feb.' or month == 'FEBRUARY' or month == 'Feb' or month == 'February':
            return '02'
        elif month == 'Mar.' or month == 'MARCH' or month == 'Mar' or month == 'March':
            return '03'
        elif month == 'Apr.' or month == 'APRIL' or month == 'Apr' or month == 'April':
            return '04'
        elif month == 'May' or month == 'MAY' or month == 'May':
            return '05'
        elif month == 'June' or month == 'JUNE' or month == 'Jun' or month == 'June':
            return '06'
        elif month == 'July' or month == 'JULY' or month == 'Jul' or month == 'July':
            return '07'
        elif month == 'Aug.' or month == 'AUGUST' or month == 'Aug' or month == 'August':
            return '08'
        elif month == 'Sept' or month == 'SEPTEMBER' or month == 'Sep' or month == 'September':
            return '09'
        elif month == 'Oct.' or month == 'OCTOBER' or month == 'Oct' or month == 'October':
            return '10'
        elif month == 'Nov.' or month == 'NOVEMBER' or month == 'Nov' or month == 'November':
            return '11'
        elif month == 'Dec.' or month == 'DECEMBER' or month == 'Dec' or month == 'December':
            return '12'
        else:
            logging.error('month parser failed')

    def get_tags_from_raw(self, raw):
        return raw['tags']
