
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


class TNationSpider(OutLinkNews):
	name = 't_nation'
	region = REGION_AMERICA
	locale = LOCALE_USA_ENGLISH
	source_name = 't_nation'
	input_type = INPUT_TYPE_CRAWL
	download_delay = 3
	datasource_type = 2
	download_maxsize = 104857600
	default_section = 60 * 60 * 24 * 1
	hd = {'pragma': 'no-cache',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
		'Content-Type': 'application/json',
		'cache-control': 'no-cache'}

	browse_times = 0
	browse_limit = 1
	page_times = 0
	page_limit = 1
	content_list = []
	channel_list = [
	'http://t-nation.com/diet-fat-loss/',
	'http://t-nation.com/diet-fat-loss?page=2'
	'http://t-nation.com/diet-fat-loss?page=3'
	'http://t-nation.com/diet-fat-loss?page=4'
	]

	def __init__(self, *a, **kw):
		super(TNationSpider, self).__init__(*a, **kw)
		dispatcher.connect(self.spider_idle, signals.spider_idle)

	def parse_list(self, response):
		raw = dict()
		raw.update(response.meta)
		selector = etree.HTML(response.body)
		urls = selector.xpath('//div[@class="articleWrap clearfix search"]/div[@class="articleImg col-sm-4 hidden-xs"]/a/@href')
		urls = [response.urljoin(url) for url in urls]	
		thumbnails = selector.xpath('//div[@class="articleWrap clearfix search"]/div[@class="articleImg col-sm-4 hidden-xs"]/a/img/@src')
		thumbnails = [response.urljoin(thumbnail) for thumbnail in thumbnails]
		for index, url in enumerate(urls):
			raw['thumbnails'] = [thumbnails[index]]
			raw['source_url'] = url
			self.content_list.append(copy.deepcopy(raw))

	def parse_page(self, response):
		raw = dict()
		
		raw.update(response.meta)
		selector = etree.HTML(response.body)
		try:
			if raw['thumbnails'] == []:
				pass
			else:
				raw['title'] = selector.xpath('//h1[@class="article-detail"]/a/text()')[0]
				raw['author'] = selector.xpath('//div[@class="article-detail-byline"]//a/text()')[0]
				time = selector.xpath('//div[@class="article-detail-byline"]/span[@class="timeStamp3"]/text()')[0]
				year ='20' + time.split('/')[2]
				month = time.split('/')[0]
				date = time.split('/')[1]
				raw['time'] = year +'-' + month + '-' + date
				raw['subtitle'] = selector.xpath('//h2[@class="article-detail"]/text()')[0]
				raw['tags'] = ['hifit_matrix']
				raw['source_name'] = 'tnation'
				raw['publisher'] = 't_nation'
				raw['keywords'] = []
				self.parse_raw(raw)

		except:
			logging.error('article fails to parse')


	def get_tags_from_raw(self, raw):
		return raw['tags']





















