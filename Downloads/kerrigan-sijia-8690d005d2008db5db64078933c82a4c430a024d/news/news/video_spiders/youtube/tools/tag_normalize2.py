# -*- coding: utf-8 -*-
import redis
import json
import time
import pymongo
import random
import hashlib
from pymongo import MongoClient
from langdetect import detect
from langdetect import detect_langs

if __name__ == '__main__':
    conn = MongoClient(
        'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
        readPreference="primary")
    my_set = conn['news']['documents']  # 连接mydb数据库，没有则自动创建

    hash_value = 2

    index = 0
    # for each in list1:
    for each in my_set.find({"lang_detect": {"$exists": False}}, no_cursor_timeout=True):
        source_hash = int(hashlib.md5(str(each['doc_id'])).hexdigest(), 16)
        if source_hash % 4 != hash_value:
            continue
        else:
            index += 1
            if index % 100 == 0:
                print index
            try:
                detect_detail = dict()
                detect_str = detect(each['title'])
                for sb in detect_langs(each['title']):
                    sb = str(sb)
                    lang = str(sb.split(':')[0])
                    rate = float(sb.split(':')[1])
                    detect_detail[lang] = rate
                my_set.update({"doc_id": str(each['doc_id'])},
                              {'$set': {"lang_detect": detect_str, "lang_detect_details": detect_detail}})
            except:
                print 'detact_error : %s' % each['title']

                my_set.update({"doc_id": str(each['doc_id'])}, {'$set': {"lang_detect": 'error'}})

    print 'done'