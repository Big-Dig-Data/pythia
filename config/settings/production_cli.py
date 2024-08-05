# these are settings tuned up to be used in production for running CLI commands
# most importantly, it disables CACHALOT, which normally messes up with synchronization scripts

from .production import *

if 'cachalot' in INSTALLED_APPS:
    INSTALLED_APPS.remove('cachalot')
