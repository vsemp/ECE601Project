from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from src.util import load_settings
from src.util.log import configure_logging
from src.util.middleware import Middleware
from kafka import SimpleProducer, KafkaClient
import logging
import json

logging.getLogger('py4j').setLevel(logging.ERROR)


def Send2Kafka(messages):
    kclient = None
    producer = None
    for message in messages:
        if not kclient:
            kclient = KafkaClient(broker)
            producer = SimpleProducer(kclient, async=True)
        try:
            producer.send_messages(dst_topic, message)
            pubdate = json.loads(message)['pubdate']
            open('/pixdata/data/news/uploader_%s' % pubdate, 'a').write(message + '\n')
        except:
            pass
    if producer:
        producer.stop()
    return messages

if __name__ == "__main__":
    conf = SparkConf()
    conf.setAppName('generator')
    conf.set('spark.streaming.kafka.maxRatePerPartition', 200)
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 10)
    settings = load_settings('src.settings')
    configure_logging(settings)
    broker = settings['BROKERS']
    src_topic = settings['SRC_TOPIC']
    dst_topic = settings['DST_TOPIC']
    mw = Middleware.from_settings(settings)
    kafkaParams = {
        'metadata.broker.list': broker,
    }
    kvs = KafkaUtils.createDirectStream(ssc, [src_topic], kafkaParams)
    stream = kvs.map(lambda x: x[1])
    for middleware in mw.middlewares:
        stream = getattr(stream, middleware.api)(middleware.process)
    stream.foreachRDD(lambda rdd: rdd.foreachPartition(Send2Kafka))
    ssc.start()
    ssc.awaitTermination()
