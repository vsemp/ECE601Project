import json
import re
from urllib import urlencode
from operator import itemgetter
import requests


class RedditComments:

    def __init__(self):
        pass

    hd_page = {'pragma': 'no-cache',
               'User-Agent': '',
               'cache-control': 'no-cache'}

    reddit_channel_params = {
        'rtj': 'debug',
        'sort_type': 'top',
        'hasSortParam': 'true',
        'allow_over18' : "",
        'include' : ""
    }

    def get_comment_list(self,source_url):
            #crawl the first page
            channel_name = re.findall("https://www.reddit.com/r/(.*?)/", source_url)[0]
            comment_id = re.findall("comments/(.*?)/", source_url)[0]
            self.reddit_channel_params['subredditName'] = channel_name
            Request_URL = 'https://gateway.reddit.com/desktopapi/v1/postcomments/' + comment_id+'?' + urlencode(
            self.reddit_channel_params)
            r_json = requests.get(Request_URL, headers= self.hd_page,verify=False).json()
            comment_list = []
            for comment in r_json['comments'].keys():#t1_e94hdst
                raw = dict()
                item = r_json['comments'][comment]
                if item['parentId'] is None:
                    raw['publisher'] = item['author']
                    raw['like_count'] = item['score']
                    raw['text'] = item['bodyMD']
                    raw['published_time'] = int(item['created'])
                    comment_list.append(raw)
            # crwal the following pages
            while r_json['moreComments']!={} and len(comment_list)<10:
                for comment in r_json['commentLists'].keys():
                    id = r_json['commentLists'][comment]['tail']['id']
                token = r_json['moreComments'][id]['token']
                body = {"token":token}
                body = json.dumps(body)
                target_url = 'https://gateway.reddit.com/desktopapi/v1/morecomments/' + comment_id + '?rtj=debug&allow_over18=&include='
                r_json = requests.post(
                    target_url,
                    data=body, headers=self.hd_page ).json()
                for comment in r_json['comments'].keys():
                    raw = dict()
                    item = r_json['comments'][comment]
                    if item['parentId'] is None:
                        raw['publisher'] = item['author']
                        raw['like_count'] = item['score']
                        raw['text'] = item['bodyMD']
                        raw['published_time'] = int(item['created'])
                        comment_list.append(raw)
            #sort the result list
            sorted_list = sorted(comment_list, key=itemgetter('like_count'))
            sorted_list.reverse()
            print (sorted_list)
            return sorted_list


if __name__ == '__main__':
   comments = RedditComments()
   comments.get_comment_list('https://www.reddit.com/r/funny/comments/9u04iq/subreddit_of_the_month_november_2018/')
