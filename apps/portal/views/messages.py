from django.contrib import messages as django_messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django_q.tasks import async_task

from apps.contact.models import ContactMessage
from apps.portal.mixins import SuperAdminRequiredMixin


class PortalMessageListView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_messages_list.html'

    def get(self, request):
        qs = ContactMessage.objects.all().order_by('-created_at')

        status_filter  = request.GET.get('status', '').strip()
        inquiry_filter = request.GET.get('inquiry_type', '').strip()
        search         = request.GET.get('q', '').strip()

        if status_filter:
            qs = qs.filter(status=status_filter)
        if inquiry_filter:
            qs = qs.filter(inquiry_type=inquiry_filter)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(subject__icontains=search)
            )

        paginator = Paginator(qs, 20)
        page_obj  = paginator.get_page(request.GET.get('page'))

        context = {
            'page_obj':       page_obj,
            'status_filter':  status_filter,
            'inquiry_filter': inquiry_filter,
            'search':         search,
            'new_count':      ContactMessage.objects.filter(status='new').count(),
            'total_count':    ContactMessage.objects.count(),
            'status_choices': ContactMessage.STATUS_CHOICES,
            'inquiry_choices': ContactMessage.INQUIRY_TYPE_CHOICES,
        }
        return render(request, self.template_name, context)


class PortalMessageDetailView(SuperAdminRequiredMixin, View):
    template_name = 'portal/portal_message_detail.html'

    def get(self, request, pk):
        message = get_object_or_404(ContactMessage, pk=pk)

        # Auto-mark as in_progress when first opened if still 'new'
        if message.status == 'new':
            message.status = 'in_progress'
            message.save(update_fields=['status'])

        context = {'message': message}
        return render(request, self.template_name, context)


class PortalMessageReplyView(SuperAdminRequiredMixin, View):
    """
    POST only. Saves reply text into admin_notes and fires the
    send_contact_reply_email task. Does not render its own template —
    always redirects back to the detail page.
    """

    def post(self, request, pk):
        message = get_object_or_404(ContactMessage, pk=pk)
        reply_text = request.POST.get('reply_text', '').strip()

        if not reply_text:
            django_messages.error(
                request,
                _('Reply cannot be empty.')
            )
            return redirect('portal:message_detail', pk=pk)

        # Append reply to admin_notes with timestamp so there's a full
        # audit trail if multiple replies are sent over time
        from django.utils import timezone
        timestamp   = timezone.now().strftime('%d %b %Y %H:%M')
        note_entry  = f'[Reply sent {timestamp}]\n{reply_text}'
        existing    = message.admin_notes or ''
        separator   = '\n\n---\n\n' if existing else ''
        message.admin_notes = existing + separator + note_entry
        message.status      = 'in_progress'
        message.save(update_fields=['admin_notes', 'status'])

        async_task(
            'apps.portal.tasks.send_contact_reply_email',
            message.pk,
            reply_text,
        )

        django_messages.success(
            request,
            _(f'Reply sent to {message.email}.')
        )
        return redirect('portal:message_detail', pk=pk)


class PortalMessageStatusView(SuperAdminRequiredMixin, View):
    """POST only. Updates status field."""

    def post(self, request, pk):
        message    = get_object_or_404(ContactMessage, pk=pk)
        new_status = request.POST.get('status', '').strip()
        valid      = {s for s, _ in ContactMessage.STATUS_CHOICES}

        if new_status not in valid:
            django_messages.error(request, _('Invalid status.'))
            return redirect('portal:message_detail', pk=pk)

        message.status = new_status
        message.save(update_fields=['status'])

        django_messages.success(
            request,
            _(f'Message marked as {message.get_status_display()}.')
        )
        return redirect('portal:message_detail', pk=pk)