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

faker_user_list = [
    '72057595152673227',
    '72057595152675438',
    '72057595152675589',
    '72057595152679440',
    '72057595152679741',
    '72057595152679792',
    '72057595152679943',
    '72057595152680044',
    '72057595152687455',
    '72057595152689886',
    '72057595152690037',
    '72057595152690138',
    '72057595152692869',
    '72057595152693170',
    '72057595152693271',
    '72057595152693322',
    '72057595152693573',
    '72057595152693724',
    '72057595152693925',
    '72057595152694026',
    '72057595152694177',
    '72057595152694278',
    '72057595152694279',
    '72057595152694480',
    '72057595152694681',
    '72057595152694782',
    '72057595152694833',
    '72057595152694934',
    '72057595152695085',
    '72057595152695286',
    '72057595152695437',
    '72057595152695488',
    '72057595152695569',
    '72057595152695720',
    '72057595152695771',
    '72057595152695922',
    '72057595152696073',
    '72057595152696124',
    '72057595152696225',
    '72057595152696226',
    '72057595152696227',
    '72057595152696228',
    '72057595152696329',
    '72057595152696380',
    '72057595152696681',
    '72057595152696782',
    '72057595152696883',
    '72057595152697034',
    '72057595152697035',
    '72057595152697086',
    '72057595152697337',
    '72057595152697388',
    '72057595152697489',
    '72057595152697590',
    '72057595152697641',
    '72057595152697692',
    '72057595152697843',
    '72057595152697894',
    '72057595152698195',
    '72057595152698496',
    '72057595152698827',
    '72057595152698978',
    '72057595152699179',
    '72057595152699380',
    '72057595152699531',
    '72057595152699632',
    '72057595152699683',
    '72057595152699734',
    '72057595152699885',
    '72057595152700066',
    '72057595152700267',
    '72057595152700518',
    '72057595152700669',
    '72057595152700820',
    '72057595152700821',
    '72057595152701022',
    '72057595152701223',
    '72057595152701274',
    '72057595152701425',
    '72057595152701476',
    '72057595152701627',
    '72057595152701928',
    '72057595152702079',
    '72057595152702180',
    '72057595152702231',
    '72057595152702532',
    '72057595152702533',
    '72057595152702584',
    '72057595152702635',
    '72057595152702686',
    '72057595152702737',
    '72057595152702788',
    '72057595152702889',
    '72057595152702940',
    '72057595152703141',
    '72057595152703242',
    '72057595152703343',
    '72057595152703594',
    '72057595152703595',
    '72057595152703596',
    '72057595152703597',
    '72057595152703898',
    '72057595152704049',
    '72057595152673227',
    '72057595152675438',
    '72057595152704200',
    '72057595152704401',
    '72057595152704402',
    '72057595152704403',
    '72057595152704404',
    '72057595152679440',
    '72057595152704555',
    '72057595152679943',
    '72057595152680044',
    '72057595152687455',
    '72057595152689886',
    '72057595152704806',
    '72057595152704957',
    '72057595152690138',
    '72057595152692869',
    '72057595152693170',
    '72057595152705558',
    '72057595152705609',
    '72057595152705710',
    '72057595152693322',
    '72057595152705861',
    '72057595152705912',
    '72057595152706113',
    '72057595152693724',
    '72057595152706264',
    '72057595152694279',
    '72057595152706365',
    '72057595152694480',
    '72057595152694782',
    '72057595152706566',
    '72057595152706817',
    '72057595152706948',
    '72057595152706999',
    '72057595152694934',
    '72057595152695085',
    '72057595152695437',
    '72057595152695488',
    '72057595152707700',
    '72057595152707731',
    '72057595152695569',
    '72057595152707782',
    '72057595152695720',
    '72057595152708033',
    '72057595152695771',
    '72057595152708084',
    '72057595152708185',
    '72057595152696124',
    '72057595152708486',
    '72057595152696225',
    '72057595152696226',
    '72057595152709087',
    '72057595152696227',
    '72057595152696228',
    '72057595152709388',
    '72057595152709439',
    '72057595152709540',
    '72057595152696380',
    '72057595152709571',
    '72057595152696681',
    '72057595152696782',
    '72057595152709722',
    '72057595152709923',
    '72057595152696883',
    '72057595152697034',
    '72057595152697035',
    '72057595152697086',
    '72057595152710374',
    '72057595152697337',
    '72057595152697388',
    '72057595152710725',
    '72057595152697489',
    '72057595152697641',
    '72057595152710926',
    '72057595152697692',
    '72057595152711177',
    '72057595152697894',
    '72057595152711328',
    '72057595152711479',
    '72057595152698195',
    '72057595152698496',
    '72057595152711680',
    '72057595152711881',
    '72057595152712082',
    '72057595152698978',
    '72057595152712333',
    '72057595152712334',
    '72057595152699179',
    '72057595152712385',
    '72057595152712436',
    '72057595152712537',
    '72057595152699531',
    '72057595152712888',
    '72057595152713039',
    '72057595152699632',
    '72057595152699683',
    '72057595152699885',
    '72057595152700066',
    '72057595152713190',
    '72057595152700267',
    '72057595152700820',
    '72057595152701022',
    '72057595152701274',
    '72057595152713741',
    '72057595152713892',
    '72057595152701627',
    '72057595152701928',
    '72057595152702079',
    '72057595152714243',
    '72057595152714444',
    '72057595152714625',
    '72057595152714676',
    '72057595152702584',
    '72057595152702737',
    '72057595152715127',
    '72057595152715228',
    '72057595152715279',
    '72057595152702788',
    '72057595152702889',
    '72057595152703141',
    '72057595152703242',
    '72057595152716180',
    '72057595152703343',
    '72057595152703595',
    '72057595152716431',
    '72057595152716432',
    '72057595152703596',
    '72057595152703597',
    '72057595152716733',
    '72057595152716784',
]

if __name__ == '__main__':
    conn = MongoClient(
        'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
        readPreference="primary")
    my_set = conn['news']['documents']  # 连接mydb数据库，没有则自动创建

    # hash_value = 1
    index = 0
    # for each in list1:
    for each in my_set.find({"$and": [{"locale": "pt_BR"}, {"input_type": "crawl"}]}, no_cursor_timeout=True):
        index += 1
        print index
        source_hash = int(hashlib.md5(str(each['inlinks'][0])).hexdigest(), 16)
        user_index = source_hash % len(faker_user_list)
        my_set.update({"doc_id": str(each['doc_id'])}, {'$set': {"user_id": str(faker_user_list[user_index])}})
    print 'done'