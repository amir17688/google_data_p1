#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from djangobmf.workflow import Workflow, State, Transition

from .tasks import calc_account_balance


class TransactionWorkflow(Workflow):
    class States:
        open = State(_(u"Open"), True, delete=False)
        balanced = State(_(u"Balanced"), update=False, delete=False)
        cancelled = State(_(u"Cancelled"), update=False, delete=False)

    class Transitions:
        balance = Transition(_("Balance"), "open", "balanced")
        cancel = Transition(_("Cancel"), "open", "cancelled", validate=False)

    def balance(self):
        if not self.instance.is_balanced():
            raise ValidationError(_('The transaction is not balanced'))

        queryset = self.instance.items.filter(draft=True)

        # we need to excecute the queryset here in oder to get
        # all affected accounts (querysets are lazy)
        update_accounts = list(queryset.distinct().values_list('account_id', flat=True).order_by('account_id'))

        queryset.update(draft=False)

        for item in update_accounts:
            calc_account_balance(item)

        # Update accounts
        self.instance.draft = False
