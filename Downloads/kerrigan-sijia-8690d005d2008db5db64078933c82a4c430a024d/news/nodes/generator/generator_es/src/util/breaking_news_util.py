# -*- coding: utf-8 -*-
from gensim import models, similarities
import time


class BreakingNewsDetector:

    def __init__(self, dictionary, corpus):
        self.dictionary = dictionary
        self.corpus = corpus
        self.model = models.TfidfModel(corpus, normalize=True)

    def judge_similarity(self, content):
        try:
            index = similarities.MatrixSimilarity(self.model[self.corpus])
            vec_bow = self.dictionary.doc2bow(content)
            similarity = index[self.model[vec_bow]]
        except IndexError:
            return False
        return max(similarity) > 0.75


def add_duration(data, location_list=None, duration=None, mode=0):
    if location_list is None:
        location_list = [u'全国']
    if duration is None:
        duration = 60 * 60 * 2
    data.setdefault('breaking_news', {})
    for location in location_list:
        if mode:
            time_content = time.mktime(time.strptime(data['time'], '%Y-%m-%d %H:%M:%S'))
            data['breaking_news'][location] = int(time_content) + duration
        else:
            data['breaking_news'][location] = int(time.time()) + duration


def detect_keywords(data):
    keys = ['title']
    keywords = [
        (u'触宝', [u'全国'], 60 * 60 * 48)
    ]
    for key in keys:
        if not data[key]:
            continue
        for keyword_info in keywords:
            if keyword_info[0] in data[key]:
                return keyword_info[1], keyword_info[2]
    return None, None
