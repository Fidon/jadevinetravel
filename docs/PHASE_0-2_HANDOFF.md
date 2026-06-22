# JADEVINE TRAVEL & TOURS — PHASE HANDOFF DOCUMENT
**Version 2.0 | April 2026 | End of Phase 0, 1 & 2**

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
DEFAULT_FROM_EMAIL=noreply@jadevinetravel.com

Settings split:
- `config/settings/base.py` — shared
- `config/settings/development.py` — SQLite, local media, console email, DEBUG=True
- `config/settings/production.py` — PostgreSQL, AWS S3, SendGrid, DEBUG=False

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
| Email | Console (dev) → SendGrid (prod) |
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
│   ├── accounts/       — CustomUser, MiniAdminProfile, auth views
│   ├── hotels/         — Hotel, HotelPhoto, HotelRoomType, views, urls ✅ COMPLETE
│   ├── tours/          — TourPackage, TourItineraryDay, TourPhoto (models only)
│   ├── cars/           — CarRental, CarPhoto, views, urls ✅ COMPLETE
│   ├── bookings/       — Booking, CancellationPolicy, views, forms, urls ✅ COMPLETE
│   ├── gallery/        — GalleryCategory, GalleryItem
│   ├── contact/        — ContactMessage, NewsletterSubscriber
│   ├── portal/         — Admin portal views only (no models)
│   └── core/           — Homepage, About, SavedFavourite
├── config/
│   ├── settings/
│   │   ├── init.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/
│   ├── base.html                        ✅ COMPLETE
│   ├── core/
│   │   ├── home.html                    ✅ COMPLETE
│   │   └── about.html                   stub only
│   ├── accounts/
│   │   └── dashboard.html               stub only
│   ├── hotels/
│   │   ├── hotel_list.html              ✅ COMPLETE
│   │   └── hotel_detail.html            ✅ COMPLETE
│   ├── tours/
│   │   ├── tour_list.html               stub only — Phase 3
│   │   └── tour_detail.html             stub only — Phase 3
│   ├── cars/
│   │   ├── car_list.html                ✅ COMPLETE
│   │   └── car_detail.html              ✅ COMPLETE
│   ├── bookings/
│   │   ├── booking_summary.html         ✅ COMPLETE
│   │   ├── payment_options.html         ✅ COMPLETE (stubbed — Phase 6 wires PesaPal)
│   │   └── booking_confirmation.html    ✅ COMPLETE
│   ├── gallery/
│   │   └── gallery.html                 stub only
│   ├── contact/
│   │   └── contact.html                 stub only
│   └── portal/
│       ├── portal_login.html            stub only
│       └── portal_dashboard.html        stub only
├── static/
│   ├── css/
│   │   ├── main.css                     ✅ COMPLETE — full design system
│   │   ├── core/
│   │   │   └── home.css                 ✅ COMPLETE
│   │   ├── hotels/
│   │   │   ├── hotel_list.css           ✅ COMPLETE
│   │   │   └── hotel_detail.css         ✅ COMPLETE
│   │   ├── cars/
│   │   │   ├── car_list.css             ✅ COMPLETE
│   │   │   └── car_detail.css           ✅ COMPLETE
│   │   ├── bookings/
│   │   │   ├── booking_summary.css      ✅ COMPLETE
│   │   │   ├── payment_options.css      ✅ COMPLETE
│   │   │   └── booking_confirmation.css ✅ COMPLETE
│   │   ├── tours/                       empty — Phase 3
│   │   ├── accounts/                    empty
│   │   ├── gallery/                     empty
│   │   ├── contact/                     empty
│   │   └── portal/                      empty
│   ├── js/
│   │   ├── main.js                      ✅ COMPLETE — global jQuery
│   │   ├── core/
│   │   │   └── home.js                  ✅ COMPLETE
│   │   ├── hotels/
│   │   │   ├── hotel_list.js            ✅ COMPLETE
│   │   │   └── hotel_detail.js          ✅ COMPLETE
│   │   ├── cars/
│   │   │   ├── car_list.js              ✅ COMPLETE
│   │   │   └── car_detail.js            ✅ COMPLETE
│   │   ├── bookings/
│   │   │   ├── booking_summary.js       ✅ COMPLETE
│   │   │   ├── payment_options.js       ✅ COMPLETE
│   │   │   └── booking_confirmation.js  ✅ COMPLETE
│   │   ├── tours/                       empty — Phase 3
│   │   ├── accounts/                    empty
│   │   ├── gallery/                     empty
│   │   ├── contact/                     empty
│   │   └── portal/                      empty
│   └── images/
│       └── favicon.png                  placeholder only
├── locale/
│   ├── en/LC_MESSAGES/
│   ├── fr/LC_MESSAGES/
│   └── ru/LC_MESSAGES/
├── media/                               local dev uploads, gitignored
├── jadevine_db.sqlite3                  dev database
├── manage.py
├── requirements.txt
├── .env                                 gitignored
└── .gitignore

