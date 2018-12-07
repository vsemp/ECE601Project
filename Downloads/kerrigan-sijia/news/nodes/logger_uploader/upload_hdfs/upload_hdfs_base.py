# -*-coding:utf-8-*-
import os
import ConfigParser
import logging
import time


class UploaderHDFS(object):
    config_key = 'HDFS_TWITTER'

    def __init__(self):
        self.init_config()

    def init_config(self):
        file_config = '../config/hdfs.conf'
        conf = ConfigParser.ConfigParser()
        self.read = conf.read(file_config)
        self.local_path = conf.get(self.config_key, 'local_path')
        self.remote_path = conf.get(self.config_key, 'remote_path')
        self.span_time = int(conf.get(self.config_key, 'span_time'))
        self.date_format = conf.get(self.config_key, 'date_format')

    @property
    def logger(self):
        FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
        DATEFORMAT = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT, level=logging.INFO)
        return logging.getLogger(self.__class__.__name__)

    def upload(self, localfilename, remotefilename, tdate):
        localfile = os.path.join(self.local_path, localfilename)
        remotefile = os.path.join(self.remote_path, tdate, remotefilename)
        return_code = os.system(
            '/usr/local/hadoop-2.6.3/bin/hdfs dfs -put -f %s %s' % (localfile, remotefile))
        self.logger.warning('return_code : %d' % return_code)
        self.logger.warning('%s upload to %s' % (localfile, remotefile))

    def _mkdir(self, tdate):
        remotefile = os.path.join(self.remote_path, tdate)
        return_code = os.system(
            '/usr/local/hadoop-2.6.3/bin/hdfs dfs -mkdir %s' % (remotefile))

    def _remove(self, localfilename):
        localfile = os.path.join(self.local_path, localfilename)
        if os.path.exists(localfile):
            os.remove(localfile)
            self.logger.warning('remove %s' % localfile)

    def run(self):
        while True:
            for file_name in os.listdir(self.local_path):
                if 'ready' not in file_name:
                    continue
                tdate = time.strftime(self.date_format,
                                      time.localtime(int(file_name.split('_')[0].strip()) * self.span_time))
                self._mkdir(tdate)
                self.upload(file_name, file_name, tdate)
                self._remove(file_name)
            self.logger.warning('no available file to upload')
            time.sleep(60)
            os.system("kinit -kt /home/darbra.chen/darbra.chen.keytab darbra.chen")


if __name__ == '__main__':
    uploader = UploaderHDFS()
    uploader.run()
