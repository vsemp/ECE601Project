from pymongo import MongoClient
import datetime
import random
import json
import lxml
import re
import requests
from lxml import html
import pprint
import hashlib
import logging
import struct


class YoutubeCommentUtil:
    fake_users = [u'6643074923', u'6643074974', u'6643075125', u'6643079926', u'6643079927', u'6643079928',
                  u'6643079979',
                  u'6643080430', u'6643080431', u'6643080482', u'6643080583', u'6643080634', u'6643084485',
                  u'6643084536',
                  u'6643084537', u'6643084538', u'6643084539', u'6643084540', u'6643084541', u'6643084592',
                  u'6643084593',
                  u'6643084644', u'6643084795', u'6643084796', u'6643084897', u'6643084948', u'6643084999',
                  u'6643085050',
                  u'6643085151', u'6643085202', u'6643085203', u'6643085204', u'6643085205', u'6643085206',
                  u'6643085257',
                  u'6643085258', u'6643085359', u'6643085360', u'6643085411', u'6643085412', u'6643085513',
                  u'6643085564',
                  u'6643085615', u'6643085766', u'6643085767', u'6643085768', u'6643085769', u'6643085770',
                  u'6643085771',
                  u'6643085772', u'6643085773', u'6643085774', u'6643085775', u'6643085776', u'6643085777',
                  u'6643085778',
                  u'6643085829', u'6643085980', u'6643085981', u'6643085982', u'6643085983', u'6643085984',
                  u'6643086135',
                  u'6643086136', u'6643086237', u'6643086288', u'6643086289', u'6643086290', u'6643086391',
                  u'6643086392',
                  u'6643086443', u'6643086494', u'6643086645', u'6643086646', u'6643086697', u'6643086698',
                  u'6643086699',
                  u'6643086700', u'6643086801', u'6643086852', u'6643086903', u'6643086954', u'6643086955',
                  u'6643087006',
                  u'6643087007', u'6643087008', u'6643087109', u'6643087110', u'6643087111', u'6643087112',
                  u'6643087113',
                  u'6643087114', u'6643087165', u'6643087166', u'6643087167', u'6643087218', u'6643087269',
                  u'6643087320',
                  u'6643087421', u'6643087472', u'6643087473', u'6643087524', u'6643087575', u'6643087576',
                  u'6643087577',
                  u'6643087578', u'6643087579', u'6643087680', u'6643087681', u'6643087682', u'6643087683',
                  u'6643087684',
                  u'6643087735', u'6643087736', u'6643087737', u'6643087838', u'6643087989', u'6643088040',
                  u'6643088141',
                  u'6643088142', u'6643088193', u'6643088294', u'6643088295', u'6643088296', u'6643088297',
                  u'6643088348',
                  u'6643088349', u'6643088350', u'6643088351', u'6643088352', u'6643088403', u'6643088454',
                  u'6643088455',
                  u'6643088456', u'6643088457', u'6643088458', u'6643088459', u'6643088510', u'6643088561',
                  u'6643088562',
                  u'6643088563', u'6643088564', u'6643088615', u'6643088616', u'6643088617', u'6643088618',
                  u'6643088669',
                  u'6643088720', u'6643088721', u'6643088722', u'6643088823', u'6643088824', u'6643088925',
                  u'6643088976',
                  u'6643089027', u'6643089078', u'6643089079', u'6643089080', u'6643089131', u'6643089182',
                  u'6643089183',
                  u'6643089234', u'6643089235', u'6643089236', u'6643089337', u'6643089338', u'6643089389',
                  u'6643089490',
                  u'6643089491', u'6643089492', u'6643089543', u'6643089594', u'6643089595', u'6643089646',
                  u'6643089697',
                  u'6643089698', u'6643089749', u'6643089750', u'6643089751', u'6643089752', u'6643089753',
                  u'6643089754',
                  u'6643089755', u'6643089756', u'6643089807', u'6643089858', u'6643089859', u'6643089860',
                  u'6643089911',
                  u'6643090062', u'6643090113', u'6643090164', u'6643090165', u'6643090166', u'6643090267',
                  u'6643090368',
                  u'6643090369', u'6643090470', u'6643090471', u'6643090572', u'6643090573', u'6643090574',
                  u'6643090625',
                  u'6643090626', u'6643090677', u'6643090728', u'6643090729', u'6643090780', u'6643090881',
                  u'6643090882',
                  u'6643090933', u'6643090984', u'6643091035', u'6643091036', u'6643091087', u'6643091088',
                  u'6643091139',
                  u'6643091190', u'6643091191', u'6643091242', u'6643091243', u'6643091344', u'6643091345',
                  u'6643091396',
                  u'6643091447', u'6643091448', u'6643091499', u'6643091500', u'6643091501', u'6643091552',
                  u'6643091553',
                  u'6643091554', u'6643091605', u'6643091606', u'6643091607', u'6643091608', u'6643091609',
                  u'6643091610',
                  u'6643091711', u'6643091712', u'6643091713', u'6643091714', u'6643091715', u'6643091766',
                  u'6643091867',
                  u'6643091918', u'6643092069', u'6643092070', u'6643092071', u'6643092072', u'6643092173',
                  u'6643092274',
                  u'6643092275', u'6643092276', u'6643092277', u'6643092278', u'6643092329', u'6643092380',
                  u'6643092381',
                  u'6643092382', u'6643092383', u'6643092434', u'6643092435', u'6643092436', u'6643092437',
                  u'6643092488',
                  u'6643092489', u'6643092490', u'6643092491', u'6643092592', u'6643092593', u'6643092644',
                  u'6643092645',
                  u'6643092746', u'6643092747', u'6643092748', u'6643092749', u'6643092800', u'6643092851',
                  u'6643092902',
                  u'6643092903', u'6643092904', u'6643092905', u'6643092956', u'6643093057', u'6643093058',
                  u'6643093109',
                  u'6643093210', u'6643093261', u'6643093262', u'6643093313', u'6643093364', u'6643093415',
                  u'6643093466',
                  u'6643093517', u'6643093568', u'6643093569', u'6643093570', u'6643093621', u'6643093622',
                  u'6643093623',
                  u'6643093624', u'6643093625', u'6643093676', u'6643093727', u'6643093728', u'6643093779',
                  u'6643093780',
                  u'6643093781', u'6643093832', u'6643093833', u'6643093834', u'6643093835', u'6643093936',
                  u'6643093937',
                  u'6643093988', u'6643094189', u'6643094190', u'6643094241', u'6643094342', u'6643094393',
                  u'6643094494',
                  u'6643094495', u'6643094496', u'6643094547', u'6643094548', u'6643094549', u'6643094550',
                  u'6643094551',
                  u'6643094602', u'6692280968', u'6692281919', u'6692281920', u'6692281921', u'6692281922',
                  u'6692281923',
                  u'6692281924', u'6692281925', u'6692281926', u'6692281977', u'6692281978', u'6692281979',
                  u'6692282030',
                  u'6692282031', u'6692282032', u'6692282033', u'6692282034', u'6692282035', u'6692282086',
                  u'6692282087',
                  u'6692282138', u'6692282189', u'6692282190', u'6692282241', u'6692282242', u'6692282293',
                  u'6692282494',
                  u'6692282645', u'6692282646', u'6692282647', u'6692282648', u'6692282649', u'6692282650',
                  u'6692282651',
                  u'6692282702', u'6692282803', u'6692282804', u'6692282805', u'6692282806', u'6692282807',
                  u'6692282808',
                  u'6692282809', u'6692282810', u'6692282811', u'6692282812', u'6692282813', u'6692282814',
                  u'6692282815',
                  u'6692282866', u'6692282967', u'6692282968', u'6692282969', u'6692283020', u'6692283021',
                  u'6692283122',
                  u'6692283173', u'6692283174', u'6692283175', u'6692283176', u'6692283177', u'6692283178',
                  u'6692283179',
                  u'6692283230', u'6692283231', u'6692283232', u'6692283583', u'6692283584', u'6692283585',
                  u'6692283586',
                  u'6692283587', u'6692283588', u'6692283589', u'6692283590', u'6692283591', u'6692283642',
                  u'6692283643',
                  u'6692283644', u'6692283645', u'6692283646', u'6692283697', u'6692283798', u'6692283799',
                  u'6692283800',
                  u'6692284001', u'6692284002', u'6692284003', u'6692284004', u'6692284055', u'6692284056',
                  u'6692284107',
                  u'6692284158', u'6692284159', u'6692284160', u'6692284211', u'6692284212', u'6692284263',
                  u'6692284264',
                  u'6692284265', u'6692284266', u'6692284267', u'6692284268', u'6692284319', u'6692284320',
                  u'6692284321',
                  u'6692284372', u'6692284373', u'6692284374', u'6692284375', u'6692284426', u'6692284427',
                  u'6692287378',
                  u'6692287379', u'6692287380', u'6692287381', u'6692287382', u'6692287383', u'6692287434',
                  u'6692287485',
                  u'6692287486', u'6692287487', u'6692287488', u'6692287489', u'6692287490', u'6692287491',
                  u'6692287542',
                  u'6692288243', u'6692288294', u'6692288345', u'6692288396', u'6692288397', u'6692288398',
                  u'6692288399',
                  u'6692288400', u'6692288401', u'6692288452', u'6692288453', u'6692288504', u'6692288555',
                  u'6692288556',
                  u'6692288557']
    conn = MongoClient(
        'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
        readPreference="primary")
    comment_set = conn['polish_data']['crawled_comments']

    def __init__(self):
        pass

    def is_stats_available(self, page):
        return 'action-panel-trigger-stats' in page

    def extract_xsrf_token(self, page):
        token_regex = re.compile('\'XSRF_TOKEN\'\s*\n*:\s*\n*"(.*)"', re.IGNORECASE)
        match = re.search(token_regex, page)
        session_token = match.groups()[0]
        return session_token

    def extract_comment_token(self, page):
        token_regex = re.compile("'COMMENTS_TOKEN': \"(.*?)\"", re.IGNORECASE)
        match = re.search(token_regex, page)
        comment_token = match.groups()[0]
        return comment_token

    def fetch_comments_page(self, video_id):
        r = requests.get('https://www.youtube.com/watch?v=' + video_id, verify=False)
        cookies = r.cookies
        xsrf_token = self.extract_xsrf_token(r.text)
        comment_token = self.extract_comment_token(r.text)
        payload = {'session_token': xsrf_token}
        stats_raw = requests.post(
            'https://www.youtube.com/watch_fragments2_ajax?frags=comments&spf=load&v=' + video_id + '&ctoken=' + comment_token,
            data=payload, cookies=cookies, verify=False)
        return stats_raw.text

    def get_comment_list(self, source_url):
        video_id = source_url.split('v=')[-1]
        print ('get_comment_list')
        comment_list = []
        html_body = json.loads(self.fetch_comments_page(video_id))['body']['watch-discussion']
        tree = lxml.html.fromstring(html_body)
        comment_sections = tree.xpath('//*[@id="comment-section-renderer-items"]/section')
        for inx, each in enumerate(comment_sections):
            # try:
            raw = dict()
            raw['text'] = each.xpath(
                'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-text"]/div[@class="comment-renderer-text-content"]'
            )[0].xpath('string(.)').strip()

            if each.xpath(
                    'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/a | div[1]/div[@class="comment-renderer-content"] \
                                     /div[@class="comment-renderer-header"]/span[@class="comment-renderer-author-comment-badge"]/a ') == []:
                raw['publisher'] = 'zhangsan'
            else:
                raw['publisher'] = each.xpath(
                    'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/a | div[1]/div[@class="comment-renderer-content"] \
                                     /div[@class="comment-renderer-header"]/span[@class="comment-renderer-author-comment-badge"]/a '
                )[0].xpath('string(.)').strip()

            if each.xpath(
                    'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-footer"]/div[@class="comment-action-buttons-toolbar"]/span[@class="comment-renderer-like-count off"]') == []:
                raw['like_count'] = 0
            else:
                raw['like_count'] = int(each.xpath(
                    'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-footer"]/div[@class="comment-action-buttons-toolbar"]/span[@class="comment-renderer-like-count off"]'
                )[0].xpath('string(.)').strip())

            raw_date_string = each.xpath(
                'div[1]/div[@class="comment-renderer-content"]/div[@class="comment-renderer-header"]/span[@class="comment-renderer-time"]/a/text()')
            raw['publish_ts'] = self.time_stamp(raw_date_string)
            if len(raw_date_string) == 1:
                raw['raw_date_string'] = raw_date_string[0]
            raw['order'] = inx
            comment_list.append(raw)
            # except:
            #     self.logger.error('partial parser failed')

        return comment_list

    def time_stamp(self, time_raw):
        time_raw = time_raw[0].split(' ')
        time_modified = ''
        if time_raw[1] == 'weeks' or time_raw[1] == 'week':
            if int(time_raw[0]) == 1:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=1 * 7)
            elif int(time_raw[0]) == 2:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=2 * 7)
            elif int(time_raw[0]) == 3:
                time_modified == datetime.datetime.now() - datetime.timedelta(days=3 * 7)
            elif int(time_raw[0]) == 4:
                time_modified == datetime.datetime.now() - datetime.timedelta(days=4 * 7)
            else:
                self.logger.error('week transfer failed')
        elif time_raw[1] == 'month' or time_raw[1] == 'months':
            if int(time_raw[0]) == 1:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=1 * 30)
            elif int(time_raw[0]) == 2:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=2 * 30)
            elif int(time_raw[0]) == 3:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=3 * 30)
            elif int(time_raw[0]) == 4:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=4 * 30)
            elif int(time_raw[0]) == 5:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=5 * 30)
            elif int(time_raw[0]) == 6:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=6 * 30)
            elif int(time_raw[0]) == 7:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=7 * 30)
            elif int(time_raw[0]) == 8:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=8 * 30)
            elif int(time_raw[0]) == 9:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=9 * 30)
            elif int(time_raw[0]) == 10:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=10 * 30)
            elif int(time_raw[0]) == 11:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=11 * 30)
            else:
                self.logger.error('month transfer failed')
        elif time_raw[1] == 'year' or time_raw[1] == 'years':
            if int(time_raw[0]) == 1:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=1 * 365)
            elif int(time_raw[0]) == 2:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=2 * 365)
            else:
                time_modified = datetime.datetime.now() - datetime.timedelta(days=3 * 365)

        return time_modified

    def get_ts(self, raw_date_string):
        if u'\u6708' in raw_date_string:
            return random.randint(1519702789, 1527392389)
        if u'\u5e74' in raw_date_string:
            return random.randint(1514777989, 1519702789)
        if u'\u9031' in raw_date_string:
            return random.randint(1528171110, 1529553510)

        if u'\u5929' in raw_date_string:
            return random.randint(1529553510, 1529985510)

        return random.randint(1529985510, 1530072078)

    def get_doc_id(self, source_url):
        dedup_key = struct.unpack("<Q", hashlib.md5(source_url.encode('utf8')).digest()[:8])[0]
        return str(dedup_key)

    def fetch_comments(self, source_url):
        doc_id = self.get_doc_id(source_url)
        comment_list = self.get_comment_list(source_url)
        # pprint.pprint(comment_list)
        self.insert_comments(source_url, comment_list)
        self.update_comments(doc_id)
        return doc_id

    def insert_comments(self, source_url, comment_list):
        raw = dict()
        raw['source_url'] = source_url
        raw['doc_id'] = self.get_doc_id(source_url)
        raw['comments_hash_dict'] = dict()
        new_comment_id_list = []
        sent_comment_id_list = []

        for i in self.comment_set.find({"_id": raw['doc_id']}):
            raw['comments_hash_dict'] = i['comments_hash_dict']
            new_comment_id_list = i['new_comment_id_list']
            sent_comment_id_list = i['sent_comment_id_list']

        if comment_list:
            for each in comment_list:
                publisher_hash = int(hashlib.md5(str(each['publisher'].encode('utf8'))).hexdigest(), 16)
                text_hash = int(hashlib.md5(str(each['text'].encode('utf8'))).hexdigest(), 16)
                comment_id = str(int(hashlib.md5("%s%s%s" % (
                    str(publisher_hash), str(text_hash),
                    raw['source_url'])).hexdigest(),
                                     16))[:16]
                if comment_id in sent_comment_id_list or comment_id in new_comment_id_list:
                    continue
                user_id = self.fake_users[publisher_hash % len(self.fake_users)]
                each['user_id'] = user_id
                each['comment_id'] = comment_id
                each['publish_ts'] = self.get_ts(each['raw_date_string'])
                each['has_send'] = False
                raw['comments_hash_dict'][each['comment_id']] = each
                new_comment_id_list.append(each['comment_id'])

            message = dict()
            message['source_url'] = raw['source_url']
            message['doc_id'] = raw['doc_id']
            message['comments_hash_dict'] = raw['comments_hash_dict']
            message['source_name'] = 'youtube'
            message['new_comment_id_list'] = new_comment_id_list
            message['sent_comment_id_list'] = sent_comment_id_list

            self.comment_set.replace_one({'_id': message['doc_id']}, message, True)
            print(json.dumps(message, ensure_ascii=False, sort_keys=True,
                             encoding='utf8').encode('utf8'))

    def update_comments(self, doc_id):
        def send_request(doc_id, user_id, create_time, comment_content, domain='https://www.veeuapp.com'):
            url = '{}/internal/docs/{}/comments?_user_id={}'.format(domain, doc_id, user_id)
            json_body = {
                "create_time": create_time,
                "comment_content": comment_content
            }
            return requests.post(url, json=json_body)

        def text_clean(origin):
            comment_content = origin.replace('\ufeff', '')
            return ''.join([c if len(c.encode('utf-8')) < 4 else '' for c in comment_content])

        for i in self.comment_set.find({"_id": doc_id}):
            index = 0
            doc_id = i['doc_id']
            send_limit = 10 + int(hashlib.md5(str(i['source_url'])).hexdigest(), 16) % 10
            print "send_limit is %d " % send_limit
            if len(i['new_comment_id_list']) == 0:
                continue
            if len(i['sent_comment_id_list']) >= send_limit:
                continue
            comments_hash_dict = i['comments_hash_dict']
            new_comment_id_list = i['new_comment_id_list']
            sent_comment_id_list = i['sent_comment_id_list']

            for index in range(0, len(i['new_comment_id_list'])):
                if len(sent_comment_id_list) >= send_limit:
                    break;
                comment_id = new_comment_id_list[0]
                comment = comments_hash_dict[comment_id]

                create_time = comment['publish_ts']
                comment_content = text_clean(comment['text'])
                if comment_content.strip() == "":
                    print "strip empty"
                    continue
                user_id = comment['user_id']
                response = send_request(doc_id, user_id, create_time, comment_content)
                if response.status_code == 204:
                    index += 1
                    sent_comment_id_list.append(new_comment_id_list.pop(0))
                    comments_hash_dict[comment_id]['has_send'] = True
                    set_path = "comments_hash_dict.%s.has_send" % comment_id
                    self.comment_set.update({"doc_id": str(doc_id)}, {'$set': {set_path: True}})
                else:
                    print response.status_code
                    print("doc_id :%s , send message error" % (doc_id))

            self.comment_set.update({"doc_id": str(doc_id)}, {'$set': {"new_comment_id_list": new_comment_id_list}})
            self.comment_set.update({"doc_id": str(doc_id)}, {'$set': {"sent_comment_id_list": sent_comment_id_list}})

            print("doc_id :%s , sent %d comments" % (doc_id, index))
        pass


if __name__ == '__main__':
    comments = YoutubeCommentUtil()
    doc_id = comments.fetch_comments('https://www.youtube.com/watch?v=QaVybn1NFZ8')
    # comments.update_comments(doc_id)
