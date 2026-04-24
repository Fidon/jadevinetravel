from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def format_email_subject(self, subject):
        import re
        return re.sub(r'^\[.*?\]\s*', '', subject)

    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        suppress = (
            'account/messages/logged_out.txt',
            'account/messages/email_confirmation_sent.txt',
            'account/messages/logged_in.txt',
        )
        if message_template in suppress:
            return
        super().add_message(request, level, message_template, message_context, extra_tags)

    def get_logout_redirect_url(self, request):
        return '/'

    def render_mail(self, template_prefix, email, context, headers=None):
        subject = render_to_string(
            f'{template_prefix}_subject.txt', context
        ).strip().replace('\n', '').replace('\r', '')

        subject = self.format_email_subject(subject)

        request = getattr(self, 'request', None)

        bodies = {}
        for ext in ('html', 'txt'):
            template_name = f'{template_prefix}_message.{ext}'
            try:
                if request is not None:
                    bodies[ext] = render_to_string(
                        template_name, context, request=request
                    ).strip()
                else:
                    bodies[ext] = render_to_string(
                        template_name, context
                    ).strip()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f'Failed to render email template {template_name}: {e}'
                )

        if 'txt' not in bodies:
            raise RuntimeError(
                f'Missing plain text template: {template_prefix}_message.txt'
            )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=bodies['txt'],
            from_email=self.get_from_email(),
            to=[email],
            headers=headers or {},
        )

        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')

        return msg

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.first_name = form.cleaned_data.get('first_name', '')
        user.last_name = form.cleaned_data.get('last_name', '')
        user.preferred_language = form.cleaned_data.get('preferred_language', 'en')
        if commit:
            user.save()
        return user