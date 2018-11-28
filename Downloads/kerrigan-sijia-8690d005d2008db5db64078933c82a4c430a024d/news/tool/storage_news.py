import json
import sys
import datetime

delta = int(sys.argv[1])
day = str(datetime.date.today() - datetime.timedelta(days=delta))

input_file = '/pixdata/data/news/newsfeeds_%s' % day
output_file = '/pixdata/data/news/storage/newsfeeds_%s' % day

source = dict()
for line in open(input_file):
    data = json.loads(line)
    if 'raw' in data:
        data.pop('raw')
    account = data['account']
    source[account] = data

fo = open(output_file, 'w')
for data in source:
    fo.write(
        json.dumps(source[data], ensure_ascii=False).encode('utf8') + '\n')
fo.close()
