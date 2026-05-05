from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task

from apps.contact.models import ContactMessage, NewsletterSubscriber


class ContactView(View):
    template_name = 'contact/contact.html'

    def get(self, request):
        from django.shortcuts import render
        return render(request, self.template_name)

    def post(self, request):
        from django.shortcuts import render
        data = request.POST

        name         = data.get('name', '').strip()
        email        = data.get('email', '').strip().lower()
        phone        = data.get('phone', '').strip() or None
        subject      = data.get('subject', '').strip()
        message_text = data.get('message', '').strip()
        inquiry_type = data.get('inquiry_type', 'general').strip()
        preferred_lang = data.get('preferred_lang', 'en').strip()

        errors = {}
        if not name:
            errors['name'] = str(_('Name is required.'))
        if not email or '@' not in email:
            errors['email'] = str(_('A valid email address is required.'))
        if not subject:
            errors['subject'] = str(_('Subject is required.'))
        if not message_text or len(message_text) < 10:
            errors['message'] = str(
                _('Message must be at least 10 characters.')
            )

        valid_inquiry_types = {'general', 'custom_tour', 'partnership', 'press'}
        if inquiry_type not in valid_inquiry_types:
            inquiry_type = 'general'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        msg = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text,
            inquiry_type=inquiry_type,
            preferred_lang=preferred_lang,
            status='new',
        )

        # Queue emails — both fire asynchronously so the POST returns fast
        async_task(
            'apps.contact.tasks.send_contact_acknowledgement_customer',
            msg.pk
        )
        async_task(
            'apps.contact.tasks.send_contact_notification_admin',
            msg.pk
        )

        return JsonResponse({
            'success': True,
            'message': str(
                _('Thank you for your message! We will respond within 24 hours.')
            ),
        })


class NewsletterSubscribeView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '').strip().lower()

        if not email or '@' not in email:
            return JsonResponse({
                'success': False,
                'error': str(_('Please enter a valid email address.'))
            })

        obj, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )

        if not created:
            if obj.is_active:
                return JsonResponse({
                    'success': False,
                    'error': str(_('This email is already subscribed.'))
                })
            else:
                obj.is_active = True
                obj.save(update_fields=['is_active'])

        return JsonResponse({
            'success': True,
            'message': str(
                _("Thank you for subscribing! We'll be in touch soon.")
            ),
        })