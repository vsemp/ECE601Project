#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.insert(0, '/home/tengchuan.wang/bwang/venv/lib/python2.7/site-packages')
from sys import argv
import re
import json
import jieba
import sklearn
from sklearn.datasets import load_svmlight_file
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from scipy import sparse
from scipy.sparse import csr_matrix
from pkg_resources import resource_filename


class Adnews(object):

    def __init__(self, *a, **kw):
        resource_filename('generator.resources', 'ad_news_lr.model_01.npy')
        resource_filename('generator.resources', 'ad_news_lr.model_02.npy')
        resource_filename('generator.resources', 'ad_news_lr.model_03.npy')
        self.clf = joblib.load(resource_filename('generator.resources', 'ad_news_lr.model'))
        self.dict_map = self.load_dict(resource_filename('generator.resources', 'news_words.dict'))

    def load_dict(self, dict_file):
        dictmap = {}
        count = 1
        for line in open(dict_file):
            line = line.strip()
            if line not in dictmap:
                dictmap[unicode(line)] = count
                count += 1
        return dictmap

    def get_feature_vector(self, content):
        feature_map = {}
        for w in jieba.cut(content):
            w = w.strip()
            windex = self.dict_map.get(w, -1)
            if windex == -1:
                continue
            windex = windex - 1
            feature_map[windex] = feature_map.get(windex, 0) + 1
        indices = []
        data = []
        indptr = [0, len(feature_map)]
        for index, value in feature_map.iteritems():
            indices.append(index)
            data.append(value)
        x_csr = csr_matrix((data, indices, indptr), dtype=int, shape=(1, len(self.dict_map)))
        return x_csr

    def predict_content(self, content):
        x_csr = self.get_feature_vector(content)
        ret = self.clf.predict(x_csr)
        cont_type = int(ret[0])
        return cont_type
