#-*-coding:utf-8-*-
from upload_hdfs_base import UploaderHDFS


class UploaderTwitter(UploaderHDFS):
    config_key = 'HDFS_ZHIHU'

if __name__ == '__main__':
    uploader = UploaderTwitter()
    uploader.run()

