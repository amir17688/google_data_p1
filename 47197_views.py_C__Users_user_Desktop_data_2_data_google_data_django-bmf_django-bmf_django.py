#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from djangobmf.models import Configuration
from djangobmf.views import ModuleCreateView


class EmployeeCreateView(ModuleCreateView):
    def get_initial(self):
        self.initial.update({
            'product': Configuration.get_setting('bmfcontrib_product', 'default'),
        })
        return super(EmployeeCreateView, self).get_initial()
