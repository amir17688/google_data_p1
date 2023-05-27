#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.core.mail.message import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import activate
from django.utils.translation import get_language


class EmailMessage(EmailMultiAlternatives):

    def __init__(self, *args, **kwargs):

        template_base = kwargs.pop('template_base', None)
        if template_base:
            templates = {
                'subject': template_base + '.subject',
                'plain': template_base + '.plain',
                'html': template_base + '.html',
            }
            for key, value in templates.items():
                try:
                    templates[key] = get_template(value)
                except TemplateDoesNotExist:
                    templates[key] = None
        else:
            templates = {}

        language = kwargs.pop('language', None)
        old_language = get_language()
        if language:
            activate(language)

        context = kwargs.pop('context', {})

        super(EmailMessage, self).__init__(*args, **kwargs)

        if 'body' not in context:
            context['body'] = self.body
        if 'subject' not in context:
            context['subject'] = self.subject

        if 'subject' in templates and templates['subject']:
            self.subject = templates['subject'].render(context).strip()

        if 'plain' in templates and templates['plain']:
            self.body = templates['plain'].render(context).strip()

        if 'html' in templates and templates['html']:
            html = templates['html'].render(context).strip()
            if html:
                if not self.body:
                    self.content_subtype = "html"
                    self.body = html
                else:
                    self.attach_alternative(html, "text/html")

        # change back to old language
        activate(old_language)
