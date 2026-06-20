from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def _get_booking(booking_id):
    """
    Centralised booking fetch with all related objects needed for email rendering.
    Used by every task in this file — never repeat this query inline.
    """
    from apps.bookings.models import Booking
    return Booking.objects.select_related(
        'user', 'hotel', 'room_type', 'tour_package', 'car'
    ).get(pk=booking_id)


def _service_label(booking):
    """Human-readable service name for email subjects and body."""
    if booking.service_type == 'hotel' and booking.hotel:
        return booking.hotel.name
    if booking.service_type == 'tour' and booking.tour_package:
        return booking.tour_package.get_name('en')
    if booking.service_type == 'car' and booking.car:
        return booking.car.name
    return booking.get_service_type_display()


def _send(subject, text_body, html_body, recipient):
    """
    Single send helper — keeps every task DRY.
    Uses EmailMultiAlternatives so the email has both a plain-text fallback
    and an HTML version. Gmail and most clients will render the HTML version.
    fail_silently=True: a broken email must never crash a booking confirmation.
    """
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)


# ---------------------------------------------------------------------------
# Pay on Arrival — Customer Confirmation
# ---------------------------------------------------------------------------
def send_poa_booking_confirmation_customer(booking_id):
    """
    Sent to the customer immediately after a Pay on Arrival booking is confirmed.
    Contains full booking details and payment instructions for arrival.

    Called by: BookingSummaryView.post() via django_q.tasks.async_task()
    NOT called for Pay Now — that confirmation is sent in Phase 6 after PesaPal IPN.
    """
    booking = _get_booking(booking_id)
    user = booking.user
    name = user.first_name or user.email
    service = _service_label(booking)

    # ── Build service-specific detail block ──────────────────────────────────
    if booking.service_type == 'hotel':
        detail_rows = f"""
        <tr>
          <td class="detail-label">Room Type</td>
          <td class="detail-value">{booking.room_type.name if booking.room_type else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Check-in</td>
          <td class="detail-value">{booking.check_in_date.strftime('%d %B %Y') if booking.check_in_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Check-out</td>
          <td class="detail-value">{booking.check_out_date.strftime('%d %B %Y') if booking.check_out_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Duration</td>
          <td class="detail-value">{booking.nights} night(s)</td>
        </tr>
        <tr>
          <td class="detail-label">Guests</td>
          <td class="detail-value">{booking.num_guests}</td>
        </tr>
        """
    elif booking.service_type == 'car':
        rental_mode = 'Self Drive' if booking.rental_mode == 'self_drive' else 'With Driver'
        detail_rows = f"""
        <tr>
          <td class="detail-label">Pickup Location</td>
          <td class="detail-value">{booking.pickup_location or '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Rental Mode</td>
          <td class="detail-value">{rental_mode}</td>
        </tr>
        <tr>
          <td class="detail-label">Pickup Date</td>
          <td class="detail-value">{booking.pickup_date.strftime('%d %B %Y') if booking.pickup_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Return Date</td>
          <td class="detail-value">{booking.return_date.strftime('%d %B %Y') if booking.return_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Duration</td>
          <td class="detail-value">{booking.num_days} day(s)</td>
        </tr>
        """
    elif booking.service_type == 'tour':
        detail_rows = f"""
        <tr>
          <td class="detail-label">Preferred Start Date</td>
          <td class="detail-value">{booking.preferred_date.strftime('%d %B %Y') if booking.preferred_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Participants</td>
          <td class="detail-value">{booking.num_participants}</td>
        </tr>
        <tr>
          <td class="detail-label">Duration</td>
          <td class="detail-value">{booking.tour_package.duration_days} day(s)</td>
        </tr>
        """
    else:
        detail_rows = ''

    special_requests_row = (
        f"""
        <tr>
          <td class="detail-label">Special Requests</td>
          <td class="detail-value">{booking.special_requests}</td>
        </tr>
        """
        if booking.special_requests else ''
    )

    # Tours need a date-confirmation notice
    tour_notice = ''
    if booking.service_type == 'tour':
        tour_notice = """
        <div style="background:#eaf4fb;border:1px solid #2471a3;border-radius:8px;
                    padding:14px 18px;margin-bottom:24px;font-size:14px;color:#2471a3;">
          <strong>📅 Date Confirmation</strong><br>
          Our team will confirm your preferred start date within <strong>24–48 hours</strong>.
          You will receive a follow-up email once the date is confirmed.
        </div>
        """

    subject = f'Booking Confirmed — {booking.reference} | Jadevine Travel & Tours'

    text_body = (
        f'Dear {name},\n\n'
        f'Your booking is confirmed!\n\n'
        f'Reference: {booking.reference}\n'
        f'Service: {service}\n'
        f'Total: {booking.currency} {booking.total_price}\n'
        f'Payment: Pay on Arrival\n\n'
        f'Please bring the full amount of {booking.currency} {booking.total_price} '
        f'when you arrive in Tanzania.\n\n'
        f'Thank you for choosing Jadevine Travel & Tours.\n'
        f'For questions, WhatsApp us or email info@jadevinetours.com\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Booking Confirmed — {booking.reference}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f5f0; color: #1e1e1e; }}
    .email-wrapper {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
    .email-header {{ background-color: #1a4d2e; padding: 36px 40px; text-align: center; }}
    .brand-name {{ font-size: 26px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px; }}
    .brand-tagline {{ font-size: 12px; color: #c89666; text-transform: uppercase; letter-spacing: 2px; margin-top: 4px; }}
    .email-body {{ padding: 44px 40px; }}
    .confirmed-badge {{ width: 72px; height: 72px; background: #e8f0eb; border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; font-size: 32px; }}
    .email-greeting {{ font-size: 22px; font-weight: 700; color: #1a4d2e; margin-bottom: 8px; text-align: center; }}
    .email-subheading {{ font-size: 15px; color: #5a5550; text-align: center; margin-bottom: 32px; line-height: 1.6; }}
    .reference-block {{ background: #1a4d2e; border-radius: 8px; padding: 18px 24px; text-align: center; margin-bottom: 28px; }}
    .reference-label {{ font-size: 11px; color: rgba(255,255,255,0.65); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; }}
    .reference-code {{ font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: 0.08em; }}
    .section-title {{ font-size: 11px; font-weight: 600; color: #9e8e7e; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 12px; }}
    .detail-table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
    .detail-label {{ font-size: 13px; color: #9e8e7e; padding: 9px 0; border-bottom: 1px solid #e0d5c8; width: 45%; }}
    .detail-value {{ font-size: 13px; color: #1e1e1e; font-weight: 500; padding: 9px 0; border-bottom: 1px solid #e0d5c8; text-align: right; }}
    .total-row td {{ font-size: 16px; font-weight: 700; color: #1a4d2e; padding-top: 14px; border-bottom: none; }}
    .poa-box {{ background: #faf3ea; border: 1px solid #e8c99a; border-radius: 8px; padding: 18px 20px; margin-bottom: 28px; }}
    .poa-box-title {{ font-size: 14px; font-weight: 700; color: #a67a50; margin-bottom: 6px; }}
    .poa-box-text {{ font-size: 13px; color: #5a5550; line-height: 1.7; }}
    .divider {{ border: none; border-top: 1px solid #e0d5c8; margin: 24px 0; }}
    .contact-text {{ font-size: 13px; color: #5a5550; text-align: center; line-height: 1.8; }}
    .contact-text a {{ color: #c89666; text-decoration: none; }}
    .email-footer {{ background: #f0ebe3; padding: 24px 40px; text-align: center; border-top: 1px solid #e0d5c8; }}
    .email-footer p {{ font-size: 12px; color: #9e8e7e; line-height: 1.8; }}
    .email-footer a {{ color: #c89666; text-decoration: none; }}
    @media (max-width: 620px) {{
      .email-wrapper {{ margin: 0; border-radius: 0; }}
      .email-body {{ padding: 32px 24px; }}
      .email-header {{ padding: 28px 24px; }}
      .email-footer {{ padding: 20px 24px; }}
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">

    <div class="email-header">
      <div class="brand-name">Jadevine Travel & Tours</div>
      <div class="brand-tagline">Zanzibar, Tanzania</div>
    </div>

    <div class="email-body">

      <div class="confirmed-badge">✅</div>

      <h1 class="email-greeting">Your booking is confirmed!</h1>
      <p class="email-subheading">
        Dear {name}, thank you for choosing Jadevine Travel & Tours.<br>
        Here are the details of your reservation.
      </p>

      <div class="reference-block">
        <div class="reference-label">Booking Reference</div>
        <div class="reference-code">{booking.reference}</div>
      </div>

      {tour_notice}

      <div class="section-title">Booking Details</div>
      <table class="detail-table">
        <tr>
          <td class="detail-label">Service</td>
          <td class="detail-value">{service}</td>
        </tr>
        {detail_rows}
        {special_requests_row}
        <tr class="total-row">
          <td class="detail-label" style="font-size:16px;font-weight:700;color:#1a4d2e;border-bottom:none;padding-top:14px;">Total Due</td>
          <td class="detail-value" style="font-size:16px;font-weight:700;color:#1a4d2e;border-bottom:none;padding-top:14px;">{booking.currency} {booking.total_price}</td>
        </tr>
      </table>

      <div class="poa-box">
        <div class="poa-box-title">💵 Pay on Arrival</div>
        <div class="poa-box-text">
          Please bring the full amount of <strong>{booking.currency} {booking.total_price}</strong>
          when you arrive in Tanzania. Payment can be made in cash (USD or TZS) or by card.
          Our team will be ready to receive you.
        </div>
      </div>

      <hr class="divider">

      <p class="contact-text">
        Questions about your booking?<br>
        <a href="https://wa.me/255683956372">WhatsApp us</a> anytime or email
        <a href="mailto:info@jadevinetours.com">info@jadevinetours.com</a>
      </p>

    </div>

    <div class="email-footer">
      <p>
        <strong>Jadevine Travel & Tours</strong><br>
        Stone Town, Zanzibar, Tanzania<br>
        <a href="mailto:info@jadevinetours.com">info@jadevinetours.com</a>
      </p>
      <p style="margin-top:12px;">
        This confirmation was sent to {user.email}.<br>
        Please keep this email for your records.
      </p>
    </div>

  </div>
</body>
</html>"""

    _send(subject, text_body, html_body, user.email)


# ---------------------------------------------------------------------------
# Pay on Arrival — Admin Notification
# ---------------------------------------------------------------------------
def send_poa_booking_notification_admin(booking_id):
    """
    Sent to Jadevine admin immediately after a Pay on Arrival booking is confirmed.
    Gives admin all details needed to prepare for the customer's arrival.

    Called by: BookingSummaryView.post() via django_q.tasks.async_task()
    """
    booking = _get_booking(booking_id)
    user = booking.user
    service = _service_label(booking)

    # ── Service detail lines for plain text ──────────────────────────────────
    if booking.service_type == 'hotel':
        detail_lines = (
            f'Room Type: {booking.room_type.name if booking.room_type else "—"}\n'
            f'Check-in:  {booking.check_in_date}\n'
            f'Check-out: {booking.check_out_date}\n'
            f'Guests:    {booking.num_guests}\n'
        )
        html_details = f"""
        <tr><td class="detail-label">Room Type</td><td class="detail-value">{booking.room_type.name if booking.room_type else '—'}</td></tr>
        <tr><td class="detail-label">Check-in</td><td class="detail-value">{booking.check_in_date}</td></tr>
        <tr><td class="detail-label">Check-out</td><td class="detail-value">{booking.check_out_date}</td></tr>
        <tr><td class="detail-label">Guests</td><td class="detail-value">{booking.num_guests}</td></tr>
        """
    elif booking.service_type == 'car':
        rental_mode = 'Self Drive' if booking.rental_mode == 'self_drive' else 'With Driver'
        detail_lines = (
            f'Pickup:    {booking.pickup_location}\n'
            f'Mode:      {rental_mode}\n'
            f'From:      {booking.pickup_date}\n'
            f'To:        {booking.return_date}\n'
            f'Days:      {booking.num_days}\n'
        )
        html_details = f"""
        <tr><td class="detail-label">Pickup Location</td><td class="detail-value">{booking.pickup_location}</td></tr>
        <tr><td class="detail-label">Rental Mode</td><td class="detail-value">{rental_mode}</td></tr>
        <tr><td class="detail-label">Pickup Date</td><td class="detail-value">{booking.pickup_date}</td></tr>
        <tr><td class="detail-label">Return Date</td><td class="detail-value">{booking.return_date}</td></tr>
        """
    elif booking.service_type == 'tour':
        detail_lines = (
            f'Preferred Date: {booking.preferred_date}\n'
            f'Participants:   {booking.num_participants}\n'
        )
        html_details = f"""
        <tr><td class="detail-label">Preferred Date</td><td class="detail-value">{booking.preferred_date}</td></tr>
        <tr><td class="detail-label">Participants</td><td class="detail-value">{booking.num_participants}</td></tr>
        """
    else:
        detail_lines = ''
        html_details = ''

    subject = f'NEW BOOKING: {booking.reference} — {service} (Pay on Arrival)'

    text_body = (
        f'New Pay on Arrival booking received.\n\n'
        f'Reference: {booking.reference}\n'
        f'Service:   {service}\n'
        f'Customer:  {user.get_full_name() or user.email} ({user.email})\n'
        f'Phone:     {user.phone or "Not provided"}\n\n'
        f'{detail_lines}'
        f'\nTotal Due on Arrival: {booking.currency} {booking.total_price}\n\n'
        f'Special Requests: {booking.special_requests or "None"}\n\n'
        f'View booking in portal: /portal/bookings/{booking.id}/'
    )

    admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', settings.DEFAULT_FROM_EMAIL)
    # Strip display name if present — send_mail needs a plain address for admin
    if '<' in admin_email:
        admin_email = admin_email.split('<')[1].rstrip('>')

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>New Booking — {booking.reference}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f5f0; color: #1e1e1e; }}
    .email-wrapper {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
    .email-header {{ background-color: #1a4d2e; padding: 28px 40px; }}
    .header-label {{ font-size: 11px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }}
    .header-title {{ font-size: 20px; font-weight: 700; color: #ffffff; }}
    .header-ref {{ font-size: 13px; color: #c89666; margin-top: 4px; letter-spacing: 0.06em; }}
    .email-body {{ padding: 36px 40px; }}
    .alert-box {{ background: #e8f0eb; border-left: 4px solid #1a4d2e; border-radius: 4px; padding: 14px 18px; margin-bottom: 28px; font-size: 14px; color: #1a4d2e; font-weight: 600; }}
    .section-title {{ font-size: 11px; font-weight: 600; color: #9e8e7e; text-transform: uppercase; letter-spacing: 0.14em; margin: 24px 0 10px; }}
    .detail-table {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; }}
    .detail-label {{ font-size: 13px; color: #9e8e7e; padding: 8px 0; border-bottom: 1px solid #e0d5c8; width: 45%; }}
    .detail-value {{ font-size: 13px; color: #1e1e1e; font-weight: 500; padding: 8px 0; border-bottom: 1px solid #e0d5c8; text-align: right; }}
    .total-highlight {{ background: #1a4d2e; border-radius: 8px; padding: 14px 20px; display: flex; justify-content: space-between; margin: 16px 0 28px; color: white; font-size: 15px; font-weight: 700; }}
    .portal-btn {{ display: block; background: #c89666; color: #ffffff; text-decoration: none; text-align: center; padding: 14px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; margin-top: 24px; }}
    .email-footer {{ background: #f0ebe3; padding: 20px 40px; text-align: center; border-top: 1px solid #e0d5c8; }}
    .email-footer p {{ font-size: 12px; color: #9e8e7e; }}
    @media (max-width: 620px) {{
      .email-wrapper {{ margin: 0; border-radius: 0; }}
      .email-body {{ padding: 24px 20px; }}
      .email-header {{ padding: 24px 20px; }}
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">

    <div class="email-header">
      <div class="header-label">New Booking Received</div>
      <div class="header-title">Pay on Arrival — Action Required</div>
      <div class="header-ref">{booking.reference}</div>
    </div>

    <div class="email-body">

      <div class="alert-box">
        📋 A new Pay on Arrival booking has been made. Please review and prepare for the customer's arrival.
      </div>

      <div class="section-title">Customer</div>
      <table class="detail-table">
        <tr>
          <td class="detail-label">Name</td>
          <td class="detail-value">{user.get_full_name() or user.email}</td>
        </tr>
        <tr>
          <td class="detail-label">Email</td>
          <td class="detail-value">{user.email}</td>
        </tr>
        <tr>
          <td class="detail-label">Phone</td>
          <td class="detail-value">{user.phone or 'Not provided'}</td>
        </tr>
      </table>

      <div class="section-title">Booking Details</div>
      <table class="detail-table">
        <tr>
          <td class="detail-label">Service</td>
          <td class="detail-value">{service}</td>
        </tr>
        {html_details}
        <tr>
          <td class="detail-label">Special Requests</td>
          <td class="detail-value">{booking.special_requests or 'None'}</td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a4d2e;border-radius:8px;margin:20px 0 8px;">
        <tr>
          <td style="padding:14px 20px;color:rgba(255,255,255,0.75);font-size:14px;font-weight:500;">
            Amount Due on Arrival:
          </td>
          <td style="padding:14px 20px;color:#ffffff;font-size:16px;font-weight:700;text-align:right;">
            {booking.currency} {booking.total_price}
          </td>
        </tr>
      </table>

      <a href="{settings.DEFAULT_SITE_URL}/portal/bookings/{booking.id}/" class="portal-btn">
        View in Admin Portal →
      </a>

    </div>

    <div class="email-footer">
      <p>Jadevine Travel & Tours — Internal Notification<br>
      This email was sent automatically by the booking system.</p>
    </div>

  </div>
</body>
</html>"""

    _send(subject, text_body, html_body, admin_email)
    

# ---------------------------------------------------------------------------
# Pay Now — Customer Confirmation (sent after PesaPal IPN confirms payment)
# ---------------------------------------------------------------------------
def send_paynow_booking_confirmation_customer(booking_id):
    """
    Sent to the customer after PesaPal IPN confirms payment_status='paid'.
    Structurally identical to the POA version but uses a 'Payment Received'
    badge instead of 'Pay on Arrival' instructions.

    Called by: pesapal_callback() via async_task()
    """
    booking = _get_booking(booking_id)
    user    = booking.user
    name    = user.first_name or user.email
    service = _service_label(booking)

    if booking.service_type == 'hotel':
        detail_rows = f"""
        <tr>
          <td class="detail-label">Room Type</td>
          <td class="detail-value">{booking.room_type.name if booking.room_type else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Check-in</td>
          <td class="detail-value">{booking.check_in_date.strftime('%d %B %Y') if booking.check_in_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Check-out</td>
          <td class="detail-value">{booking.check_out_date.strftime('%d %B %Y') if booking.check_out_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Duration</td>
          <td class="detail-value">{booking.nights} night(s)</td>
        </tr>
        <tr>
          <td class="detail-label">Guests</td>
          <td class="detail-value">{booking.num_guests}</td>
        </tr>
        """
    elif booking.service_type == 'car':
        rental_mode = 'Self Drive' if booking.rental_mode == 'self_drive' else 'With Driver'
        detail_rows = f"""
        <tr>
          <td class="detail-label">Pickup Location</td>
          <td class="detail-value">{booking.pickup_location or '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Rental Mode</td>
          <td class="detail-value">{rental_mode}</td>
        </tr>
        <tr>
          <td class="detail-label">Pickup Date</td>
          <td class="detail-value">{booking.pickup_date.strftime('%d %B %Y') if booking.pickup_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Return Date</td>
          <td class="detail-value">{booking.return_date.strftime('%d %B %Y') if booking.return_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Duration</td>
          <td class="detail-value">{booking.num_days} day(s)</td>
        </tr>
        """
    elif booking.service_type == 'tour':
        detail_rows = f"""
        <tr>
          <td class="detail-label">Preferred Start Date</td>
          <td class="detail-value">{booking.preferred_date.strftime('%d %B %Y') if booking.preferred_date else '—'}</td>
        </tr>
        <tr>
          <td class="detail-label">Participants</td>
          <td class="detail-value">{booking.num_participants}</td>
        </tr>
        <tr>
          <td class="detail-label">Duration</td>
          <td class="detail-value">{booking.tour_package.duration_days} day(s)</td>
        </tr>
        """
    else:
        detail_rows = ''

    special_requests_row = (
        f"""
        <tr>
          <td class="detail-label">Special Requests</td>
          <td class="detail-value">{booking.special_requests}</td>
        </tr>
        """
        if booking.special_requests else ''
    )

    tour_notice = ''
    if booking.service_type == 'tour':
        tour_notice = """
        <div style="background:#eaf4fb;border:1px solid #2471a3;border-radius:8px;
                    padding:14px 18px;margin-bottom:24px;font-size:14px;color:#2471a3;">
          <strong>📅 Date Confirmation</strong><br>
          Our team will confirm your preferred start date within <strong>24–48 hours</strong>.
          You will receive a follow-up email once the date is confirmed.
        </div>
        """

    subject = f'Payment Confirmed — {booking.reference} | Jadevine Travel & Tours'

    text_body = (
        f'Dear {name},\n\n'
        f'Your payment has been received and your booking is confirmed!\n\n'
        f'Reference: {booking.reference}\n'
        f'Service:   {service}\n'
        f'Total Paid: {booking.currency} {booking.total_price}\n'
        f'Payment Method: Online (PesaPal)\n\n'
        f'Thank you for choosing Jadevine Travel & Tours.\n'
        f'For questions, WhatsApp us or email info@jadevinetours.com\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Payment Confirmed — {booking.reference}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f5f0; color: #1e1e1e; }}
    .email-wrapper {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
    .email-header {{ background-color: #1a4d2e; padding: 36px 40px; text-align: center; }}
    .brand-name {{ font-size: 26px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px; }}
    .brand-tagline {{ font-size: 12px; color: #c89666; text-transform: uppercase; letter-spacing: 2px; margin-top: 4px; }}
    .email-body {{ padding: 44px 40px; }}
    .confirmed-badge {{ width: 72px; height: 72px; background: #e8f0eb; border-radius: 50%; margin: 0 auto 24px; display: table-cell; vertical-align: middle; text-align: center; font-size: 32px; }}
    .email-greeting {{ font-size: 22px; font-weight: 700; color: #1a4d2e; margin-bottom: 8px; text-align: center; }}
    .email-subheading {{ font-size: 15px; color: #5a5550; text-align: center; margin-bottom: 32px; line-height: 1.6; }}
    .reference-block {{ background: #1a4d2e; border-radius: 8px; padding: 18px 24px; text-align: center; margin-bottom: 28px; }}
    .reference-label {{ font-size: 11px; color: rgba(255,255,255,0.65); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; }}
    .reference-code {{ font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: 0.08em; }}
    .section-title {{ font-size: 11px; font-weight: 600; color: #9e8e7e; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 12px; }}
    .detail-table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
    .detail-label {{ font-size: 13px; color: #9e8e7e; padding: 9px 0; border-bottom: 1px solid #e0d5c8; width: 45%; }}
    .detail-value {{ font-size: 13px; color: #1e1e1e; font-weight: 500; padding: 9px 0; border-bottom: 1px solid #e0d5c8; text-align: right; }}
    .payment-confirmed-box {{ background: #e8f0eb; border: 1px solid #1a4d2e; border-radius: 8px; padding: 18px 20px; margin-bottom: 28px; }}
    .payment-confirmed-box-title {{ font-size: 14px; font-weight: 700; color: #1a4d2e; margin-bottom: 6px; }}
    .payment-confirmed-box-text {{ font-size: 13px; color: #5a5550; line-height: 1.7; }}
    .divider {{ border: none; border-top: 1px solid #e0d5c8; margin: 24px 0; }}
    .contact-text {{ font-size: 13px; color: #5a5550; text-align: center; line-height: 1.8; }}
    .contact-text a {{ color: #c89666; text-decoration: none; }}
    .email-footer {{ background: #f0ebe3; padding: 24px 40px; text-align: center; border-top: 1px solid #e0d5c8; }}
    .email-footer p {{ font-size: 12px; color: #9e8e7e; line-height: 1.8; }}
    .email-footer a {{ color: #c89666; text-decoration: none; }}
    @media (max-width: 620px) {{
      .email-wrapper {{ margin: 0; border-radius: 0; }}
      .email-body {{ padding: 32px 24px; }}
      .email-header {{ padding: 28px 24px; }}
      .email-footer {{ padding: 20px 24px; }}
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    <div class="email-header">
      <div class="brand-name">Jadevine Travel & Tours</div>
      <div class="brand-tagline">Zanzibar, Tanzania</div>
    </div>
    <div class="email-body">
      <table width="72" height="72" cellpadding="0" cellspacing="0"
             style="background:#e8f0eb;border-radius:50%;margin:0 auto 24px;">
        <tr><td align="center" valign="middle" style="font-size:32px;">✅</td></tr>
      </table>
      <h1 class="email-greeting">Payment Received!</h1>
      <p class="email-subheading">
        Dear {name}, your payment has been confirmed.<br>
        Your booking is now active. Here are your details.
      </p>
      <div class="reference-block">
        <div class="reference-label">Booking Reference</div>
        <div class="reference-code">{booking.reference}</div>
      </div>
      {tour_notice}
      <div class="section-title">Booking Details</div>
      <table class="detail-table">
        <tr>
          <td class="detail-label">Service</td>
          <td class="detail-value">{service}</td>
        </tr>
        {detail_rows}
        {special_requests_row}
        <tr>
          <td class="detail-label" style="font-size:16px;font-weight:700;color:#1a4d2e;border-bottom:none;padding-top:14px;">Total Paid</td>
          <td class="detail-value" style="font-size:16px;font-weight:700;color:#1a4d2e;border-bottom:none;padding-top:14px;">{booking.currency} {booking.total_price}</td>
        </tr>
      </table>
      <div class="payment-confirmed-box">
        <div class="payment-confirmed-box-title">💳 Payment Confirmed</div>
        <div class="payment-confirmed-box-text">
          Your payment of <strong>{booking.currency} {booking.total_price}</strong>
          has been received and processed securely via PesaPal.
          No further payment is required.
        </div>
      </div>
      <hr class="divider">
      <p class="contact-text">
        Questions about your booking?<br>
        <a href="https://wa.me/255683956372">WhatsApp us</a> anytime or email
        <a href="mailto:info@jadevinetours.com">info@jadevinetours.com</a>
      </p>
    </div>
    <div class="email-footer">
      <p>
        <strong>Jadevine Travel & Tours</strong><br>
        Stone Town, Zanzibar, Tanzania<br>
        <a href="mailto:info@jadevinetours.com">info@jadevinetours.com</a>
      </p>
      <p style="margin-top:12px;">
        This confirmation was sent to {user.email}.<br>
        Please keep this email for your records.
      </p>
    </div>
  </div>
</body>
</html>"""

    _send(subject, text_body, html_body, user.email)


# ---------------------------------------------------------------------------
# Pay Now — Admin Notification (sent after PesaPal IPN confirms payment)
# ---------------------------------------------------------------------------
def send_paynow_booking_notification_admin(booking_id):
    """
    Sent to Jadevine admin after PesaPal IPN confirms payment.

    Called by: pesapal_callback() via async_task()
    """
    booking = _get_booking(booking_id)
    user    = booking.user
    service = _service_label(booking)

    if booking.service_type == 'hotel':
        detail_lines = (
            f'Room Type: {booking.room_type.name if booking.room_type else "—"}\n'
            f'Check-in:  {booking.check_in_date}\n'
            f'Check-out: {booking.check_out_date}\n'
            f'Guests:    {booking.num_guests}\n'
        )
        html_details = f"""
        <tr><td class="detail-label">Room Type</td><td class="detail-value">{booking.room_type.name if booking.room_type else '—'}</td></tr>
        <tr><td class="detail-label">Check-in</td><td class="detail-value">{booking.check_in_date}</td></tr>
        <tr><td class="detail-label">Check-out</td><td class="detail-value">{booking.check_out_date}</td></tr>
        <tr><td class="detail-label">Guests</td><td class="detail-value">{booking.num_guests}</td></tr>
        """
    elif booking.service_type == 'car':
        rental_mode = 'Self Drive' if booking.rental_mode == 'self_drive' else 'With Driver'
        detail_lines = (
            f'Pickup:  {booking.pickup_location}\n'
            f'Mode:    {rental_mode}\n'
            f'From:    {booking.pickup_date}\n'
            f'To:      {booking.return_date}\n'
            f'Days:    {booking.num_days}\n'
        )
        html_details = f"""
        <tr><td class="detail-label">Pickup Location</td><td class="detail-value">{booking.pickup_location}</td></tr>
        <tr><td class="detail-label">Rental Mode</td><td class="detail-value">{rental_mode}</td></tr>
        <tr><td class="detail-label">Pickup Date</td><td class="detail-value">{booking.pickup_date}</td></tr>
        <tr><td class="detail-label">Return Date</td><td class="detail-value">{booking.return_date}</td></tr>
        """
    elif booking.service_type == 'tour':
        detail_lines = (
            f'Preferred Date: {booking.preferred_date}\n'
            f'Participants:   {booking.num_participants}\n'
        )
        html_details = f"""
        <tr><td class="detail-label">Preferred Date</td><td class="detail-value">{booking.preferred_date}</td></tr>
        <tr><td class="detail-label">Participants</td><td class="detail-value">{booking.num_participants}</td></tr>
        """
    else:
        detail_lines = ''
        html_details = ''

    subject = f'PAYMENT RECEIVED: {booking.reference} — {service}'

    text_body = (
        f'Payment confirmed for booking {booking.reference}.\n\n'
        f'Service:   {service}\n'
        f'Customer:  {user.get_full_name() or user.email} ({user.email})\n'
        f'Phone:     {user.phone or "Not provided"}\n\n'
        f'{detail_lines}'
        f'\nAmount Paid: {booking.currency} {booking.total_price}\n'
        f'Payment Method: Online (PesaPal)\n\n'
        f'Special Requests: {booking.special_requests or "None"}\n\n'
        f'View booking in portal: /portal/bookings/{booking.id}/'
    )

    admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', settings.DEFAULT_FROM_EMAIL)
    if '<' in admin_email:
        admin_email = admin_email.split('<')[1].rstrip('>')

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Payment Received — {booking.reference}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8f5f0; color: #1e1e1e; }}
    .email-wrapper {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
    .email-header {{ background-color: #1a4d2e; padding: 28px 40px; }}
    .header-label {{ font-size: 11px; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }}
    .header-title {{ font-size: 20px; font-weight: 700; color: #ffffff; }}
    .header-ref {{ font-size: 13px; color: #c89666; margin-top: 4px; letter-spacing: 0.06em; }}
    .email-body {{ padding: 36px 40px; }}
    .alert-box {{ background: #e8f0eb; border-left: 4px solid #1a4d2e; border-radius: 4px; padding: 14px 18px; margin-bottom: 28px; font-size: 14px; color: #1a4d2e; font-weight: 600; }}
    .section-title {{ font-size: 11px; font-weight: 600; color: #9e8e7e; text-transform: uppercase; letter-spacing: 0.14em; margin: 24px 0 10px; }}
    .detail-table {{ width: 100%; border-collapse: collapse; margin-bottom: 8px; }}
    .detail-label {{ font-size: 13px; color: #9e8e7e; padding: 8px 0; border-bottom: 1px solid #e0d5c8; width: 45%; }}
    .detail-value {{ font-size: 13px; color: #1e1e1e; font-weight: 500; padding: 8px 0; border-bottom: 1px solid #e0d5c8; text-align: right; }}
    .portal-btn {{ display: block; background: #c89666; color: #ffffff; text-decoration: none; text-align: center; padding: 14px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; margin-top: 24px; }}
    .email-footer {{ background: #f0ebe3; padding: 20px 40px; text-align: center; border-top: 1px solid #e0d5c8; }}
    .email-footer p {{ font-size: 12px; color: #9e8e7e; }}
    @media (max-width: 620px) {{
      .email-wrapper {{ margin: 0; border-radius: 0; }}
      .email-body {{ padding: 24px 20px; }}
      .email-header {{ padding: 24px 20px; }}
    }}
  </style>
</head>
<body>
  <div class="email-wrapper">
    <div class="email-header">
      <div class="header-label">Payment Confirmed</div>
      <div class="header-title">Online Payment Received</div>
      <div class="header-ref">{booking.reference}</div>
    </div>
    <div class="email-body">
      <div class="alert-box">
        💳 Payment has been confirmed via PesaPal. Booking is now active.
      </div>
      <div class="section-title">Customer</div>
      <table class="detail-table">
        <tr>
          <td class="detail-label">Name</td>
          <td class="detail-value">{user.get_full_name() or user.email}</td>
        </tr>
        <tr>
          <td class="detail-label">Email</td>
          <td class="detail-value">{user.email}</td>
        </tr>
        <tr>
          <td class="detail-label">Phone</td>
          <td class="detail-value">{user.phone or 'Not provided'}</td>
        </tr>
      </table>
      <div class="section-title">Booking Details</div>
      <table class="detail-table">
        <tr>
          <td class="detail-label">Service</td>
          <td class="detail-value">{service}</td>
        </tr>
        {html_details}
        <tr>
          <td class="detail-label">Special Requests</td>
          <td class="detail-value">{booking.special_requests or 'None'}</td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0"
             style="background:#1a4d2e;border-radius:8px;margin:20px 0 8px;">
        <tr>
          <td style="padding:14px 20px;color:rgba(255,255,255,0.75);font-size:14px;font-weight:500;">
            Amount Paid (Online):
          </td>
          <td style="padding:14px 20px;color:#ffffff;font-size:16px;font-weight:700;text-align:right;">
            {booking.currency} {booking.total_price}
          </td>
        </tr>
      </table>
      <a href="{settings.DEFAULT_SITE_URL}/portal/bookings/{booking.id}/" class="portal-btn">
        View in Admin Portal →
      </a>
    </div>
    <div class="email-footer">
      <p>Jadevine Travel & Tours — Internal Notification<br>
      This email was sent automatically by the booking system.</p>
    </div>
  </div>
</body>
</html>"""

    _send(subject, text_body, html_body, admin_email)


# ---------------------------------------------------------------------------
# Orphan Cleanup — scheduled via Django-Q
# ---------------------------------------------------------------------------
def cancel_orphan_paynow_bookings():
    """
    Cancels PAY_NOW bookings that:
      - payment_status = 'pending'
      - pesapal_tracking_id is null/empty  (never reached PesaPal)
      - created more than 24 hours ago

    Schedule this in Django-Q as a cron task (runs every hour).
    In portal Settings or via shell:

        from django_q.models import Schedule
        Schedule.objects.create(
            name='Cancel orphan Pay Now bookings',
            func='apps.bookings.tasks.cancel_orphan_paynow_bookings',
            schedule_type=Schedule.HOURLY,
        )

    These are bookings where the customer dropped off between the summary
    page and PesaPal redirect — the DB record exists but payment never started.
    """
    from django.utils import timezone
    from datetime import timedelta
    from apps.bookings.models import Booking

    cutoff = timezone.now() - timedelta(hours=24)

    qs = Booking.objects.filter(
        payment_mode='pay_now',
        payment_status='pending',
        pesapal_tracking_id__isnull=True,
        created_at__lt=cutoff,
    ).exclude(
        pesapal_tracking_id=''
    )

    # Also catch empty-string tracking IDs (belt and braces)
    qs2 = Booking.objects.filter(
        payment_mode='pay_now',
        payment_status='pending',
        pesapal_tracking_id='',
        created_at__lt=cutoff,
    )

    total = qs.count() + qs2.count()
    qs.update(status='cancelled', cancellation_reason='Orphan — payment never initiated')
    qs2.update(status='cancelled', cancellation_reason='Orphan — payment never initiated')

    if total:
        import logging
        logging.getLogger(__name__).info(
            'Orphan cleanup — cancelled %d stale Pay Now booking(s)', total
        )