## URL STRUCTURE (config/urls.py)
```python
# NOT language-prefixed
/admin/                          — Django built-in admin (developer only)
/book/                           — All booking flow URLs (includes PesaPal callback)
/portal/                         — Admin portal
/i18n/                           — Django language switching

# Booking flow URLs (mounted under /book/ — NOT language-prefixed intentionally)
/book/summary/<reference>/       — Booking summary + payment mode selection
/book/payment/<reference>/       — Payment options (PesaPal stub until Phase 6)
/book/confirm/<reference>/       — Booking confirmation
/book/pesapal/callback/          — PesaPal IPN webhook

# Language-prefixed via i18n_patterns (English has no prefix)
/                                — Homepage
/hotels/                         — Hotel listing
/hotels/<slug>/                  — Hotel detail
/hotels/<slug>/book/             — Hotel booking form POST (HotelBookingView)
/tours/                          — Tour listing
/tours/<slug>/                   — Tour detail
/tours/<slug>/book/              — Tour booking form POST (Phase 3)
/cars/                           — Car listing
/cars/<slug>/                    — Car detail
/cars/<slug>/book/               — Car booking form POST (CarBookingView)
/gallery/                        — Gallery
/about/                          — About Us
/contact/                        — Contact Us
/contact/newsletter/             — Newsletter subscribe (AJAX POST)
/accounts/dashboard/             — User dashboard
/accounts/...                    — allauth URLs included here

# Language-prefixed examples
/fr/hotels/                      — French hotel listing
/ru/tours/                       — Russian tour listing
```

App namespaces: `core`, `hotels`, `tours`, `cars`, `bookings`, `gallery`, `contact`, `accounts`, `portal`

## ALL DATABASE MODELS (fully migrated)

### apps/accounts/models.py
**CustomUser** (extends AbstractUser)
- `email` — login identifier for customers
- `username` — login identifier for admin/mini-admin
- `first_name`, `last_name`, `phone`, `nationality`
- `preferred_language` — choices: en, fr, ru
- `profile_photo` — ImageField
- `is_staff` — True for Super Admin and Mini-Admin portal access
- `AUTH_USER_MODEL = 'accounts.CustomUser'`

**MiniAdminProfile**
- `user` — OneToOneField → CustomUser
- `created_by` — ForeignKey → CustomUser
- Check `hasattr(user, 'miniadminprofile')` to distinguish mini-admin from super admin

### apps/hotels/models.py
**Hotel**
- `name`, `slug` (auto-generated), `location` (zanzibar/dar_es_salaam)
- `description_en`, `description_fr`, `description_ru`
- `stars` (1–5), `price_per_night` (USD), `address`, `latitude`, `longitude`
- `tripadvisor_url`
- `created_by` — ForeignKey → CustomUser (null = Super Admin)
- `approval_status` — pending/approved/rejected
- `rejection_reason`
- `is_active` — True only when approval_status = approved
- Public visibility: `is_active=True AND approval_status='approved'`
- Method: `get_description(lang='en')` — fallback to English
- Property: `cover_photo` — first photo with `is_cover=True`, else first photo
- Property: `is_publicly_visible`

