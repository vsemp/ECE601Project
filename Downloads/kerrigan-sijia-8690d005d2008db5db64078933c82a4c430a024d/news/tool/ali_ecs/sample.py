#!/usr/bin/env python
#coding: utf-8
import json
from ali_ecs import AliECS

if __name__ == '__main__':
    access_key_id = '**'
    access_key_secret = '***'
    ali = AliECS(access_key_id, access_key_secret)
    query_params = {
            'Action': 'DescribeInstanceStatus',
            'RegionId': 'cn-hangzhou',
        }
    result = ali.make_request(query_params)
    print json.dumps(result, sort_keys = True, indent = 4)
