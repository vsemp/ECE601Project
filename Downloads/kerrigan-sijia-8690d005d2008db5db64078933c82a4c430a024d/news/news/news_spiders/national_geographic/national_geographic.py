# -*- coding: utf-8 -*-
import scrapy
import copy
import re
import json
import scrapy
from scrapy import signals
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
import requests
import lxml
# from feeds_back_utils import *
from lxml import etree
import traceback
import pprint
import hashlib
import datetime
from ..news_spider_base import NewsSpider
from ...spider_const import *
import json
import random

class NationalGeoSpider(NewsSpider):
    name = 'national_geo'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    source_name = 'national_geo'
    input_type = INPUT_TYPE_CRAWL
    download_delay = 3
    datasource_type = 2
    download_maxsize = 104857600
    default_section = 60 * 60 * 24 * 1
    hd = {'pragma': 'no-cache',
          'User-Agent': '',
          'Content-Type': 'application/json',
          'cache-control': 'no-cache'}

    browse_times = 0
    browse_limit = 1
    page_times = 0
    page_limit = 1
    content_list = []
    channel_list = [
        'http://nationalgeographic.com/latest-stories//',
    ]

    def __init__(self, *a, **kw):
        super(NationalGeoSpider, self).__init__(*a, **kw)
        dispatcher.connect(self.spider_idle, signals.spider_idle)

    def spider_idle(self):
        if self.content_list:
            raw = self.content_list.pop(0)
            # source_url 去重
            if False:
                self.logger.info('source_url exists: ' + str(raw['source_url']))
                self.spider_idle()
            else:
                self.logger.warning('content_list pop ed')
                rq = Request(
                    raw['source_url'],
                    headers=self.hd,
                    meta=raw,
                    dont_filter=True,
                    callback=self.parse_page
                )
                self.crawler.engine.crawl(rq, self)
        elif self.channel_list:
            self.browse_times = 0
            for rq in self.start_requests():
                self.crawler.engine.crawl(rq, self)

    def start_requests(self):
        channel_url = self.channel_list.pop()
        raw = dict()
        raw['inlinks'] = [channel_url]
        yield Request(
            url=channel_url,
            meta=raw,
            headers=self.hd,
            dont_filter=True,
            callback=self.parse_list
        )

    def parse_list(self, response):
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


        raw = dict()
        raw.update(response.meta)
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                   'Connection': 'keep-alive',
                   'Cookie': 'ak_bmsc=E8D83307E06646D157C885C8F1DAEEAE60110C0B404E0000A9A3325BB3003140~plyvHQAO/PlTRaU6kVnCgMGh9QN8UxYI2HJcg+cBLRgvKEYMXbbhVEs9zU8V2SFFFP14Ji6Xr9vIfZemP7q085O9aWpU5pEacuFR6MEVB+xVCYy5jrQCvKxkGfr4Q6t3JcWvXUMVtq1CEzlS70zuxn4ujaVsMXBuXgATgMAIfmfDHzFBBDOaFPzOchFLQWZsGmovOFAyfB8Dtt4kuMkCP3FtVO7XnGV0CNeVPl9XMzjJaIp1f5QB9wuE7+N/HJDPt6; ajs_group_id=null; ajs_anonymous_id=%226bb3af18-12da-4b06-ae3d-e127563471a3%22; mt.v=2.1950966652.1530045355260; s_fid=4D5882224DD2946E-10052952724EBB21; c_m=undefinedwww.google.comNatural%20Search; s_c18_stack=%5B%5B%27Natural%2520Search%27%2C%271530045355278%27%5D%5D; s_cc=true; mt.pc=2.1; BCSessionID=1b69c1f2-a864-4056-951f-cf5398f5c84d; seg_xid=4737a21a-ba0b-4d02-a4b3-25480b6817f6; seg_xid_fd=sync.foxnews.com; seg_xid_ts=1530045356179; AMCVS_5BFD123F5245AECB0A490D45%40AdobeOrg=1; _ga=GA1.2.1354855110.1530045358; _gid=GA1.2.1668237410.1530045358; _cb_ls=1; _cb=C9exucCmLsLeBzMe0; __gads=ID=43856b4a69eccd2f:T=1530045360:S=ALNI_Mb84FBE8-TIyVblOrR9bNiS54nLJg; mt.g.2d3efbec=2.1950966652.1530045355260; ats-cid-AM-141131-sid=79393701x; _sp_ses.17c9=*; __utmc=240918044; optimizelyEndUserId=oeu1530045369215r0.5739897466181341; uuidv4=3656e8f9-0b29-4759-99f8-28228273124f; segment-device-id=3656e8f9-0b29-4759-99f8-28228273124f; FOXANONACCT=%7B%22accessToken%22%3A%22eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg5REEwNkVEMjAxOCIsInR5cCI6IkpXVCJ9.eyJwaWQiOiJ3ZWIzNjU2ZThmOS0wYjI5LTQ3NTktOTlmOC0yODIyODI3MzEyNGYiLCJ1aWQiOiJkMlZpTXpZMU5tVTRaamt0TUdJeU9TMDBOelU1TFRrNVpqZ3RNamd5TWpneU56TXhNalJtIiwic2lkIjoiNmMwMTg2NDQtY2E5NS00ZWZlLWIyMDktNzcwYTg4ODc1ZGU2Iiwic2RjIjoidXMtZWFzdC0xIiwiYXR5cGUiOiJhbm9ueW1vdXMiLCJkdHlwZSI6IndlYiIsInV0eXBlIjoiZGV2aWNlSWQiLCJkaWQiOiIzNjU2ZThmOS0wYjI5LTQ3NTktOTlmOC0yODIyODI3MzEyNGYiLCJtdnBkaWQiOiIiLCJ2ZXIiOjIsImV4cCI6MTUzNzgyMTM3MiwianRpIjoiOGZjYjc3N2QtNTljNi00ZmRkLWFkZjgtMmY2ZDFiMTFlMmViIiwiaWF0IjoxNTMwMDQ1MzcyfQ.cD_-jOmRZgY0hr8J-WcngFwhEbZIIG-5XNAiAiw3oRnhOVb3VkmjG7tJOCnWMQ9BAJVGKu40zZPJqZqpKQpXo7DNG1jhmsDLRUric4voZ-_uIVrhwhjUUa_XE8p0vWTG4oWge82qnq5XHujsu8e6W0asVD3fd4S6Ie10zaBIDIIjg7DCUNwCKw7dqgMm8SYYC_cQeQw9LKDU0JdNY-0PGrYrHbmz9zLIgIB-M3I9dvrV5SN0zR10iIHdKd8E53Y5v-koL9Xz64xWhYl-jPB0n-PzfGLGncPj_bJ6sgdIifEELp_C1IrnzVS6RC2nDQ7gFi00oa2Uh8R7cuWG9s6TIw%22%2C%22tokenExpiration%22%3A1537821372000%2C%22profileId%22%3A%22d2ViMzY1NmU4ZjktMGIyOS00NzU5LTk5ZjgtMjgyMjgyNzMxMjRm%22%2C%22deviceId%22%3A%223656e8f9-0b29-4759-99f8-28228273124f%22%2C%22accountType%22%3A%22anonymous%22%2C%22userType%22%3A%22deviceId%22%2C%22brand%22%3A%22ngc%22%2C%22platform%22%3A%22delta_ngc_web_en-US%22%2C%22isVerified%22%3Afalse%2C%22newsLetter%22%3Afalse%2C%22hasSocialLogin%22%3Afalse%2C%22hasEmail%22%3Afalse%2C%22device%22%3A%22web%22%2C%22viewerId%22%3A%22web3656e8f9-0b29-4759-99f8-28228273124f%22%2C%22dma%22%3A%22807%22%2C%22ipAddress%22%3A%2212.20.58.226%2C%2096.17.12.44%2C%2023.216.7.222%22%2C%22userAgent%22%3A%22Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_13_4)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F67.0.3396.87%20Safari%2F537.36%22%2C%22firstName%22%3A%22%22%2C%22lastName%22%3A%22%22%7D; ajs_user_id=%22d2ViMzY1NmU4ZjktMGIyOS00NzU5LTk5ZjgtMjgyMjgyNzMxMjRm%22; aam_uuid=24520033567180882473857415950506826198; fox-favorites-0=%5B%5D; ats-cid-AM-141086-sid=12324046x; mvpd-auth=%7B%22accessToken%22%3A%22eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg5REEwNkVEMjAxOCIsInR5cCI6IkpXVCJ9.eyJwaWQiOiJ3ZWIzNjU2ZThmOS0wYjI5LTQ3NTktOTlmOC0yODIyODI3MzEyNGYiLCJ1aWQiOiJkMlZpTXpZMU5tVTRaamt0TUdJeU9TMDBOelU1TFRrNVpqZ3RNamd5TWpneU56TXhNalJtIiwic2lkIjoiNmMwMTg2NDQtY2E5NS00ZWZlLWIyMDktNzcwYTg4ODc1ZGU2Iiwic2RjIjoidXMtZWFzdC0xIiwiYXR5cGUiOiJhbm9ueW1vdXMiLCJkdHlwZSI6IndlYiIsInV0eXBlIjoiZGV2aWNlSWQiLCJkaWQiOiIzNjU2ZThmOS0wYjI5LTQ3NTktOTlmOC0yODIyODI3MzEyNGYiLCJtdnBkaWQiOiJUZW1wUGFzc19mYmNmb3hfNjBtaW4iLCJ2ZXIiOjIsImV4cCI6MTUzNzgyMTM5NywianRpIjoiNDliNDVkYTgtZjNiMC00NTliLTk0MGUtZTMyMzJkNWI0N2U0IiwiaWF0IjoxNTMwMDQ1Mzk3fQ.dsBF8FaLRjywDoRPlgJ7gbsNx0AfMVVVNm3w6jR8p2GHaHcFvSkbZfnAdt2hfy7uwNsDIgT_UVBUOtWqAHqDL91HgCK01BAn_0VemklUb9W7akH9WOVQ63egw2_G1pwhyn6VNwfOpBRa9D9xvS1ai4csmAUlb3U0rcT_nHKGyRxa19gyQQYHK-LS8n6C9DY4HoJkIPYpuEDkNxkIEqap1TQ44RZiQOU8jj3TjrjcbsQtarOXtYWxZmV49mTTaqJzaFp99cg6usPbJO2Rtg329Sswyq6MnQjhouMCrOTVKaK2kUL381sBr9d5NKDu8nsWZLMs2VXOZPwtAbj1HtNgNg%22%2C%22tokenExpiration%22%3A1537821397000%2C%22mvpd%22%3A%22TempPass_fbcfox_60min%22%2C%22authn_expire%22%3A1530048989000%2C%22preauthorizedResources%22%3A%5B%22fbc-fox%22%2C%22fs1%22%2C%22fs2%22%2C%22fx%22%2C%22fxm%22%2C%22fxx%22%2C%22ngc%22%2C%22ngw%22%5D%2C%22metadata%22%3A%7B%22zip%22%3A%5B%5D%2C%22encryptedZip%22%3A%22%22%2C%22upstreamUserID%22%3A%22%22%2C%22mvpd%22%3A%22TempPass_fbcfox_60min%22%2C%22maxRating%22%3A%7B%7D%2C%22encrypted%22%3A%5B%5D%2C%22updated%22%3A1530045398665%7D%7D; __olapicU=1530045482175; _v__chartbeat3=0H_0gCbn12rBNA-q8; __utmz=240918044.1530045793.3.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); mt.s-lbx=2; mt.pv_m=(NGMUSDESK:(pageViewCount:2,remainingViewCount:1)); AMCV_5BFD123F5245AECB0A490D45%40AdobeOrg=1406116232%7CMCIDTS%7C17709%7CMCMID%7C24706441725938475083874910533539169589%7CMCAAMLH-1530652158%7C9%7CMCAAMB-1530652158%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1530054558s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-17716%7CvVersion%7C2.5.0; utag_vnum=1532637354907&vn=2; utag_invisit=true; utag_dslv_s=Less than 1 day; s_visit=1; s_vnum=1530428400279%26vn%3D2; s_invisit=true; __utma=240918044.1354855110.1530045358.1530045793.1530049940.4; __atuvc=4%7C26; __atuvs=5b32b58a8781e977000; __utmb=240918044.2.8.1530050268326; _cb_svref=null; s_sq=%5B%5BB%5D%5D; _ceg.s=payaec; _ceg.u=payaec; RT="sl=0&ss=1530045922143&tt=0&obo=0&sh=1530049940057%3D1%3A0%3A11353%2C1530047431714%3D25%3A5%3A108945%2C1530047406311%3D24%3A5%3A100134%2C1530047368902%3D23%3A5%3A95088%2C1530046503579%3D22%3A5%3A83597&dm=nationalgeographic.com&si=4eb200d8-739a-42eb-ac8d-12355814ebfd&bcn=%2F%2F17d98a59.akstat.io%2F&r=https%3A%2F%2Fwww.nationalgeographic.com%2Flatest-stories%2F&ul=1530051072321&hd=1530051072566"; utag_main=v_id:01643dcf539500202ed90b8ce8080407800230700093c$_sn:2$_ss:0$_st:1530052872890$vapi_domain:nationalgeographic.com$ses_id:1530049930215%3Bexp-session$_pn:10%3Bexp-session; utag_dslv=1530051072897; bm_sv=1CC90DC76CC49B21BF11C1E7333A288E~2BIBCFNGowj5r0+Sc5StRYnIIT2Pk2yixvSiOAHceBWz4n+DNaTGa6schm14QZtiMxb0OEHesJ6S4GI5gqBMVJTY7FwBhMu3hsNB5lXGC6fDPMVWcqJYP9ZaCLzbmSizjG3X7iqfE4yCgU9zfam8elOxugigenV0pYwpYSq5E7E=; _chartbeat2=.1530045359526.1530051073156.1.CUfmlKprSloD2mIE5DcWktEBeYbZQ.4; _sp_id.17c9=17aac7e73a9cd9ee.1530045362.1.1530051073.1530045362; _dc_gtm_UA-28236326-1=1; _gat_verificationTracker=1; GED_PLAYLIST_ACTIVITY=W3sidSI6ImkxYTEiLCJ0c2wiOjE1MzAwNTEwNzQsIm52IjowLCJ1cHQiOjE1MzAwNDk5NDAsImx0IjoxNTMwMDUwMzE3fV0.',
                   'Host': 'www.nationalgeographic.com',
                   'Referer': 'https://www.nationalgeographic.com/',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
                   'X-NewRelic-ID': 'Uw4AWVVACgsJVVlWAwM=',
                   'X-Requested-With': 'XMLHttpRequest', }
        page_number = 300
        for i in range(page_number):
            url = 'https://www.nationalgeographic.com/bin/services/core/public/query/content.json?contentTypes=adventure/components/pagetypes/story/article,adventure/components/pagetypes/story/interactive,adventure/components/pagetypes/story/multipage,animals/components/pagetypes/story/article,animals/components/pagetypes/story/interactive,animals/components/pagetypes/profile/animal,archaeologyandhistory/components/pagetypes/story/article,archaeologyandhistory/components/pagetypes/story/interactive,environment/components/pagetypes/story/article,environment/components/pagetypes/story/interactive,magazine/components/pagetypes/story/article,magazine/components/pagetypes/story/interactive,news/components/pagetypes/story/article,news/components/pagetypes/story/interactive,peopleandculture/components/pagetypes/story/article,peopleandculture/components/pagetypes/story/interactive,photography/components/pagetypes/story/article,photography/components/pagetypes/story/interactive,science/components/pagetypes/story/article,science/components/pagetypes/story/interactive,travel/components/pagetypes/story/article,travel/components/pagetypes/story/interactive,travel/components/pagetypes/story/multipage,video/components/pagetypes/story/article&sort=newest&operator=or&includedTags=&excludedTags=ngs_genres:reference,ngs_series:expedition_antarctica,ngs_visibility:omit_from_hp&excludedGuids=beda7baa-e63b-4276-8122-34e47a4e653e&pageSize=12&page={}&offset=0'.format(
                i)
            json_list = requests.get(url, headers=headers,proxies=proxies)
            for json_test in json.loads(json_list.text):
                raw['source_url'] = json_test['page']['url']
                self.content_list.append(copy.deepcopy(raw))

    def parse_page(self, response):
        raw = dict()
        raw.update(response.meta)
        # try:
        content = []
        selector = etree.HTML(response.body)
        json_data = selector.xpath('//div[@data-pestle-module="PresentationMode"]/script[@type="text/json"]/text()')
        dict_content = {}
        title = json.loads(json_data[0])['json']['title']
        raw["title"] = title
        images = []

        for items in json.loads(json_data[0])['json']['items'][0]['items']:
            images.append(items['url'])
        time = selector.xpath('//time[@itemprop="datePublished"]/text()')
        new_string = time[0].split(',')[1]
        month = self.month_transfer(time[0].strip().split(',')[0].split()[0])
        date = time[0].strip().split(',')[0].split()[1]
        if len(date) == 2:
            new_string += '-' + month + '-' + date
        else:
            new_string += '-' + month + '-' + '0' + date
            raw['author'] = ''
            raw["time"] = new_string
            raw['keywords'] = []
            raw['tags'] = []
            raw['publisher'] = ''
            raw['subtitle'] = ''
            raw['content'] = []
        if len(images) >= 3:
            raw['thumbnails'] = images[:3]

            for image in images:
                dict_content['image'] = image
                dict_content['text'] = ''
                dict_content['rich_content'] = ''
                content.append(copy.deepcopy(dict_content))
            articles = selector.xpath('//div[@class="parbase smartbody section text"]/p')
            for article in articles:
                html_tag = etree.tostring(article, method='html', with_tail=False)
                text = re.sub('<[^>]*>', '', html_tag)
                dict_content['image'] = ''
                dict_content['text'] = text
                dict_content['rich_content'] = ''
                content.append(copy.deepcopy(dict_content))
            raw['content'] = content

            self.parse_raw(raw)

        # except:
        #     self.logger.error('article parser failed')

    def generate_message(self, article_info):
        message = super(NationalGeoSpider, self).generate_message(article_info)
        if 'inlinks' in article_info['raw']:
            message['inlinks'] = article_info['raw']['inlinks']
        return message

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
            self.logger.error('month parser failed')

    def get_time_from_raw(self, raw):
        time = datetime.datetime.strptime(raw['time'], '%Y-%m-%d')
        return str(time)[:19]

    def get_html_from_raw(self, raw):
        return ''

    def get_raw_tags_from_raw(self, raw):
        tag_list = raw['tags']
        return tag_list

    def get_title_from_raw(self, raw):
        return raw['title']

    def get_thumbnails_from_raw(self, raw):
        return raw['thumbnails']

    def get_doc_id_from_raw(self, raw):
        return hashlib.md5(str(raw['source_url'])).hexdigest()

    def get_source_url_from_raw(self, raw):
        return raw['source_url']

    def get_locale_from_raw(self, raw):
        return self.locale

    def get_content_from_raw(self, raw):
        return raw['content']

    def get_publish_time_from_raw(self, raw):
        return str(datetime.datetime.now())[:19]

    def get_keywords_from_raw(self, raw):
        return []

    def get_tags_from_raw(self, raw):
        return []

    def get_extra_from_raw(self, raw):
        return {'key': 'extra_key'}

    def get_publisher_from_raw(self, raw):
        return ""

    def get_publisher_icon_from_raw(self, raw):
        return []

    def get_publisher_id_from_raw(self, raw):
        return -1

    def get_source_name_from_raw(self, raw):
        return self.source_name

    def get_subtitle_from_raw(self, raw):
        return ""

    def get_input_type_from_raw(self, raw):
        return self.input_type
