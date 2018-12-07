from ...g9ag.g9ag_base import g9agSpiderBase
from ....spider_const import *
import json
import re


class g9agSpider(g9agSpiderBase):
    name = 'gif_9gag'
    region = REGION_AMERICA
    locale = LOCALE_USA_ENGLISH
    input_type = INPUT_TYPE_CRAWL
    channel_list = ['https://9gag.com/gif']

    browse_limit = 5

    def parse_page(self, response):
        tjson = json.loads(
            re.findall('GAG.App.loadConfigs\((.*?)\).loadAsynScripts', response.body_as_unicode())[0])
        # try:
        video = tjson['data']['post']['images']['image460sv']['h265Url']
        raw = dict()
        raw.update(response.meta)
        if video.split('.')[-1] == 'mp4':
            raw['video'] = video
            raw['duration'] = tjson['data']['post']['images']['image460sv']['duration']
            raw['source_url'] = response.url
            raw['title'] = tjson['data']['post']['title']
            raw['tags'].extend(tjson['data']['post']['sections'])
            raw['thumbnails'] = [tjson['data']['post']['images']['image460']['url']]
            raw['doc_id'] = tjson['data']['post']['id']
            raw['video_width'] = tjson['data']['post']['images']['image460sv']['width']
            raw['video_height'] = tjson['data']['post']['images']['image460sv']['height']
            keywords = []
            for each in tjson['data']['post']['tags']:
                keywords.append(each['key'])
            raw['keywords'] = keywords
            raw['inlinks'] = ['https://9gag.com/gif']
            self.parse_raw(raw)
        else:
            self.logger.error('not a mp4 gif')
            # except Exception, e:
            #     self.logger.warning(e)
            #     return

    def get_video_type_from_raw(self, raw):
        return VIDEO_TYPE_GIF_VIDEO