**HotelPhoto**
- `hotel`, `image`, `caption`, `is_cover`, `order`

**HotelRoomType**
- `hotel`, `name`, `description_en/fr/ru`
- `price_per_night` (overrides hotel base price if set)
- `max_guests`, `amenities` (JSONField list), `is_available`
- Method: `get_effective_price()` — returns room price or hotel base price

### apps/tours/models.py
**TourPackage**
- `name_en/fr/ru`, `slug`, `tour_type` (safari/beach/cultural/climbing/combined)
- `description_en/fr/ru`
- `duration_days`, `group_size_max`, `price_per_person` (USD)
- `highlights_en/fr/ru` (JSONField list)
- `inclusions_en/fr/ru` (JSONField list)
- `exclusions_en/fr/ru` (JSONField list)
- `what_to_bring_en/fr/ru`
- `cover_image`, `is_active`, `is_featured`
- **NO `created_by` or `approval_status`** — Super Admin only, no approval workflow
- Methods: `get_name(lang)`, `get_description(lang)`, `get_highlights(lang)`, `get_inclusions(lang)`, `get_exclusions(lang)`

**TourItineraryDay**
- `package`, `day_number`, `title_en/fr/ru`, `description_en/fr/ru`
- Ordered by `day_number`, unique together [package, day_number]

**TourPhoto**
- `package`, `image`, `caption`, `order`

### apps/cars/models.py
**CarRental**
- `name`, `slug`, `vehicle_type` (sedan/suv/minibus/4x4/van)
- `make`, `model`, `year`, `capacity`, `fuel_type`, `transmission`
- `price_per_day` (USD)
- `offers_self_drive`, `offers_driver`
- `driver_speaks_en`, `driver_speaks_fr`
- `pickup_locations` (JSONField list of strings)
- `description_en/fr/ru`
- `created_by` — ForeignKey → CustomUser
- `approval_status` — pending/approved/rejected
- `rejection_reason`
- `is_available` — toggled by mini-admin (maintenance)
- `is_active` — True only when approval_status = approved
- Public visibility: `is_active=True AND is_available=True AND approval_status='approved'`
- Property: `is_publicly_visible`, `cover_photo`
- Method: `get_description(lang)`

**CarPhoto**
- `car`, `image`, `is_cover`, `order`

### apps/bookings/models.py
**CancellationPolicy** (seeded with default tiers)
- `service_type` (hotel/tour/car)
- `days_before_service`, `refund_percentage`, `label_en`, `is_active`
- Default tiers: 14+ days = 100%, 7–13 days = 50%, 0–6 days = 0%
- Configurable by Super Admin from portal

**Booking** (single model for all service types — polymorphic pattern)
- `reference` — auto-generated JDV-YYYY-NNNNN (uses `apps.get_model` to avoid circular import)
- `user` — ForeignKey → CustomUser
- `service_type` — hotel/tour/car
- `hotel`, `room_type`, `tour_package`, `car` — only one populated per booking
- Date fields: `check_in_date`, `check_out_date` (hotels), `preferred_date` (tours), `pickup_date`, `return_date` (cars)
- `num_guests`, `num_participants`, `num_days`
- Car fields: `pickup_location`, `rental_mode` (self_drive/with_driver), `driver_licence_number`
- Pricing: `base_price`, `total_price`, `currency` (USD/TZS/EUR) — **SNAPSHOTTED at booking time**
- `payment_mode` — pay_now/pay_on_arrival
- `payment_status` — pending/paid/refunded/failed
- `pesapal_order_id`, `pesapal_tracking_id`
- `status` — pending_confirmation/confirmed/cancelled/completed/no_show
- `special_requests`, `cancellation_reason`, `cancelled_at`, `cancelled_by`
- Property: `service_date` (primary date for cancellation calculation)
- Property: `nights` (hotel bookings only)

### apps/gallery/models.py
**GalleryCategory**
- `name_en/fr/ru`, `slug`, `order`

**GalleryItem**
- `category`, `media_type` (photo/video)
- `image` (ImageField), `video_url` (YouTube/Vimeo), `video_file`
- `caption_en/fr/ru`
- `is_featured` — shown in homepage Gallery Highlights
- `order`

