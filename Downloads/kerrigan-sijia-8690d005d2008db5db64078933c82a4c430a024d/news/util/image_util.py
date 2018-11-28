# -*- coding: utf-8 -*-
import ConfigParser
import qrtools
import os
import re
from cStringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


PATH_CURRENT = os.path.realpath('.')
PATH_TRUNK = PATH_CURRENT[:PATH_CURRENT.rfind('/news')]
FILE_CONFIG = '%s/news/conf/news.conf' % PATH_TRUNK
parser_config = ConfigParser.ConfigParser()
parser_config.read(FILE_CONFIG)
PATH_RESULT = parser_config.get('Paths', 'path_result')


MIN_SIZE = (50.0, 50.0)
SMALL_SIZE = (192.0, 144.0)
LARGE_SIZE = (584.0, 278.0)


def check_min_size(file_image):
    try:
        width, height = Image.open(os.path.join(PATH_RESULT, file_image)).size
    except IOError:
        return True
    datasource_type = file_image.split('/')[-1].split('-')[0][0]
    if datasource_type == '1':
        return width < MIN_SIZE[0] or height < MIN_SIZE[1]
    else:
        return width < MIN_SIZE[0] and height < MIN_SIZE[1]


def check_qr_code(file_image):
    qr = qrtools.QR()
    try:
        return qr.decode(os.path.join(PATH_RESULT, file_image))
    except IOError:
        return True


def compare_image(image_type, image_src, image_dst):
    if check_qr_code(image_dst):
        return image_src
    try:
        image_info_dst = Image.open(os.path.join(PATH_RESULT, image_dst))
    except IOError:
        return image_src
    if image_info_dst.format == 'GIF':
        return image_src
    width_dst, height_dst = image_info_dst.size
    image_size = SMALL_SIZE if image_type == 'small' else LARGE_SIZE
    if width_dst < image_size[0] * 0.95 or height_dst < image_size[1] * 0.75:
        return image_src
    ratio = float(image_size[0]) / image_size[1]
    ratio_dst = float(width_dst) / height_dst
    if not ratio <= ratio_dst <= ratio * 1.5:
        return image_src
    if not image_src:
        return image_dst
    width_src, height_src = Image.open(os.path.join(PATH_RESULT, image_src)).size
    ratio_src = float(width_src) / height_src
    if ratio_dst < ratio_src:
        return image_dst
    else:
        return image_src


def get_image_info(file_image):
    image_info = {
        'name': file_image,
        'norm_name': get_norm_name(file_image),
        'width': 0.0,
        'height': 0.0,
        'ratio': 0.0,
        'format': '',
        'qr_code': True,
    }
    try:
        image = Image.open(os.path.join(PATH_RESULT, file_image))
    except IOError:
        return image_info
    image_info['width'] = float(image.size[0])
    image_info['height'] = float(image.size[1])
    image_info['ratio'] = image_info['width'] / image_info['height']
    image_info['format'] = image.format
    qr = qrtools.QR()
    try:
        image_info['qr_code'] = qr.decode(os.path.join(PATH_RESULT, file_image))
    except IOError:
        image_info['qr_code'] = True
    return image_info


def get_image_info_with_io(file_image, imgbody):
    image_info = {
        'name': file_image,
        'norm_name': get_norm_name(file_image),
        'width': 0.0,
        'height': 0.0,
        'ratio': 0.0,
        'format': '',
        'qr_code': True,
    }
    try:
        image = Image.open(StringIO(imgbody))
    except IOError:
        return image_info
    image_info['width'] = float(image.size[0])
    image_info['height'] = float(image.size[1])
    image_info['size'] = len(imgbody)
    image_info['ratio'] = image_info['width'] / image_info['height']
    image_info['format'] = image.format
    qr = qrtools.QR()
    try:
        image_info['qr_code'] = qr.decode(StringIO(imgbody))
    except (IOError, UnboundLocalError):
        image_info['qr_code'] = True
    return image_info


def get_norm_name(file_image):
    m = re.search('(\d+-\w+-\w+)', file_image.split('/')[-1])
    if not m:
        return ''
    return m.group(1)


def check_min_size_info(image_info):
    datasource_type = image_info['norm_name'].split('-')[0][0]
    if not datasource_type:
        return True
    elif datasource_type == '1':
        return image_info['width'] < MIN_SIZE[0] or image_info['height'] < MIN_SIZE[1]
    else:
        return image_info['width'] < MIN_SIZE[0] and image_info['height'] < MIN_SIZE[1]


def compare_image_info(image_type, image_src, image_dst):
    if image_dst['qr_code']:
        return image_src
    image_size = SMALL_SIZE if image_type == 'small' else LARGE_SIZE
    if image_dst['width'] < image_size[0] * 0.9 or image_dst['height'] < image_size[1] * 0.9:
        return image_src
    if image_dst['format'] == 'GIF':
        return image_src
    ratio = image_size[0] / image_size[1]
    if not ratio / 1.1 <= image_dst['ratio'] <= ratio * 1.1:
        return image_src
    if not image_src:
        return image_dst
    if image_dst['ratio'] < image_src['ratio']:
        return image_dst
    else:
        return image_src
