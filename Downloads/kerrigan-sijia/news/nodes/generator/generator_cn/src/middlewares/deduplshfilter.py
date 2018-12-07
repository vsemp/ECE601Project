# -*- coding: utf-8 -*-
from src.middlewares.base import FilterMiddleware
from src.util.deduplsh_util import *


class DedupLshFilter(FilterMiddleware):
    def __init__(self, *a, **kw):
        super(DedupLshFilter, self).__init__(*a, **kw)
        self.lsh_Environment = LSHEnvironment()

    def process(self, item):
        message = item
        if message['account'].startswith('9'):
            return True
        else:
            if not message['content']:
                return True
            else:
                article = Article(message)
                article.article_init(self.lsh_Environment)
                query_result = self.query(article)
                if query_result:
                    log_content = article.account + ',' + ','.join(query_result)
                    self.filter_standard_log(log_content)
                    return False
                else:
                    return True

    def query(self, article):
        with self.redis_cli.pipeline() as pipe:
            for i, band_signature in enumerate(article.band_signatures):
                lsh_key = LSHEnvironment.get_key(i, band_signature)
                pipe.hget(self.lsh_look_table, lsh_key)
            pipe_result = pipe.execute()
        pipe_result = {ele for ele in pipe_result if ele is not None}
        return pipe_result