### apps/contact/models.py
**ContactMessage**
- `name`, `email`, `phone`, `subject`, `message`
- `inquiry_type` — general/custom_tour/partnership/press
- `preferred_lang`, `status` (new/in_progress/resolved), `admin_notes`

**NewsletterSubscriber**
- `email` (unique), `is_active`, `subscribed_at`

### apps/core/models.py
**SavedFavourite**
- `user`, `hotel`, `tour_package`, `car` — only one service FK populated
- UniqueConstraints prevent duplicate favourites per user per item

## BOOKING SYSTEM ARCHITECTURE (Phase 2 decision — critical)
The booking flow uses a **session-first, DB-on-confirm** pattern. This is a deliberate
architectural decision made in Phase 2 to eliminate orphaned DB records.

**Flow:**
1. User submits booking form on detail page (hotel or car)
2. View validates data server-side. On success, stores validated data + **snapshotted price** in `request.session[SESSION_BOOKING_KEY]`. No DB write.
3. User sees summary page rendered from session data.
4. User selects payment mode (Pay Now or Pay on Arrival) and clicks Confirm.
5. **Only at this point** is the `Booking` DB record created.
6. Pay on Arrival → `status='confirmed'` immediately, redirect to confirmation.
7. Pay Now → `status='pending_confirmation'`, redirect to payment stub → Phase 6 wires PesaPal here.

**Session key constant:** `SESSION_BOOKING_KEY = 'pending_booking'` — defined in `apps/bookings/views.py`.

**Orphan cleanup (Phase 6 task):** PAY_NOW bookings with `payment_status='pending'` and no `pesapal_tracking_id` older than 24 hours should be cancelled by a Django-Q scheduled task. Flag this when implementing Phase 6.

**Price snapshotting:** Price is captured into the session at form validation time in `HotelBookingView` / `CarBookingView` — NOT at booking creation time. This prevents race conditions where a listing price changes between the summary page and the confirm click.

**Tour bookings (Phase 3):** Tours always start as `status='pending_confirmation'` even after payment — Jadevine must manually confirm the preferred date. This is different from hotels and cars which move to `confirmed` after payment.

## BOOKING FORMS (apps/bookings/forms.py)
**HotelBookingForm**
- Fields: `room_type_id` (hidden), `check_in_date`, `check_out_date`, `num_guests`, `special_requests`
- Server-side validation: check-in cannot be in past, check-out must be after check-in
- Date input format: `Y-m-d` (Flatpickr sends this format)

**CarBookingForm**
- Fields: `rental_mode`, `pickup_location`, `pickup_date`, `return_date`, `driver_licence_number`, `special_requests`
- Server-side validation: `driver_licence_number` required if `rental_mode='self_drive'` — enforced in `clean()`, not just jQuery
- Date input format: `Y-m-d`

**PaymentModeForm**
- Fields: `payment_mode` (pay_now / pay_on_arrival)
- Submitted on the summary page to trigger DB record creation

**TourBookingForm (Phase 3 — to be created)**
- Fields: `preferred_date`, `num_participants`, `special_requests`
- No room type selection needed
- Always creates booking with `status='pending_confirmation'`

## AUTHENTICATION SYSTEM
Two completely separate auth flows:

**1. Customers** — email + password via django-allauth
- Register at `/accounts/signup/`
- Login at `/accounts/login/`
- Email verification required (`ACCOUNT_EMAIL_VERIFICATION = 'mandatory'`)
- Email backend in dev: console (prints to terminal)
- After login, redirected to `LOGIN_REDIRECT_URL = '/accounts/dashboard/'`

**2. Admin / Mini-Admin** — username + password via Django built-in auth
- Login at `/portal/login/`
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
```

## DESIGN SYSTEM
**Typography:**
- Headings: Cormorant Garamond (serif, elegant)
- Body: Jost (clean sans-serif)
- CSS variables: `--font-heading`, `--font-body`

**Core colour palette (all defined as CSS variables in `static/css/main.css`):**
```css
--color-primary:        #1a4d2e   /* deep forest green */
--color-primary-dark:   #122f1c
--color-primary-light:  #2a6b40
--color-primary-xlight: #e8f0eb

