"""
PesaPal REST API 3.0 service module.

Three public functions consumed by views and tasks:
  - get_auth_token()              → bearer token string
  - submit_order_request(booking) → PesaPal hosted payment URL
  - get_transaction_status(order_tracking_id) → dict with payment_status_description

Environment variables required (in .env):
  PESAPAL_CONSUMER_KEY
  PESAPAL_CONSUMER_SECRET
  PESAPAL_ENVIRONMENT   → 'sandbox' | 'production'

Sandbox base URL : https://cybqa.pesapal.com/pesapalv3
Production base URL: https://pay.pesapal.com/v3
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_SANDBOX_URL    = 'https://cybqa.pesapal.com/pesapalv3'
_PRODUCTION_URL = 'https://pay.pesapal.com/v3'


def _base_url() -> str:
    env = getattr(settings, 'PESAPAL_ENVIRONMENT', 'sandbox')
    return _PRODUCTION_URL if env == 'production' else _SANDBOX_URL


def _credentials() -> tuple[str, str]:
    key    = getattr(settings, 'PESAPAL_CONSUMER_KEY', '')
    secret = getattr(settings, 'PESAPAL_CONSUMER_SECRET', '')
    if not key or not secret:
        raise ValueError(
            'PESAPAL_CONSUMER_KEY and PESAPAL_CONSUMER_SECRET must be set in .env'
        )
    return key, secret


# ---------------------------------------------------------------------------
# 1. Authentication
# ---------------------------------------------------------------------------
def get_auth_token() -> str:
    """
    Authenticate with PesaPal and return a bearer token.
    Tokens are valid for ~5 minutes — fetch fresh on every transaction.
    """
    key, secret = _credentials()
    url = f'{_base_url()}/api/Auth/RequestToken'
    payload = {'consumer_key': key, 'consumer_secret': secret}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.Timeout:
        logger.error('PesaPal auth timed out')
        raise
    except requests.HTTPError:
        logger.error('PesaPal auth HTTP error: %s — %s', resp.status_code, resp.text)
        raise

    data  = resp.json()
    token = data.get('token')
    if not token:
        raise RuntimeError(f'PesaPal auth returned no token. Response: {data}')

    return token


# ---------------------------------------------------------------------------
# 2. Register IPN URL
# ---------------------------------------------------------------------------
def _register_ipn_url(token: str) -> str:
    """
    Register our IPN callback URL with PesaPal and return the ipn_id (GUID).

    IMPORTANT: ipn_notification_type must be 'GET' — PesaPal sends IPN
    notifications as GET requests with query parameters, not POST body.
    Our pesapal_callback view handles GET accordingly.

    The returned ipn_id is the notification_id required by SubmitOrderRequest.
    """
    site_url = settings.DEFAULT_SITE_URL.rstrip('/')
    ipn_url  = f'{site_url}/book/pesapal/callback/'

    url = f'{_base_url()}/api/URLSetup/RegisterIPN'
    payload = {
        'url': ipn_url,
        'ipn_notification_type': 'GET',   # PesaPal sends GET with query params
    }
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.Timeout:
        logger.error('PesaPal IPN registration timed out')
        raise
    except requests.HTTPError:
        logger.error(
            'PesaPal IPN registration HTTP error: %s — %s', resp.status_code, resp.text
        )
        raise

    data   = resp.json()
    ipn_id = data.get('ipn_id')
    if not ipn_id:
        raise RuntimeError(
            f'PesaPal IPN registration returned no ipn_id. Response: {data}'
        )

    return ipn_id


# ---------------------------------------------------------------------------
# 3. Submit order request
# ---------------------------------------------------------------------------
def submit_order_request(booking) -> str:
    """
    Submit a payment order to PesaPal and return the hosted payment redirect URL.

    Saves pesapal_order_id and pesapal_tracking_id to the booking before returning.

    Constraints from PesaPal docs:
      - id (merchant reference): max 50 chars, alphanumeric + dash/underscore/dot/colon only
      - description: max 100 characters
      - billing_address.state: max 3 characters
      - billing_address: email OR phone required (at minimum one)
    """
    token  = get_auth_token()
    ipn_id = _register_ipn_url(token)

    site_url     = settings.DEFAULT_SITE_URL.rstrip('/')
    callback_url = f'{site_url}/book/confirm/{booking.reference}/'

    user = booking.user

    # state must be ≤ 3 characters per PesaPal docs — use ISO country subdivision code
    billing = {
        'email_address': user.email,
        'country_code': 'TZ',
        'first_name': (user.first_name or '')[:50],
        'last_name': (user.last_name or '')[:50],
        'line_1': 'Zanzibar, Tanzania',
        'city': 'Zanzibar',
        'state': 'ZNZ',   # 3-char max — Zanzibar subdivision code
    }

    # Add phone only if present — strip non-numeric chars, PesaPal is strict
    if user.phone:
        phone = str(user.phone).strip()
        billing['phone_number'] = phone

    amount      = float(booking.total_price)
    currency    = booking.currency
    description = _build_description(booking)   # already capped at 100 chars

    payload = {
        'id': booking.reference,           # our merchant reference, max 50 chars
        'currency': currency,
        'amount': amount,
        'description': description,
        'callback_url': callback_url,
        'notification_id': ipn_id,
        'billing_address': billing,
    }

    url = f'{_base_url()}/api/Transactions/SubmitOrderRequest'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.Timeout:
        logger.error(
            'PesaPal submit_order_request timed out — booking %s', booking.reference
        )
        raise
    except requests.HTTPError:
        logger.error(
            'PesaPal submit_order_request HTTP error: %s — %s — booking %s',
            resp.status_code, resp.text, booking.reference
        )
        raise

    data         = resp.json()
    redirect_url = data.get('redirect_url')
    tracking_id  = data.get('order_tracking_id')

    if not redirect_url:
        raise RuntimeError(
            f'PesaPal submit_order_request returned no redirect_url. '
            f'Response: {data} — booking {booking.reference}'
        )

    # Persist immediately — IPN will arrive before customer returns to callback
    booking.pesapal_order_id    = booking.reference   # our merchant reference
    booking.pesapal_tracking_id = tracking_id         # PesaPal's tracking ID
    booking.save(update_fields=['pesapal_order_id', 'pesapal_tracking_id'])

    logger.info(
        'PesaPal order submitted — booking %s — tracking_id %s',
        booking.reference, tracking_id
    )
    return redirect_url


# ---------------------------------------------------------------------------
# 4. Get transaction status — independent verification
# ---------------------------------------------------------------------------
def get_transaction_status(order_tracking_id: str) -> dict:
    """
    Independently verify payment status with PesaPal.

    NEVER trust the IPN/callback params alone — always call this.

    payment_status_description values (from docs):
        'Completed'  → payment successful   (status_code: 1)
        'Failed'     → payment failed        (status_code: 2)
        'Invalid'    → invalid transaction   (status_code: 0)
        'Reversed'   → payment reversed      (status_code: 3)
    """
    token = get_auth_token()
    url   = f'{_base_url()}/api/Transactions/GetTransactionStatus'
    # PesaPal uses camelCase query param: orderTrackingId
    params  = {'orderTrackingId': order_tracking_id}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.Timeout:
        logger.error(
            'PesaPal get_transaction_status timed out — tracking_id %s', order_tracking_id
        )
        raise
    except requests.HTTPError:
        logger.error(
            'PesaPal get_transaction_status HTTP error: %s — %s — tracking_id %s',
            resp.status_code, resp.text, order_tracking_id
        )
        raise

    data = resp.json()
    if not data:
        raise RuntimeError(
            f'PesaPal get_transaction_status returned empty response '
            f'for tracking_id {order_tracking_id}'
        )

    logger.info(
        'PesaPal status check — tracking_id %s — status %s',
        order_tracking_id,
        data.get('payment_status_description', 'UNKNOWN')
    )
    return data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _build_description(booking) -> str:
    """
    Build payment description. PesaPal hard limit: 100 characters.
    Truncate to 97 and append '...' if needed.
    """
    if booking.service_type == 'hotel' and booking.hotel:
        desc = f'Hotel: {booking.hotel.name} — {booking.reference}'
    elif booking.service_type == 'tour' and booking.tour_package:
        name = booking.tour_package.get_name('en')
        desc = f'Tour: {name} — {booking.reference}'
    elif booking.service_type == 'car' and booking.car:
        desc = f'Car Rental: {booking.car.name} — {booking.reference}'
    else:
        desc = f'Jadevine Travel & Tours — {booking.reference}'

    if len(desc) > 100:
        desc = desc[:97] + '...'

    return desc