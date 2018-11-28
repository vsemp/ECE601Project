# -*- coding: utf-8 -*-
from copy import deepcopy


MIN_SIZE = (50.0, 50.0)
SMALL_SIZE = (192.0, 144.0)
LARGE_SIZE = (584.0, 278.0)


def check_minimal_size_image(image_info):
    return image_info['width'] < MIN_SIZE[0] and \
        image_info['height'] < MIN_SIZE[1]


def check_minimal_size_thumbnail(image_type, image_info):
    image_size = SMALL_SIZE if image_type == 'small' else LARGE_SIZE
    if image_info['width'] < image_size[0] * 0.9 or \
            image_info['height'] < image_size[1] * 0.9:
        return False
    return True


def compare_image_package(image_type, image_package_src, image_package_dst):
    image_src = image_package_src.get('image_info')
    image_dst = image_package_dst['image_info']
    if image_dst['qr_code']:
        return image_package_src
    image_size = SMALL_SIZE if image_type == 'small' else LARGE_SIZE
    if image_dst['width'] < image_size[0] * 0.9 or \
            image_dst['height'] < image_size[1] * 0.9:
        return image_package_src
    if image_dst['format'] == 'GIF':
        return image_package_src
    ratio = image_size[0] / image_size[1]
    if not ratio / 1.1 <= image_dst['ratio'] <= ratio * 1.1:
        return image_package_src
    if not image_src or image_dst['ratio'] < image_src['ratio']:
        return image_package_dst
    else:
        return image_package_src


def find_focus(image_info, faces=None):
    if not faces:
        return image_info['width'] / 2, image_info['height'] / 2
    sum_width = 0
    sum_height = 0
    for face in faces:
        sum_width += (face[0] + face[2])
        sum_height += (face[1] + face[3])
    return sum_width / len(faces) / 2, sum_height / len(faces) / 2


def resize_thumbnail(image_type, image_package):
    image_size = SMALL_SIZE if image_type == 'small' else LARGE_SIZE
    ratio = image_size[0] / image_size[1]
    image_info = image_package['image_info']
    focus_width, focus_height = find_focus(image_info, None)
    resize_width_0 = int(focus_width * (1 - ratio / image_info['ratio']))
    resize_width_1 = resize_width_0 + int(image_info['height'] * ratio)
    resize_height_0 = 0
    resize_height_1 = int(image_info['height'])
    return resize_width_0, resize_width_1, resize_height_0, resize_height_1


def is_fit(image_type, image_info, image_size):
    ratio = image_size[0] / image_size[1]
    if image_type == 'video':
        if image_info['width'] > 0.8 * image_size[0] \
                and image_info['height'] > 0.8 * image_size[1]:
            if ratio / 1.1 <= image_info['ratio'] <= ratio * 1.1:
                return True
        return False  # todo
    else:
        if image_info['width'] > 0.9 * image_size[0] \
                and image_info['height'] > 0.9 * image_size[1]:
            if ratio / 1.1 <= image_info['ratio'] <= ratio * 1.1:
                return True
        return False


def is_unfit(image_type, image_info, image_size):
    ratio = image_size[0] / image_size[1]
    if image_type == 'video':
        if image_info['width'] > 0.8 * image_size[0] \
                and image_info['height'] > 0.8 * image_size[1]:
            if ratio / 1.6 < image_info['ratio'] < ratio * 1.55:
                return True
        return False  # todo
    elif image_type == 'large':
        return False
    elif image_type == 'small':
        if image_info['width'] > 0.9 * image_size[0] \
                and image_info['height'] > 0.9 * image_size[1]:
            if ratio * 1.1 < image_info['ratio'] < ratio * 1.55:
                return True
        return False


def crop_image_by_ratio(ratio, image_size, center_position, expand=True):
    '''
    ratio: target of cropping, e.g. 1.62(668.0w/412.0h)
    image_size: original size of physical image, e.g. (625, 351)
    center_position: coordinates of center of cropped box, e.g. (292.8, 97.3)
    expand: whether box is allowed to expand to cover as much as image, despite center_position
    return: box represented by a 4-elements tuple, e.g. (8, 0, 577, 351),
            i.e. coordinates of leftupper and rightlower points.
    '''
    width, height = image_size
    max_width = int(width)
    max_height = int(height)
    focus_x, focus_y = center_position
    max_box_width = int(min(ratio * max_height, max_width))
    max_box_height = int(min(max_width / ratio, max_height))
    if not expand:
        box_width = min(min(focus_x, max_width - focus_x) * 2, max_box_width)
        box_height = min(
            min(focus_y, max_height - focus_y) * 2, max_box_height)
        if float(box_width) / box_height < ratio:
            box_height = int(box_width / ratio)
        else:
            box_width = int(box_height * ratio)
        left_x = focus_x - box_width / 2
        right_x = focus_x + box_width / 2
        upper_y = focus_y - box_height / 2
        lower_y = focus_y + box_height / 2
    else:
        if focus_x <= max_width / 2:
            left_x = max(focus_x - max_box_width / 2, 0)
            right_x = left_x + max_box_width
        else:
            right_x = min(focus_x + max_box_width / 2, max_width)
            left_x = right_x - max_box_width
        if focus_y <= max_height / 2:
            upper_y = max(focus_y - max_box_height / 2, 0)
            lower_y = upper_y + max_box_height
        else:
            lower_y = min(focus_y + max_box_height / 2, max_height)
            upper_y = lower_y - max_box_height
    return left_x, upper_y, right_x, lower_y


def center_crop_image_by_ratio(ratio, image_size):
    center_position = int(image_size[0]) / 2, int(image_size[1]) / 2
    return crop_image_by_ratio(ratio, image_size, center_position)


def select_thumbnails(image_type, image_list):
    image_size = SMALL_SIZE if image_type == 'small' else LARGE_SIZE
    ratio = image_size[0] / image_size[1]
    list_fit = []
    list_unfit = []
    for image_package in image_list:
        if not image_package:
            continue
        image_info = image_package.get('image_info', None)
        if not image_info:
            continue
        if image_info['format'] == 'GIF':
            continue
        if image_info['qr_code']:
            continue
        # if not check_minimal_size_thumbnail(image_type, image_info):
            # continue
        if is_fit(image_type, image_info, image_size):
            list_fit.append(image_package)
        elif is_unfit(image_type, image_info, image_size):
            list_unfit.append(image_package)
    if list_fit:
        list_fit = sorted(list_fit, key=lambda image_package: abs(
            image_package['image_info']['ratio'] - ratio))
        return list_fit[0]
    for image_package in list_unfit:
        image_info = image_package['image_info']
        original_size = (image_info['width'], image_info['height'])
        box = center_crop_image_by_ratio(ratio, original_size)
        left_x, upper_y, right_x, lower_y = box
        image_package_resize = deepcopy(image_package)
        resize_info = {
            'point_w': left_x,
            'point_h': upper_y,
            'width': right_x - left_x,
            'height': lower_y - upper_y,
        }
        image_package_resize['resize_info'] = resize_info
        return image_package_resize
    return None
