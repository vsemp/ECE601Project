#-*-coding:utf-8-*-
import ConfigParser
import paramiko
import os
import time
import datetime
import logging


class Uploader(object):
    config_key = 'SSH_TWITTER'
    def __init__(self):
        self.init_config()
        self.init_ssh()

    def init_ssh(self):
        key = paramiko.RSAKey.from_private_key_file(self.ssh_private_key)
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.connect(self.ssh_host, self.ssh_port, self.ssh_name, pkey=key)
        t = s.get_transport()
        self.sftp_handler = paramiko.SFTPClient.from_transport(t)
        self.ssh_handler = s

    def init_config(self):
        file_config = '/config/upload.conf'
        conf = ConfigParser.ConfigParser()
        self.read = conf.read(file_config)
        self.ssh_host = conf.get(self.config_key, 'ssh_host')
        self.ssh_port = int(conf.get(self.config_key, 'ssh_port'))
        self.ssh_name = conf.get(self.config_key, 'ssh_name')
        self.ssh_private_key = conf.get(self.config_key, 'ssh_private_key')
        self.local_path = conf.get(self.config_key, 'local_path')
        self.remote_path = conf.get(self.config_key, 'remote_path')
        self.span_time = int(conf.get(self.config_key, 'span_time'))

    @property
    def logger(self):
        FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
        DATEFORMAT = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(format=FORMAT, datefmt=DATEFORMAT, level=logging.INFO)
        return logging.getLogger(self.__class__.__name__)

    def _upload(self, local_file, remote_file):
        local_total = os.path.join(self.local_path, local_file)
        remote_total = os.path.join(self.remote_path, remote_file)
        logging.info(local_total)
        logging.info(remote_total)
        self.sftp_handler.put(local_total, remote_total)
        self._rename(remote_total)
        os.remove(local_total)

    def _rename(self, remote_file):
        self.ssh_handler.exec_command('mv %s %s' % (remote_file, remote_file+'_ready'))

    def run(self):

        while True:
            for file_name in os.listdir(self.local_path):
                if '_' not in file_name:
                    continue
                available_ts_15min = int(time.time()/self.span_time) - 1
                try:
                    ts_15min = int(file_name.split('_')[0])
                except:
                    continue
                if ts_15min > available_ts_15min:
                    continue
                self.logger.warning(file_name)
                self._upload(file_name, file_name)
                self.logger.warning(datetime.datetime.now())
            self.logger.warning('no file to upload now')
            time.sleep(60)


if __name__ == '__main__':
    uploader = Uploader()
    uploader.run()

