# Copyright (c) 2016, DjaoDjin inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from stripe.error import APIConnectionError as ProcessorConnectionError
from stripe.error import StripeError as ProcessorError
from stripe.error import CardError as BaseCardError

from .. import settings


class CardError(BaseCardError):

    def __unicode__(self):
        if self.code == 'card_declined':
            return "Your card was declined. We are taking your security"\
" seriously. When we submit a charge to your bank, they have automated"\
" systems that determine whether or not to accept the charge. Check you"\
" entered the card  number, expiration date, CVC and address correctly."\
" If problems persist, please contact your bank."
        return self._message

    def processor_details(self):
        return super(CardError, self).__unicode__()


def load_backend(path):
    dot_pos = path.rfind('.')
    module, attr = path[:dot_pos], path[dot_pos + 1:]
    try:
        mod = import_module(module)
    except (ImportError, ValueError)  as err:
        raise ImproperlyConfigured(
            'Error importing backend %s: "%s"' % (path, err))
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s"'\
' backend' % (module, attr))
    return cls()


def get_processor_backend(provider):
    if settings.PROCESSOR_BACKEND_CALLABLE:
        from saas.compat import import_string
        func = import_string(settings.PROCESSOR_BACKEND_CALLABLE)
        processor_backend = func(provider)
    else:
        processor_backend = load_backend(
            'saas.backends.stripe_processor.StripeBackend')
    return processor_backend
