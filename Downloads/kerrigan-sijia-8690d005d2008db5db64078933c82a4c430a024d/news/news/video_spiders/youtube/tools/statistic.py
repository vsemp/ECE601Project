import json
import re
import requests
import lxml
from lxml import etree
import random
import copy
import logging


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
    def get_comments_page(video_id):
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
                    raw['publisher'] = each.xpath(
                        'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/a'
                    )[0].xpath('string(.)').strip()
                    raw['like_count'] = int(each.xpath(
                        'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-footer"]/div[@class="comment-action-buttons-toolbar"]/span[@class="comment-renderer-like-count off"]'
                    )[0].xpath('string(.)').strip())
                    comment_list.append(raw)
                except:
                    logging.error('partial parser failed')
        except:
            logging.error('video_comment parser failed')

        return comment_list


if __name__ == '__main__':
    from lxml import html
    from lxml import etree

    source_url_list = [
        #'https://www.youtube.com/watch?v=EkA6GrvjNl0',
        'https://www.youtube.com/watch?v=3uXOqbic2xg',
        # 'https://www.youtube.com/watch?v=uSu0XeVitNE',
        # 'https://www.youtube.com/watch?v=R-m6OKabqI0',
        # 'https://www.youtube.com/watch?v=Sq8MVps-C4s',
        # 'https://www.youtube.com/watch?v=bKU4hMv2mOg',
        # 'https://www.youtube.com/watch?v=asj1klIcDqw',
        # 'https://www.youtube.com/watch?v=Rj6zFECRSII',
    ]
    videoId_list = []

    # with open('youtube_url_samples', 'r') as fh:
    for line in source_url_list:
        videoId_list.append(line.split('v=')[1].strip())

    comment_lists = []

    count = 0
    for video_id in videoId_list:
        count += 1
        print('99', count, video_id)
        raw = YoutubeStatistic.get_comment_list(video_id)
        print json.dumps(raw, ensure_ascii=False, sort_keys=True,
                         encoding='utf8').encode('utf8')
        #     comment_lists.append(raw)
        #
        # for comment_list in comment_lists:
        #         print comment_list
