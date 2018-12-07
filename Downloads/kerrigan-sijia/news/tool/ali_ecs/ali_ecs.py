#!/usr/bin/env python
#coding: utf-8
import sys,os
import urllib,urllib2
import base64
import hmac
import hashlib
from hashlib import sha1
import time
import uuid
import json

class AliECS(object):
    def __init__(self, access_key_id, access_key_secret):
        self.access_key_id = access_key_id #input the access_key here
        self.access_key_secret = access_key_secret #input the access_key_secret here
        self.server_address = 'https://ecs.aliyuncs.com'

    def percent_encode(self, str):
        res = urllib.quote(str.decode(sys.stdin.encoding).encode('utf8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def compute_signature(self, parameters, access_key_secret):
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
        canonicalizedQueryString = ''
        for (k,v) in sortedParameters:
            canonicalizedQueryString += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)
        stringToSign = 'GET&%2F&' + self.percent_encode(canonicalizedQueryString[1:])
        h = hmac.new(access_key_secret + "&", stringToSign, sha1)
        signature = base64.encodestring(h.digest()).strip()
        return signature

    def compose_url(self, user_params):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        parameters = {
                'Format'        : 'JSON',
                'Version'       : '2014-05-26',
                'AccessKeyId'   : self.access_key_id,
                'SignatureVersion'  : '1.0',
                'SignatureMethod'   : 'HMAC-SHA1',
                'SignatureNonce'    : str(uuid.uuid1()),
                'TimeStamp'         : timestamp,
        }
        for key in user_params.keys():
            parameters[key] = user_params[key]
        signature = self.compute_signature(parameters, self.access_key_secret)
        parameters['Signature'] = signature
        url = self.server_address + "/?" + urllib.urlencode(parameters)
        return url

    def make_request(self, user_params):
        url = self.compose_url(user_params)
        request = urllib2.Request(url)
        try:
            conn = urllib2.urlopen(request)
            response = conn.read()
        except urllib2.HTTPError, e:
            print(e.read().strip())
            raise SystemExit(e)
        try:
            result = json.loads(response)
            return result
        except ValueError, e:
            raise SystemExit(e)