# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import jieba
import scipy
from sklearn.externals import joblib
import os


class RealTimeFilter(FilterMiddleware):
    def __init__(self, *a, **kw):
        super(RealTimeFilter, self).__init__(*a, **kw)
        self.path = self.get_resource_file_path('real_time')

        self.dictionary = joblib.load(os.path.join(self.path, 'dic.model'))
        self.tfidf_model = joblib.load(os.path.join(self.path, 'tfidf.model'))
        self.clf = joblib.load(os.path.join(self.path, 'clf1.model'))
        self.dictionary_size = len(list(self.dictionary.items()))

        self.dictionary2 = joblib.load(os.path.join(self.path, 'dic2.model'))
        self.tfidf_model2 = joblib.load(os.path.join(self.path, 'tfidf2.model'))
        self.clf2 = joblib.load(os.path.join(self.path, 'clf2.model'))
        self.dictionary_size2 = len(list(self.dictionary2.items()))

        self.stop_word = joblib.load(os.path.join(self.path, 'stopword.model'))
        self.sports_tags = [u'体育', u'乒羽', u'排球', u'网球', u'游泳', u'高尔夫',
                            u'田径', u'英超', u'西甲', u'中超', u'欧冠', u'意甲',
                            u'德甲', u'NBA', u'CBA']

    def check(self, title, content):
        if (self.clf.predict(self.doc2tfidf(content)) == '1') or (self.clf2.predict(self.doc2tfidf2(title)) == '1'):
            return 0
        return 1

    def process(self, item):
        account = item['account']
        if account.startswith('9') or u'触宝_美图' in item['raw']['raw_tags'] or u'触宝_图集' in item['raw']['raw_tags']:
            return True
        tags = [x[0] for x in item['tags']]
        if u'体育' in item['raw'].get('raw_tags', []) or len(set(tags) & set(self.sports_tags)) > 0:
            if self.check(item['title'].encode('utf-8'), item['content'].encode('utf-8')) == 1:
                return True
            else:
                self.filter_standard_log(account)
                return False
        return True

    # -------------------------------------------content---------------------------------------------------------#

    def doc2list(self, doc):
        return_list = []
        doc = list(jieba.cut(doc))
        for item in doc:
            if (not (item in self.stop_word or item.encode('utf8') in self.stop_word or item.isdigit())):
                return_list.append(item)
        return return_list

    def to_csr_matrix(self, matrix):
        data = []
        rows = []
        cols = []
        line_count = 0
        for line in matrix:
            for elem in line:
                rows.append(line_count)
                cols.append(elem[0])
                data.append(elem[1])
            line_count += 1
        sparse_matrix = scipy.sparse.csr_matrix((data, (rows, cols)), shape=(line_count, self.dictionary_size))
        return sparse_matrix

    def doc2tfidf(self, doc):
        return self.to_csr_matrix(self.tfidf_model[[self.dictionary.doc2bow(self.doc2list(doc))]])

    # -------------------------------------------title---------------------------------------------------------#

    def doc2list2(self, doc):
        return_list = []
        doc = list(jieba.cut(doc))
        for item in doc:
            return_list.append(item)
        return return_list

    def to_csr_matrix2(self, matrix):
        data = []
        rows = []
        cols = []
        line_count = 0
        for line in matrix:
            for elem in line:
                rows.append(line_count)
                cols.append(elem[0])
                data.append(elem[1])
            line_count += 1
        sparse_matrix = scipy.sparse.csr_matrix((data, (rows, cols)), shape=(line_count, self.dictionary_size2))
        return sparse_matrix

    def doc2tfidf2(self, doc):
        return self.to_csr_matrix2(self.tfidf_model2[[self.dictionary2.doc2bow(self.doc2list2(doc))]])
