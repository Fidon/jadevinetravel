from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext as _


def _send(subject, text_body, html_body, recipient):
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=True)


def _get_admin_email():
    raw = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', settings.DEFAULT_FROM_EMAIL)
    if '<' in raw:
        raw = raw.split('<')[1].rstrip('>')
    return raw


def _get_portal_url(path=''):
    base = getattr(settings, 'DEFAULT_SITE_URL', 'http://jadevinetravel.com/')
    return f"{base.rstrip('/')}{path}"


# ── Shared HTML chrome ────────────────────────────────────────────────────

def _email_wrap(title, body_html, recipient_email=''):
    note = (
        f'<p style="margin-top:12px;font-size:12px;color:#9e8e7e;">'
        f'This email was sent to {recipient_email}.</p>'
        if recipient_email else ''
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f8f5f0;
             font-family:'Segoe UI',Arial,sans-serif;color:#1e1e1e;">
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#f8f5f0;padding:40px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background:#ffffff;border-radius:12px;overflow:hidden;
              box-shadow:0 4px 24px rgba(0,0,0,0.08);
              max-width:600px;width:100%;">
  <tr>
    <td style="background:#1a4d2e;padding:32px 40px;text-align:center;">
      <div style="font-size:26px;font-weight:700;color:#ffffff;
                  letter-spacing:0.5px;">
        Jadevine Travel &amp; Tours
      </div>
      <div style="font-size:12px;color:#c89666;text-transform:uppercase;
                  letter-spacing:2px;margin-top:4px;">
        Zanzibar, Tanzania
      </div>
    </td>
  </tr>
  <tr><td style="padding:40px 40px 8px;">
    {body_html}
  </td></tr>
  <tr>
    <td style="background:#f0ebe3;padding:24px 40px;
               border-top:1px solid #e0d5c8;text-align:center;">
      <p style="font-size:12px;color:#9e8e7e;margin:0;line-height:1.8;">
        <strong>Jadevine Travel &amp; Tours</strong><br>
        Stone Town, Zanzibar, Tanzania<br>
        <a href="mailto:info@jadevinetravel.com"
           style="color:#c89666;text-decoration:none;">
          info@jadevinetravel.com
        </a>
      </p>
      {note}
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>"""


def _detail_row(label, value):
    return (
        f'<tr>'
        f'<td style="font-size:13px;color:#9e8e7e;padding:9px 0;'
        f'border-bottom:1px solid #e0d5c8;width:40%;">{label}</td>'
        f'<td style="font-size:13px;color:#1e1e1e;font-weight:500;'
        f'padding:9px 0;border-bottom:1px solid #e0d5c8;'
        f'text-align:right;">{value}</td>'
        f'</tr>'
    )


# ── Task 1: Acknowledgement to customer ──────────────────────────────────

def send_contact_acknowledgement_customer(message_id):
    """
    Sent to the customer immediately after they submit the contact form.
    Confirms receipt and sets the expectation of a 24-hour response.
    """
    from apps.contact.models import ContactMessage
    msg = ContactMessage.objects.get(pk=message_id)

    inquiry_labels = {
        'general':     'General Inquiry',
        'custom_tour': 'Custom Tour Request',
        'partnership': 'Partnership',
        'press':       'Press / Media',
    }
    inquiry_label = inquiry_labels.get(msg.inquiry_type, msg.inquiry_type)

    subject   = f'We received your message — {msg.subject}'
    recipient = msg.email

    text_body = (
        f'Dear {msg.name},\n\n'
        f'Thank you for reaching out to Jadevine Travel & Tours.\n\n'
        f'We have received your message and will respond within 24 hours.\n\n'
        f'Your reference:\n'
        f'  Subject: {msg.subject}\n'
        f'  Type: {inquiry_label}\n\n'
        f'In the meantime, you are welcome to WhatsApp us at +255 713 529 019 '
        f'for urgent enquiries.\n\n'
        f'Warm regards,\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    body_html = f"""
    <div style="text-align:center;margin-bottom:28px;">
      <div style="width:72px;height:72px;background:#edf7f1;border-radius:50%;
                  margin:0 auto 16px;line-height:72px;font-size:32px;
                  display:inline-flex;align-items:center;justify-content:center;">
        ✉️
      </div>
      <h2 style="font-size:22px;font-weight:700;color:#1a4d2e;margin-bottom:8px;
                 font-family:'Segoe UI',Arial,sans-serif;">
        Message Received!
      </h2>
      <p style="font-size:15px;color:#5a5550;line-height:1.6;margin:0;">
        Dear {msg.name}, thank you for getting in touch.
      </p>
    </div>

    <div style="font-size:11px;font-weight:600;color:#9e8e7e;
                text-transform:uppercase;letter-spacing:0.14em;
                margin-bottom:10px;">
      Your Message Details
    </div>
    <table width="100%" cellpadding="0" cellspacing="0"
           style="margin-bottom:24px;">
      {_detail_row('Subject', msg.subject)}
      {_detail_row('Type', inquiry_label)}
      {_detail_row('Submitted', msg.created_at.strftime('%d %b %Y, %H:%M'))}
    </table>

    <div style="background:#edf7f1;border:1px solid #2d7a4f;border-radius:8px;
                padding:16px 20px;margin-bottom:24px;font-size:14px;
                color:#2d7a4f;line-height:1.7;">
      <strong>✅ What happens next:</strong><br>
      Our team will review your message and respond to
      <strong>{msg.email}</strong> within <strong>24 hours</strong>.
    </div>

    <p style="font-size:13px;color:#5a5550;text-align:center;line-height:1.8;">
      Need a faster response? WhatsApp us at<br>
      <a href="https://wa.me/255683956372"
         style="color:#c89666;text-decoration:none;font-weight:600;">
        +255 713 529 019
      </a>
    </p>
    """

    _send(subject, text_body, _email_wrap(subject, body_html, recipient), recipient)


# ── Task 2: Notification to admin ────────────────────────────────────────

def send_contact_notification_admin(message_id):
    """
    Sent to ADMIN_NOTIFICATION_EMAIL immediately after a contact form submission.
    Contains full message details and a link to the portal message.
    """
    from apps.contact.models import ContactMessage
    msg      = ContactMessage.objects.get(pk=message_id)
    admin    = _get_admin_email()
    portal_url = _get_portal_url(f'/portal/messages/{msg.pk}/')

    inquiry_labels = {
        'general':     'General Inquiry',
        'custom_tour': 'Custom Tour Request',
        'partnership': 'Partnership',
        'press':       'Press / Media',
    }
    inquiry_label = inquiry_labels.get(msg.inquiry_type, msg.inquiry_type)

    subject = f'New Message: {inquiry_label} from {msg.name}'

    text_body = (
        f'New contact message received.\n\n'
        f'From:    {msg.name} ({msg.email})\n'
        f'Phone:   {msg.phone or "Not provided"}\n'
        f'Type:    {inquiry_label}\n'
        f'Subject: {msg.subject}\n\n'
        f'Message:\n{msg.message}\n\n'
        f'View in portal: {portal_url}'
    )

    body_html = f"""
    <div style="background:#fdf6ee;border-left:4px solid #c89666;
                border-radius:4px;padding:14px 18px;margin-bottom:28px;
                font-size:14px;color:#7a5200;font-weight:600;">
      📬 New {inquiry_label} received — action may be required.
    </div>

    <div style="font-size:11px;font-weight:600;color:#9e8e7e;
                text-transform:uppercase;letter-spacing:0.14em;
                margin-bottom:10px;">
      Sender Details
    </div>
    <table width="100%" cellpadding="0" cellspacing="0"
           style="margin-bottom:20px;">
      {_detail_row('Name', msg.name)}
      {_detail_row('Email', f'<a href="mailto:{msg.email}" style="color:#c89666;">{msg.email}</a>')}
      {_detail_row('Phone', msg.phone or 'Not provided')}
      {_detail_row('Type', inquiry_label)}
      {_detail_row('Language', msg.preferred_lang.upper())}
      {_detail_row('Received', msg.created_at.strftime('%d %b %Y, %H:%M'))}
    </table>

    <div style="font-size:11px;font-weight:600;color:#9e8e7e;
                text-transform:uppercase;letter-spacing:0.14em;
                margin-bottom:10px;">
      Subject
    </div>
    <p style="font-size:15px;font-weight:600;color:#1e1e1e;
              margin-bottom:16px;">{msg.subject}</p>

    <div style="font-size:11px;font-weight:600;color:#9e8e7e;
                text-transform:uppercase;letter-spacing:0.14em;
                margin-bottom:10px;">
      Message
    </div>
    <div style="background:#f8f5f0;border:1px solid #e0d5c8;
                border-radius:8px;padding:16px 20px;font-size:14px;
                color:#1e1e1e;line-height:1.8;white-space:pre-wrap;
                margin-bottom:24px;">{msg.message}</div>

    <a href="{portal_url}"
       style="display:block;background:#c89666;color:#ffffff;
              text-decoration:none;text-align:center;padding:14px 24px;
              border-radius:6px;font-size:14px;font-weight:600;">
      View &amp; Reply in Portal →
    </a>
    """

    _send(subject, text_body, _email_wrap(subject, body_html), admin)