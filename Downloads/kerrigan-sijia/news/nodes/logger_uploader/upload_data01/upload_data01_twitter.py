#-*-coding:utf-8-*-
from upload_data01_base import Uploader


class UploaderTwitter(Uploader):
    config_key = 'SSH_TWITTER'

if __name__ == '__main__':
    uploader = UploaderTwitter()
    uploader.run()

