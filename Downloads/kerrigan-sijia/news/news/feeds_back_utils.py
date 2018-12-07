import requests
import json
from requests.adapters import HTTPAdapter
import logging
import random

domain_url = "http://13.57.134.12:3001/api/v1.0"
convert_md5_url = "/login/convertMD5"
login_url = "/login/auth"
find_record_url = "/interface/record/findAll"
find_all_url = "/interface/rule/findAll"
changeState_url = "/interface/record/changeState"
max_retries = 200
time_out = 10

ta = ['23.95.140.220:13228', '23.95.140.193:13228', '23.95.140.162:13228', '23.95.140.119:13228',
      '23.95.140.111:13228', '23.95.140.22:13228', '23.95.139.115:13228', '23.95.139.93:13228',
      '23.95.139.70:13228', '23.95.140.11:13228', '23.95.140.96:13228', '23.95.139.19:13228',
      '198.23.195.16:13228', '192.210.248.207:13228', '192.210.248.100:13228', '192.210.248.86:13228',
      '192.210.248.18:13228', '192.210.248.120:13228', '192.210.248.73:13228', '192.210.248.62:13228',
      '198.23.195.104:13228', '198.23.195.47:13228',
      '198.23.195.163:13228', '192.210.248.247:13228', '198.23.195.58:13228', ]
tp = random.choice(ta)
proxies = {
    'http': 'http://{}'.format(tp),
    'https': 'http://{}'.format(tp)
}


def get_token(rs):
    payload = {"key": "cootek"}
    r = rs.get(domain_url + convert_md5_url, proxies=proxies, params=payload, timeout=time_out)
    md5_str = r.json()["data"]['md5']
    r = rs.get(domain_url + login_url, proxies=proxies, params={"username": "xinyu.du@cootek.cn", "password": md5_str},
               timeout=time_out)
    token_str = r.json()["data"]['token']
    return token_str


def get_ids(token_str, rs, source_name, nation_name):
    r = rs.post(domain_url + find_all_url, proxies=proxies, data={"token": token_str}, timeout=time_out)
    for each in r.json()['data']['results']:
        if each['sourceName'] == source_name:
            for country in each['countries']:
                na_str = " ".join(str(country['country'].encode('utf-8')).strip().split(' ')[:-1])
                if na_str == nation_name:
                    return country['ruleId'], country['id']
            return None, None


def get_channel_list(source_name, nation_name):
    rs = get_rs()
    token_str = get_token(rs)
    rule_id, country_id = get_ids(token_str, rs=rs, source_name=source_name, nation_name=nation_name)
    if rule_id is None or country_id is None:
        return []
    post_dict = {
        "token": token_str,
        "query": json.dumps({
            "ruleID": rule_id,
            "countryId": country_id
        })
    }
    r = rs.post(domain_url + find_record_url, proxies=proxies, data=post_dict, timeout=time_out)
    url_list = []
    for each in r.json()['data']['results']:
        url_list.append(each['url'])

    return url_list


def get_channel_list_with_other_keys_inner(source_name, nation_name):
    rs = get_rs()
    token_str = get_token(rs)
    rule_id, country_id = get_ids(token_str, rs=rs, source_name=source_name, nation_name=nation_name)
    print rule_id
    print country_id
    if rule_id is None or country_id is None:
        return []
    post_dict = {
        "token": token_str,
        "query": json.dumps({
            "ruleID": rule_id,
            "countryId": country_id
        })
    }
    r = rs.post(domain_url + find_record_url, proxies=proxies, data=post_dict, timeout=time_out)
    url_list = []
    for each in r.json()['data']['results']:
        source_url_dict = {"source_url": each['url'], "source_url_id": int(each['id']),
                           "create_date": each['create_time'][:10],
                           "state": each['state'], "tags": []}
        for sb in each['tags']:
            source_url_dict['tags'].append(sb['name'].strip())
        # source_url_dict['tags'].append(each)
        url_list.append(source_url_dict)
    return url_list


