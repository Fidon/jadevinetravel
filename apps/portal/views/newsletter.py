from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.contact.models import NewsletterSubscriber
from apps.portal.mixins import SuperAdminRequiredMixin


class PortalNewsletterView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_newsletter.html'

    def get(self, request):
        subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
        context = {
            'subscribers':    subscribers,
            'total_count':    subscribers.count(),
            'active_count':   subscribers.filter(is_active=True).count(),
            'inactive_count': subscribers.filter(is_active=False).count(),
        }
        return render(request, self.template_name, context)


class PortalNewsletterToggleView(SuperAdminRequiredMixin, View):
    """POST only. Toggles is_active on a single subscriber."""

    def post(self, request, pk):
        subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
        subscriber.is_active = not subscriber.is_active
        subscriber.save(update_fields=['is_active'])

        action = _('reactivated') if subscriber.is_active else _('unsubscribed')
        messages.success(
            request,
            _(f'{subscriber.email} has been {action}.')
        )
        return redirect('portal:newsletter')