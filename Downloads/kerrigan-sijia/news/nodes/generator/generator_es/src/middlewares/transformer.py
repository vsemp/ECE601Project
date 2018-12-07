# -*- coding: utf-8 -*-
from src.middlewares.base import MapMiddleware
from pkg_resources import resource_filename
from src.util.image_util import check_minimal_size_image


class Transformer(MapMiddleware):

    def process(self, item):
        html = self.transform(item)
        if html:
            item['html'] = html['html_raw'] if 'html_raw' in html else None
            item['html_data'] = html['html_data'] if 'html_data' in html else None
        else:
            item['html'] = None
            item['html_data'] = None
        if not item['html']:
            self.logger.info('Html is None %s' % item['account'])
        return item

    def transform(self, item):
        if item['need_upload']:
            page_type = item['page_type']
            #hard code page_type to using webview in Android
            #can remove if old version goes down
            if page_type == 'tencent_open' and item['account'].startswith('9'):
                page_type = 'href_article'
            pbFactory = PBFactory(self.settings)
            pb = pbFactory.getPB(page_type)
            html = pb.build(item)
            return html
        else:
            return None

class PBFactory(object):

    def __init__(self, settings):
        self.settings = settings


    def getPB(self, hint):
        if hint == 'album':
            return PB_Album(self.settings, hint)
        elif hint == 'video':
            return PB_Video(self.settings, hint)
        elif hint == 'fall_video':
            return PB_Video(self.settings, hint)
        elif hint == 'tencent_open':
            return PB_TencentNews(self.settings, hint)
        else:
            return PB_Article(self.settings, hint)


class PB_Video(object):

    def __init__(self, settings, hint):
        self.settings = settings
        self.pb_type = hint
        self.default_share_icon = self.settings['DEFAULT_SHARE_ICON']
        self.pattern_html = open(
                resource_filename('resources', 'video_share_article.html')).read()

    def select_video_thumb(self, item):
        thumb = ''
        if item['large_img_url']:
            thumb = item['large_img_url']
            return thumb
        if item['small_img_url']:
            thumb = item['small_img_url']
            return thumb
        if thumb:
            return ''.join(thumb.split('@')[0:-1]) + '@400w_400h'
        return self.default_share_icon.split('@')[0] + '@400w_400h'

    def build(self, item):
        html = {}
        share_icon = item['share_icon'].encode('utf8')
        target_url = item['target_url'].encode('utf8')
        video_type = 'video/' +  target_url.rsplit('.')[-1]
        published = item['time'].encode('utf8')
        if published.endswith(' 00:00:00'):
            published = published[:-9]
        else:
            published = published[:-3]
        html['html_raw'] = self.pattern_html % {
            'title': item['title'].encode('utf8'),
            'subtitle': item['subtitle'].encode('utf8'),
            'source_url': item['source_url'].encode('utf8'),
            'share_icon': share_icon,
            'thumbnail': self.select_video_thumb(item).encode('utf8'),
            'video_type': video_type,
            'target_url': target_url,
            }

        html['html_data'] = {
            'type': self.pb_type,
            'title': item['title'].encode('utf8'),
            'subtitle': item['subtitle'].encode('utf8'),
            'published': published,
            'source_url': item['source_url'].encode('utf8'),
            'share_icon': share_icon,
            'thumbnail': self.select_video_thumb(item).encode('utf8'),
            'video_type': video_type,
            'target_url': target_url,
            }
        return html

class PB_TencentNews(object):

    def __init__(self, settings, hint):
        self.settings = settings
        self.pb_type = hint
        self.pattern_html = open(
            resource_filename('resources', 'tencent_open_article.html')).read()
        self.iframe = '<iframe src="%(iframe_url)s"></iframe>'

    def build(self, item):
        iframe = self.iframe % {'iframe_url': item['source_url']}
        share_icon = item['share_icon'].encode('utf8')
        html = {}
        html['html_raw'] = self.pattern_html % {
            'title': item['title'].encode('utf8'),
            'iframe': iframe.encode('utf8'),
            'share_icon': share_icon,
            }
        html['html_data'] = {
            'type': self.pb_type,
            'title': item['title'].encode('utf8'),
            'subtitle': '',
            'published': '',
            'content': '',
            'source_url': '',
            'share_icon': share_icon,
            }
        return html