def get_channel_list_with_other_keys_new_platform(raw_source_name, nation_name):
    source_name = ''
    source_type = ''
    locale = ''
    if raw_source_name == 'youtube':
        source_name = 'youtube'
        source_type = 'channel'
    elif raw_source_name == 'musically':
        source_name = 'musically'
        source_type = 'channel'
    elif raw_source_name == 'like':
        source_name = 'like'
        source_type = 'channel'
    elif raw_source_name == 'douyin':
        source_name = 'douyin'
        source_type = 'channel'
    elif raw_source_name == 'muse':
        source_name = 'muse'
        source_type = 'channel'
    elif raw_source_name == 'youtube_tops':
        source_name = 'youtube'
        source_type = 'tops'
    elif raw_source_name == 'facebook_tops':
        source_name = 'facebook'
        source_type = 'tops'
    elif raw_source_name == 'facebook':
        source_name = 'facebook'
        source_type = 'channel'
    elif raw_source_name == 'youtube_hifit':
        source_name = 'youtube'
        source_type = 'channel'
    elif raw_source_name == 'youtube_playlist':
        source_name = 'youtube'
        source_type = 'playlist'
    elif raw_source_name == 'instagram':
        source_name = 'instagram'
        source_type = 'channel'
    elif raw_source_name == 'youtube_hifit_trend':
        source_name = 'youtube'
        source_type = 'instant'
    elif raw_source_name == 'youtube_ugc':
        source_name = 'youtube'
        source_type = 'ugc'
    elif raw_source_name == 'facebook_ugc':
        source_name = 'facebook'
        source_type = 'ugc'
    elif raw_source_name == 'instagram_ugc':
        source_name = 'instagram'
        source_type = 'ugc'
    elif raw_source_name == 'buzzvideo':
        source_name = 'buzzvideo'
        source_type = 'channel'
    elif raw_source_name == 'youtube_instant':
        source_name = 'youtube'
        source_type = 'instant'
    elif raw_source_name == 'facebook_instant':
        source_name = 'facebook'
        source_type = 'instant'

    if 'Russia' in nation_name:
        locale = ['ru_RU']
    elif 'Brazil' in nation_name:
        locale = ['pt_BR']
    elif 'Indonesia' in nation_name:
        locale = ['in_ID']
    elif 'Taiwan' in nation_name:
        locale = ['cn_TW']
    elif 'Saudi Arabia' in nation_name:
        locale = ['ar_AR']
    elif 'India(English)' in nation_name:
        locale = ['en_IN']
    elif 'Global' in nation_name:
        locale = ['en_ZZ']
    elif 'India(Hindi)' in nation_name:
        locale = ['hi_IN']
    elif 'Thailand' in nation_name:
        locale = ['th_TH']
    elif 'Japan' in nation_name:
        locale = ['ja_JP']
    elif 'Korea' in nation_name:
        locale = ['ko_KR']
    elif 'Mexico' in nation_name:
        locale = ['es_MX']
    elif 'France' in nation_name:
        locale = ['fr_FR']
    elif 'United States of America' in nation_name:
        locale = ['en_US']

    params = {
        'source_name': source_name,
        'source_type': source_type,
    }

    if locale and 'en_ZZ' not in locale:
        params['locales'] = locale[0]

    r = requests.get('http://monitor-veeuapp.corp.cootek.com:18050/spider/tasks', params=params)
    url_list = []
    for each in json.loads(r.content):
        source_url_dict = {"source_url": each['url'], "source_url_id": each['id'],
                           "state": 0, "tags": each['tags'], "locales": each['locales']}
        if 'extra_info' in each and each['extra_info'] is not None:
            for key in each['extra_info'].keys():
                source_url_dict[key] = each['extra_info'][key]
        url_list.append(source_url_dict)

    return url_list


# def get_channel_list_with_other_keys(source_name, nation_name):
#     return get_channel_list_with_other_keys_inner(source_name, nation_name)


def get_channel_list_with_other_keys(source_name, nation_name):
    return get_channel_list_with_other_keys_new_platform(source_name, nation_name)


def get_rs():
    rs = requests.session()
    rs.mount('http://', HTTPAdapter(max_retries=max_retries))
    rs.mount('https://', HTTPAdapter(max_retries=max_retries))
    return rs


def set_source_url_crawled(source_url_id):
    return set_source_url_state(source_url_id, 1)


def set_source_url_start_crawl(source_url_id):
    return set_source_url_state(source_url_id, -1)


def set_source_url_state(source_url_id, state):
    return True
    # rs = get_rs()
    # token_str = get_token(rs)
    # post_dict = {
    #     "token": token_str,
    #     "state": str(state)
    # }
    # r = rs.put(domain_url + changeState_url + '/' + str(source_url_id), proxies=proxies, data=post_dict,
    #            timeout=time_out)
    #
    # if r.json()['code'] == 200:
    #     return True
    # else:
    #     logging.error('set_source_url_state error_code == %d' % r.json()['code'])
    #     return False


if __name__ == '__main__':
    channel_list = get_channel_list_with_other_keys('youtube_hifit', 'United States of America')

    for each in channel_list:
        print(each)
    print(len(channel_list))

    # for each in channel_list:
    #     if each['create_date'] == '2018-02-27':
    #         bool_temp = set_source_url_crawled(each['source_url_id'])
    #         print bool_temp

    print ('done')
