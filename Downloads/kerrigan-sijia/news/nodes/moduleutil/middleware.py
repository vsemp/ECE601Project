import logging
from collections import defaultdict
from moduleutil import load_object
from moduleutil.exception import create_traceback_info


logger = logging.getLogger('middleware')


def build_component_list(custom):
    """Compose a component list based on a custom dict of components
    """
    items = (x for x in custom.items() if x[1] is not None)
    return [x[0] for x in sorted(items, key=lambda x:x[1])]


class Middleware(object):

    """Base class for implementing middleware"""

    component_name = 'middleware'

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.methods = defaultdict(list)
        for mw in middlewares:
            self._add_middleware(mw)

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(settings['MIDDLEWARES'])

    @classmethod
    def from_settings(cls, settings):
        mwlist = cls._get_mwlist_from_settings(settings)
        middlewares = []
        for clspath in mwlist:
            try:
                mwcls = load_object(clspath)
                if hasattr(mwcls, 'from_settings'):
                    mw = mwcls.from_settings(settings)
                else:
                    mw = mwcls()
                middlewares.append(mw)
            except Exception as e:
                clsname = clspath.split('.')[-1]
                logger.warning("Disabled %(clsname)s because %(reason)s", {'clsname': clsname, 'reason': str(e)})
        enabled = [x.__class__.__name__ for x in middlewares]
        logger.info("Enabled %(componentname)ss: %(enabledlist)s",
                    {'componentname': cls.component_name,
                     'enabledlist': ', '.join(enabled)})
        return cls(*middlewares)

    def _add_middleware(self, mw):
        if hasattr(mw, 'open'):
            self.methods['open'].append(mw.open)
        if hasattr(mw, 'close'):
            self.methods['close'].insert(0, mw.close)
        if hasattr(mw, 'process_message'):
            self.methods['process_message'].append(mw.process_message)
        if hasattr(mw, 'process_exception'):
            self.methods['process_exception'].insert(0, mw.process_exception)

    def open(self, module):
        for method in self.methods['open']:
            method(module)

    def close(self, module):
        for method in self.methods['close']:
            method(module)

    def process_message(self, message, module):
        """
        if process_message returns None: message is passed to next middleware
        elif it returns a message: that message is rescheduled to the head of middleware
        """
        message_cls = message.__class__
        for method in self.methods['process_message']:
            ret = method(message=message, module=module)
            assert ret is None or isinstance(ret, message_cls), \
                'Middleware %s.process_message must return None or %s, got %s' % \
                (method.im_self.__class__.__name__, message_cls.__name__, ret.__class__.__name__)
            if ret:
                return ret
        return None

    def process_exception(self, message, exception, module):
        """
        if process_exception returns None: message is dropped
        elif it returns a message: that message is rescheduled to the head of middleware
        """
        logger.error(create_traceback_info(str(exception)))
        message_cls = message.__class__
        for method in self.methods['process_exception']:
            ret = method(message=message, exception=exception, module=module)
            assert ret is None or isinstance(ret, message_cls), \
                'Middleware %s.process_exception must return None or %s, got %s' % \
                (method.im_self.__class__.__name__, message_cls.__name__, ret.__class__.__name__)
            if ret:
                return ret
        return None
