#-*-coding:utf-8-*-
from upload_data01_twitter import Uploader


class UploaderComment(Uploader):
    config_key = 'SSH_TWITTER_COMMENT'

if __name__ == '__main__':
    uploader = UploaderComment()
    uploader.run()

