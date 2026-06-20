# JADEVINE TRAVEL & TOURS — PHASE 6 HANDOFF
**Version 1.0 | June 2026 | PesaPal Payment Integration + Pre-Deployment**

---

## OVERVIEW

This document covers all work completed in the Phase 6 conversation. It supersedes the Phase 6 stub in `PHASE_0-5B_HANDOFF.md`. Load this document alongside `PHASE_0-5B_HANDOFF.md` at the start of the next conversation.

---

## 1. WHAT WAS COMPLETED

- **Phase 6: PesaPal REST API 3.0 integration** — full Pay Now flow, IPN callback, confirmation emails, orphan cleanup task
- **`production.py` rewrite** — all bugs fixed, production-ready
- **`config/urls.py` fix** — bookings URLs were commented out and misconfigured
- **`booking_summary.html` rebuild** — the file contained a copy of the confirmation template; the real summary/review page was missing
- **Discount display on booking summary** — strikethrough original price, discounted price, savings row
- **`BookingConfirmationView` dual-verification** — verifies payment on customer return from PesaPal (fallback for IPN failures)
- **DNS setup** — `jadevinetravel.com` registered on Namecheap, added to DigitalOcean, pointing to `64.225.77.225`
- **PesaPal tested live** — real production transaction processed (USD 0.46 via Visa), payment confirmed end-to-end

---

## 2. PESAPAL INTEGRATION ARCHITECTURE

### Service module: `apps/bookings/pesapal.py`

Four functions:

```python
get_auth_token() -> str
# Authenticates with PesaPal, returns bearer token.
# Token valid ~5 minutes — fetch fresh on every transaction, never cache.

_register_ipn_url(token) -> str
# Registers our IPN callback URL with PesaPal, returns ipn_id (GUID).
# ipn_notification_type MUST be 'GET' — PesaPal sends GET with query params.
# Called internally by submit_order_request() on every order.

submit_order_request(booking) -> str
# Submits order to PesaPal, returns hosted payment page redirect URL.
# Saves pesapal_order_id and pesapal_tracking_id to booking before returning.
# billing.state MUST be max 3 chars — use 'ZNZ' not 'Zanzibar'.
# description MUST be max 100 chars — truncated to 97 + '...' if needed.
# amount MUST be float, not Decimal — JSON serialisation fails otherwise.

get_transaction_status(order_tracking_id) -> dict
# Independent payment verification. ALWAYS call this — never trust IPN body alone.
# Returns dict with 'payment_status_description': 'Completed'|'Failed'|'Invalid'|'Reversed'
```

### Environment variables (`.env`)

```
PESAPAL_CONSUMER_KEY=M7tBfudOfbo35XA5WQS8zvhYoKpGbYz3
PESAPAL_CONSUMER_SECRET="DEljFX+Zg+HyDZ/cuDq5qXkqjuA="
PESAPAL_ENVIRONMENT=production
```

**These are the client's live production credentials from their merchant account at `pesapal.com`.** There are no separate sandbox credentials — PesaPal's developer portal registration form is broken and cannot be submitted. Testing was done directly against production with a real card (USD 0.46).

**Secret must be quoted in `.env`** — contains `+` and `=` characters. python-dotenv reads correctly when quoted.

### PesaPal base URLs (in `pesapal.py`)

```python
_SANDBOX_URL    = 'https://cybqa.pesapal.com/pesapalv3'
_PRODUCTION_URL = 'https://pay.pesapal.com/v3'
```

`_base_url()` returns production URL when `PESAPAL_ENVIRONMENT=production`.

### Settings loading (`config/settings/base.py`)

These three lines MUST exist in `base.py` — they were added during this phase:

```python
PESAPAL_CONSUMER_KEY    = os.environ.get('PESAPAL_CONSUMER_KEY', '')
PESAPAL_CONSUMER_SECRET = os.environ.get('PESAPAL_CONSUMER_SECRET', '')
PESAPAL_ENVIRONMENT     = os.environ.get('PESAPAL_ENVIRONMENT', 'sandbox')
```

Without these, `getattr(settings, 'PESAPAL_CONSUMER_KEY', '')` returns empty string even when `.env` has the values.

---

## 3. PAY NOW FLOW (end-to-end)

