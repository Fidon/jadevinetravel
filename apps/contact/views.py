from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from .models import NewsletterSubscriber


class ContactView(TemplateView):
    template_name = 'contact/contact.html'


class NewsletterSubscribeView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '').strip().lower()

        if not email or '@' not in email:
            return JsonResponse({'success': False, 'error': 'Please enter a valid email address.'})

        obj, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )

        if not created:
            if obj.is_active:
                return JsonResponse({'success': False, 'error': 'This email is already subscribed.'})
            else:
                obj.is_active = True
                obj.save()

        return JsonResponse({
            'success': True,
            'message': 'Thank you for subscribing! We\'ll be in touch soon.'
        })