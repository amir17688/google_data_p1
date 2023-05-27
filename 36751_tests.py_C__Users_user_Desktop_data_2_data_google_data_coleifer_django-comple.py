import warnings

from django.conf import settings

from completion import constants
from completion.completion_tests.site import *
from completion.completion_tests.utils import *
from completion.completion_tests.db_backend import *

try:
    import redis
except ImportError:
    warnings.warn('Skipping redis backend tests, redis-py not installed')
else:
    if not constants.REDIS_CONNECTION:
        warnings.warn('Skipping redis backend tests, no connection configured')
    else:
        from completion.completion_tests.redis_backend import *

try:
    import pysolr
except ImportError:
    warnings.warn('Skipping solr backend tests, pysolr not installed')
else:
    if not constants.SOLR_CONNECTION:
        warnings.warn('Skipping solr backend tests, no connection configured')
    else:
        from completion.completion_tests.solr_backend import *