```
1. Customer clicks Confirm on summary page (payment_mode='pay_now')
   → BookingSummaryView._create_booking() creates Booking with payment_status='pending'
   → Redirect to /book/payment/<reference>/

2. PaymentOptionsView.get()
   → Calls submit_order_request(booking)
   → submit_order_request() calls get_auth_token() → _register_ipn_url() → SubmitOrderRequest
   → Saves pesapal_tracking_id and pesapal_order_id to booking
   → Returns PesaPal hosted payment page URL
   → View redirects customer to PesaPal

3. Customer completes payment on PesaPal hosted page
   → PesaPal sends GET IPN to /book/pesapal/callback/ (server-to-server)
   → PesaPal redirects customer to /book/confirm/<ref>/?OrderTrackingId=...&OrderMerchantReference=...

4. IPN path (pesapal_callback view):
   → Reads OrderTrackingId, OrderMerchantReference from GET params
   → Calls get_transaction_status(order_tracking_id)
   → If 'Completed': booking.payment_status='paid', booking.status='confirmed' (hotel/car)
     Tours stay 'pending_confirmation' — Jadevine must confirm tour date manually
   → Queues send_paynow_booking_confirmation_customer and send_paynow_booking_notification_admin
   → Returns JSON: {"orderNotificationType":"IPNCHANGE","orderTrackingId":"...","orderMerchantReference":"...","status":200}

5. Customer redirect path (BookingConfirmationView.get()):
   → Reads OrderTrackingId from GET params
   → If booking still pending: calls get_transaction_status() as fallback verification
   → Updates booking if Completed (idempotent — IPN may have already done it)
   → Queues emails only if IPN hasn't already (payment_status guard)
   → Renders confirmation template based on booking.payment_status
```

**Dual verification is intentional.** IPN is primary. Customer redirect callback is fallback. Both paths have an idempotency guard: `if booking.payment_status == 'pending'`. Whichever fires first wins; second is a no-op.

---

## 4. IPN CALLBACK — CRITICAL DETAILS

**View:** `pesapal_callback` in `apps/bookings/views.py`  
**URL:** `/book/pesapal/callback/` — registered outside `i18n_patterns` in `config/urls.py`  
**Decorator:** `@csrf_exempt` — PesaPal cannot send CSRF tokens  
**Method:** GET — `ipn_notification_type='GET'` was registered in `_register_ipn_url()`

**Query params PesaPal sends:**
- `OrderTrackingId` — PesaPal's tracking ID
- `OrderMerchantReference` — our booking reference
- `OrderNotificationType` — `'IPNCHANGE'` for IPN, `'CALLBACKURL'` for customer redirect

**Required JSON response** (PesaPal retries if it gets anything else):
```json
{
  "orderNotificationType": "IPNCHANGE",
  "orderTrackingId": "...",
  "orderMerchantReference": "...",
  "status": 200
}
```

**NEVER return non-200 HTTP status** — PesaPal will flood the endpoint with retries.

---

## 5. EMAIL TASKS ADDED (`apps/bookings/tasks.py`)

Two new tasks appended to existing `tasks.py` (POA tasks were already there):

- `send_paynow_booking_confirmation_customer(booking_id)` — sent after IPN confirms payment. "Payment Received!" email with green payment confirmed badge. Same table-based HTML pattern as POA email.
- `send_paynow_booking_notification_admin(booking_id)` — sent to `ADMIN_NOTIFICATION_EMAIL`. "PAYMENT RECEIVED: JDV-..." subject.
- `cancel_orphan_paynow_bookings()` — cancels PAY_NOW bookings with `payment_status='pending'` and no `pesapal_tracking_id` older than 24 hours. Register as hourly Django-Q schedule:

```python
from django_q.models import Schedule
Schedule.objects.create(
    name='Cancel orphan Pay Now bookings',
    func='apps.bookings.tasks.cancel_orphan_paynow_bookings',
    schedule_type=Schedule.HOURLY,
)
```

---

## 6. BOOKING MODEL — PAYMENT FIELDS

Already existed before Phase 6 — no migrations required:

```python
pesapal_order_id    = models.CharField(max_length=100, blank=True, null=True)
pesapal_tracking_id = models.CharField(max_length=100, blank=True, null=True)
payment_status      = models.CharField(choices=[('pending','Pending'),('paid','Paid'),
                                                 ('refunded','Refunded'),('failed','Failed')])
```

`pesapal_order_id` stores our booking reference (merchant reference).  
`pesapal_tracking_id` stores PesaPal's GUID tracking ID.

---

## 7. DISCOUNT DISPLAY ON BOOKING SUMMARY

### Session dict additions (all three booking views in `views.py`)

Hotel:
```python
'original_price_per_night': str(original_price_per_night),
'original_total': str(original_total),
'discount_percent': room_type.discount_percent,
'has_discount': room_type.has_active_discount,
'savings': str(original_total - total_price) if room_type.has_active_discount else '0',
```

