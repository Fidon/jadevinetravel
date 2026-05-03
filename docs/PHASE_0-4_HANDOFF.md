# JADEVINE TRAVEL & TOURS — PHASE HANDOFF DOCUMENT
**Version 4.2 | April 2026 | End of Phase 0, 1, 2, 3 & 4**

## PROJECT IDENTITY
**Project:** Jadevine Travel & Tours — full-stack Django booking & marketing platform
**Client:** Zanzibar-based travel company
**Developer:** Fidon (fidonamos@gmail.com, +255 713 529 019)
**Root folder:** jadevinetravel/
**Django version:** 6.0.4
**Python:** 3.13 (venv)
**OS:** Windows (PowerShell)
**Database (dev):** SQLite — file named jadevine_db.sqlite3
**Database (prod):** PostgreSQL
**Media (dev):** Local filesystem
**Media (prod):** AWS S3

## DJANGO SETTINGS MODULE
Active settings: `config.settings.development`

Set in `.env`:
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-secret-key-here
DEFAULT_FROM_EMAIL=Jadevine Travel & Tours fidonamos@gmail.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_NOTIFICATION_EMAIL=fidontakakwa@gmail.com

Settings split:
- `config/settings/base.py` — shared
- `config/settings/development.py` — SQLite, local media, DEBUG=True
- `config/settings/production.py` — PostgreSQL, AWS S3, SendGrid, DEBUG=False

**Key settings in `config/settings/base.py`:**
```python
ACCOUNT_ADAPTER = 'apps.accounts.adapters.AccountAdapter'
ACCOUNT_FORMS = {'signup': 'apps.accounts.forms.CustomSignupForm'}
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = '/accounts/password/change/'
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ADMIN_NOTIFICATION_EMAIL = os.environ.get('ADMIN_NOTIFICATION_EMAIL', 'fidontakakwa@gmail.com')
```

## TECH STACK
| Layer | Technology |
|---|---|
| Backend | Python / Django 6.0.4 |
| Frontend | HTML5, CSS3, jQuery 3.7.1, Bootstrap 5.3.3 |
| Icons | Bootstrap Icons 1.11.3 |
| Fonts | Cormorant Garamond + Jost (Google Fonts) |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Auth | django-allauth 65.16.0 (email/password; OAuth post-launch) |
| Task Queue | django-q2 with Django ORM broker |
| Media Storage | Local (dev) → AWS S3 via django-storages (prod) |
| Email | Gmail SMTP (dev) → SendGrid (prod) |
| PDF Generation | ReportLab |
| Payments | PesaPal REST API 3.0 (Phase 6) |
| Lightbox | GLightbox (CDN) |
| Date Pickers | Flatpickr (CDN) |
| Flights | Amadeus API — POST-LAUNCH, do not implement |
| Hotels API | Expedia EAN — POST-LAUNCH, do not implement |
| Hosting | VPS: DigitalOcean or Hetzner, Nginx + Gunicorn |
| SSL | Let's Encrypt |

## INSTALLED PACKAGES (requirements.txt)
asgiref==3.11.1
boto3==1.42.89
botocore==1.42.89
certifi==2026.2.25
charset-normalizer==3.4.7
Django==6.0.4
django-allauth==65.16.0
django-picklefield==3.4.0
django-q2==1.9.0
django-storages==1.14.6
gunicorn==25.3.0
idna==3.11
jmespath==1.1.0
packaging==26.0
pillow==12.2.0
psycopg2-binary==2.9.11
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
reportlab==4.4.10
requests==2.33.1
s3transfer==0.16.0
six==1.17.0
sqlparse==0.5.5
tzdata==2026.1
urllib3==2.6.3
whitenoise==6.12.0

