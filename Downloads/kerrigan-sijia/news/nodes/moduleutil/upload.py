import sys
from oss.oss_api import *
from oss.oss_util import *
from oss.oss_xml_handler import *


DEFAUL_HOST = "oss-cn-hangzhou.aliyuncs.com"
OSS_HOST = DEFAUL_HOST
ID = "vtum99z0ySLlf8Yg"
KEY = "OAsidmqnTd5hxrrVtpVNMqwWZJSQxT"
STS_TOKEN = None

SEND_BUF_SIZE = 8192
RECV_BUF_SIZE = 1024*1024*10
IS_DEBUG = False

RET_OK = 0
RET_FAIL = -1
RET_SKIP = 1


def get_oss(show_bar=True):
    oss = OssAPI(OSS_HOST, ID, KEY, sts_token=STS_TOKEN)
    oss.show_bar = show_bar
    oss.set_send_buf_size(SEND_BUF_SIZE)
    oss.set_recv_buf_size(RECV_BUF_SIZE)
    oss.set_debug(IS_DEBUG)
    return oss


def put_object(bucket, object, content, is_replace=False, retry_times=2):
    '''
    return RET_OK, RET_FAIL, RET_SKIP
    '''
    show_bar = False
    oss = get_oss(show_bar)
    object = smart_code(object)
    if len(object) == 0:
        print "object is empty when put /%s/%s, skip" % (bucket, object)
        return RET_SKIP
    if not is_replace:
        res = oss.head_object(bucket, object)
        if res.status == 200:
            return RET_SKIP
    for i in xrange(retry_times):
        try:
            res = oss.put_object_with_data(bucket, object, content)
            if 200 == res.status:
                return RET_OK
            else:
                print "upload to /%s/%s FAIL, status:%s, request-id:%s" % (bucket, object, res.status, res.getheader("x-oss-request-id"))
        except:
            print "upload %s/%s occur exception" % (bucket, object)
            print sys.exc_info()[0], sys.exc_info()[1]
    return RET_FAIL
