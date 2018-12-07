import os.path
import unittest
from kafka import KafkaConsumer
from execute import Generator, IgnoreMessage
from src.util import load_settings


def record_message(ceil_limit, message_path):
    group_id = 'script'
    brokers = 'data-kafka01:9092,data-kafka02:9092,data-kafka03:9092'
    src_topic = 'feedsgenerator'
    consumer = KafkaConsumer(src_topic, group_id=group_id, bootstrap_servers=brokers)

    limit = 0
    for message in consumer:
        with open(message_path, 'a') as f:
            f.write(message.value + '\n')
            limit += 1
            print("ceil_limit :" + str(ceil_limit) +
                  " getting :" + str(limit))
            if limit >= ceil_limit:
                return


class Test(unittest.TestCase):
    def setUp(self):
        self.MESSAGES_PATH = "resources/test_messages.log"
        self.MESSAGE_PATH = 'resources/test_message.log'
        self.generator = Generator(load_settings('settings'))
        if not os.path.isfile(self.MESSAGES_PATH):
            record_message(2000, self.MESSAGES_PATH)

    def test_generator(self):
        for message in open(self.MESSAGES_PATH):
            self.generator.process_throughout(message)

    def test_one_message(self):
        if os.path.isfile(self.MESSAGE_PATH):
            with open(self.MESSAGE_PATH) as f:
                message = f.readline()
                generator = self.generator
                for middleware in generator.mw.middlewares:
                    api = middleware.api
                    handler = getattr(generator, api)
                    try:
                        message = handler(middleware, message)
                        if message:
                            print(str(middleware.__class__.__name__))
                            print(message)
                    except IgnoreMessage:
                        return


if __name__ == '__main__':
    unittest.main()