## PROJECT FOLDER STRUCTURE
jadevinetravel/
├── apps/
│   ├── init.py
│   ├── accounts/
│   │   ├── adapters.py               ✅ COMPLETE
│   │   ├── forms.py                  ✅ COMPLETE
│   │   ├── models.py                 ✅ COMPLETE
│   │   ├── tasks.py                  ✅ COMPLETE — cancellation + cleanup emails
│   │   ├── urls.py                   ✅ COMPLETE
│   │   └── views.py                  ✅ COMPLETE
│   ├── bookings/
│   │   ├── models.py                 ✅ COMPLETE (cancellation_requested + is_refundable added)
│   │   ├── forms.py                  ✅ COMPLETE
│   │   ├── tasks.py                  ✅ COMPLETE — POA booking emails (HTML)
│   │   ├── views.py                  ✅ COMPLETE
│   │   └── urls.py                   ✅ COMPLETE
│   ├── hotels/                       ✅ COMPLETE (Phase 2 + discount + refund policy)
│   ├── tours/                        ✅ COMPLETE (Phase 3 + discount + refund policy)
│   ├── cars/                         ✅ COMPLETE (Phase 2 + discount + refund policy)
│   ├── reviews/                      ✅ COMPLETE — Review model, SubmitReviewView
│   ├── gallery/                      — models only
│   ├── contact/                      — models only
│   ├── portal/                       — stub only (Phase 5)
│   └── core/                         ✅ COMPLETE (Phase 1)
├── templates/
│   ├── base.html                     ✅ COMPLETE
│   ├── account/                      ← allauth overrides (singular)
│   │   ├── login.html                ✅ COMPLETE
│   │   ├── signup.html               ✅ COMPLETE
│   │   ├── email_confirm.html        ✅ COMPLETE — auto-confirms on page load
│   │   ├── verification_sent.html    ✅ COMPLETE
│   │   ├── resend_verification.html  ✅ COMPLETE
│   │   ├── password_reset.html       ✅ COMPLETE
│   │   ├── password_reset_done.html  ✅ COMPLETE
│   │   ├── password_reset_from_key.html          ✅ COMPLETE
│   │   ├── password_reset_from_key_done.html     ✅ COMPLETE
│   │   ├── password_change.html      ✅ COMPLETE — extends dashboard_base.html
│   │   ├── logout.html               ✅ COMPLETE
│   │   └── email/
│   │       ├── email_confirmation_signup_subject.txt
│   │       ├── email_confirmation_signup_message.txt
│   │       ├── email_confirmation_signup_message.html    ✅ branded HTML
│   │       ├── email_confirmation_subject.txt
│   │       ├── email_confirmation_message.txt
│   │       ├── email_confirmation_message.html           ✅ branded HTML
│   │       ├── password_reset_key_subject.txt
│   │       ├── password_reset_key_message.txt
│   │       ├── password_reset_key_message.html           ✅ branded HTML
│   │       ├── cancellation_requested_customer_message.html  ✅ branded HTML
│   │       ├── cancellation_confirmed_customer_message.html  ✅ branded HTML
│   │       └── cancellation_admin_message.html               ✅ branded HTML
│   ├── accounts/                     ← our dashboard templates (plural)
│   │   ├── dashboard_base.html       ✅ COMPLETE
│   │   ├── dashboard.html            ✅ COMPLETE
│   │   ├── booking_history.html      ✅ COMPLETE — full card clickable
│   │   ├── booking_detail.html       ✅ COMPLETE — review form/display included
│   │   ├── profile.html              ✅ COMPLETE
│   │   ├── favourites.html           ✅ COMPLETE
│   │   └── includes/
│   │       └── dashboard_sidebar.html ✅ COMPLETE
│   ├── core/                         ✅ COMPLETE
│   ├── hotels/                       ✅ COMPLETE — discount badges, refund notices
│   ├── tours/                        ✅ COMPLETE — discount badges, refund notices
│   ├── cars/                         ✅ COMPLETE — discount badges, refund notices
│   ├── bookings/                     ✅ COMPLETE
│   ├── gallery/                      stub only
│   ├── contact/                      stub only
│   └── portal/                       stub only
├── static/
│   ├── css/
│   │   ├── main.css                  ✅ COMPLETE
│   │   ├── accounts/
│   │   │   ├── auth.css              ✅ COMPLETE
│   │   │   └── dashboard.css         ✅ COMPLETE
│   │   ├── core/home.css             ✅ COMPLETE
│   │   ├── hotels/                   ✅ COMPLETE
│   │   ├── tours/                    ✅ COMPLETE
│   │   ├── cars/                     ✅ COMPLETE
│   │   └── bookings/                 ✅ COMPLETE
│   └── js/
│       ├── main.js                   ✅ COMPLETE
│       ├── accounts/
│       │   ├── auth.js               ✅ COMPLETE
│       │   ├── dashboard_base.js     ✅ COMPLETE
│       │   ├── dashboard.js          ✅ COMPLETE
│       │   ├── booking_detail.js     ✅ COMPLETE — star picker integrated
│       │   ├── profile.js            ✅ COMPLETE
│       │   └── favourites.js         ✅ COMPLETE
│       ├── core/home.js              ✅ COMPLETE
│       ├── hotels/                   ✅ COMPLETE
│       ├── tours/                    ✅ COMPLETE
│       ├── cars/                     ✅ COMPLETE
│       └── bookings/                 ✅ COMPLETE
└── locale/
├── en/LC_MESSAGES/
├── fr/LC_MESSAGES/
└── ru/LC_MESSAGES/

## URL STRUCTURE (config/urls.py)
```python
# NOT language-prefixed
/admin/                              — Django built-in admin (developer only)
/book/                               — All booking flow URLs
/reviews/                          — reviews flow URLs
/portal/                             — Admin portal (Phase 5)
/i18n/                               — Django language switching

# Language-prefixed via i18n_patterns
/                                    — Homepage
/hotels/                             — Hotel listing
/hotels/<slug>/                      — Hotel detail
/hotels/<slug>/book/                 — Hotel booking POST
/tours/                              — Tour listing
/tours/<slug>/                       — Tour detail
/tours/<slug>/book/                  — Tour booking POST
/cars/                               — Car listing
/cars/<slug>/                        — Car detail
/cars/<slug>/book/                   — Car booking POST
/gallery/                            — Gallery
/about/                              — About Us
/contact/                            — Contact Us
/contact/newsletter/                 — Newsletter subscribe (AJAX POST)

# Accounts — our views (language-prefixed)
/accounts/dashboard/
/accounts/bookings/
/accounts/bookings/<reference>/
/accounts/bookings/<reference>/cancel/
/accounts/bookings/<reference>/pdf/
/accounts/bookings/<reference>/review/   — SubmitReviewView (POST only)
/accounts/profile/
/accounts/favourites/
/accounts/favourites/toggle/
/accounts/resend-verification/

# Allauth URLs (language-prefixed)
/accounts/login/                     — JadevineLoginView (custom override)
/accounts/signup/                    — uses CustomSignupForm
/accounts/logout/
/accounts/confirm-email/<key>/
/accounts/confirm-email/
/accounts/password/reset/
/accounts/password/reset/done/
/accounts/password/reset/key/<key>/
/accounts/password/change/           — extends dashboard_base.html
```

App namespaces: `core`, `hotels`, `tours`, `cars`, `bookings`, `reviews`, `gallery`, `contact`, `accounts`, `portal`

## ALL DATABASE MODELS (fully migrated)

