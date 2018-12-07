# -*-coding:utf-8-*-

import shutil
import os
from pymongo import MongoClient
import pandas as pd

from mailer import Mailer
import time
import requests
import json

domain = 'http://gct-storage01.uscasv2.cootek.com:18050'


def request_with_session(suffix, domain=domain,
                         method='get', session=None,
                         **kwargs):
    headers = {
        'name': 'xinyu.du',
        'token': '$2b$12$ArhupzTiMRVSbWH/MmU55eaympbixksSBbH6x6RdvsbK7ME/WzhGi'
    }
    url = '{}/{}'.format(domain, suffix)
    print(url)
    response = requests.request(url=url, headers=headers, method=method, **kwargs)
    print(response.status_code)
    if response.text:
        return response.json()


def get_channel_list():
    suffix = 'content/channels'
    return request_with_session(suffix)


if __name__ == '__main__':
    conn = MongoClient('192.168.173.130', 27017)
    my_set = conn['news']['documents']
    str1 = ""
    for locale in ['en_US', 'th_TH']:
        channel_dict = dict()
        str1 += locale + ":\n"
        result = my_set.aggregate([
            # match the documents possible
            {"$match": {"$and": [{"locale": locale}, {"editor_scores": {"$exists": True}}]}},

            # Group the documents and "count" via $sum on the values
            {"$group": {
                "_id": "$editor_score",
                "count": {"$sum": 1}
            }},
            # order by _id dictionary sequence
            {"$sort": {
                "_id": 1}}
        ])

        for each in result:
            str1 += ("%s^%s" % (each['_id'], each['count']) + '\n')

        str1 += "\n\n\n"
    import redis

    channel_dict = dict()
    for each in get_channel_list():
        channel_dict[each['id']] = '%s %s' % (each['id'], each['display_name'])

    score_dict = dict()
    raw_channel = redis.Redis('redis01.uscasv2.cootek.com', 17090, 0)
    for channel_key in channel_dict:
        key = channel_dict[channel_key]
        try:
            docs = (json.loads(raw_channel[channel_key]))['docs']
            for doc in docs:
                try:
                    for true_doc in my_set.find({"_id": doc['doc_id']}):
                        if key not in score_dict:
                            score_dict[key] = dict()
                            score_dict[key][true_doc['editor_score']] = 1
                        else:
                            if true_doc['editor_score'] in score_dict[key]:
                                score_dict[key][true_doc['editor_score']] += 1
                            else:
                                score_dict[key][true_doc['editor_score']] = 1
                except Exception, e:
                    pass

        except Exception, e:
            print e.message

    import pandas as pd

    df = pd.DataFrame(score_dict)
    df.fillna(0).astype('int64').to_csv('editor_scores.csv')
    print '生成本地csv'
    data_string = time.strftime("%Y%m%d", time.localtime())

    receivers = ['xinyu.du@cootek.cn',
                 'dongdong.zhang@cootek.cn',
                 'feedsinalllanguages@cootek.cn',
                 'guibin.tian@cootek.cn',
                 'contentoperation@cootek.cn'
                 ]
    mailer = Mailer(receivers)
    send_str = 'to dongdong :' + '\n'
    send_str += str1
    file_path = os.getcwd() + '/editor_scores.csv'
    print file_path
    attach_file = mailer.get_attach_from_file(filepath=file_path,
                                              attach_filename=data_string + ' editor_scores.csv')
    mailer.send_mail(subject='editor_scores' + ' log', text=send_str, attach_list=[attach_file])
    print '邮件已发送'

    shutil.rmtree(file_path)
    print '删除csv'
