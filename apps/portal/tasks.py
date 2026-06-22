from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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


def _get_listing(listing_type, listing_id):
    if listing_type == 'hotel':
        from apps.hotels.models import Hotel
        return Hotel.objects.select_related('created_by').get(pk=listing_id)
    if listing_type == 'car':
        from apps.cars.models import CarRental
        return CarRental.objects.select_related('created_by').get(pk=listing_id)
    raise ValueError(f"Unknown listing_type: {listing_type}")


def _listing_label(listing_type):
    return 'Hotel' if listing_type == 'hotel' else 'Car Rental'


def _portal_detail_path(listing_type, listing_id):
    if listing_type == 'hotel':
        return f'/portal/hotels/{listing_id}/'
    return f'/portal/cars/{listing_id}/'


# ---------------------------------------------------------------------------
# Shared email chrome — returns the outer HTML wrapper strings
# ---------------------------------------------------------------------------

def _email_header(title, subtitle=''):
    sub_row = (
        f'<div style="font-size:12px;color:#c89666;margin-top:6px;'
        f'letter-spacing:0.06em;">{subtitle}</div>'
        if subtitle else ''
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f8f5f0;font-family:'Segoe UI',Arial,sans-serif;color:#1e1e1e;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f5f0;padding:40px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background:#ffffff;border-radius:12px;overflow:hidden;
              box-shadow:0 4px 24px rgba(0,0,0,0.08);max-width:600px;width:100%;">
  <!-- HEADER -->
  <tr>
    <td style="background:#1a4d2e;padding:32px 40px;text-align:center;">
      <div style="font-size:26px;font-weight:700;color:#ffffff;letter-spacing:0.5px;">
        Jadevine Travel &amp; Tours
      </div>
      <div style="font-size:12px;color:#c89666;text-transform:uppercase;letter-spacing:2px;margin-top:4px;">
        Zanzibar, Tanzania
      </div>
      {sub_row}
    </td>
  </tr>
  <!-- BODY START -->
  <tr><td style="padding:40px 40px 8px;">
"""


def _email_footer(recipient_email=''):
    note = (
        f'<p style="margin-top:12px;font-size:12px;color:#9e8e7e;">'
        f'This email was sent to {recipient_email}.</p>'
        if recipient_email else ''
    )
    return f"""
  </td></tr>
  <!-- FOOTER -->
  <tr>
    <td style="background:#f0ebe3;padding:24px 40px;border-top:1px solid #e0d5c8;
               text-align:center;">
      <p style="font-size:12px;color:#9e8e7e;margin:0;line-height:1.8;">
        <strong>Jadevine Travel &amp; Tours</strong><br>
        Stone Town, Zanzibar, Tanzania<br>
        <a href="mailto:info@jadevinetravel.com"
           style="color:#c89666;text-decoration:none;">info@jadevinetravel.com</a>
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
    """Single two-column table row for booking/listing detail tables."""
    return (
        f'<tr>'
        f'<td style="font-size:13px;color:#9e8e7e;padding:9px 0;'
        f'border-bottom:1px solid #e0d5c8;width:45%;">{label}</td>'
        f'<td style="font-size:13px;color:#1e1e1e;font-weight:500;padding:9px 0;'
        f'border-bottom:1px solid #e0d5c8;text-align:right;">{value}</td>'
        f'</tr>'
    )


def _portal_button(url, label='View in Admin Portal →'):
    return (
        f'<a href="{url}" style="display:block;background:#c89666;color:#ffffff;'
        f'text-decoration:none;text-align:center;padding:14px 24px;border-radius:6px;'
        f'font-size:14px;font-weight:600;margin-top:24px;">{label}</a>'
    )


def _section_title(text):
    return (
        f'<div style="font-size:11px;font-weight:600;color:#9e8e7e;'
        f'text-transform:uppercase;letter-spacing:0.14em;margin:24px 0 10px;">'
        f'{text}</div>'
    )


# ===========================================================================
# TASK 1 — Notify Super Admin: new listing pending review
# ===========================================================================

def notify_superadmin_new_listing(listing_type, listing_id):
    """
    Sent to ADMIN_NOTIFICATION_EMAIL when:
      - A mini-admin creates a new hotel or car listing
      - A mini-admin resubmits a rejected listing
      - A mini-admin saves edits to an approved listing (resets to pending)

    Called via:
        async_task('apps.portal.tasks.notify_superadmin_new_listing',
                   'hotel', hotel.pk)
    """
    listing = _get_listing(listing_type, listing_id)
    label = _listing_label(listing_type)
    portal_url = _get_portal_url(_portal_detail_path(listing_type, listing_id))
    admin_email = _get_admin_email()

    mini_name = listing.created_by.get_full_name() if listing.created_by else 'Unknown'
    mini_email = listing.created_by.email if listing.created_by else '—'
    listing_name = listing.name

    subject = f'Action Required: New {label} pending review — {listing_name}'

    text_body = (
        f'A new {label} listing has been submitted and requires your review.\n\n'
        f'Listing:  {listing_name}\n'
        f'Partner:  {mini_name} ({mini_email})\n'
        f'Status:   Pending Approval\n\n'
        f'Review it here: {portal_url}'
    )

    html_body = (
        _email_header(f'New {label} Pending Review')
        + f"""
        <div style="background:#fdf6ee;border-left:4px solid #c89666;border-radius:4px;
                    padding:14px 18px;margin-bottom:28px;font-size:14px;color:#7a5200;
                    font-weight:600;">
          ⏳ A new {label} listing is waiting for your approval before it goes live.
        </div>

        {_section_title('Listing Details')}
        <table width="100%" cellpadding="0" cellspacing="0">
          {_detail_row('Listing Name', listing_name)}
          {_detail_row('Type', label)}
          {_detail_row('Submitted By', f'{mini_name} ({mini_email})')}
          {_detail_row('Status', 'Pending Approval')}
        </table>

        {_portal_button(portal_url, f'Review {label} Listing →')}
        """
        + _email_footer()
    )

    _send(subject, text_body, html_body, admin_email)


# ===========================================================================
# TASK 2 — Notify mini-admin: listing approved
# ===========================================================================

def send_listing_approved_email(listing_type, listing_id):
    """
    Sent to the mini-admin when Super Admin approves their listing.

    Called via:
        async_task('apps.portal.tasks.send_listing_approved_email',
                   'hotel', hotel.pk)
    """
    listing = _get_listing(listing_type, listing_id)

    if not listing.created_by:
        return  # Super Admin listing — no mini-admin to notify

    label = _listing_label(listing_type)
    portal_url = _get_portal_url(_portal_detail_path(listing_type, listing_id))
    recipient = listing.created_by.email
    first_name = listing.created_by.first_name or listing.created_by.username
    listing_name = listing.name

    subject = f'Your {label} listing is now live — {listing_name}'

    text_body = (
        f'Dear {first_name},\n\n'
        f'Great news! Your {label} listing "{listing_name}" has been approved '
        f'and is now live on the Jadevine Travel & Tours website.\n\n'
        f'Customers can now find and book your listing.\n\n'
        f'View your listing in the portal: {portal_url}\n\n'
        f'Thank you for partnering with Jadevine Travel & Tours.\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    html_body = (
        _email_header('Your Listing is Live!', listing_name)
        + f"""
        <div style="text-align:center;margin-bottom:28px;">
          <div style="width:72px;height:72px;background:#edf7f1;border-radius:50%;
                      margin:0 auto 16px;display:inline-flex;align-items:center;
                      justify-content:center;font-size:32px;line-height:72px;">✅</div>
          <h2 style="font-size:22px;font-weight:700;color:#1a4d2e;margin-bottom:8px;">
            Approved &amp; Live!
          </h2>
          <p style="font-size:15px;color:#5a5550;line-height:1.6;margin:0;">
            Dear {first_name}, your {label} listing has been reviewed
            and approved by the Jadevine team.
          </p>
        </div>

        {_section_title('Listing')}
        <table width="100%" cellpadding="0" cellspacing="0">
          {_detail_row('Listing Name', listing_name)}
          {_detail_row('Type', label)}
          {_detail_row('Status', '&#x2705; Approved &amp; Live')}
        </table>

        <div style="background:#edf7f1;border:1px solid #2d7a4f;border-radius:8px;
                    padding:16px 20px;margin-top:24px;font-size:14px;color:#2d7a4f;
                    line-height:1.7;">
          Customers searching on our website can now discover and book your listing.
          Keep your details up to date for the best results.
        </div>

        {_portal_button(portal_url, 'View Your Listing →')}
        """
        + _email_footer(recipient)
    )

    _send(subject, text_body, html_body, recipient)


# ===========================================================================
# TASK 3 — Notify mini-admin: listing rejected
# ===========================================================================

def send_listing_rejected_email(listing_type, listing_id):
    """
    Sent to the mini-admin when Super Admin rejects their listing.
    The rejection_reason field on the listing is read here — it was already
    saved to the DB before this task is queued in PortalHotelRejectView.

    Called via:
        async_task('apps.portal.tasks.send_listing_rejected_email',
                   'hotel', hotel.pk)
    """
    listing = _get_listing(listing_type, listing_id)

    if not listing.created_by:
        return

    label = _listing_label(listing_type)
    portal_url = _get_portal_url(_portal_detail_path(listing_type, listing_id))
    recipient = listing.created_by.email
    first_name = listing.created_by.first_name or listing.created_by.username
    listing_name = listing.name
    reason = listing.rejection_reason or 'No reason provided.'

    subject = f'Your {label} listing needs attention — {listing_name}'

    text_body = (
        f'Dear {first_name},\n\n'
        f'Your {label} listing "{listing_name}" has been reviewed and requires '
        f'some changes before it can be published.\n\n'
        f'Reason:\n{reason}\n\n'
        f'Please log in to the portal, make the required changes, and resubmit '
        f'your listing for review.\n\n'
        f'Edit your listing here: {portal_url}\n\n'
        f'If you have questions, contact the Jadevine team.\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    html_body = (
        _email_header('Your Listing Needs Attention', listing_name)
        + f"""
        <div style="text-align:center;margin-bottom:28px;">
          <div style="width:72px;height:72px;background:#fdf0ee;border-radius:50%;
                      margin:0 auto 16px;line-height:72px;font-size:32px;
                      display:inline-flex;align-items:center;justify-content:center;">
            ⚠️
          </div>
          <h2 style="font-size:22px;font-weight:700;color:#b03a2e;margin-bottom:8px;">
            Changes Required
          </h2>
          <p style="font-size:15px;color:#5a5550;line-height:1.6;margin:0;">
            Dear {first_name}, your {label} listing has been reviewed and
            needs some corrections before it can go live.
          </p>
        </div>

        {_section_title('Listing')}
        <table width="100%" cellpadding="0" cellspacing="0">
          {_detail_row('Listing Name', listing_name)}
          {_detail_row('Type', label)}
          {_detail_row('Status', '&#x26A0;&#xFE0F; Rejected')}
        </table>

        {_section_title('Reason for Rejection')}
        <div style="background:#fdf0ee;border:1px solid #b03a2e;border-radius:8px;
                    padding:16px 20px;margin-bottom:24px;font-size:14px;
                    color:#7a2018;line-height:1.7;">
          {reason}
        </div>

        <div style="background:#eaf4fb;border:1px solid #2471a3;border-radius:8px;
                    padding:14px 18px;font-size:14px;color:#2471a3;line-height:1.7;
                    margin-bottom:8px;">
          <strong>What to do next:</strong> Log in to the partner portal,
          open this listing, make the required changes, and click
          <strong>Resubmit for Approval</strong>.
        </div>

        {_portal_button(portal_url, 'Edit &amp; Resubmit Listing →')}
        """
        + _email_footer(recipient)
    )

    _send(subject, text_body, html_body, recipient)


# ===========================================================================
# TASK 4 — Welcome email for new mini-admin accounts
# ===========================================================================

def send_miniadmin_welcome_email(user_id):
    """
    Sent when a Super Admin creates a new mini-admin account.
    Contains their username, portal URL, and a password-reset link so they
    can set their own password.

    NEVER sends a plaintext password. The user is created with
    set_unusable_password() and must set their own via the reset link.

    Called via:
        async_task('apps.portal.tasks.send_miniadmin_welcome_email', user.pk)
    """
    from apps.accounts.models import CustomUser
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    user = CustomUser.objects.get(pk=user_id)
    recipient = user.email
    first_name = user.first_name or user.username

    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_path = f'/portal/set-password/{uid}/{token}/'
    reset_url  = _get_portal_url(reset_path)
    portal_login_url = _get_portal_url('/portal/login/')

    subject = 'Welcome to Jadevine Staff Portal — Set Your Password'

    text_body = (
        f'Dear {first_name},\n\n'
        f'You have been added as a Partner on the Jadevine Travel & Tours '
        f'staff portal.\n\n'
        f'Your login details:\n'
        f'  Portal URL: {portal_login_url}\n'
        f'  Username:   {user.username}\n\n'
        f'You must set a password before you can log in. Click the link below:\n'
        f'{reset_url}\n\n'
        f'This link expires in 3 days. If it has expired, go to the portal login '
        f'page and use "Forgot password?" to get a new link.\n\n'
        f'Once logged in you can create and manage your hotel or car rental listings. '
        f'All listings require approval from the Jadevine team before going live.\n\n'
        f'Questions? Contact the Jadevine team at info@jadevinetravel.com\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    html_body = (
        _email_header('Welcome to the Staff Portal')
        + f"""
        <div style="text-align:center;margin-bottom:32px;">
          <div style="width:72px;height:72px;background:#e8f0eb;border-radius:50%;
                      margin:0 auto 16px;line-height:72px;font-size:32px;
                      display:inline-flex;align-items:center;justify-content:center;">
            🌿
          </div>
          <h2 style="font-size:22px;font-weight:700;color:#1a4d2e;margin-bottom:8px;">
            Welcome, {first_name}!
          </h2>
          <p style="font-size:15px;color:#5a5550;line-height:1.6;margin:0;">
            You have been added as a <strong>Partner</strong> on the
            Jadevine Travel &amp; Tours staff portal.
          </p>
        </div>

        {_section_title('Your Login Details')}
        <table width="100%" cellpadding="0" cellspacing="0">
          {_detail_row('Portal URL', f'<a href="{portal_login_url}" style="color:#c89666;">{portal_login_url}</a>')}
          {_detail_row('Username', f'<strong>{user.username}</strong>')}
          {_detail_row('Password', 'Set via the link below')}
        </table>

        <div style="background:#fdf6ee;border:1px solid #e8c99a;border-radius:8px;
                    padding:16px 20px;margin:24px 0;font-size:14px;color:#7a5200;
                    line-height:1.7;">
          <strong>⚠️ Action Required:</strong> You must set your password before
          you can log in. Click the button below — the link expires in
          <strong>3 days</strong>.
        </div>

        <a href="{reset_url}"
           style="display:block;background:#1a4d2e;color:#ffffff;text-decoration:none;
                  text-align:center;padding:16px 24px;border-radius:6px;font-size:15px;
                  font-weight:600;margin-bottom:24px;">
          Set My Password →
        </a>

        {_section_title('What You Can Do')}
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding:8px 0;font-size:13px;color:#5a5550;border-bottom:
                       1px solid #e0d5c8;">
              ✅ Create and manage your hotel or car rental listings
            </td>
          </tr>
          <tr>
            <td style="padding:8px 0;font-size:13px;color:#5a5550;border-bottom:
                       1px solid #e0d5c8;">
              📋 View bookings made for and moderate reviews of your listings
            </td>
          </tr>
          <tr>
            <td style="padding:8px 0;font-size:13px;color:#5a5550;">
              ⏳ All new listings require approval from the Jadevine team before going live
            </td>
          </tr>
        </table>

        <hr style="border:none;border-top:1px solid #e0d5c8;margin:28px 0;">
        <p style="font-size:13px;color:#9e8e7e;text-align:center;line-height:1.7;">
          Questions? Email us at
          <a href="mailto:info@jadevinetravel.com"
             style="color:#c89666;text-decoration:none;">info@jadevinetravel.com</a>
        </p>
        """
        + _email_footer(recipient)
    )

    _send(subject, text_body, html_body, recipient)


# ===========================================================================
# TASK 5 — Contact message reply
# ===========================================================================

def send_contact_reply_email(message_id, reply_text):
    """
    Sent to the customer when a Super Admin replies to their contact message.
    The original message is quoted below the reply for context.

    Called via:
        async_task('apps.portal.tasks.send_contact_reply_email',
                   message.pk, reply_text)
    """
    from apps.contact.models import ContactMessage

    msg = ContactMessage.objects.get(pk=message_id)
    recipient = msg.email
    customer_name = msg.name

    subject = f'Re: {msg.subject} — Jadevine Travel & Tours'

    text_body = (
        f'Dear {customer_name},\n\n'
        f'{reply_text}\n\n'
        f'---\n'
        f'Your original message:\n'
        f'Subject: {msg.subject}\n'
        f'{msg.message}\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania\ninfo@jadevinetravel.com'
    )

    quoted_original = (
        f'<div style="border-left:3px solid #e0d5c8;padding-left:16px;'
        f'margin-top:24px;color:#9e8e7e;font-size:13px;line-height:1.7;">'
        f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.1em;'
        f'margin-bottom:8px;color:#c8b89a;">Your original message</div>'
        f'<strong style="color:#5a5550;">{msg.subject}</strong><br>'
        f'<span style="white-space:pre-wrap;">{msg.message}</span>'
        f'</div>'
    )

    html_body = (
        _email_header(f'Re: {msg.subject}')
        + f"""
        <p style="font-size:16px;font-weight:600;color:#1a4d2e;margin-bottom:16px;">
          Dear {customer_name},
        </p>
        <div style="font-size:14px;color:#1e1e1e;line-height:1.8;
                    white-space:pre-wrap;margin-bottom:8px;">
{reply_text}
        </div>
        {quoted_original}
        <hr style="border:none;border-top:1px solid #e0d5c8;margin:28px 0;">
        <p style="font-size:13px;color:#9e8e7e;text-align:center;line-height:1.7;">
          Questions? Reply to this email or WhatsApp us at
          <a href="https://wa.me/255683956372"
             style="color:#c89666;text-decoration:none;">+255 713 529 019</a>
        </p>
        """
        + _email_footer(recipient)
    )

    _send(subject, text_body, html_body, recipient)


# ===========================================================================
# TASK 6 — Notify mini-admin: their listing was edited by Super Admin
# ===========================================================================
def send_listing_edited_by_admin_email(listing_type, listing_id, edited_by_id):
    """
    Sent to the mini-admin who owns the listing when a Super Admin edits it.
    Does NOT fire when the mini-admin edits their own listing (that path
    already goes through the approval reset flow).

    Called via:
        async_task(
            'apps.portal.tasks.send_listing_edited_by_admin_email',
            'hotel', hotel.pk, request.user.pk,
        )
    """
    from apps.accounts.models import CustomUser

    listing = _get_listing(listing_type, listing_id)

    if not listing.created_by:
        return  # Super Admin's own listing — nobody to notify

    if not hasattr(listing.created_by, 'miniadminprofile'):
        return  # Created by another Super Admin — skip

    editor = CustomUser.objects.get(pk=edited_by_id)
    label = _listing_label(listing_type)
    portal_url = _get_portal_url(_portal_detail_path(listing_type, listing_id))
    recipient = listing.created_by.email
    first_name = listing.created_by.first_name or listing.created_by.username
    listing_name = listing.name
    editor_name = editor.get_full_name() or editor.username
    edited_at = timezone.now().strftime('%d %b %Y at %H:%M UTC')

    subject = f'Your {label} listing has been updated — {listing_name}'

    text_body = (
        f'Dear {first_name},\n\n'
        f'The Jadevine team has made updates to your {label} listing '
        f'"{listing_name}".\n\n'
        f'Updated by: {editor_name}\n'
        f'Date:       {edited_at}\n\n'
        f'Your listing remains live. You can review the changes in the portal:\n'
        f'{portal_url}\n\n'
        f'If you have questions about the changes made, please contact the '
        f'Jadevine team at info@jadevinetravel.com.\n\n'
        f'Jadevine Travel & Tours\nZanzibar, Tanzania'
    )

    html_body = (
        _email_header(f'Your {label} Listing Was Updated', listing_name)
        + f"""
        <div style="text-align:center;margin-bottom:28px;">
          <div style="width:72px;height:72px;background:#eaf4fb;border-radius:50%;
                      margin:0 auto 16px;line-height:72px;font-size:32px;
                      display:inline-flex;align-items:center;justify-content:center;">
            ✏️
          </div>
          <h2 style="font-size:22px;font-weight:700;color:#1a4d2e;margin-bottom:8px;">
            Listing Updated
          </h2>
          <p style="font-size:15px;color:#5a5550;line-height:1.6;margin:0;">
            Dear {first_name}, the Jadevine team has made changes to
            your {label} listing. It remains live on the website.
          </p>
        </div>

        {_section_title('Update Details')}
        <table width="100%" cellpadding="0" cellspacing="0">
          {_detail_row('Listing Name', listing_name)}
          {_detail_row('Type', label)}
          {_detail_row('Updated By', editor_name)}
          {_detail_row('Date', edited_at)}
          {_detail_row('Status', '&#x2705; Still Live')}
        </table>

        <div style="background:#eaf4fb;border:1px solid #2471a3;border-radius:8px;
                    padding:14px 18px;margin-top:24px;font-size:14px;color:#2471a3;
                    line-height:1.7;">
          Your listing is still live and accepting bookings. Log in to the portal
          to review any changes. If anything looks incorrect, contact the Jadevine
          team at
          <a href="mailto:info@jadevinetravel.com"
             style="color:#2471a3;">info@jadevinetravel.com</a>.
        </div>

        {_portal_button(portal_url, 'Review My Listing →')}
        """
        + _email_footer(recipient)
    )

    _send(subject, text_body, html_body, recipient)