### apps/accounts/models.py
**CustomUser** (extends AbstractUser)
- `email` — login identifier for customers
- `username` — login identifier for admin/mini-admin
- `first_name`, `last_name`, `phone`, `nationality`
- `preferred_language` — choices: en, fr, ru
- `profile_photo` — ImageField (upload_to='profiles/')
- `is_staff` — True for Super Admin and Mini-Admin portal access
- `AUTH_USER_MODEL = 'accounts.CustomUser'`
- Property: `full_name` — returns `first_name + last_name` stripped, fallback to email
- Use `user.get_full_name()` in Python code
- Use `{{ user.get_full_name|default:user.email }}` in templates

**MiniAdminProfile**
- `user` — OneToOneField → CustomUser
- `created_by` — ForeignKey → CustomUser
- Check `hasattr(user, 'miniadminprofile')` to distinguish mini-admin from super admin

### apps/hotels/models.py
**Hotel** — unchanged field list from Phase 2. No discount or policy at hotel level.
**HotelRoomType** — two new fields added in Phase 2 updates:
- `is_refundable` — BooleanField (default `True`). When `False`, global `CancellationPolicy` tiers are bypassed — no refund issued regardless of cancellation timing.
- `allows_pay_on_arrival` — BooleanField (default `True`). When `False`, Pay on Arrival option is suppressed in UI and enforced server-side in `BookingSummaryView._create_booking()`.
- `discount_percent` — PositiveIntegerField (0–99, default 0). Active discount percentage.
- `discount_expires_at` — DateTimeField (nullable). When `None`, discount is permanent. When set, discount becomes inactive automatically once datetime passes — checked at query time via `timezone.now()`, no scheduled task needed.
- Method: `get_discounted_price()` — returns calculated discounted price if active discount exists, else `None`.
- Method: `get_display_price()` — returns discounted price if active, else base price. **This is the single method used everywhere a price is shown or snapshotted. Never call `price_per_night` directly for display or snapshotting.**
- Property: `has_active_discount` — boolean, used in templates and serializers.

**Why discount is at room type level, not hotel level:** A hotel can have a flexible rate room and a non-refundable discounted room simultaneously.

### apps/cars/models.py
**CarRental** — two new fields added in Phase 2 updates:
- `is_refundable` — BooleanField (default `True`). Same semantics as `HotelRoomType.is_refundable`.
- `allows_pay_on_arrival` — BooleanField (default `True`). Same semantics as `HotelRoomType.allows_pay_on_arrival`.
- `discount_percent` — PositiveIntegerField (0–99, default 0).
- `discount_expires_at` — DateTimeField (nullable).
- Method: `get_discounted_price()` — discounted price or `None`.
- Method: `get_display_price()` — discounted price if active, else `price_per_day`. **Always use this for display and snapshotting.**
- Property: `has_active_discount` — boolean.

### apps/tours/models.py
**TourPackage** — two new fields added in Phase 2 updates:
- `is_refundable` — BooleanField (default `True`).
- `allows_pay_on_arrival` — BooleanField (default `True`).
- `discount_percent` — PositiveIntegerField (0–99, default 0).
- `discount_expires_at` — DateTimeField (nullable).
- Method: `get_discounted_price()` — discounted price per person or `None`.
- Method: `get_display_price()` — discounted price per person if active, else `price_per_person`. **Always use this for display and snapshotting.**
- Property: `has_active_discount` — boolean.

### apps/bookings/models.py
**CancellationPolicy** — unchanged from Phase 3.
**Booking** — updated fields:
STATUS_CHOICES = [
    ('pending_confirmation', _('Pending Confirmation')),
    ('confirmed', _('Confirmed')),
    ('cancellation_requested', _('Cancellation Requested')),  # added Phase 4
    ('cancelled', _('Cancelled')),
    ('completed', _('Completed')),
    ('no_show', _('No Show')),
]

New field added in Phase 2 updates:
- `is_refundable` — BooleanField (default `True`). **Snapshotted at booking creation time** from the listing's `is_refundable` value. Never retroactively affected by future listing changes. If `False`, cancellation always produces 0% refund regardless of `CancellationPolicy` tiers.

**Snapshotting order of operations in `BookingSummaryView._create_booking()`:**
1. Read `get_display_price()` from listing → snapshot into `base_price` and `total_price`
2. Read `is_refundable` from listing → snapshot into `booking.is_refundable`
3. Check `allows_pay_on_arrival` from listing → enforce server-side if `payment_mode='pay_on_arrival'` was selected

### apps/reviews/models.py (new app — Phase 4)
**Review**
id                  AutoField (PK)
user                ForeignKey → CustomUser (on_delete=PROTECT)
booking             OneToOneField → Booking (on_delete=PROTECT)
— OneToOneField enforces one review per booking at DB level.
No application-layer deduplication needed. No race condition possible.
service_type        CharField — choices: hotel/tour/car (discriminator)
hotel               ForeignKey → Hotel (nullable)
tour_package        ForeignKey → TourPackage (nullable)
car                 ForeignKey → CarRental (nullable)
rating              PositiveIntegerField — 1 to 10
— validated by MinValueValidator(1) and MaxValueValidator(10)
comment             TextField (nullable, blank=True)
status              CharField — choices: pending/approved/rejected
— all reviews start as 'pending', require moderation before appearing publicly
rejection_reason    TextField (nullable) — populated when status='rejected',
surfaced to customer on booking detail page
moderated_by        ForeignKey → CustomUser (nullable, related_name='moderated_reviews')
moderated_at        DateTimeField (nullable)
created_at          DateTimeField (auto_now_add=True)
updated_at          DateTimeField (auto_now=True)

**Review display threshold:** Ratings are only displayed when a listing has **at least 3 approved reviews**. Below that threshold, no rating badge appears anywhere on the site. This prevents misleading single-review ratings on new listings.

