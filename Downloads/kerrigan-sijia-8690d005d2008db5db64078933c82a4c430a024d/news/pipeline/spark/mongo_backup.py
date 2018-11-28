# coding: utf-8

import datetime
import time
from pyspark import SparkContext

if 'spark' not in locals() and 'spark' not in globals():
    sc = SparkContext()

import time
import pymongo
from pymongo import MongoClient

conn = MongoClient('192.168.173.130', 27017)
db = conn.news
doc_set = db.documents
data_string = time.strftime("%Y%m%d", time.localtime())
import json
import copy


def save_to_hdfs(list, page):
    df = sc.read.json(sc.parallelize(list))
    print(df.count())
    path = "/user/xinyu.du/gct/data/documents/%s/page_%s" % (data_string, page)
    df.write.parquet(path, 'overwrite')
    print(path)


total_list = []
index = 0
page = 0
for i in doc_set.find({}):
    total_list.append(json.dumps(i))
    index += 1
    if index >= 20000:
        page += 1
        save_to_hdfs(copy.deepcopy(total_list), page)
        print("save_to_hdfs")
        total_list = []
        index = 0

page += 1
save_to_hdfs(copy.deepcopy(total_list), page)
print("save_to_hdfs")
total_list = []
index = 0