--color-accent:         #c89666   /* warm gold */
--color-accent-dark:    #a67a50
--color-accent-light:   #e8c99a
--color-accent-xlight:  #faf3ea

--color-off-white:      #f8f5f0
--color-light:          #f0ebe3
--color-border:         #e0d5c8
--color-border-dark:    #c8b89a
--color-text:           #1e1e1e
--color-text-light:     #5a5550
--color-muted:          #9e8e7e
--color-dark:           #111111
--color-overlay:        rgba(18, 47, 28, 0.62)

--color-success:        #2d7a4f
--color-success-bg:     #edf7f1
--color-danger:         #b03a2e
--color-danger-bg:      #fdf0ee
--color-warning:        #c89666
--color-warning-bg:     #fdf6ee
--color-info:           #2471a3
--color-info-bg:        #eaf4fb
```

**Button classes:**
- `.btn-primary-jd` — green filled
- `.btn-accent-jd` — gold filled
- `.btn-outline-jd` — green outline
- `.btn-outline-white-jd` — white outline (dark backgrounds)
- `.btn-ghost-jd` — underline only, inline CTAs

**Card class:** `.jd-card` with hover lift effect

**Form classes:** `.jd-form-group`, `.jd-label`, `.jd-input`, `.jd-input-icon-wrap`, `.jd-input-icon`

**Badge classes:** `.jd-badge`, `.jd-badge-primary`, `.jd-badge-accent`, `.jd-badge-success`, `.jd-badge-warning`, `.jd-badge-danger`

**Section utilities:** `.section-py` (100px), `.section-py-sm` (60px), `.section-py-lg` (140px)

**Typography utilities:** `.eyebrow`, `.eyebrow-white`, `.section-heading`, `.section-subheading`

**Scroll reveal:** Add `.jd-reveal` to any element — JS triggers `.revealed` class on scroll.
Delay classes: `.jd-reveal-delay-1` through `.jd-reveal-delay-5`

## JAVASCRIPT GLOBALS (main.js)
`window.JD` object is globally available:

```javascript
JD.toast('Message', 'success')   // types: success, error, info, ''
JD.csrfToken()                   // returns CSRF token for AJAX calls
```

**jQuery is loaded AFTER Bootstrap bundle.** Load order in base.html:
1. Bootstrap 5 CSS
2. Bootstrap Icons CSS
3. Google Fonts
4. `main.css`
5. `[page CSS via block extra_css]`
6. Bootstrap 5 JS bundle (includes Popper)
7. jQuery 3.7.1
8. `main.js`
9. `[page JS via block extra_js]`

**Global handlers already in main.js (do NOT re-implement):**
- Navbar scroll (transparent → solid) — **respects `navbar-scrolled` set by template**
- Mobile hamburger menu
- Active nav link detection
- Scroll reveal (IntersectionObserver)
- Toast notifications
- CSRF helper
- Language switcher (submits Django i18n form)
- Smooth scroll for anchor links
- Newsletter form AJAX (`.jd-newsletter-form` class)

**Navbar fix (Phase 2):** `main.js` now checks `isAlwaysSolid = $navbar.hasClass('navbar-scrolled')` on load. If the template renders the navbar as `navbar-scrolled` (inner pages), the scroll handler never switches it back to transparent. The homepage uses `navbar-transparent` and transitions normally on scroll.

## BASE TEMPLATE BLOCKS
{% block title %}            — page title
{% block meta_description %} — meta description
{% block navbar_class %}     — default: navbar-transparent. Use 'navbar-scrolled' for inner pages
{% block body_class %}       — body CSS classes
{% block extra_css %}        — page-specific CSS (after main.css)
{% block content %}          — main page content
{% block extra_js %}         — page-specific JS (after main.js)

**All inner pages (non-hero) must set:**
```html
{% block navbar_class %}navbar-scrolled{% endblock %}
```

## JS TRANSLATION PATTERN (Phase 2 decision)
Static JS files are not processed by Django's template engine, so `{% trans %}` tags
do not work inside `.js` files. The correct pattern established in Phase 2:

**In the template's `{% block extra_js %}`**, define strings before loading the page JS:
```html
{% block extra_js %}
<script>
  window.JD_STRINGS = window.JD_STRINGS || {};
  window.JD_STRINGS.viewHotel = "{% trans 'View Hotel' %}";
  window.JD_STRINGS.someError = "{% trans 'Something went wrong.' %}";