**Average rating computation:** Calculated as a queryset annotation using Django's `Avg` and `Count` aggregates in list and detail views. No denormalized field on the listing model — no sync issues possible.

```python
# Pattern used in list and detail views:
from django.db.models import Avg, Count
from apps.reviews.models import Review

hotels = Hotel.objects.filter(...).annotate(
    avg_rating=Avg(
        'reviews__rating',
        filter=Q(reviews__status='approved')
    ),
    review_count=Count(
        'reviews',
        filter=Q(reviews__status='approved')
    ),
).filter(review_count__gte=3)  # threshold applied here

# Badge only rendered when review_count >= 3
```

**Who can moderate reviews:**
- Super Admin: can approve or reject any review across all listings
- Mini-Admin: can approve or reject reviews for their own hotel and car listings only
- Mini-Admin cannot moderate tour package reviews (tours are Super Admin only)
- Moderation UI lives in the admin portal (Phase 5 deliverable)

### apps/gallery/models.py
GalleryCategory, GalleryItem — unchanged from Phase 3.

### apps/contact/models.py
ContactMessage, NewsletterSubscriber — unchanged from Phase 3.

### apps/core/models.py
SavedFavourite — unchanged from Phase 3.

## AUTHENTICATION SYSTEM
**Two completely separate auth flows:**

**1. Customers** — email + password via django-allauth
- Extra fields at signup: `first_name`, `last_name`, `preferred_language`
- `AccountAdapter.save_user()` saves extra fields
- Email verification mandatory
- `JadevineLoginView` — custom login view override

**2. Admin / Mini-Admin** — username + password via Django built-in auth
- Login at `/portal/login/` (Phase 5)
- `is_staff = True` required
- Check `hasattr(user, 'miniadminprofile')` to identify mini-admin vs super admin

**Allauth settings in base.py:**
```python
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_ADAPTER = 'apps.accounts.adapters.AccountAdapter'
ACCOUNT_FORMS = {'signup': 'apps.accounts.forms.CustomSignupForm'}
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = '/accounts/password/change/'
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
```

## CUSTOM ALLAUTH ADAPTER (apps/accounts/adapters.py)
Full responsibilities:
- `save_user()` — saves `first_name`, `last_name`, `preferred_language` from signup form
- `format_email_subject()` — strips `[Site Name]` prefix from all email subjects using regex
- `add_message()` — suppresses these allauth system messages:
  - `account/messages/logged_out.txt`
  - `account/messages/email_confirmation_sent.txt`
  - `account/messages/logged_in.txt`
- `get_logout_redirect_url()` — redirects to `/` after logout
- `render_mail()` — forces HTML+plain multipart emails for all allauth emails. Handles `self.request = None` safely. Logs warnings on template render failure.

**Critical — allauth 65.x email template prefixes (verified by logging):**
| Email type | Template prefix |
|---|---|
| Signup verification | `account/email/email_confirmation_signup` |
| Resend verification | `account/email/email_confirmation` |
| Password reset | `account/email/password_reset_key` |

Each prefix requires: `_subject.txt`, `_message.txt`, `_message.html`

## CUSTOM SIGNUP FORM (apps/accounts/forms.py)
**CustomSignupForm** — extends `AllauthSignupForm`:
- Adds: `first_name`, `last_name`, `preferred_language`
- Applies `jd-input` CSS class to all fields
- `save(request)` delegates to adapter via `super()`

**ProfileUpdateForm** — ModelForm for CustomUser:
- Fields: `first_name`, `last_name`, `phone`, `nationality`, `preferred_language`, `profile_photo`
- Profile photo rendered as **raw `<input type="file">`** — NOT `{{ form.profile_photo }}`
- "Remove" checkbox: `name="profile_photo-clear"` — Django recognises this as the clear signal

**CancellationForm**: `cancellation_reason` (optional), `confirm` (required checkbox)

## DISCOUNT SYSTEM
Applies to all three bookable services. Architecture is identical across all three.

### How it works
- `discount_percent` (0–99) and `discount_expires_at` (nullable DateTimeField) are on each listing model at the appropriate level (room type for hotels, listing level for cars and tours).
- When `discount_expires_at` is `None` → discount is permanent until manually removed.
- When `discount_expires_at` is set → discount expires automatically at that datetime. Checked at query time via `timezone.now()` comparison in model method. No scheduled task required.

### Three methods on each model
```python
def get_discounted_price(self):
    """Returns calculated discounted price if active discount exists, else None."""
    if self.discount_percent > 0:
        expires = self.discount_expires_at
        if expires is None or expires > timezone.now():
            return self.base_price * (1 - self.discount_percent / 100)
    return None

def get_display_price(self):
    """Single method used for ALL display and snapshotting. Never bypass this."""
    discounted = self.get_discounted_price()
    return discounted if discounted is not None else self.base_price

@property
def has_active_discount(self):
    return self.get_discounted_price() is not None
```

### Display across surfaces
- **List cards:** Red pill badge "X% OFF" in top-right corner of card image. Original price struck through with `.jd-price-original` CSS class. Discounted price shown in primary price position. Injected by JavaScript as part of AJAX card rendering.
- **Detail pages:** Discount badge in price panel header alongside struck-through original and discounted price. Rendered server-side.
- **Hotel room type cards:** Each room shows its own discount badge and price treatment independently.
- **Booking summary page:** Price breakdown reflects already-discounted price per unit (snapshotted at form submission time).

### Price snapshotting with discount
When user submits booking form, `get_display_price()` is called and the result stored in session. This discounted price is what gets snapshotted into `Booking.base_price` and `Booking.total_price` at confirm. Customer pays what was shown. Never recalculate from listing after booking is created.