Car:
```python
'original_price_per_day': str(original_price_per_day),
'original_total': str(original_total),
'discount_percent': car.discount_percent,
'has_discount': car.has_active_discount,
'savings': str(original_total - total_price) if car.has_active_discount else '0',
```

Tour:
```python
'original_price_per_person': str(original_price_per_person),
'original_total': str(original_total),
'discount_percent': tour.discount_percent,
'has_discount': tour.has_active_discount,
'savings': str(original_total - total_price) if tour.has_active_discount else '0',
```

### CSS additions (`static/css/bookings/booking_summary.css`)

Classes added: `.price-original`, `.price-original-total`, `.price-discounted`, `.price-discount-badge`, `.price-savings-row`, `.price-savings-amount`.

When `d.has_discount` is False, no discount markup is rendered — layout identical to non-discounted state.

---

## 8. BUGS FIXED DURING THIS PHASE

### `config/urls.py`
`path('book/', include('apps.bookings.urls'))` was commented out. The replacement line `path('book/pesapal/callback/', include('apps.bookings.urls'))` was wrong — it prefixed ALL booking URLs with `/book/pesapal/callback/`. Fixed: single `path('book/', include('apps.bookings.urls'))` outside `i18n_patterns`.

### `templates/bookings/booking_summary.html`
File contained a copy of `booking_confirmation.html`. The actual summary/review page with the payment mode form was never built. Rebuilt from scratch with session data rendering, payment option radio buttons, price breakdown with discount support, and trust sidebar.

### `production.py` — `ALLOWED_HOSTS` as string not list
`ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '')` returns a string. Django requires a list. Fixed: split on comma.

### `production.py` — `DEFAULT_SITE_URL` hardcoded in `base.py`
`base.py` had `DEFAULT_SITE_URL = "http://jadevinetravel.com/"` at the bottom, overwriting the `os.environ.get()` call above it. Fixed: removed the hardcoded line, reads from env only.

### `production.py` — `AWS_DEFAULT_ACL = 'public-read'`
Breaks on S3 buckets with `BlockPublicAcls` enforced (AWS default since 2023). Fixed: `AWS_DEFAULT_ACL = None`, `AWS_QUERYSTRING_AUTH = False`.

### `pesapal.py` — `ipn_notification_type` was `'POST'`
PesaPal sends IPN as GET with query params. Registering as POST meant callback never received params correctly. Fixed: `'GET'`.

### `pesapal.py` — `billing.state` max 3 chars
Was sending `'Zanzibar'` (8 chars). PesaPal validates billing fields strictly. Fixed: `'ZNZ'`.

### `pesapal.py` — `description` max 100 chars
Fixed: truncated to 97 + `'...'` if over limit.

### `views.py` — `@require_POST` on `pesapal_callback`
PesaPal sends both IPN and customer redirect as GET. `@require_POST` returned 405 on every real callback. Fixed: removed decorator, view accepts GET only.

---

## 9. PRODUCTION SETTINGS (`config/settings/production.py`)

Key additions vs the old version:

```python
# ALLOWED_HOSTS as list (was string — broke all requests)
_raw_hosts = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]

# CSRF trusted origins — required when behind Nginx proxy
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

# Connection pooling — new connection per request was expensive
'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', 60)),

# S3 — no ACL (AWS blocks public ACLs by default since 2023)
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

# Django-Q production config — no 'sync' key (would block Gunicorn workers)
Q_CLUSTER = {
    'name': 'jadevine_prod',
    'workers': 2,
    'timeout': 120,
    'retry': 180,
    'save_limit': 250,
    'compress': True,
    'orm': 'default',
}

# Full logging to /var/log/jadevine/django.log + mail_admins on ERROR
LOGGING = { ... }  # RotatingFileHandler, 10MB, 5 backups
```

Production `.env` keys required:
```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<64-char random>
ALLOWED_HOSTS=jadevinetravel.com,www.jadevinetravel.com
CSRF_TRUSTED_ORIGINS=https://jadevinetravel.com,https://www.jadevinetravel.com
DEFAULT_SITE_URL=https://jadevinetravel.com
DB_NAME=jadevine_db
DB_USER=jadevine_user
DB_PASSWORD=<strong password>
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=60
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=jadevine-media
AWS_S3_REGION_NAME=eu-west-1
SENDGRID_API_KEY=...
DEFAULT_FROM_EMAIL=Jadevine Travel & Tours <info@jadevinetravel.com>
ADMIN_NOTIFICATION_EMAIL=jadevinetravel@gmailcom
PESAPAL_CONSUMER_KEY=M7tBfudOfbo35XA5WQS8zvhYoKpGbYz3
PESAPAL_CONSUMER_SECRET="DEljFX+Zg+HyDZ/cuDq5qXkqjuA="
PESAPAL_ENVIRONMENT=production
```

