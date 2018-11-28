# /usr/bin/env python
# -*- coding: utf-8 -*-
import shutil


INDENT = ' ' * 4


def translate_tag():
    tag_all = translate_classification()
    tag_all_str = get_tag_all_str(tag_all)
    line_accept = True
    file_middlewares_checker = open('../feeds/checker/middlewares.py.bck', 'w')
    for line in open('../feeds/checker/middlewares.py'):
        if 'Finished' in line:
            line_accept = True
        if line_accept:
            file_middlewares_checker.write(line)
        if 'Initialize tag_all' in line:
            line_accept = False
            file_middlewares_checker.write(tag_all_str)
    file_middlewares_checker.close()
    shutil.move('../feeds/checker/middlewares.py.bck', '../feeds/checker/middlewares.py')


def translate_classification():
    tag_all = []
    for line in open('../tags/res/tags_map'):
        tag_all.append(line.split(' ')[0].strip())
    return tag_all


def get_tag_all_str(tag_all):
    tag_str = ''
    tag_all.extend(['图集', '视频', '热门', '触宝_美图'])
    for tag in tag_all:
        tag_str += INDENT * 2
        tag_str += "u'%s'" % tag
        tag_str += ',\n'
    return '%stag_all = {\n%s%s}\n' % (INDENT * 1, tag_str, INDENT * 1)


if __name__ == '__main__':
    translate_tag()