## PER-LISTING REFUND & PAYMENT POLICY

### Fields
- `is_refundable` (BooleanField, default `True`) — on `HotelRoomType`, `CarRental`, `TourPackage`
- `allows_pay_on_arrival` (BooleanField, default `True`) — on `HotelRoomType`, `CarRental`, `TourPackage`
- `is_refundable` (BooleanField, default `True`) — also snapshotted onto `Booking` model at creation

### `is_refundable` behaviour
- When `True`: normal `CancellationPolicy` tier lookup applies.
- When `False`: global `CancellationPolicy` tiers are bypassed entirely. Refund is always 0% regardless of cancellation timing. The `_get_refund_info()` helper in `views.py` checks `booking.is_refundable` before querying `CancellationPolicy`.

### `allows_pay_on_arrival` behaviour
- When `True`: Pay on Arrival is available (if not disabled globally).
- When `False`: Pay on Arrival option suppressed in UI. Enforced server-side in `BookingSummaryView._create_booking()` — if `payment_mode='pay_on_arrival'` arrives in POST but session data shows `allows_pay_on_arrival=False`, the request is rejected. UI suppression alone is not sufficient.

### Snapshotting
`booking.is_refundable` is written at booking creation time from the listing's current value. Future changes to the listing do not affect existing bookings. This mirrors the price snapshotting pattern.

### UI propagation
- **Hotel detail page:** When a non-refundable room type is selected, a red warning notice appears in the booking panel. Pay on Arrival footer note is hidden for rooms where `allows_pay_on_arrival=False`. These notices toggled by JavaScript on room selection.
- **Car/Tour detail pages:** Refund notice and Pay on Arrival availability rendered server-side (not toggled by JS, since there is no room selection step).
- **Booking summary page:** When `allows_pay_on_arrival=False` is stored in session, Pay on Arrival radio is not rendered — replaced with a notice: "Online payment required for this booking." The trust sidebar "Free Cancellation" item is replaced with "Non-refundable" when the booking is non-refundable.
- **Booking confirmation page:** Non-refundable badge appears in booking summary row.

## CUSTOMER REVIEWS SYSTEM (apps/reviews/)

### Architecture decisions
- **One review per booking:** Enforced by `OneToOneField` on `booking` at DB level. No race condition, no application-layer deduplication needed.
- **Eligibility gate:** `booking.status == 'completed'` AND `booking.user == request.user` — both checked server-side in `SubmitReviewView` before any form validation.
- **All reviews start as `pending`:** No review appears publicly until moderated.
- **Moderation:** Super Admin moderates all. Mini-Admin moderates only their own hotel and car listing reviews. Mini-Admin cannot moderate tour reviews. Moderation UI is a Phase 5 portal deliverable.

### SubmitReviewView (apps/reviews/views.py)
- POST only — no GET (form is rendered inside `booking_detail.html`)
- URL: `/accounts/bookings/<reference>/review/`
- Guards: `LoginRequiredMixin`, ownership check, `status == 'completed'` check
- On valid submission: creates `Review` with `status='pending'`, returns success state
- On duplicate attempt: returns already-submitted state (OneToOneField will raise `IntegrityError` if bypassed)

### ReviewForm (apps/reviews/forms.py)
- Fields: `rating` (hidden input, set by JS star picker), `comment` (optional textarea)
- Client-side guard: form submit blocked by JS if no rating committed (hidden input empty)
- Server-side validation: `MinValueValidator(1)`, `MaxValueValidator(10)` on model

### BookingDetailView context additions
Two new context variables passed to `booking_detail.html`:
```python
existing_review = Review.objects.filter(booking=booking).first()
can_review = (booking.status == 'completed') and (existing_review is None)
context['existing_review'] = existing_review
context['can_review'] = can_review
```

### Three states in booking_detail.html review section
1. **Not completed:** Nothing rendered — no review prompt shown.
2. **Completed, no review yet:** Star picker form rendered. Submit POSTs to `accounts:submit_review`.
3. **Completed, review submitted:** Read-only display of rating, comment, and current moderation status badge (`pending` / `approved` / `rejected`). If `rejected`, `rejection_reason` is shown to the customer.

### Star rating picker (booking_detail.js)
- 10-star interactive picker built in jQuery, integrated into existing IIFE
- Hover: preview fill up to hovered position (CSS class)
- Click: lock in rating, update `#id_rating` hidden input, enable submit button
- Keyboard: `Enter` and `Space` on focused star — fully accessible
- Colour scale per star: CSS custom properties per `nth-child`, red (1) → amber → yellow (5–6) → green (10)
- Human-readable labels (Terrible through Perfect) defined in `window.JD_STRINGS` before JS loads — translatable

### Rating display on listing cards and detail pages
- **Threshold rule:** Rating badge only shown when listing has ≥ 3 approved reviews. Below threshold, no badge appears anywhere.
- **List cards:** Average rating and review count injected by JavaScript as part of AJAX card rendering.
- **Detail pages:** Rendered server-side by Django view annotation.
- **Annotation pattern:**
```python
from django.db.models import Avg, Count, Q
queryset = queryset.annotate(
    avg_rating=Avg('reviews__rating', filter=Q(reviews__status='approved')),
    review_count=Count('reviews', filter=Q(reviews__status='approved')),
)
# In template: only show badge when review_count >= 3
```

## DASHBOARD VIEWS (apps/accounts/views.py)
**JadevineLoginView** — extends `AllauthLoginView`:
- `get_context_data()` — sets `unverified_email=True` only when submitted email belongs to an existing `is_active=False` account
- Error message: "Incorrect email address or password."
- Resend verification link only shown when `{{ unverified_email }}` is `True`

