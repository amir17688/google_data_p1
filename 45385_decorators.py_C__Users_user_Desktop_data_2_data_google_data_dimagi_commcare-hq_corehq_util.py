from celery.task import task
from functools import wraps
import logging
import requests
from corehq.toggles import NAMESPACE_DOMAIN
from corehq.util.global_request import get_request
from dimagi.utils.couch.cache.cache_core import get_redis_client
from dimagi.utils.logging import notify_exception
from django.conf import settings
from toggle.shortcuts import update_toggle_cache, clear_toggle_cache


class ContextDecorator(object):
    """
    A base class that enables a context manager to also be used as a decorator.
    https://docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator
    """
    def __call__(self, fn):
        @wraps(fn)
        def decorated(*args, **kwds):
            with self:
                return fn(*args, **kwds)
        return decorated


def handle_uncaught_exceptions(mail_admins=True):
    """Decorator to log uncaught exceptions and prevent them from
    bubbling up the call chain.
    """
    def _outer(fn):
        @wraps(fn)
        def _handle_exceptions(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                msg = "Uncaught exception from {}.{}".format(fn.__module__, fn.__name__)
                if mail_admins:
                    notify_exception(get_request(), msg)
                else:
                    logging.exception(msg)

        return _handle_exceptions
    return _outer


class change_log_level(ContextDecorator):
    """
    Temporarily change the log level of a specific logger.
    Can be used as either a context manager or decorator.
    """
    def __init__(self, logger, level):
        self.logger = logging.getLogger(logger)
        self.new_level = level
        self.original_level = self.logger.level

    def __enter__(self):
        self.logger.setLevel(self.new_level)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


class require_debug_true(ContextDecorator):
    def __enter__(self):
        if not settings.DEBUG:
            raise Exception("This can only be called in DEBUG mode.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CouldNotAqcuireLock(Exception):
    pass


# Sorry this is so magic
def _get_unique_key(format_str, fn, *args, **kwargs):
    """
    Lines args and kwargs up with those specified in the definition of fn and
    passes the result to `format_str.format()`.
    """
    varnames = fn.func_code.co_varnames
    kwargs.update(dict(zip(varnames, args)))
    return ("{}-" + format_str).format(fn.__name__, **kwargs)


def serial_task(unique_key, default_retry_delay=30, timeout=5*60, max_retries=3,
                queue='background_queue'):
    """
    Define a task to be executed one at a time.  If another serial_task with
    the same unique_key is currently in process, this will retry after a delay.

    :param unique_key: string used to lock the task.  There will be one lock
        per unique value.  You may use any arguments that will be passed to the
        function.  See example.
    :param default_retry_delay: seconds to wait before retrying if a lock is
        encountered
    :param timeout: timeout on the lock (in seconds).  Normally the lock should
        be released when the task completes, but you should also define a
        timeout in case something goes wrong.  This must be greater than the
        maximum length of the task.

    Usage:
        @serial_task("{user.username}-{from}", default_retry_delay=2)
        def greet(user, from="Dimagi"):
            ...

        greet.delay(joeshmoe)
        # Locking key used would be "greet-joeshmoe@test.commcarehq.org-Dimagi"
    """
    def decorator(fn):
        # register task with celery.  Note that this still happens on import
        @task(bind=True, queue=queue, ignore_result=True,
              default_retry_delay=default_retry_delay, max_retries=max_retries)
        @wraps(fn)
        def _inner(self, *args, **kwargs):
            if settings.UNIT_TESTING:  # Don't depend on redis
                fn(*args, **kwargs)
                return

            client = get_redis_client()
            key = _get_unique_key(unique_key, fn, *args, **kwargs)
            lock = client.lock(key, timeout=timeout)
            if lock.acquire(blocking=False):
                try:
                    # Actually call the function
                    fn(*args, **kwargs)
                except Exception:
                    # Don't leave the lock around if the task fails
                    lock.release()
                    raise
                lock.release()
            else:
                msg = "Could not aquire lock '{}' for task '{}'.".format(
                    key, fn.__name__)
                self.retry(exc=CouldNotAqcuireLock(msg))
        return _inner
    return decorator


def analytics_task(default_retry_delay=10, max_retries=3, queue='background_queue'):
    '''
        defines a task that posts data to one of our analytics endpoints. It retries the task
        up to 3 times if the post returns with a status code indicating an error with the post
        that is not our fault.
    '''
    def decorator(func):
        @task(bind=True, queue=queue, ignore_result=True, acks_late=True,
              default_retry_delay=default_retry_delay, max_retries=max_retries)
        @wraps(func)
        def _inner(self, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                # if its a bad request, raise the exception because it is our fault
                res = e.response
                status_code = res.status_code if isinstance(res, requests.models.Response) else res.status
                if status_code == 400:
                    raise
                else:
                    self.retry(exc=e)
        return _inner
    return decorator


class temporarily_enable_toggle(ContextDecorator):

    def __init__(self, toggle, item, namespace=NAMESPACE_DOMAIN):
        self.toggle_slug = toggle.slug
        self.item = item
        self.namespace = namespace

    def __enter__(self):
        update_toggle_cache(self.toggle_slug, self.item, True, namespace=self.namespace)

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_toggle_cache(self.toggle_slug, self.item, self.namespace)
