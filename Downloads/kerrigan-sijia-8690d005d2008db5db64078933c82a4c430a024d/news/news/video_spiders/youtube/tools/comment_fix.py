# import redis
# import json
# import time
# import pymongo
# import random
# from pymongo import MongoClient
# import hashlib
# import requests
# conn = MongoClient(
#     'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
#     readPreference="primary")
# my_set = conn['comments']['crawled_comments']
# data_string = time.strftime("%Y%m%d", time.localtime())
#
# hash_value = 0
#
# def get_ts(raw_date_string):
#     if u'\u6708' in raw_date_string:
#         return random.randint(1519702789, 1527392389)
#     if u'\u5e74' in raw_date_string:
#         return random.randint(1514777989, 1519702789)
#     if u'\u9031' in raw_date_string:
#         return random.randint(1528171110, 1529553510)
#
#     if u'\u5929' in raw_date_string:
#         return random.randint(1529553510, 1529985510)
#
#     return random.randint(1529985510, 1530072078)
#
# # r = requests.get('https://www.veeuapp.com/content/feeds?page_type=channel&id=c_1&history=false&count=10000')
# # doc_list = r.json()['doc_list']
# # doc_url_list = []
# # for each in doc_list:
# #     doc_url_list.append(each['doc_id'])
# # print(len(doc_list))
#
# for i in my_set.find({}):
#     if 'with_comment_ts' in i:
#         continue
#     source_hash = int(hashlib.md5(str(i['doc_id'])).hexdigest(), 16)
#     if source_hash % 4 != hash_value:
#         continue
#     else:
#         pass
#
#     new_list = []
#     comment_list = i['comment_list']
#     for each in comment_list:
#         each['publish_ts'] = get_ts(each['raw_date_string'])
#         new_list.append(each)
#
#     my_set.update({"doc_id": i['doc_id']}, {'$set': {"comment_list": new_list}}, multi=True)
#     my_set.update({"doc_id": i['doc_id']}, {'$set': {"with_comment_ts": True}}, multi=True)
#     my_set.update({"doc_id": i['doc_id']}, {'$set': {"send_to_xialu": False}}, multi=True)
#     print(i['doc_id'])