**DashboardView** — upcoming bookings via Q objects across all three date fields.

**BookingHistoryView** — paginated (10/page), filterable by status.

**BookingDetailView**:
- Ownership: `get_object_or_404(..., user=request.user)`
- `cancellable`: status in `pending_confirmation/confirmed` AND `service_date > today`
- Refund info only shown when `booking.payment_status == 'paid'` AND `booking.is_refundable == True`
- Cancellation modal refund summary: same guard
- Status banner with descriptive sentence per status
- `existing_review` and `can_review` context variables for review section

**CancelBookingView**:
- Checks `booking.is_refundable` before computing refund — if `False`, refund is 0% regardless of `CancellationPolicy`
- `PAY_NOW` + refund > 0% → `status='cancellation_requested'`
- `PAY_NOW` + 0% refund OR `PAY_ON_ARRIVAL` → `status='cancelled'` immediately

**ProfileView**: raw file input for photo, not Django widget.

**FavouritesView** + **ToggleFavouriteView**: AJAX toggle.

**BookingPDFView**: ReportLab PDF — flat Table header (no nested tables), gold accent line, status colour-coded, footer with +255 713 529 019.

**ResendVerificationView**: sends only to existing unverified accounts, silent for unknown emails.

## CANCELLATION FLOW
Customer submits cancellation:
│
├── booking.is_refundable == False (snapshotted at booking time)
│     → refund = 0% regardless of cancellation timing
│     → status = 'cancelled' immediately
│     → Customer email: no refund applies
│     → Admin notified
│
├── booking.is_refundable == True, PAY_NOW + refund > 0%
│     → status = 'cancellation_requested'
│     → Branded HTML email to customer
│     → Branded HTML alert to fidontakakwa@gmail.com
│     → Admin processes PesaPal refund manually
│     → Admin marks payment_status='refunded' in portal (Phase 5)
│
├── booking.is_refundable == True, PAY_NOW + 0% refund (0-6 days)
│     → status = 'cancelled' immediately
│     → Customer email: no refund applies
│     → Admin notified
│
└── PAY_ON_ARRIVAL (any)
→ status = 'cancelled' immediately
→ Customer email sent
→ Admin notified (no refund action needed)

**Refund info display rules:**
- Cancellation policy card: only when `payment_status == 'paid'` AND `booking.is_refundable == True`
- Cancel modal refund summary: same guard
- PAY_ON_ARRIVAL pending → no refund messaging anywhere

## EMAIL TASKS

### apps/accounts/tasks.py — Cancellation emails
Admin emails always go to `fidontakakwa@gmail.com` (`ADMIN_EMAIL` constant).

Template context variables:

**cancellation_requested_customer_message.html:**
`first_name`, `reference`, `service_name`, `payment_mode`, `currency`, `refund_pct`, `refund_amount`

**cancellation_confirmed_customer_message.html:**
`first_name`, `reference`, `service_name`, `payment_mode`, `no_refund` (bool)

**cancellation_admin_message.html:**
`reference`, `customer_name`, `customer_email`, `service_name`, `payment_mode`, `reason`, `is_pay_now` (bool)
When `is_pay_now=True`: also `currency`, `total`, `refund_pct`, `refund_amount`, `portal_url`

**Cleanup task:**
`cleanup_unverified_accounts()` — daily Django-Q scheduled task. Deletes `is_active=False` users older than 7 days with no bookings. Never deletes `is_staff=True` accounts. Registered via migration `accounts/0002_seed_cleanup_schedule`.

### apps/bookings/tasks.py — POA booking emails
- `send_poa_booking_confirmation_customer(booking_id)` — branded HTML to customer
- `send_poa_booking_notification_admin(booking_id)` — branded HTML to admin at `ADMIN_NOTIFICATION_EMAIL`

**Admin email amount display:** `<table>` based — Gmail strips `display:flex`. Amount right-aligned via `text-align:right` on `<td>`.
**Portal button color:** `#c89666` (gold) — never blue.

Admin email recipient resolution:
```python
admin_email = getattr(settings, 'ADMIN_NOTIFICATION_EMAIL', settings.DEFAULT_FROM_EMAIL)
if '<' in admin_email:
    admin_email = admin_email.split('<')[1].rstrip('>')
```

## EMAIL HTML DESIGN RULES
**Never use `display:flex` or `display:grid` in email HTML.**
Gmail strips these. Use `<table>` for all multi-column layouts, amount rows, and header layouts.

**Correct two-column pattern:**
```html
<table width="100%" cellpadding="0" cellspacing="0">
  <tr>
    <td style="...">Left content</td>
    <td style="text-align:right;...">Right content</td>
  </tr>
</table>
```

**All email templates use:**
- Green header `#1a4d2e` with brand name and gold tagline `#c89666`
- Inline CSS only — no `<link>` tags
- Plain text body always included
- Mobile responsive via `@media (max-width: 620px)`
- Footer: `Jadevine Travel & Tours | Zanzibar, Tanzania | info@jadevinetours.com | +255 713 529 019`

## PDF BOOKING CONFIRMATION (BookingPDFView)
**Header:** Single flat `Table` with 2 rows × 2 columns. No nested tables — ReportLab clips nested content.
```python
header_table = Table(
    [[brand_paragraph, label_paragraph],
     [tagline_paragraph, doc_title_paragraph]],
    colWidths=[usable_w * 0.55, usable_w * 0.45],
)
```
Right column: `('ALIGN', (-1, 0), (-1, -1), 'RIGHT')` in TableStyle.
Gold accent line: `('LINEBELOW', (0, -1), (-1, -1), 3, ACCENT)`.
`topMargin=10 * mm` — prevents clipping.

