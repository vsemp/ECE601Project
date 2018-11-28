from importlib import import_module


def load_settings(settings_module_path):
    settings = {}
    module = import_module(settings_module_path)
    for key in dir(module):
        if key.isupper():
            settings[key] = getattr(module, key)
    return settings

def load_object(path):
    """Load an object given its absolute object path, and return it.
    object can be a class, function, variable o instance.
    path ie: 'middlewares.release.PatchMiddleware'
    """
    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)
    module, name = path[:dot], path[dot+1:]
    mod = import_module(module)
    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))
    return obj