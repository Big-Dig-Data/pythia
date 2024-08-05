from .base import *


# debug toolbar
INSTALLED_APPS += ["debug_toolbar", "django_extensions"]
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'querycount.middleware.QueryCountMiddleware',
]
# debug toolbar
INTERNAL_IPS = ['127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
CACHE_MIDDLEWARE_SECONDS = 1


DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
]

if not DISABLE_CACHALOT:
    DEBUG_TOOLBAR_PANELS.append('cachalot.panels.CachalotPanel')

DEBUG_TOOLBAR_PANELS += [
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]