---

## 10. DJANGO-Q2 vs CELERY DECISION

**Decision: keep Django-Q2 in production.** Rationale: Jadevine is a boutique travel company. Async tasks are low-frequency (confirmation emails, admin notifications). Django-Q2 with PostgreSQL broker handles this with zero additional infrastructure. Celery would require Redis as a third service on a 2GB VPS for zero business gain.

**Critical:** Remove any `'sync': True` key from `Q_CLUSTER` in production — this would execute tasks synchronously inside Gunicorn workers, blocking requests.

**Production Q_CLUSTER is defined entirely in `production.py`** — it overrides `base.py`'s definition completely.

---

## 11. PESAPAL MERCHANT ACCOUNT STATUS

- **Merchant account:** `pesapal.com` — client's business account (Jadevine Travel & Tours)
- **Consumer Status:** Valid
- **Transaction Level:** Unlimited
- **IPN URL registered:** `https://jadevinetravel.com/book/pesapal/callback/` ✅
- **Contract warning:** PesaPal email states a contract must be signed before settlements are processed. **Client must sign the PesaPal merchant contract** before going live — payments will process but funds will not be released to bank account until signed. Client logs into `pesapal.com` → Ecommerce section.
- **Sandbox:** PesaPal developer portal sign-up form is broken (does not submit). No sandbox credentials available. All testing done against production API.

---

## 12. SERVER STATE (DigitalOcean Droplet)

- **Provider:** DigitalOcean
- **IP:** `64.225.77.225`
- **Region:** AMS3 (Amsterdam)
- **Spec:** 2GB RAM / 50GB Disk
- **OS:** Ubuntu 24.04.4 LTS
- **Nginx:** 1.24.0 ✅ installed, running, default page showing
- **PostgreSQL:** 16.14 ✅ installed
- **Python:** 3.12.3 ✅
- **`/var/www/`:** only `html/` (default nginx dir) — no app deployed yet
- **Nginx sites-enabled:** only `default` — clean slate
- **Domain:** `jadevinetravel.com` → `64.225.77.225` ✅ DNS propagated
- **SSL:** not yet configured (certbot not yet run)
- **Deployment status:** NOT YET DEPLOYED — server is ready, waiting for Phase 9

---

## 13. WHAT'S NEXT — PHASE 8 (i18n, SEO & QA)

Phase 9 deployment comes after Phase 8. Do not deploy until QA is complete.

### Phase 8 — Three workstreams:

**i18n Completion:**
- French and Russian machine translations already generated — need auditing
- Portal locked to English via `PortalLanguageLockMiddleware` — do not change
- `apps/portal/` excluded from `makemessages` — do not change
- Public pages need `hreflang` meta tags for Google to serve correct language per country
- Confirm all new templates added in Phase 6 have `{% trans %}` on every user-facing string:
  - `templates/bookings/booking_summary.html` — rebuilt this phase, needs audit
  - `templates/bookings/payment_options.html` — rebuilt this phase, needs audit
  - `templates/bookings/booking_confirmation.html` — rebuilt this phase, needs audit

**SEO:**
- `sitemap.xml` auto-generated for all public pages and language variants
- `robots.txt`
- Google Analytics 4 tag in `base.html`
- Google Search Console verification meta tag

**QA checklist (from implementation plan):**

Booking flow:
- [ ] Hotel: Pay Now end-to-end — confirmed, email received, DB updated correctly
- [ ] Hotel: Pay on Arrival end-to-end
- [ ] Tour: Pay Now — stays `pending_confirmation` after payment (not `confirmed`)
- [ ] Tour: Pay on Arrival end-to-end
- [ ] Car: Pay Now with self-drive (licence number required)
- [ ] Car: Pay Now with driver option
- [ ] Car: Pay on Arrival end-to-end
- [ ] Cancellation: 14+ days → 100% refund flagged correctly
- [ ] Cancellation: 7–13 days → 50% refund flagged correctly
- [ ] Cancellation: 0–6 days → 0% refund, booking cancelled
- [ ] All confirmation emails received by customer
- [ ] All admin notification emails received

Listing approval workflow:
- [ ] Mini-admin creates hotel → approval_status=PENDING, not visible publicly
- [ ] Super Admin approves → listing appears publicly, mini-admin notified
- [ ] Super Admin rejects with reason → listing hidden, mini-admin notified with reason
- [ ] Mini-admin edits approved listing → resets to PENDING, removed from public site
- [ ] Mini-admin direct URL to another's listing → 403 Forbidden
- [ ] Mini-admin direct URL to Super Admin-only page → 403 Forbidden
- [ ] Customer account attempts to access /portal/ → redirected to portal login

