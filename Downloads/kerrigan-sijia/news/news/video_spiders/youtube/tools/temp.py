# -*- coding: UTF-8 -*-
import json
import re
import requests
import lxml
from lxml import etree
import sys
import copy
import json
import logging
import datetime
import random

class YoutubeStatistic:
    @staticmethod
    def is_stats_available(page):
        return 'action-panel-trigger-stats' in page

    @staticmethod
    def extract_xsrf_token(page):
        token_regex = re.compile('\'XSRF_TOKEN\'\s*\n*:\s*\n*"(.*)"', re.IGNORECASE)
        match = re.search(token_regex, page)
        session_token = match.groups()[0]
        return session_token

    @staticmethod
    def extract_comment_token(page):
        token_regex = re.compile("'COMMENTS_TOKEN': \"(.*?)\"", re.IGNORECASE)
        match = re.search(token_regex, page)
        comment_token = match.groups()[0]
        return comment_token

    @staticmethod
    def extract_statistics(page):
        statistics_regex = re.compile('<graph_data><!\[CDATA(.*)]><\/graph_data>', re.IGNORECASE)
        match = re.search(statistics_regex, page)
        return match.groups()[0]

    @staticmethod
    def fetch_statistic_page(video_id):
        r = requests.get('https://www.youtube.com/watch?v=' + video_id)
        if YoutubeStatistic.is_stats_available(r.text):
            cookies = r.cookies
            xsrf_token = YoutubeStatistic.extract_xsrf_token(r.text)
            payload = {'session_token': xsrf_token}
            stats_raw = requests.post(
                'https://www.youtube.com/insight_ajax?action_get_statistics_and_data=1&v=' + video_id, data=payload,
                cookies=cookies)
            return stats_raw.text

    @staticmethod
    def fetch_comments_page(video_id):
        r = requests.get('https://www.youtube.com/watch?v=' + video_id)
        cookies = r.cookies
        xsrf_token = YoutubeStatistic.extract_xsrf_token(r.text)
        comment_token = YoutubeStatistic.extract_comment_token(r.text)
        payload = {'session_token': xsrf_token}
        stats_raw = requests.post(
            'https://www.youtube.com/watch_fragments2_ajax?frags=comments&spf=load&v=' + video_id + '&ctoken=' + comment_token,
            data=payload, cookies=cookies)
        return stats_raw.text

    @staticmethod
    def get_comments_count(video_id):
        html_body = json.loads(YoutubeStatistic.fetch_comments_page(video_id))['body']['watch-discussion']
        tree = lxml.html.fromstring(html_body)
        int(re.findall("&#8226; ([0-9,]+)",
                       etree.tostring(tree.xpath('//*[@id="comment-section-renderer"]/div[1]/h2')[0], method='html',
                                      with_tail=False))[0].replace(',', ""))

    """
    @staticmethod
    def get_comment_list(video_id):

        raw = []
        #try:
        html_body = json.loads(YoutubeStatistic.fetch_comments_page(video_id))['body']['watch-discussion']
        tree = html.fromstring(html_body)

        dict_content = {}
        texts = tree.xpath('//div[@class="comment-renderer-text-content"]')
        publishers = tree.xpath('//div[@class="comment-renderer-header"]/a/text() | //div[@class="comment-renderer-header"]/span/a/text()')
        print(publishers)
        publishers = [publisher for publisher in publishers if 'ago' not in publisher]

        likes = tree.xpath('//span[@class="comment-renderer-like-count on"]/text()')
        publish_ts = tree.xpath('//span[@class="comment-renderer-time"]/a/text()')

        for i in range(len(texts)):

            text = etree.tostring(texts[i], method = 'html', with_tail=False)

            text = re.sub('<[^>]*>', '', text)
            dict_content['text'] = text.encode('utf-8').decode('utf-8-sig').strip().replace('&#65279','')
            dict_content['publisher'] = publishers[i].encode('utf-8').decode('utf-8-sig').strip()
            dict_content['like'] = likes[i]
            dict_content['publish_ts'] = publish_ts[i]

            raw.append(copy.deepcopy(dict_content))

        #except:
            #logging.error('video_comment parser failed')

        return raw
    """

    @staticmethod
    def get_comment_list(video_id):
        comment_list = []

        try:

            html_body = json.loads(YoutubeStatistic.fetch_comments_page(video_id))['body']['watch-discussion']

            tree = html.fromstring(html_body)

            comment_sections = tree.xpath('//*[@id="comment-section-renderer-items"]/section')

            for each in comment_sections:
                try:

                    raw = dict()
                    raw['text'] = each.xpath(
                        'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-text"]/div[@class="comment-renderer-text-content"]'
                    )[0].xpath('string(.)').strip()

                    if each.xpath(
                            'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/a | div[1]/div[@class="comment-renderer-content"] \
                                             /div[@class="comment-renderer-header"]/span[@class="comment-renderer-author-comment-badge"]/a ') == []:
                        raw['publisher'] = 'zhangsan'
                    else:

                        raw['publisher'] = each.xpath(
                            'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/a | div[1]/div[@class="comment-renderer-content"] \
                                             /div[@class="comment-renderer-header"]/span[@class="comment-renderer-author-comment-badge"]/a '
                        )[0].xpath('string(.)').strip()

                    if each.xpath(
                            'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-footer"]/div[@class="comment-action-buttons-toolbar"]/span[@class="comment-renderer-like-count off"]') == []:
                        raw['like_count'] = 0
                    else:
                        raw['like_count'] = int(each.xpath(
                            'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-footer"]/div[@class="comment-action-buttons-toolbar"]/span[@class="comment-renderer-like-count off"]'
                        )[0].xpath('string(.)').strip())

                    raw_date_string = each.xpath(
                        'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/span[@class="comment-renderer-time"]/a/text()')
                    raw['raw_date_string'] = raw_date_string
                    raw['publish_ts'] = YoutubeStatistic.time_stamp(raw_date_string)

                    comment_list.append(raw)
                except:
                    logging.error('partial parser failed')
        except:
            logging.error('video_comment parser failed')

        return comment_list

    @staticmethod
    def time_stamp(time_raw):

        time_raw = time_raw[0].split(' ')
        time_modified = ''

        if time_raw[1] == 'weeks' or time_raw[1] == 'week':
            if int(time_raw[0]) == 1:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=1 * 7)
            elif int(time_raw[0]) == 2:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=2 * 7)
            elif int(time_raw[0]) == 3:
                time_modified == datetime.datetime.now() - datetime.timedelta(days=3 * 7)
            elif int(time_raw[0]) == 4:
                time_modified == datetime.datetime.now() - datetime.timedelta(days=4 * 7)
            else:
                logging.error('week transfer failed')
        elif time_raw[1] == 'month' or time_raw[1] == 'months':
            if int(time_raw[0]) == 1:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=1 * 30)
            elif int(time_raw[0]) == 2:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=2 * 30)
            elif int(time_raw[0]) == 3:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
            elif int(time_raw[0]) == 4:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=4 * 30)
            elif int(time_raw[0]) == 5:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=5 * 30)
            elif int(time_raw[0]) == 6:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=6 * 30)
            elif int(time_raw[0]) == 7:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=7 * 30)
            elif int(time_raw[0]) == 8:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=8 * 30)
            elif int(time_raw[0]) == 9:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=9 * 30)
            elif int(time_raw[0]) == 10:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=10 * 30)
            elif int(time_raw[0]) == 11:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=11 * 30)
            else:
                logging.error('month transfer failed')
        elif time_raw[1] == 'year' or time_raw[1] == 'years':
            if int(time_raw[0]) == 1:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=1 * 365)
            elif int(time_raw[0]) == 2:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=2 * 365)
            else:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=3 * 365)

        return time_modified


if __name__ == '__main__':
    from lxml import html
    from lxml import etree

    source_url_list = [
        'https://www.youtube.com/watch?v=EkA6GrvjNl0',
        'https://www.youtube.com/watch?v=3uXOqbic2xg',
        'https://www.youtube.com/watch?v=uSu0XeVitNE',
        'https://www.youtube.com/watch?v=R-m6OKabqI0',
        'https://www.youtube.com/watch?v=Sq8MVps-C4s',
        'https://www.youtube.com/watch?v=bKU4hMv2mOg',
        'https://www.youtube.com/watch?v=asj1klIcDqw',
        'https://www.youtube.com/watch?v=Rj6zFECRSII',
    ]
    videoId_list = []

    for line in source_url_list:
        videoId_list.append(line.split('v=')[1].strip())

    comment_lists = []

    count = 0
    for video_id in videoId_list:
        count += 1
        print('99', count, video_id)
        raw = YoutubeStatistic.get_comment_list(video_id)
        print raw
    #     comment_lists.append(raw)
    #
    # for comment_list in comment_lists:
    #         print comment_list