**Status colour:** Green (`confirmed`), red (`cancelled`), gold (all others).
**Footer:** `+255 713 529 019`

## BOOKING DETAIL PAGE — KEY BEHAVIOURS
**Status banner:** Icon + bold status + descriptive sentence per status. `.dash-status-icon` has `line-height: 1.5` for alignment.

**Cancellation policy card:**
Only shown when: cancellable=True AND refund_info is not None
AND booking.payment_status == 'paid'
AND booking.is_refundable == True

**Cancel modal refund summary:** Same guard as above.

**Review section:** Three conditional states based on `can_review` and `existing_review` context variables.

**Clickable booking cards (dashboard + booking history):**
- Entire card is clickable via CSS absolute-positioned anchor (`position: absolute; inset: 0`)
- Card set to `position: relative`
- Interactive children (badges, buttons) lifted via `z-index: 2`
- Arrow `<a>` tag converted to `<span>` — purely decorative now
- Accessible label carried by the stretched anchor

## DJANGO-Q SCHEDULED TASKS
Registered via migration `accounts/0002_seed_cleanup_schedule`:
```python
Schedule(
    name='Cleanup unverified accounts',
    func='apps.accounts.tasks.cleanup_unverified_accounts',
    schedule_type='D',
    repeats=-1,
)
```

Run worker: `python manage.py qcluster`

## DASHBOARD LAYOUT SYSTEM
**Navbar overlap fix:**
```css
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  padding-top: 72px;
}
```

**Sidebar desktop:** `position: sticky; top: 0; height: calc(100vh)`
**Sidebar mobile:** `position: fixed; transform: translateX(-100%)` — opens via `#sidebarToggleBtn`
**`password_change.html`** extends `dashboard_base.html`. Located at `templates/account/password_change.html` (allauth path, singular).

## PROFILE PHOTO — IMPLEMENTATION NOTE
Raw `<input type="file">` used instead of `{{ form.profile_photo }}`:
```html
<input type="file" name="profile_photo" id="id_profile_photo"
       accept="image/jpeg,image/png,image/gif">
```
Remove checkbox: `name="profile_photo-clear"`. Only rendered when `{% if user.profile_photo %}`.

## FAVOURITE TOGGLE — AJAX
**Request:** JSON `{ "item_type": "hotel"|"tour"|"car", "item_id": <int> }`
**Note:** `item_type='tour'` maps to FK field `tour_package` — not `tour`.
**Response:** `{ "saved": true|false }`

## MESSAGES SYSTEM
**Suppressed (never shown):**
- "You have signed out"
- "Verification email sent"
- "Successfully signed in as X"

**Auto-dismiss:** `auth.js` fades `.auth-alert-info` and `.auth-alert-success` after 4 seconds.
**Password change success:** Shows on `/accounts/password/change/` page.

## SITES FRAMEWORK
Configure at `/admin/sites/site/`:
- **Domain:** `127.0.0.1:8000` (dev) → `yourdomain.com` (prod)
- **Display name:** `Jadevine Travel & Tours`

Without this, allauth emails show `[example.com]` in subjects.

## EMAIL CONFIRM PAGE — AUTO-CONFIRM
1. Page loads → spinner + "Verifying…"
2. After 800ms → AJAX POST to confirm URL
3. Success → green checkmark + "Email confirmed!" + Sign In button
4. After 2.5s → auto-redirects to login
5. AJAX error → manual confirm button fallback
6. Invalid/expired → error state + resend link

## BOOKING SYSTEM ARCHITECTURE (unchanged from Phase 3)
Session-first, DB-on-confirm. `SESSION_BOOKING_KEY = 'pending_booking'`

**Snapshotting at session storage time:**
1. `get_display_price()` → stored in session
2. `is_refundable` from listing → stored in session
3. `allows_pay_on_arrival` from listing → stored in session, enforced server-side

**At DB creation (Confirm click):**
- `base_price`, `total_price` written from session
- `booking.is_refundable` written from session
- `payment_mode` validated against `allows_pay_on_arrival` from session

Tour bookings always `status='pending_confirmation'` — permanent architecture.

## EMAIL CONFIGURATION
```dotenv
DEFAULT_FROM_EMAIL=Jadevine Travel & Tours <your-email@gmail.com>
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend   # real
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend  # silent
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend  # file
```

## CURRENTLY WORKING
- Full signup → verification email (branded HTML) → auto-confirm → login
- Login: custom error, resend link only for unverified accounts
- Logout → homepage, no messages
- Password reset: branded HTML email
- Password change: success on same page
- Dashboard: upcoming bookings, stats, clickable cards
- Booking history: paginated, filterable, clickable cards
- Booking detail: status banner, refund info (gated by payment status + is_refundable), review section
- Review submission: star picker, one per booking, pending moderation
- Cancellation: correct flow per payment mode and is_refundable, branded emails
- Cancellation admin alert: `fidontakakwa@gmail.com`, gold portal button, table layout
- POA admin email: amount right-aligned via table, gold portal button
- PDF: flat header, gold accent, correct phone
- Discount badges: list cards and detail pages for all three services
- Per-listing refund/POA policy: enforced in UI and server-side
- Profile: raw file input, photo preview
- Favourites: AJAX toggle
- Change password: dashboard layout
- Logout page: styled
- Unverified cleanup: daily Django-Q task

## PHASE 5 SCOPE — Admin Portal

### Portal authentication
- `/portal/login/` — username + password, `is_staff=True`
- `@portal_required` decorator on every portal view
- `@superadmin_required` for Super Admin-only views
- `portal_base.html` — separate from `base.html` and `dashboard_base.html`
- Session timeout: 8 hours

