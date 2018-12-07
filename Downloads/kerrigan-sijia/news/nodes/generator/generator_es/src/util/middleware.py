from src.util import load_object
import logging


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
                logging.error(str(e))
        return cls(*middlewares)
