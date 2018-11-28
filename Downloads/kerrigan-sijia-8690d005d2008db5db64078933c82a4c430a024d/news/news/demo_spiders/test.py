import re

import requests
from scrapy import Selector

source_url= 'https://video.sanook.com/player/1338891/'


def parse_page():
    print (111)
    url = 'https://video.sanook.com/player/839809/'
    u='https://video.sanook.com/liveplay/839809.m3u8'
    r = requests.get(u)

    link = re.findall('https:(.*?)m3u8', r.content)[0]
    link="https:"+link+'m3u8'
    print (link)

parse_page()