</script>
<script src="{% static 'js/hotels/hotel_list.js' %}"></script>
{% endblock %}
```

**In the JS file**, consume from `window.JD_STRINGS`:
```javascript
const label = window.JD_STRINGS.viewHotel || 'View Hotel';
```

Apply this pattern to every page JS file that contains user-facing strings. Never put
`{% trans %}` tags directly inside static `.js` files.

## DATA PASSING FROM DJANGO VIEW TO JS
For data that needs to be available to JavaScript (model data, config), pass it via
a `<script>` block in the template's `{% block extra_js %}`, before the page JS file:

```html
<script>
  window.JD_ROOM_TYPES = {{ room_types_json|safe }};
  window.JD_HOTEL_BASE_PRICE = "{{ hotel.price_per_night }}";
  window.JD_CAR_PRICE_PER_DAY = "{{ car.price_per_day }}";
</script>
```

Never use inline `data-*` attributes on hidden inputs for complex data objects.
Use `json.dumps()` in the view and `|safe` filter in the template.

## MULTILINGUAL SETUP
**3 languages at launch:** English (default, no URL prefix), French (`/fr/`), Russian (`/ru/`)

**Pattern for all views that serve model content:**
```python
lang = request.LANGUAGE_CODE  # 'en', 'fr', or 'ru'
value = getattr(obj, f'field_{lang}', None) or obj.field_en
# Always fall back to English if translated field is empty
```

**In templates:** All UI strings use `{% trans "..." %}` or `{% blocktrans %}...{% endblocktrans %}`

**In Python code:** Use `_("string")` from `django.utils.translation import gettext_lazy as _`

**DO NOT defer translation wrapping** — wrap every string as you write each template.

## LISTING APPROVAL WORKFLOW
Applies to Hotels and Car Rentals created by mini-admins. Tours are Super Admin only and skip this entirely.

- Mini-admin creates listing → `approval_status='pending'`, `is_active=False`, NOT publicly visible
- Super Admin approves → `approval_status='approved'`, `is_active=True`, publicly visible
- Super Admin rejects → `approval_status='rejected'`, `rejection_reason` saved, NOT visible
- Mini-admin edits rejected listing and resubmits → back to `approval_status='pending'`
- Mini-admin edits an APPROVED listing → resets to `approval_status='pending'`, `is_active=False` (removed from public site until re-approved)
- Super Admin creates listing directly → `approval_status='approved'`, `is_active=True` (skips queue)

**Server-side enforcement helpers (use in every portal view):**
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

## BOOKING SYSTEM RULES
- Pay on Arrival is NOT available for Expedia hotel bookings or Amadeus flights (both post-launch)
- Prices are ALWAYS snapshotted into session at validation time, and into DB at confirm time — never recalculate
- Tour bookings always start as `status='pending_confirmation'` even after payment — Jadevine must manually confirm the date
- Hotel and Car Pay Now bookings move to `status='confirmed'` in Phase 6 after PesaPal IPN confirms payment. Currently stubbed.
- Hotel and Car Pay on Arrival bookings move to `status='confirmed'` immediately on creation
- Cancellation refund logic: query `CancellationPolicy` by `service_type` and `days_before_service` — find the matching tier

## THIRD-PARTY LIBRARIES (CDN — used in detail pages)
Both loaded in the template's `{% block extra_js %}` only on pages that need them.
Do not load them globally in `base.html`.

**GLightbox** (photo gallery lightbox):
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/glightbox/dist/css/glightbox.min.css">
<script src="https://cdn.jsdelivr.net/npm/glightbox/dist/js/glightbox.min.js"></script>
```
Usage: `GLightbox({ selector: '.gallery-link', touchNavigation: true, loop: true })`

