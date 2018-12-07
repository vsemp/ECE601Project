from moduleutil.exception import IgnoreMessage
import logging
from moduleutil.middleware import Middleware


class MessageStream(object):

    def __init__(self, settings, module):
        self.settings = settings
        self.middleware = Middleware.from_settings(settings)
        self.logger = logging.getLogger('stream')
        self.module = module

    def open(self):
        self.middleware.open(self.module)

    def close(self):
        self.middleware.close(self.module)

    def process_message_in_middleware(self, message):
        """
        return None: message is dropped
        return message: that message is fully processed
        """
        message_cls = message.__class__
        try:
            ret = self.middleware.process_message(message, self.module)
        except IgnoreMessage:
            return None
        except Exception as e:
            return self.process_exception_in_middleware(message, e)
        else:
            if ret is None:
                return message
            elif isinstance(ret, message_cls):
                return self.process_message_in_middleware(ret)

    def process_exception_in_middleware(self, message, exception):
        """
        trigger when any unpredictable exception happens in process_message_in_middleware
        return None: message is dropped
        return message: that message is fully processed
        """
        message_cls = message.__class__
        try:
            ret = self.middleware.process_exception(message, exception, self.module)
        except Exception as e:  # exception occurs in process_exception will be ignored
            self.logger.error(str(e))
            return None
        else:
            if ret is None:
                return None
            elif isinstance(ret, message_cls):
                return self.process_message_in_middleware(ret)

    def process(self, message):
        processed_message = self.process_message_in_middleware(message)
        if processed_message is None:
            self.logger.debug('Message dropped: %s' % message)
            return None
        else:
            return processed_message


class NewsFeedsStream(MessageStream):

    def __init__(self, *a, **kw):
        super(NewsFeedsStream, self).__init__(*a, **kw)