User accounts:
- [ ] Registration: verification email received, link activates account
- [ ] Login: email + password, redirects correctly
- [ ] Password reset: link received, new password works
- [ ] Booking history shows correct records for logged-in user only
- [ ] Favourite add and remove via AJAX
- [ ] Profile updates saved

Admin portal:
- [ ] Super Admin login and access to all sections
- [ ] Super Admin creates hotel, tour, car with photos
- [ ] Super Admin views and updates all bookings
- [ ] Super Admin creates mini-admin, welcome email received
- [ ] Mini-admin login: sees only own sections
- [ ] Export bookings CSV downloads correctly

i18n:
- [ ] Language switcher changes UI text on every page
- [ ] Hotel/tour/car descriptions in correct language with English fallback
- [ ] /fr/ and /ru/ URL prefixes work on all public pages

Responsive and cross-browser:
- [ ] Mobile 375px: all pages usable, forms submittable
- [ ] Tablet 768px: layout correct
- [ ] Desktop 1280px+: full layout
- [ ] Chrome, Firefox, Safari, Edge: no layout breakage
- [ ] iOS Safari: Flatpickr date pickers work
- [ ] Android Chrome: same

---

## 14. AFTER PHASE 8 — PHASE 9 DEPLOYMENT

Server is ready and waiting. Domain is pointed. Execute Phase 9 after QA passes.

**Pre-deployment checklist (do before starting Phase 9):**
- [ ] Push all local changes to GitHub: `git push origin main`
- [ ] Generate production SECRET_KEY: `py -c "import secrets; print(secrets.token_urlsafe(64))"`
- [ ] Have all production `.env` values from Section 9 above ready to paste
- [ ] Have AWS S3 bucket name, IAM key and secret ready
- [ ] Have SendGrid API key ready (or confirm Gmail SMTP for initial launch)

**Phase 9 deployment sequence (12 steps):**
1. Create non-root deploy user `jadevine`, copy SSH keys
2. `apt install git python3-venv` (Nginx and PostgreSQL already installed)
3. Create PostgreSQL database and user
4. `git clone <repo> /var/www/jadevine/`
5. Create virtualenv, `pip install -r requirements.txt`
6. Create `/var/www/jadevine/.env` with all production values
7. `python manage.py migrate`
8. `python manage.py collectstatic --noinput`
9. `python manage.py createsuperuser`
10. Create systemd services: `jadevine.service` (Gunicorn) + `jadevine-qcluster.service` (Django-Q)
11. Configure Nginx: HTTP → HTTPS redirect + HTTPS proxy to Gunicorn socket
12. `certbot --nginx -d jadevinetravel.com -d www.jadevinetravel.com`

After deployment:
- Create log directory: `sudo mkdir -p /var/log/jadevine && sudo chown www-data:www-data /var/log/jadevine`
- Register orphan cleanup schedule in Django shell
- Smoke test: homepage, booking flow, PesaPal payment, admin portal, confirmation emails

---

## 14. KEY PATTERNS ADDED THIS PHASE

### PesaPal token — never cache
```python
# Always fetch fresh — tokens expire in ~5 minutes
token = get_auth_token()
```

### IPN registration — on every order, not once
`_register_ipn_url()` is called inside `submit_order_request()` on every transaction. This means the correct ngrok/domain URL is always registered, even after ngrok restarts in development.

### Dual payment verification
```python
# IPN path (pesapal_callback view) — primary
# Confirmation view path (BookingConfirmationView.get()) — fallback
# Both guarded by: if booking.payment_status == 'pending'
# Whichever fires first wins — second is a no-op
```

### Django-Q BadSignature error
Occurs when `qcluster` and `async_task()` caller use different `SECRET_KEY` values (loaded at different times). Fix: restart qcluster before running shell commands that call `async_task()`.

### Discount session keys
Always include all five discount keys in session dict when creating booking views:
`original_price_*`, `original_total`, `discount_percent`, `has_discount`, `savings`.
Template uses `d.has_discount` to conditionally render strikethrough and savings row.

---

*End of Phase 6 Handoff — Version 1.0 | June 2026*
*Prepared by Fidon for Jadevine Travel & Tours*
*This document covers Phase 6 (PesaPal) and pre-deployment state.*
*Load alongside PHASE_0-5B_HANDOFF.md in next conversation.*