class PB_Article(object):

    def __init__(self, settings, hint):
        self.settings = settings
        self.pb_type = hint
        self.pattern_html = open(
            resource_filename('resources', 'base_article_v1.html')).read()
        self.pattern_image = '<div class="large_img_container"><img alt="%(description)s" data-type="%(img_format)s" src="/news/img/blank_1x1.png" data-src="%(url)s" img_width="%(img_width)d" img_height="%(img_height)d"></img><p>%(description)s</p></div>'
        self.pattern_text = '<p>%s</p>'
        self.version = self.settings['VERSION']

    def build(self, item):
        result = []
        image_zoom = True
        if 'rich_content' in item['raw']:
            result.append(item['raw']['rich_content'])
            image_zoom = False
        else:
            content = item['raw']['content']
            for element in content:
                if 'image' in element:
                    image_package = element['image']
                    image_info = image_package['image_info']
                    if check_minimal_size_image(image_info):
                        continue
                    if image_info['qr_code']:
                        continue
                    result.append(self.pattern_image % {
                        'url': 'img/%s' % image_package['norm_name'],
                        'img_width': image_info['width'],
                        'img_height': image_info['height'],
                        'description': element['text'],
                        'img_format': image_info.get('format', 'unknown').lower(),
                    })
                else:
                    if 'rich_content' in element:
                        result.append(element['rich_content'])
                        image_zoom = False
                    else:
                        result.append(self.pattern_text % element['text'])
        title = item['title'].encode('utf8')
        subtitle = item['subtitle'].encode('utf8')
        published = item['time'].encode('utf8')
        if published.endswith(' 00:00:00'):
            published = published[:-9]
        else:
            published = published[:-3]
        source_url = item['source_url'].encode('utf8')
        share_icon = item['share_icon'].encode('utf8')
        html = {}
        html['html_raw'] = self.pattern_html % {
            'title': title,
            'subtitle': subtitle,
            'published': published,
            'content': '\n'.join(result).encode('utf8'),
            'image_zoom': 'no_zoom' if image_zoom == False else '',
            'source_url': source_url,
            'share_icon': share_icon,
        }
        html['html_data'] = {
            'type': self.pb_type,
            'title': item['title'].encode('utf8'),
            'subtitle': subtitle,
            'published': published,
            'content': '\n'.join(result).encode('utf8'),
            'image_zoom': 'no_zoom' if image_zoom == False else '',
            'source_url': source_url,
            'share_icon': share_icon,
            }
        return html

class PB_Album(object):

    def __init__(self, settings, hint):
        self.settings = settings
        self.pb_type = hint
        self.pattern_html = open(
            resource_filename('resources', 'base_album.html')).read()
        self.pattern_image = '<figure><figcaption>%(description)s</figcaption><img data-type="%(img_format)s" alt-src="%(url)s"img-width="%(img_width)d"img-height="%(img_height)d"/></figure>'
        self.version = self.settings['VERSION']
        self.html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }

    def html_escape(self, text):
        return "".join(self.html_escape_table.get(c, c) for c in text)

    def build(self, item):
        content = item['raw']['content']
        result = []
        imgindex = 0
        for element in content:
            if 'image' in element:
                image_package = element['image']
                image_info = image_package['image_info']
                if check_minimal_size_image(image_info):
                    continue
                if image_info['qr_code']:
                    continue
                text = self.html_escape(element['text'])
                result.append(self.pattern_image % {
                    'imgindex': imgindex,
                    'url': 'img/%s' % image_package['norm_name'],
                    'img_width': image_info['width'],
                    'img_height': image_info['height'],
                    'description': text,
                    'img_format': image_info.get('format', 'unknown').lower(),
                })
                imgindex += 1
        share_icon = item['share_icon'].encode('utf8')
        published = item['time'].encode('utf8')
        if published.endswith(' 00:00:00'):
            published = published[:-9]
        else:
            published = published[:-3]
        html = {}
        html['html_raw'] = self.pattern_html % {
            'title': item['title'].encode('utf8'),
            'content': '\n'.join(result).encode('utf8'),
            'share_icon': share_icon,
        }
        html['html_data'] = {
            'type': self.pb_type,
            'title': item['title'].encode('utf8'),
            'subtitle': '',
            'published': published,
            'content': '\n'.join(result).encode('utf8'),
            'source_url': '',
            'share_icon': share_icon,
            }
        return html
