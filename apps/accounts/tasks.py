from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _
from apps.bookings.models import Booking

ADMIN_EMAIL = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', settings.DEFAULT_FROM_EMAIL)

def _get_booking(booking_id):
    return Booking.objects.select_related(
        'user', 'hotel', 'tour_package', 'car'
    ).get(pk=booking_id)


def _service_name(booking):
    if booking.service_type == 'hotel' and booking.hotel:
        return booking.hotel.name
    if booking.service_type == 'tour' and booking.tour_package:
        return booking.tour_package.name_en
    if booking.service_type == 'car' and booking.car:
        return booking.car.name
    return booking.get_service_type_display()


def _send_html_email(subject, to_email, txt_body, html_body):
    msg = EmailMultiAlternatives(
        subject=subject,
        body=txt_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)


def send_cancellation_requested_customer_email(booking_id, refund_info):
    booking = _get_booking(booking_id)
    refund_pct = refund_info.get('refund_percentage', 0)
    refund_amt = refund_info.get('refund_amount', 0)

    subject = f'Cancellation Request Received — {booking.reference}'

    context = {
        'first_name': booking.user.first_name or booking.user.email,
        'reference': booking.reference,
        'service_name': _service_name(booking),
        'payment_mode': booking.get_payment_mode_display(),
        'currency': booking.currency,
        'refund_pct': refund_pct,
        'refund_amount': f'{refund_amt:.2f}',
    }

    txt = (
        f'Dear {context["first_name"]},\n\n'
        f'Your cancellation request for {booking.reference} has been received.\n'
        f'Refund: {booking.currency} {refund_amt:.2f} ({refund_pct}%)\n'
        f'We will process within 2-3 business days.\n\n'
        f'Jadevine Travel & Tours'
    )
    html = render_to_string(
        'account/email/cancellation_requested_customer_message.html', context
    )
    _send_html_email(subject, booking.user.email, txt, html)


def send_cancellation_requested_admin_email(booking_id, refund_info):
    booking = _get_booking(booking_id)
    refund_amt = refund_info.get('refund_amount', 0)
    refund_pct = refund_info.get('refund_percentage', 0)

    subject = f'[ACTION REQUIRED] Cancellation & Refund — {booking.reference}'

    context = {
        'reference': booking.reference,
        'customer_name': booking.user.get_full_name() or booking.user.email,
        'customer_email': booking.user.email,
        'service_name': _service_name(booking),
        'currency': booking.currency,
        'total': f'{booking.total_price:.2f}',
        'refund_pct': refund_pct,
        'refund_amount': f'{refund_amt:.2f}',
        'reason': booking.cancellation_reason or 'Not provided',
        'payment_mode': booking.get_payment_mode_display(),
        'portal_url': f'/portal/bookings/{booking.id}/',
        'is_pay_now': True,
    }

    txt = (
        f'ACTION REQUIRED: {booking.reference}\n'
        f'Customer: {context["customer_name"]} ({context["customer_email"]})\n'
        f'Refund: {booking.currency} {refund_amt:.2f} ({refund_pct}%)\n'
        f'Reason: {context["reason"]}\n'
        f'Process refund via PesaPal then mark as refunded in portal.'
    )
    html = render_to_string(
        'account/email/cancellation_admin_message.html', context
    )
    _send_html_email(subject, ADMIN_EMAIL, txt, html)


def send_cancellation_confirmed_customer_email(booking_id, refund_info):
    booking = _get_booking(booking_id)
    refund_pct = refund_info.get('refund_percentage', 0) if refund_info else 0

    subject = f'Booking Cancelled — {booking.reference}'

    context = {
        'first_name': booking.user.first_name or booking.user.email,
        'reference': booking.reference,
        'service_name': _service_name(booking),
        'payment_mode': booking.get_payment_mode_display(),
        'no_refund': refund_pct == 0,
    }

    txt = (
        f'Dear {context["first_name"]},\n\n'
        f'Your booking {booking.reference} has been cancelled.\n'
        + ('No refund applies per our cancellation policy.\n\n' if refund_pct == 0 else '\n')
        + 'Jadevine Travel & Tours'
    )
    html = render_to_string(
        'account/email/cancellation_confirmed_customer_message.html', context
    )
    _send_html_email(subject, booking.user.email, txt, html)


def send_cancellation_confirmed_admin_email(booking_id, refund_info):
    booking = _get_booking(booking_id)

    subject = f'Booking Cancelled (No Action Required) — {booking.reference}'

    context = {
        'reference': booking.reference,
        'customer_name': booking.user.get_full_name() or booking.user.email,
        'customer_email': booking.user.email,
        'service_name': _service_name(booking),
        'payment_mode': booking.get_payment_mode_display(),
        'reason': booking.cancellation_reason or 'Not provided',
        'is_pay_now': False,
    }

    txt = (
        f'Booking {booking.reference} cancelled by customer.\n'
        f'Customer: {context["customer_name"]}\n'
        f'Service: {context["service_name"]}\n'
        f'No refund action required.'
    )
    html = render_to_string(
        'account/email/cancellation_admin_message.html', context
    )
    _send_html_email(subject, ADMIN_EMAIL, txt, html)
    

def cleanup_unverified_accounts():
    """
    Deletes CustomUser accounts that:
    - Have is_active=False (never verified email)
    - Were created more than 7 days ago
    - Have no bookings (safety guard)

    Run via Django-Q scheduled task. Recommended schedule: daily.

    Why 7 days not 3? The verification link expires in 3 days, but we give
    the user 4 extra days to notice and use the resend feature before we
    delete their account. This is generous without polluting the DB forever.
    """
    from datetime import timedelta
    from django.utils import timezone
    from django.contrib.auth import get_user_model
    from allauth.account.models import EmailAddress

    User = get_user_model()
    cutoff = timezone.now() - timedelta(days=7)

    # Find unverified users older than cutoff
    unverified_emails = EmailAddress.objects.filter(
        verified=False,
        user__is_active=False,
        user__date_joined__lt=cutoff,
        user__is_staff=False,  # never touch staff accounts
    ).select_related('user')

    deleted_count = 0
    for email_record in unverified_emails:
        user = email_record.user
        # Safety guard: never delete a user who has any bookings
        if user.bookings.exists():
            continue
        user.delete()  # cascades to EmailAddress via OneToOne
        deleted_count += 1

    return f'Cleaned up {deleted_count} unverified accounts older than 7 days.'
