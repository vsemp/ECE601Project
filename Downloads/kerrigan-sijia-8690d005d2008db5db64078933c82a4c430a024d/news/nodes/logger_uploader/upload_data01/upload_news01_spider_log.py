# -*-coding:utf-8-*-
from upload_data01_base import Uploader
import datetime
import sys
import os
import time
import shutil
import pandas as pd

sys.path.append('..')
from mailer import Mailer


# 待整理
class UploaderTwitter(Uploader):
    config_key = 'SSH_NEWS01'

    def _gen_email(self, filename):
        with open('%s/%s/log' % (self.local_path, filename), 'r') as f:
            data = (line.strip() for line in f)
            data_json = "[{0}]".format(','.join(data))
            df = pd.read_json(data_json, 'records')
        import datetime

        spider_start_ts = df[(df['type'] == 'start')]['ts'].tolist()[0]
        start_datetime = datetime.datetime.strptime(str(spider_start_ts), '%Y%m%d%H%M%S')
        spider_end_ts = df[(df['type'] == 'stop')]['ts'].tolist()[0]
        end_datetime = datetime.datetime.strptime(str(spider_end_ts), '%Y%m%d%H%M%S')

        spider_crawl_id = filename
        spider_name = spider_crawl_id[:15]

        source_start_numbers = df[(df['source_url_state'] == 'start')].drop_duplicates(
            ['source_url']).source_url.count()
        source_finished_numbers = df[(df['source_url_state'] == 'finished')].drop_duplicates(
            ['source_url']).source_url.count()
        source_account_exist_numbers = df[(df['info'] == 'account exists')].drop_duplicates(
            ['source_url']).source_url.count()
        source_account_exists = df[(df['info'] == 'account exists')].drop_duplicates(['source_url']).source_url

        source_failed_numbers = df[(df['source_url_state'] == 'error')].drop_duplicates(
            ['source_url']).source_url.count()
        source_faileds = df[(df['source_url_state'] == 'error')].drop_duplicates(['source_url', 'info'])

        send_str = ''
        send_str += ('爬虫名：%s' % filename[:-15])
        send_str += ('\n')
        send_str += ('爬取开始时间：%s' % start_datetime)
        send_str += ('\n')
        send_str += ('爬取结束时间：%s' % end_datetime)
        send_str += ('\n')
        send_str += ('运行时间：%s' % (end_datetime - start_datetime))
        send_str += ('\n')
        send_str += ('\n')
        send_str += ('爬取source总量：%s' % source_start_numbers)
        send_str += ('\n')
        send_str += ('爬取成功总量：%s' % source_finished_numbers)
        send_str += ('\n')
        send_str += ('\n')
        send_str += ('account_重复量：%s' % source_account_exist_numbers)
        send_str += ('\n')
        send_str += ('爬取失败条目：%s' % source_failed_numbers)
        send_str += ('\n')
        send_str += ('\n')
        send_str += str(df[(df['type'] != 'error')].groupby(df['info']).count().source_url)
        send_str += ('\n')
        send_str += ('\n')
        if source_failed_numbers != 0:
            send_str += ('errors:')
            send_str += ('\n')
            send_str += (str(df[(df['type'] == 'error')].groupby(df['info']).count().source_url))

        trackback_str = ''
        if source_failed_numbers != 0:
            if 'traceback' in df[(df['type']) == "error"]:
                tarcks = df[(df['type']) == "error"]['traceback'].tolist()
                for each in tarcks:
                    # 处理掉空字段
                    if len(str(each)) > 10:
                        trackback_str += ('\n')
                        trackback_str += str(each)

        return send_str, trackback_str

    def run(self):
        while True:
            for filename in os.listdir(self.local_path):
                full_file_path = os.path.join(self.local_path, filename)
                print (full_file_path)
                # move invalid folder to trash
                if filename == 'trash':
                    continue

                if not os.path.exists(full_file_path + '/' + 'spider_started'):
                    if os.path.exists(self.local_path + '/trash/' + filename):
                        shutil.rmtree(self.local_path + '/trash/' + filename)
                    else:
                        # 处理一天前的错误
                        if (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d%H%M%S') > filename[
                                                                                                             -14:]:
                            os.system('mv %s %s' % (full_file_path, self.local_path + '/trash/' + filename))
                            print ('invalid folder: %s moved !' % filename)
                    continue
                if os.path.exists(full_file_path + '/' + 'spider_finished') and os.path.exists(
                                        full_file_path + '/' + 'log'):
                    print ('spider_finished found !')

                    with open(full_file_path + '/' + 'spider_finished', 'r') as f:
                        finished_ts = f.read()
                    print ('finished_ts is %s' % finished_ts)
                    interval_sec = (datetime.datetime.now() - datetime.datetime.strptime(str(finished_ts),
                                                                                         '%Y%m%d%H%M%S')).total_seconds()
                    print ('interval_sec is %s' % interval_sec)

                    if interval_sec > self.span_time:
                        print ('%s found ' % filename)
                        # 4，生成邮件body
                        receivers = ['xinyu.du@cootek.cn']
                        mailer = Mailer(receivers)
                        send_str, trackback_str = self._gen_email(filename)
                        attach_file = mailer.get_attach_from_str(str=trackback_str,
                                                                 attach_filename='error_trackback.txt')
                        # 5, 发送邮件
                        mailer.send_mail(subject=filename + ' log', text=send_str, attach_list=[attach_file])

                        # 6, 发送data01
                        log_file_name = filename + '/log'
                        log_file_remote_name = filename + '_log'
                        self.logger.warning(log_file_name)
                        self._upload(log_file_name, log_file_remote_name)

                        if os.path.exists(full_file_path + '/' + 'items'):
                            item_file_name = filename + '/items'
                            item_file_remote_name = filename + '_items'

                            self.logger.warning(item_file_name)
                            self._upload(item_file_name, item_file_remote_name)

                        self.logger.warning(datetime.datetime.now())

                        # 7, 删除本地文件
                        shutil.rmtree(self.local_path + '/' + filename)
            self.logger.warning('no file to upload now')
            time.sleep(60)


if __name__ == '__main__':
    uploader = UploaderTwitter()
    uploader.run()
