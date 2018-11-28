import redis

e03_redis_server = redis.Redis('192.168.173.130', 7664, 4)
crawl01_redis_server = redis.Redis('localhost', 7664, 4)
crawled_list = list(e03_redis_server.hgetall('feeds_crawled_source_url'))

index = 0
for each in crawled_list[10:]:
    fingerprint = "d41d8cd98f00b204e9800998ecf8427e"
    crawl01_redis_server.hset('feeds_crawled_source_url', each, fingerprint)
    index += 1
    if index % 100 == 0:
        print index
