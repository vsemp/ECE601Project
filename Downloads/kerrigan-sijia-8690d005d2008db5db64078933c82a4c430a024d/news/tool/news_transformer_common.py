# coding: utf-8
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment
import re
import math
import sys
import json
import os
import shutil


skipStuffFromDomains__links = [
    'doubleclick.net', 'fastclick.net', 'adbrite.com', 'adbureau.net',
    'admob.com', 'bannersxchange.com', 'buysellads.com', 'impact-ad.jp',
    'atdmt.com', 'advertising.com', 'itmedia.jp', 'microad.jp',
    'serving-sys.com', 'adplan-ds.com',
]

skipStuffFromDomain__images = [
    'googlesyndication.com', 'fastclick.net', '.2mdn.net', 'de17a.com',
    'content.aimatch.com', 'bannersxchange.com',
    'buysellads.com', 'impact-ad.jp', 'atdmt.com', 'advertising.com',
    'itmedia.jp', 'microad.jp', 'serving-sys.com', 'adplan-ds.com',
]

parsingOptions = {
    '_elements_ignore': '|button|input|select|textarea|optgroup|command|datalist|--|frame|frameset|noframes|--'
    '|style|link|script|noscript|--|canvas|applet|map|--|marquee|area|base|',
    '_elements_ignore_tag': '|form|fieldset|details|dir|--|center|font|span|',
    '_elements_self_closing': '|br|hr|--|img|--|col|--|source|--|embed|param|--|iframe|',
    '_elements_visible': '|article|section|--|ul|ol|li|dd|--|table|tr|td|--|div|--|p|--|h1|h2|h3|h4|h5|h6|--|span|',
    '_elements_too_much_content': '|b|i|em|strong|--|h1|h2|h3|h4|h5|--|td|',
    '_elements_container': '|body|--|article|section|--|div|--|tbody||td|--|li|--|dd|dt|',
    '_elements_link_density': '|div|--|table|ul|ol|--|section|aside|header|',
    '_elements_floating': '|div|--|table|',
    '_elements_above_target_ignore': '|br|--|ul|ol|dl|--|table|',
    '_elements_keep_attributes': {
        'a': ['href', 'title', 'name'],
        'img': ['src', 'width', 'height', 'alt', 'title'],
        'video': ['src', 'width', 'height', 'poster', 'audio', 'preload', 'autoplay', 'loop', 'controls'],
        'audio': ['src', 'preload', 'autoplay', 'loop', 'controls'],
        'source': ['src', 'type'],
        'object': ['data', 'type', 'width', 'height', 'classid', 'codebase', 'codetype'],
        'param': ['name', 'value'],
        'embed': ['src', 'type', 'width', 'height', 'flashvars', 'allowscriptaccess', 'allowfullscreen', 'bgcolor'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'scrolling'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan'],
    }
}


def getContent__findInPage(soup, title):
    _stuff = getContent__exploreNodeAndGetStuff(soup.body)
    _processedCandidates = getContent__processCandidates(_stuff['_candidates'])
    _firstCandidate = _processedCandidates[0]
    _content = getContent__buildHTMLForNode(_firstCandidate['__node'], title)
    _content_text = re.sub('\s', '', _content.get_text())
    if len(_content_text) < 65 * 3:
        return None
    else:
        return _content


def nodeType(node):
    if isinstance(node, Tag):
        return 1
    elif isinstance(node, Comment):
        return 8
    elif isinstance(node, NavigableString):
        return 3
    else:
        return 0


def measureText__getTextLength(_text):
    """count English and Chinese charactors"""
    _text = re.sub('[\s\n\r]', '', _text)
    return len(_text)


def measureText__getWordCount(_text):
    """count English and Chinese words"""
    _text = re.sub('[.,\?!:;\(\)\[\]\'\"\-]', '', _text)
    _words_match_en = re.findall('[a-zA-Z]{3,}', _text)
    _count = len(_words_match_en)
    _words_match_chs = re.findall(
        u'[\u3000\u30FB\uFF65\u300C\u300D\u300E\u300F\u3014\u3015\u3008\u3009'
        '\u300A\u300B\u3010\u3011\u3016\u3017\u3018\u3019\u301A\u301B\u301D'
        '\u301E\u301F\u30A0\u3002\uff0c\u3001\u301C\u2026\u2025\u4e00-\u9fa5]', _text)
    _count += len(_words_match_chs)
    return _count


def img_need_skip(imgsrc):
    for i in skipStuffFromDomain__images:
        if i in imgsrc:
            return True
    return False


def href_need_skip(href):
    for i in skipStuffFromDomains__links:
        if i in href:
            return True
    return False


def contains(_candidates1, _candidates2):
    """if _candidates1 is parent of _candidates2"""
    _index1 = str(_candidates1['__index'])
    _index2 = str(_candidates2['__index'])
    return _index2.startswith(_index1)


def getContent__processCandidates(_candidates):
    # sort _candidates -- the smaller index is, the closer to position 0
    _candidates.sort(key=lambda x: x['__index'])
    # _main is the outer of all contents
    _main = _candidates[0]
    for i in range(len(_candidates)):
        _count__pieces = 0
        for k in range(i + 1, len(_candidates)):
            if _candidates[k]['_count__candidates'] > 0:
                # look for deepest candidates
                continue
            if not contains(_candidates[i], _candidates[k]):
                # count within children candidates
                continue
            _count__pieces += 1
        # set pieces
        _candidates[i]['_count__pieces'] = _count__pieces
        # candidate details
        _candidates[i]['__candidate_details'] = getContent__computeDetailsForCandidate(_candidates[i], _main)
        # pieces ratio
        _candidates[i]['__candidate_details']['_ratio__count__pieces_to_total_pieces'] = float(_count__pieces) / (_candidates[0]['_count__pieces'] + 1)
        # points
        _candidates[i]['__points_history'] = getContent__computePointsForCandidate(_candidates[i], _main)
        _candidates[i]['__points'] = _candidates[i]['__points_history'][0]
    # sort _candidates -- the bigger points is, the closer to position 0
    _candidates.sort(key=lambda x: x['__points'], reverse=True)
    # for i in _candidates:
    #    print '=============================='
    #    print i
    return _candidates


def getContent__computeDetailsForCandidate(_e, _main):
    _r = {}
    # paragraphs
    # ==========
    _r['_count__lines_of_65_characters'] = (_e['_length__plain_text'] / 65.0)
    _r['_count__paragraphs_of_3_lines'] = (_r['_count__lines_of_65_characters'] / 3.0)
    _r['_count__paragraphs_of_5_lines'] = (_r['_count__lines_of_65_characters'] / 5.0)

    _r['_count__paragraphs_of_50_words'] = (_e['_count__plain_words'] / 50.0)
    _r['_count__paragraphs_of_80_words'] = (_e['_count__plain_words'] / 80.0)

    # total text
    # ==========
    _r['_ratio__length__plain_text_to_total_plain_text'] = float(_e['_length__plain_text']) / _main['_length__plain_text']
    _r['_ratio__count__plain_words_to_total_plain_words'] = float(_e['_count__plain_words']) / _main['_count__plain_words']

    # links
    # =====
    _r['_ratio__length__links_text_to_plain_text'] = float(_e['_length__links_text']) / _e['_length__plain_text']
    _r['_ratio__count__links_words_to_plain_words'] = float(_e['_count__links_words']) / _e['_count__plain_words']

    _r['_ratio__length__links_text_to_all_text'] = float(_e['_length__links_text']) / _e['_length__all_text']
    _r['_ratio__count__links_words_to_all_words'] = float(_e['_count__links_words']) / _e['_count__all_words']

    _r['_ratio__length__links_text_to_total_links_text'] = float(_e['_length__links_text']) / (_main['_length__links_text'] + 1)
    _r['_ratio__count__links_words_to_total_links_words'] = float(_e['_count__links_words']) / (_main['_count__links_words'] + 1)

    _r['_ratio__count__links_to_total_links'] = float(_e['_count__links']) / (_main['_count__links'] + 1)
    _r['_ratio__count__links_to_plain_words'] = float(_e['_count__links'] * 2) / _e['_count__plain_words']

    # text above
    # ==========
    _divide__candidates = float(max(2, math.ceil(_e['_count__above_candidates'] * 0.5)))

    _above_text = (_e['_length__above_plain_text'] + (_e['_length__above_plain_text'] / _divide__candidates)) / 2

    _above_words = (_e['_count__above_plain_words'] + (_e['_count__above_plain_words'] / _divide__candidates)) / 2

    _r['_ratio__length__above_plain_text_to_total_plain_text'] = (_above_text / _main['_length__plain_text'])
    _r['_ratio__count__above_plain_words_to_total_plain_words'] = (_above_words / _main['_count__plain_words'])

    # candidates
    # ==========
    _r['_ratio__count__candidates_to_total_candidates'] = float(_e['_count__candidates']) / (_main['_count__candidates'] + 1)
    _r['_ratio__count__containers_to_total_containers'] = float(_e['_count__containers']) / (_main['_count__containers'] + 1)

    return _r


def getContent__computePointsForCandidate(_e, _main):
    _details = _e['__candidate_details']
    _points_history = []
    _really_big = (_main['_length__plain_text'] / 65.0) > 250

    basic = (
        _details['_count__paragraphs_of_3_lines'] +
        (_details['_count__paragraphs_of_5_lines'] * 1.5) +
        (_details['_count__paragraphs_of_50_words']) +
        (_details['_count__paragraphs_of_80_words'] * 1.5) +
        (_e['_count__images_large'] * 3) -
        ((_e['_count__images_skip'] + _e['_count__images_small']) * 0.5)
    ) * 1000
    _points_history.insert(0, basic)
    if _points_history[0] < 0:
        return [0]
    _divide__pieces = max(5, math.ceil(_e['_count__pieces'] * 0.25))
    _divide__candidates = max(5, math.ceil(_e['_count__candidates'] * 0.25))
    _divide__containers = max(10, math.ceil(_e['_count__containers'] * 0.25))
    new = (
        (_points_history[0] * 3) +
        (_points_history[0] / _divide__pieces) +
        (_points_history[0] / _divide__candidates) +
        (_points_history[0] / _divide__containers)
    ) / 6
    _points_history.insert(0, new)

    # total text
    getContent__computePointsForCandidate__do(0.1, 2, _details['_ratio__length__plain_text_to_total_plain_text'], _points_history)
    getContent__computePointsForCandidate__do(0.1, 2, _details['_ratio__count__plain_words_to_total_plain_words'], _points_history)
    # text above
    getContent__computePointsForCandidate__do(0.1, 5, (1 - _details['_ratio__length__above_plain_text_to_total_plain_text']), _points_history)
    getContent__computePointsForCandidate__do(0.1, 5, (1 - _details['_ratio__count__above_plain_words_to_total_plain_words']), _points_history)
    # links outer
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__length__links_text_to_total_links_text']), _points_history)
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__count__links_words_to_total_links_words']), _points_history)
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__count__links_to_total_links']), _points_history)
    # links inner
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__length__links_text_to_plain_text']), _points_history)
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__count__links_words_to_plain_words']), _points_history)
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__length__links_text_to_all_text']), _points_history)
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__count__links_words_to_all_words']), _points_history)
    getContent__computePointsForCandidate__do(0.75, 1, (1 - _details['_ratio__count__links_to_plain_words']), _points_history)
    # candidates, containers, pieces
    getContent__computePointsForCandidate__do(0.1, 2, (1 - _details['_ratio__count__candidates_to_total_candidates']), _points_history)
    getContent__computePointsForCandidate__do(0.1, 2, (1 - _details['_ratio__count__containers_to_total_containers']), _points_history)
    getContent__computePointsForCandidate__do(0.1, 2, (1 - _details['_ratio__count__pieces_to_total_pieces']), _points_history)

    return _points_history


def getContent__computePointsForCandidate__do(_ratio_remaining, _power, _ratio, _points_history):
    """_ratio_remaining: remaining effect of last _points"""
    _points_remaining = (_points_history[0] * _ratio_remaining)
    _points_to_compute = (_points_history[0] - _points_remaining)
    if _ratio < 0:
        _points_return = _points_remaining
    else:
        _points_return = _points_remaining + (_points_to_compute * math.pow(_ratio, _power))
    _points_history.insert(0, _points_return)


def getContent__exploreNodeAndGetStuff(_nodeToExplore, _justExploring=False):
    global _global__element_index
    global _global__inside_link
    global _global__inside_link__element_index
    global _global__length__above_plain_text
    global _global__count__above_plain_words
    global _global__length__above_links_text
    global _global__count__above_links_words
    global _global__count__above_candidates
    global _global__count__above_containers
    global _global__above__plain_text
    global _global__above__links_text
    global _return__containers
    global _return__candidates
    global _return__links

    _global__element_index = 0
    _global__inside_link = False
    _global__inside_link__element_index = 0
    _global__length__above_plain_text = 0
    _global__count__above_plain_words = 0
    _global__length__above_links_text = 0
    _global__count__above_links_words = 0
    _global__count__above_candidates = 0
    _global__count__above_containers = 0
    _global__above__plain_text = ''
    _global__above__links_text = ''
    _return__containers = []
    _return__candidates = []
    _return__links = []

    def _recursive(_node, __index=0):
        # global _global__element_index
        if not __index:
            __index = 0.1
        global _global__inside_link
        global _global__inside_link__element_index
        global _global__length__above_plain_text
        global _global__count__above_plain_words
        global _global__length__above_links_text
        global _global__count__above_links_words
        global _global__count__above_candidates
        global _global__count__above_containers
        global _global__above__plain_text
        global _global__above__links_text
        global _return__containers
        global _return__candidates
        global _return__links
        #_global__element_index += 1
        if nodeType(_node) == 3:
            _tag_name = 'text'
        elif nodeType(_node) == 1:
            _tag_name = _node.name
        else:
            _tag_name = None
        if _tag_name is None:
            return
        if ('|' + _tag_name + '|') in parsingOptions['_elements_ignore']:
            return
        if ('|' + _tag_name + '|') in parsingOptions['_elements_self_closing'] and _tag_name != 'img':
            return

        _result = {
            '__index': __index,
            '__node': _node,
            '_is__container': ('|' + _tag_name + '|') in parsingOptions['_elements_container'],
            '_is__candidate': False,
            '_is__text': False,
            '_is__link': False,
            '_is__link_skip': False,
            '_is__image_small': False,
            '_is__image_medium': False,
            '_is__image_large': False,
            '_is__image_skip': False,
            '_length__above_plain_text': _global__length__above_plain_text,
            '_count__above_plain_words': _global__count__above_plain_words,
            '_length__above_links_text': _global__length__above_links_text,
            '_count__above_links_words': _global__count__above_links_words,
            '_length__above_all_text': (_global__length__above_plain_text + _global__length__above_links_text),
            '_count__above_all_words': (_global__count__above_plain_words + _global__count__above_links_words),
            '_count__above_candidates': _global__count__above_candidates,
            '_count__above_containers': _global__count__above_containers,
            '_length__plain_text': 0,
            '_count__plain_words': 0,
            '_length__links_text': 0,
            '_count__links_words': 0,
            '_length__all_text': 0,
            '_count__all_words': 0,
            '_count__containers': 0,
            '_count__candidates': 0,
            '_count__links': 0,
            '_count__links_skip': 0,
            '_count__images_small': 0,
            '_count__images_medium': 0,
            '_count__images_large': 0,
            '_count__images_skip': 0
        }
        if _tag_name == 'text':
            _result['_is__text'] = True
            _nodeText = _node.strip()
            if not _nodeText:
                return
            _result['_length__plain_text'] = measureText__getTextLength(_nodeText)
            _result['_count__plain_words'] = measureText__getWordCount(_nodeText)
            if _global__inside_link:
                _global__length__above_links_text += _result['_length__plain_text']
                _global__count__above_links_words += _result['_count__plain_words']
            else:
                _global__length__above_plain_text += _result['_length__plain_text']
                _global__count__above_plain_words += _result['_count__plain_words']
            return _result
        elif _tag_name == 'a':
            if _node.has_attr('href') and _node['href']:
                href = _node['href']
                _result['_is__link'] = True
                if href_need_skip(href):
                    _result['_is__link_skip'] = True
            if not _global__inside_link:
                _global__inside_link = True
                _global__inside_link__element_index = _result['__index']
            _return__links.append(_result)
        elif _tag_name == 'img':
            if _node.has_attr('src') and img_need_skip(_node['src']):
                _result['_is__image_skip'] = True

        # child nodes
        _child__index = 1
        for _child in _node.children:
            _child_result = _recursive(_child, float(str(__index) + str(_child__index)))
            _child__index += 1
            if not _child_result:
                continue
            # add to result
            _result['_count__links'] += _child_result['_count__links'] + int(bool(_child_result['_is__link']))
            _result['_count__links_skip'] += _child_result['_count__links_skip'] + int(bool(_child_result['_is__link_skip']))

            _result['_count__images_skip'] += _child_result['_count__images_skip'] + int(bool(_child_result['_count__images_skip']))

            _result['_count__containers'] += _child_result['_count__containers'] + int(bool(_child_result['_is__container']))
            _result['_count__candidates'] += _child_result['_count__candidates'] + int(bool(_child_result['_is__candidate']))
            _result['_length__all_text'] += _child_result['_length__plain_text'] + _child_result['_length__links_text']
            _result['_count__all_words'] += _child_result['_count__plain_words'] + _child_result['_count__links_words']
            # plain text / link text
            if _child_result['_is__link']:
                _result['_length__links_text'] += _child_result['_length__plain_text'] + _child_result['_length__links_text']
                _result['_count__links_words'] += _child_result['_count__plain_words'] + _child_result['_count__links_words']
            else:
                _result['_length__plain_text'] += _child_result['_length__plain_text']
                _result['_count__plain_words'] += _child_result['_count__plain_words']
                _result['_length__links_text'] += _child_result['_length__links_text']
                _result['_count__links_words'] += _child_result['_count__links_words']

        # after child nodes
        # mark as not in link anymore
        if _result['_is__link'] and _global__inside_link__element_index == _result['__index']:
            _global__inside_link = False
            _global__inside_link__element_index = 0
        # add to containers
        if _result['_is__container'] or ((_result['__index'] == 0.1) and _justExploring):
            _return__containers.append(_result)
            _global__count__above_containers += 1
            # add to candidates, assure language is cjk firstly
            # if one of children is candidate, parent is candidate too
            if not _justExploring and _result['_length__plain_text'] >= 10 and _result['_count__plain_words'] >= 2:
                _result['_is__candidate'] = True
                _return__candidates.append(_result)
                _global__count__above_candidates += 1
        return _result

    # actually do it
    _recursive(_nodeToExplore)
    # just exploring -- return first thing
    if _justExploring:
        if _return__containers:
            return _return__containers.pop()
        else:
            return None
    # return containers list
    return {
        '_containers': _return__containers,
        '_candidates': _return__candidates,
        '_links': _return__links,
    }


def getContent__buildHTMLForNode(_nodeToBuildHTMLFor, title):

    global _global__exploreNodeToBuildHTMLFor
    _global__exploreNodeToBuildHTMLFor = getContent__exploreNodeAndGetStuff(_nodeToBuildHTMLFor, True)

    def _recursive(_node):

        if nodeType(_node) == 3:
            _tag_name = 'text'
            if title.decode('utf8') == _node.strip():
                _node.replace_with('')
            elif u'来源：' in _node.strip() and len(_node.strip()) < 65:
                _node.replace_with('')
            return
        elif nodeType(_node) == 8:
            _node.replace_with('')
            return
        elif nodeType(_node) == 1:
            _tag_name = _node.name
        else:
            _tag_name = None
        if _tag_name is None:
            _node.decompose()
            return
        if ('|' + _tag_name + '|') in parsingOptions['_elements_ignore']:
            _node.decompose()
            return
        if _tag_name in ['embed', 'iframe']:
            _src = _node.get('src')
            if not _src:
                _node.decompose()
                return
        # skip link
        if _tag_name in ['a', 'li']:
            _explored = getContent__exploreNodeAndGetStuff(_node, True)
            if _explored:
                if _explored['_is__link_skip']:
                    _node.decompose()
                    return
                if _explored['_count__images_skip'] > 0 and _explored['_length__plain_text'] < 65:
                    _node.decompose()
                    return
                if _explored['_length__plain_text'] == 0:
                    _node.decompose()
                    return
        # link density:
        if ('|' + _tag_name + '|') in parsingOptions['_elements_link_density']:
            _explored = getContent__exploreNodeAndGetStuff(_node, True)
            if _explored:
                if _explored['_length__plain_text'] < 65 * 3 and _explored['_count__links'] > 1 and float(_explored['_length__plain_text']) / _global__exploreNodeToBuildHTMLFor['_length__plain_text'] < 0.5:
                    _node.decompose()
                    return
        # img
        if _tag_name == 'img':
            if not _node.has_attr('src') and _node.has_attr('original'):
                _node['src'] = _node['original']
            _node['style'] = 'display:block;margin:0;max-width:100%;text-align:center'

        # child nodes
        if ('|' + _tag_name + '|') not in parsingOptions['_elements_self_closing']:
            for _child in _node.children:
                _recursive(_child)

    _recursive(_nodeToBuildHTMLFor)
    return _nodeToBuildHTMLFor


def getContent__find__getIsolatedTitleInHTML(soup):
    _heading_pregs = ['h1', 'h2', 'h3', 'h4, h5', 'h6', 'title']
    _doc_title_pregs = ['( [-][-] |( [-] )|( [>][>] )|( [<][<] )|( [|] )|( [\/] ))', '(([:] ))']
    _heading_text = ''
    for i in _heading_pregs:
        _match = soup.find(i)
        if not _match:
            continue
        _heading_type = i
        _heading_text = re.sub('\s+', ' ', _match.get_text())
        break
    _doc_title_parts = []
    for i in _doc_title_pregs:
        _doc_title_parts = _heading_text.split(i)
        if len(_doc_title_parts) > 1:
            break
    _doc_title_parts.sort(key=lambda x: len(x), reverse=True)
    _title = _doc_title_parts[0].encode('utf-8')
    return _title


style = '<style type="text/css">body {margin:0;padding:0;background:#F3F2EE;} div{position:relative;border:0;outline:0;text-align:center;font-size:16px;} div h1{position:static;+position:absolute;font-size:36px;margin-top:20px;margin-bottom:20px;text-align:left} div p{position:static;+position:absolute;font-size:20px;margin-bottom:20px;text-align:left} div img{max-width:100%;min-width:200px;position:static;+position:relative;vertical-align:middle;width:100%;}</style>'

html_base = '<html><head><meta <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head><body>%(style)s<div id="box", style="width:80%%;margin-left:50%%;transform:translateX(-50%%)"><div id="box_inner"><div id="text"><div id="pages"><div class="page" id="page1"><div id="articleHeader"><h1>%(title)s</h1></div><div style="color:#4A4A4A;text-align:center;"><span id="pubtime_cootek">发布时间：%(pubtime)s</span>&nbsp;&nbsp;<span id="source_cootek">来源：%(subtitle)s</span>&nbsp;&nbsp;</div></div><div id="page-info">%(logo)s%(content)s</div><ol id="footnotedLinks"></ol></div></div></div></body></html>'


def transform(filename):
    data = json.loads(open(filename).read())
    body = data['html']
    subtitle = data['subtitle'].encode('utf8')
    pubtime = data['time'].encode('utf8')
    logo_url = data['url']['logo_url'].encode('utf8')
    soup = BeautifulSoup(body)
    title = getContent__find__getIsolatedTitleInHTML(soup)
    content = getContent__findInPage(soup, title)
    if not content:
        return
    if content.find('img'):
        logo = ''
    else:
        logo = '<img src="%s"></img>' % logo_url
    trans = html_base % {'title': title, 'content': content, 'style': style, 'pubtime': pubtime, 'subtitle': subtitle, 'logo': logo}
    return trans


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s filename/filedir' % sys.argv[0]
        sys.exit(1)
    outdir = 'trans'
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.mkdir(outdir)
    if os.path.isfile(sys.argv[1]):
        absfn = sys.argv[1]
        fn = os.path.split(absfn)[-1]
        trans = transform(absfn)
        absfn_dst = os.path.join(outdir, fn)
        if not absfn_dst.endswith('.html'):
            absfn_dst += '.html'
        open(absfn_dst, 'w').write(trans)
    else:
        for fn in os.listdir(sys.argv[1]):
            absfn = os.path.join(sys.argv[1], fn)
            trans = transform(absfn)
            absfn_dst = os.path.join(outdir, fn)
            if not absfn_dst.endswith('.html'):
                absfn_dst += '.html'
            open(absfn_dst, 'w').write(trans)