### Access control helpers (use in EVERY portal view touching listings/bookings)
```python
def get_accessible_hotels(user):
    if hasattr(user, 'miniadminprofile'):
        return Hotel.objects.filter(created_by=user)
    return Hotel.objects.all()

def get_accessible_cars(user):
    if hasattr(user, 'miniadminprofile'):
        return CarRental.objects.filter(created_by=user)
    return CarRental.objects.all()
```
Enforced server-side in VIEW — never only in template.

### Super Admin portal
- Dashboard: booking counts, revenue, **Pending Approvals at top** (hotel + car counts)
- Hotels: full CRUD, pending queue, approve/reject with required reason, inline photos + room types, discount fields, is_refundable + allows_pay_on_arrival per room type
- Cars: same structure as hotels, discount and policy fields at vehicle level
- Tours: full CRUD, inline itinerary days + photos, featured toggle, discount and policy fields (no approval workflow)
- Bookings: filterable table, status updates, mark POA as paid, CSV export
- **Reviews moderation:** Approve/reject any review. Shows pending count badge on dashboard. Rejection requires a reason (stored in `rejection_reason`, surfaced to customer).
- Gallery: upload, categorise, reorder, set featured
- Users: search, view history, deactivate/reactivate
- Mini-Admins: create, welcome email via Django-Q, deactivate
- Contact messages: view, status, reply via Django-Q
- Newsletter: subscriber list, CSV export
- Cancellation policies: edit tiers
- Settings: own username/password

### Mini-Admin portal
- Own listings only (Hotels and/or Cars)
- Warning before editing approved listing
- My Bookings: read-only, own listings only
- **Reviews moderation:** Can approve/reject reviews for their own hotel and car listings only. Cannot moderate tour reviews.
- Change password

### Listing approval workflow
- Mini-admin creates → `approval_status='pending'`, `is_active=False`
- Super Admin approves → `approval_status='approved'`, `is_active=True`, notifies mini-admin
- Super Admin rejects → `approval_status='rejected'`, reason saved, notifies mini-admin
- Mini-admin edits rejected → resets to `pending`
- Mini-admin edits approved → `approval_status='approved'`, `is_active=True`, notifies mini-admin
- Super Admin creates directly → `approved`, `is_active=True` (skips queue)

### Phase 5 email tasks to add
- `send_listing_approved_email(listing_type, listing_id)` — to mini-admin
- `send_listing_rejected_email(listing_type, listing_id, reason)` — to mini-admin
- `send_miniadmin_welcome_email(user_id)` — welcome + credentials

## POST-LAUNCH ONLY
- Domestic flights (Amadeus API)
- Expedia hotel API / Booking.com
- Discover Cars API
- TripAdvisor Content API
- Google OAuth / Facebook OAuth
- Arabic (RTL), Dutch, Italian languages
- Pay on Arrival deposit requirement
- Automated PesaPal refund processing
- SMS/WhatsApp automated notifications
- Mobile app

---

## KEY CONVENTIONS
1. Every user-facing string: `{% trans %}` or `_()` — never hardcode English
2. Never store card data — PesaPal handles all card processing
3. Mini-admin restrictions enforced in VIEW — never only in template
4. Server-side Django validation is authoritative — jQuery is UX only
5. All secrets in `.env`
6. Snapshot prices at booking time via `get_display_price()` — never use raw price field directly
7. Snapshot `is_refundable` at booking time — never retroactively affected by listing changes
8. Django ORM only — no raw SQL
9. `select_related()` and `prefetch_related()` — avoid N+1
10. DB backup before every production migration
11. Test mobile before moving to next phase
12. Commit to GitHub daily
13. Language fallback: `getattr(obj, f'field_{lang}', None) or obj.field_en`
14. Portal ≠ Django `/admin/` — `/admin/` is developer-only
15. Warn mini-admins before saving edits to approved listing
16. JS strings → `window.JD_STRINGS` in template, never in static `.js`
17. Django → JS data: `window.JD_*` globals in `<script>` block before page JS
18. Booking DB record created only at Confirm click — not at form submit
19. Tour bookings always `status='pending_confirmation'` — permanent
20. `.jd-load-reveal` for above-fold; `.jd-reveal` for scroll-triggered
21. JS files: IIFE pattern `(function($){ 'use strict'; ... })(jQuery);`
22. `templates/account/` (singular) = allauth; `templates/accounts/` (plural) = dashboard
23. Profile photo: raw `<input type="file" name="profile_photo">` — never `{{ form.profile_photo }}`
24. Never call Python methods with args in Django templates — resolve in view
25. allauth email prefixes differ from docs — always verify with logging before creating templates
26. Never use `display:flex` or `display:grid` in email HTML — use `<table>` for all layouts
27. Refund info hidden when `payment_status != 'paid'` OR `booking.is_refundable == False`
28. PDF headers: flat Table only, no nested tables — ReportLab clips nested content
29. Rating badges only shown when listing has ≥ 3 approved reviews — never below threshold
30. Review eligibility: `booking.status == 'completed'` AND `booking.user == request.user` — enforced server-side before form validation
31. `get_display_price()` is the single source of truth for any price shown or snapshotted — never read `price_per_night`, `price_per_day`, or `price_per_person` directly for display
32. `allows_pay_on_arrival=False` must be enforced server-side in `BookingSummaryView._create_booking()` — UI suppression alone is not sufficient


*End of Handoff — Version 4.2 | April 2026*
*Prepared by Fidon for Jadevine Travel & Tours*
*Supersedes versions 1.0, 1.1, 1.2, 2.0, 3.0, 4.0, 4.1.*