**Flatpickr** (date pickers):
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
```
Usage: `flatpickr('#id_check_in_date', { minDate: 'today', dateFormat: 'Y-m-d', altInput: true, altFormat: 'D, d M Y', disableMobile: true })`

The `dateFormat: 'Y-m-d'` is what gets submitted in the POST. The `altFormat` is what the user sees. Django forms are configured with `input_formats=['%Y-%m-%d', '%d/%m/%Y']` to accept both.

## CURRENTLY WORKING
- `python manage.py runserver` starts cleanly with zero errors and zero warnings
- `http://jadevinetravel.com//` loads full homepage
- `http://jadevinetravel.com//admin/` loads Django admin, superuser login works
- `http://jadevinetravel.com//hotels/` loads hotel list with AJAX filtering and skeleton loaders
- `http://jadevinetravel.com//hotels/<slug>/` loads hotel detail with photo gallery (GLightbox), room type selector, Flatpickr date pickers, price breakdown
- Hotel booking flow end-to-end: detail → summary (session) → Pay on Arrival → confirmation ✅
- Hotel booking flow end-to-end: detail → summary (session) → Pay Now → payment stub → confirmation ✅
- `http://jadevinetravel.com//cars/` loads car list with AJAX filtering and skeleton loaders
- `http://jadevinetravel.com//cars/<slug>/` loads car detail with rental mode toggle, licence field conditional display, Flatpickr, price breakdown
- Car booking flow end-to-end: same as hotel ✅
- Booking records verified in `/admin/` with correct `service_type`, `status`, `payment_mode`, and snapshotted prices
- Navbar stays solid on all inner pages (navbar fix applied to `main.js`)
- Language switcher switches EN/FR/RU on all pages
- Newsletter subscribe endpoint works (`/contact/newsletter/` POST)
- All migrations applied cleanly
- Django-Q worker runs: `python manage.py qcluster`

## PHASE 3 SCOPE — Safaris & Tours: Listings + Booking Flow
Build in this order:

### Tours backend
1. **`TourListView`** in `apps/tours/views.py`
   - Filterable by `tour_type`, `duration_days` range, `price_per_person` range
   - Public queryset always: `is_active=True`
   - AJAX endpoint returns filtered results as JSON (same pattern as `HotelListView`)
   - Language fallback pattern applied on all translated fields

2. **`TourDetailView`** in `apps/tours/views.py`
   - Retrieves package with `prefetch_related('itinerary_days', 'photos')`
   - Itinerary days ordered by `day_number`
   - All multilingual fields served with English fallback
   - Passes `itinerary_json` and `highlights_json` to template for JS consumption

3. **`TourBookingView`** in `apps/bookings/views.py` (extend existing file)
   - POST only — same session-first pattern as `HotelBookingView` and `CarBookingView`
   - Fields: `preferred_date`, `num_participants`, `special_requests`
   - Snapshot: `price_per_person × num_participants` at validation time → stored in session
   - Always creates booking with `status='pending_confirmation'` — Jadevine confirms date manually
   - Add `TourBookingForm` to `apps/bookings/forms.py`

4. **Add tour booking URL** to `apps/tours/urls.py`:
   - `path('<slug:slug>/book/', TourBookingView.as_view(), name='book')`
   - Import `TourBookingView` from `apps.bookings.views`

5. **Extend `BookingSummaryView._create_booking()`** in `apps/bookings/views.py` to handle `service_type='tour'`

### Tours frontend
Each page has exactly 3 files: `html` + `css` + `js`.
**`templates/tours/tour_list.html`** + `static/css/tours/tour_list.css` + `static/js/tours/tour_list.js`
- Filter tabs: All / Safari / Beach / Cultural / Climbing / Combined
- Tour cards: cover image, name, type badge, duration, group size, price per person, 2–3 highlights, Book Now button
- AJAX filtering — same pattern as hotel list and car list
- `window.JD_STRINGS` pattern for all translatable JS strings

