import json
import redis

UGC_EXPIRATION = 30 * 24 * 3600

UGC_FILTER_MAP = {
    'TimeFilter': 1,
    'CrawlTimeFilter': 2,
    'TitleFilter': 3,
    'TagsFilter': 4,
    'ContentFilter': 5,
    'DedupKeyFilter': 6,
    'DupeFilter': 7,
    'PageTypeFilter': 8,
}

def ugc_record_init(uid, ctid, url, exp):
    ''' write uid and ctid into ugc_redis '''
    ugc_redis = redis.Redis('data-cache003')
    ugc_uid_name = 'ugc:%s' % uid
    try:
        ugc_record = json.loads(ugc_redis.hget(ugc_uid_name, url))
        ugc_record.update({'ctid': ctid})
        ugc_redis.hset(ugc_uid_name, url, json.dumps(ugc_record))
    except: pass
    ugc_redis.sadd("ugc:uid:set", uid)
    ugc_count_name = "ugc:count:%s" % ctid
    if not ugc_redis.exists(ugc_count_name):
        ugc_redis.hmset(ugc_count_name, {'ed':0, 'clk': 0})
        ugc_redis.expire(ugc_count_name, exp)

def ugc_record_filter(item, filter_type):
    ugc_redis = redis.Redis('data-cache003')
    uid = item['raw']['subtitle'].split('-')[-1].strip()
    url = item['raw']['url']['source_url']
    ugc_uid_name = 'ugc:%s' % uid
    try:
        ugc_record = json.loads(ugc_redis.hget(ugc_uid_name, url))
        ugc_record.update({'type': filter_type})
        ugc_redis.hset(ugc_uid_name, url, json.dumps(ugc_record))
    except: pass

def is_ugc(msg):
    return isinstance(msg, dict) and msg.get('raw', {}).get('subtitle', '').startswith('ugc')

def ugc_set(message, mw):
    mw_name = mw.__class__.__name__
    if mw_name == 'DedupKeyMaker':
        uid = message['raw']['subtitle'].split('-')[-1].strip()
        url = message['raw']['url']['source_url']
        dedup_key = message['dedup_key']
        ugc_record_init(uid, dedup_key, url, UGC_EXPIRATION)

def ugc_filter(message, mw):
    mw_name = mw.__class__.__name__
    if mw_name in UGC_FILTER_MAP:
        filter_type = UGC_FILTER_MAP[mw_name]
        ugc_record_filter(message, filter_type)
