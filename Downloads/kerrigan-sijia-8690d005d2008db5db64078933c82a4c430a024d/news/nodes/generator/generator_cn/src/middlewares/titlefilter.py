# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
import re


class TitleFilter(FilterMiddleware):

    brackets = [u'(', u')', u'（', u'）']

    def process(self, item):
        account = item['raw']['account']
        title = item['raw']['title']
        if len(title) <= 4:
            self.filter_standard_log(account)
            return False
        cn_title = re.findall(ur'[\u4e00-\u9fa5]+', title)
        if sum([len(x) for x in cn_title]) < len(title) / 5:
            self.filter_standard_log(account)
            return False
        for bracket in self.brackets:
            title = title.replace(bracket, u')' if self.brackets.index(bracket) & 1 else u'(')
        if title.find(u'(') == 0 and title.find(u')') == len(title) - 1:
            self.filter_standard_log(account)
            return False
        return True