**`templates/tours/tour_detail.html`** + `static/css/tours/tour_detail.css` + `static/js/tours/tour_detail.js`
- Hero image with overlay (no gallery grid — single cover image, additional photos below)
- Package overview: duration, group size, price per person, tour type badge
- Itinerary: Bootstrap accordion, one panel per day, ordered by `day_number`
- Inclusions checklist (green ticks) and Exclusions checklist (red X)
- What to Bring section
- Photo gallery with GLightbox (same pattern as hotel detail)
- Booking form on the right panel:
  - Flatpickr date picker for preferred start date
  - Participant counter (+/- buttons, same pattern as hotel guest counter)
  - Running total price update via jQuery
  - Special requests textarea
  - Informational note: "We will confirm your preferred date within 24–48 hours"
  - Pay Now and Pay on Arrival both available
- Reuse `.booking-price-header`, `.booking-form-body`, `.poa-note` CSS patterns from hotel_detail.css

### Seed data for testing
Add via Django admin at `/admin/`:
- At least 3 tour packages with `is_active=True`, cover image, at least 2 itinerary days each, highlights, inclusions, exclusions
- Recommended: Serengeti National Park Safari (5 days), Zanzibar Beach Package (3 days), Spice Tour (1 day)

## PHASES 4–9 SUMMARY (future reference)
| Phase | Name | Key Deliverables |
|---|---|---|
| 4 | User Accounts & Dashboard | Registration, login, email verification, booking history, cancellations, favourites, profile, PDF download |
| 5 | Admin Portal | Super Admin full portal, Mini-Admin restricted portal, listing approval workflow, booking management |
| 6 | PesaPal Payment | Pay Now end-to-end (sandbox), IPN callback, booking status updates, orphan cleanup task, Pay on Arrival complete |
| 7 | Gallery, Contact, Newsletter | Gallery page with GLightbox, contact form full processing, newsletter full processing |
| 8 | i18n, SEO & QA | .po files for FR and RU, all templates audited for {% trans %}, hreflang, sitemap, GA4, full QA checklist |
| 9 | Deployment | VPS setup, PostgreSQL, AWS S3, Nginx + Gunicorn, SSL, smoke test |

## POST-LAUNCH ONLY (do not implement in any phase)
- Domestic flights (Amadeus API) — do not install any Amadeus package
- Expedia hotel API
- Booking.com affiliate
- Discover Cars API
- TripAdvisor Content API (widget placeholder only until launch)
- Google OAuth and Facebook OAuth for customers
- Arabic (RTL) language
- Dutch and Italian languages
- Pay on Arrival deposit requirement
- Automated PesaPal refund processing (manual flagging only at launch)
- SMS/WhatsApp automated notifications
- Mobile app

## KEY CONVENTIONS (apply in every phase)
1. Every user-facing string uses `{% trans %}` or `_()` — never hardcode English
2. Never store card data — PesaPal handles all card processing
3. Mini-admin access restrictions enforced in the VIEW, not just the template
4. Every form has server-side Django validation — jQuery validation is UX only
5. All secrets in `.env` — never commit API keys
6. Snapshot prices at booking time — never recalculate from listing
7. Use Django ORM only — no raw SQL unless documented reason exists
8. Use `select_related()` and `prefetch_related()` to avoid N+1 queries
9. Backup database before every production migration
10. Test every page on mobile before moving to next phase
11. Commit to GitHub at end of every working day
12. Language fallback pattern: `getattr(obj, f'field_{lang}', None) or obj.field_en`
13. Portal is NEVER Django's built-in `/admin/` — that is developer-only
14. Warn mini-admins before saving edits to an approved listing
15. JS translation strings go in `window.JD_STRINGS` in the template — never in static `.js` files
16. Data from Django view to JS goes via `window.JD_*` globals in a `<script>` block before the page JS
17. Booking DB record is created only when user clicks Confirm on the summary page — not at form submit
18. Tour bookings always start as `status='pending_confirmation'` — even after payment