import pymongo
from pymongo import MongoClient
import requests
import logging
import random
import hashlib

if __name__ == '__main__':
    conn = MongoClient(
        'gct-storage01.uscasv2.cootek.com:27017,gct-storage02.uscasv2.cootek.com:27017,gct-storage03.uscasv2.cootek.com:27017',
        readPreference="primary")
    my_set = conn['comments']['crawled_comments']

    hash_value = 2

    def send_request(doc_id, user_id, create_time, comment_content, domain='https://www.veeuapp.com'):
        url = '{}/internal/docs/{}/comments?_user_id={}'.format(domain, doc_id, user_id)
        json_body = {
            "create_time": create_time,
            "comment_content": comment_content
        }
        return requests.post(url,json=json_body)


    def text_clean(origin):
        comment_content = origin.replace('\ufeff', '')
        return ''.join([c if len(c.encode('utf-8')) < 4 else '' for c in comment_content])


    # r = requests.get('https://www.veeuapp.com/content/feeds?page_type=channel&id=c_1&history=false&count=10000')
    # doc_list = r.json()['doc_list']
    # doc_url_list = []
    # for each in doc_list:
    #     doc_url_list.append(each['doc_id'])
    # print(len(doc_list))

    for i in my_set.find({"source_name": "buzzvideo"}):
        # if i['doc_id'] not in doc_url_list:
        #     continue
        source_hash = int(hashlib.md5(str(i['doc_id'])).hexdigest(), 16)
        if source_hash % 4 != hash_value:
            continue
        else:
            pass

        index = 0
        doc_id = i['doc_id']
        send_limit =10 + int(hashlib.md5(str(i['source_url'])).hexdigest(), 16) % 10
        print "send_limit is %d " % send_limit
        if len(i['new_comment_id_list']) == 0:
            continue
        if len(i['sent_comment_id_list']) >= send_limit:
            continue
        comments_hash_dict = i['comments_hash_dict']
        new_comment_id_list = i['new_comment_id_list']
        sent_comment_id_list = i['sent_comment_id_list']

        for each in i['new_comment_id_list']:
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
                my_set.update({"doc_id": str(doc_id)}, {'$set': {set_path: True}})
            else:
                print response.status_code
                print("doc_id :%s , send message error" % (doc_id))

        my_set.update({"doc_id": str(doc_id)}, {'$set': {"new_comment_id_list": new_comment_id_list}})
        my_set.update({"doc_id": str(doc_id)}, {'$set': {"sent_comment_id_list": sent_comment_id_list}})

        print("doc_id :%s , sent %d comments" % (doc_id, index))
