import os
import imp
import importlib

from django.conf import settings

_RACE_PROTECTION = False

"""
Import any app's consumers.py file so that consumers registered by user are 
discovered. This is lifted almost entirely from djcelery's 
[loaders module](https://github.com/celery/django-celery/blob/master/djcelery/loaders.py).
"""

class ConsumerManager(object):
    def __init__(self):
        self.consumers = set()

    def autodiscover(self):
        self.consumers.update(mod.__name__ for mod in autodiscover() or ())


def autodiscover():
    """Include tasks for all applications in ``INSTALLED_APPS``."""
    global _RACE_PROTECTION

    if _RACE_PROTECTION:
        return
    _RACE_PROTECTION = True
    try:
        return filter(None, [find_related_module(app, 'consumers')
                                for app in settings.INSTALLED_APPS])
    finally:
        _RACE_PROTECTION = False



def find_related_module(app, related_name):
    """Given an application name and a module name, tries to find that
    module in the application."""

    try:
        app_path = importlib.import_module(app).__path__
    except AttributeError:
        return

    try:
        imp.find_module(related_name, app_path)
    except ImportError:
        return

    return importlib.import_module('{0}.{1}'.format(app, related_name))