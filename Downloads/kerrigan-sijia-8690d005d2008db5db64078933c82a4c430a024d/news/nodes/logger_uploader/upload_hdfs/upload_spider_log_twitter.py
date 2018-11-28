# -*-coding:utf-8-*-
from upload_hdfs_base import UploaderHDFS
import time
import os
import datetime


class UploaderTwitter(UploaderHDFS):
    config_key = 'HDFS_SPIDER_LOG'

    def run(self):
        while True:
            for file_name in os.listdir(self.local_path):
                if 'ready' not in file_name:
                    continue
                tdate = datetime.datetime.now().strftime('%Y%m%d')

                if file_name.split('_')[-2] == 'items':
                    self._mkdir(tdate)
                    self._mkdir(str(tdate) + '/' + 'items')
                    self.upload(file_name, 'items/' + file_name, tdate)
                elif file_name.split('_')[-2] == 'log':
                    self._mkdir(tdate)
                    self._mkdir(str(tdate) + '/' + 'log')
                    self.upload(file_name, 'log/' + file_name, tdate)
                self.logger.warning(file_name + 'uploaded')
                self._remove(file_name)
            self.logger.warning('no available file to upload')
            time.sleep(60)
            os.system("kinit -kt /home/xinyu.du/xinyu.du.keytab xinyu.du")


if __name__ == '__main__':
    uploader = UploaderTwitter()
    uploader.run()
