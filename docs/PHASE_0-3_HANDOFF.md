\# JADEVINE TRAVEL \& TOURS — PHASE HANDOFF DOCUMENT

\*\*Version 3.0 | April 2026 | End of Phase 0, 1, 2 \& 3\*\*



\---



\## PROJECT IDENTITY

\*\*Project:\*\* Jadevine Travel \& Tours — full-stack Django booking \& marketing platform

\*\*Client:\*\* Zanzibar-based travel company

\*\*Developer:\*\* Fidon (fidonamos@gmail.com, +255 713 529 019)

\*\*Root folder:\*\* jadevinetravel/

\*\*Django version:\*\* 6.0.4

\*\*Python:\*\* 3.13 (venv)

\*\*OS:\*\* Windows (PowerShell)

\*\*Database (dev):\*\* SQLite — file named jadevine\_db.sqlite3

\*\*Database (prod):\*\* PostgreSQL

\*\*Media (dev):\*\* Local filesystem

\*\*Media (prod):\*\* AWS S3



\---



\## DJANGO SETTINGS MODULE

Active settings: `config.settings.development`



Set in `.env`:

```

DJANGO\_SETTINGS\_MODULE=config.settings.development

SECRET\_KEY=your-secret-key-here

DEFAULT\_FROM\_EMAIL=noreply@jadevinetours.com

```



Settings split:

\- `config/settings/base.py` — shared

\- `config/settings/development.py` — SQLite, local media, console email, DEBUG=True

\- `config/settings/production.py` — PostgreSQL, AWS S3, SendGrid, DEBUG=False



\---



\## TECH STACK

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



\---



\## INSTALLED PACKAGES (requirements.txt)

```

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

```



\---



\## PROJECT FOLDER STRUCTURE

```

jadevinetravel/

├── apps/

│   ├── \_\_init\_\_.py

│   ├── accounts/       — CustomUser, MiniAdminProfile, auth views

│   ├── hotels/         — Hotel, HotelPhoto, HotelRoomType, views, urls ✅ COMPLETE

│   ├── tours/          — TourPackage, TourItineraryDay, TourPhoto, views, urls ✅ COMPLETE

│   ├── cars/           — CarRental, CarPhoto, views, urls ✅ COMPLETE

│   ├── bookings/       — Booking, CancellationPolicy, views, forms, urls ✅ COMPLETE

│   ├── gallery/        — GalleryCategory, GalleryItem

│   ├── contact/        — ContactMessage, NewsletterSubscriber

│   ├── portal/         — Admin portal views only (no models)

│   └── core/           — Homepage, About, SavedFavourite

├── config/

│   ├── settings/

│   │   ├── \_\_init\_\_.py

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

│   │   ├── hotel\_list.html              ✅ COMPLETE

│   │   └── hotel\_detail.html            ✅ COMPLETE

│   ├── tours/

│   │   ├── tour\_list.html               ✅ COMPLETE

│   │   └── tour\_detail.html             ✅ COMPLETE

│   ├── cars/

│   │   ├── car\_list.html                ✅ COMPLETE

│   │   └── car\_detail.html              ✅ COMPLETE

│   ├── bookings/

│   │   ├── booking\_summary.html         ✅ COMPLETE

│   │   ├── payment\_options.html         ✅ COMPLETE (stubbed — Phase 6 wires PesaPal)

│   │   └── booking\_confirmation.html    ✅ COMPLETE

│   ├── gallery/

│   │   └── gallery.html                 stub only

│   ├── contact/

│   │   └── contact.html                 stub only

│   └── portal/

│       ├── portal\_login.html            stub only

│       └── portal\_dashboard.html        stub only

├── static/

│   ├── css/

│   │   ├── main.css                     ✅ COMPLETE — full design system + reveal system

│   │   ├── core/

│   │   │   └── home.css                 ✅ COMPLETE

│   │   ├── hotels/

│   │   │   ├── hotel\_list.css           ✅ COMPLETE

│   │   │   └── hotel\_detail.css         ✅ COMPLETE

│   │   ├── tours/

│   │   │   ├── tour\_list.css            ✅ COMPLETE

│   │   │   └── tour\_detail.css          ✅ COMPLETE

│   │   ├── cars/

│   │   │   ├── car\_list.css             ✅ COMPLETE

│   │   │   └── car\_detail.css           ✅ COMPLETE

│   │   ├── bookings/

│   │   │   ├── booking\_summary.css      ✅ COMPLETE

│   │   │   ├── payment\_options.css      ✅ COMPLETE

│   │   │   └── booking\_confirmation.css ✅ COMPLETE

│   │   ├── accounts/                    empty

│   │   ├── gallery/                     empty

│   │   ├── contact/                     empty

│   │   └── portal/                      empty

│   ├── js/

│   │   ├── main.js                      ✅ COMPLETE — global jQuery + both reveal systems

│   │   ├── core/

│   │   │   └── home.js                  ✅ COMPLETE

│   │   ├── hotels/

│   │   │   ├── hotel\_list.js            ✅ COMPLETE

│   │   │   └── hotel\_detail.js          ✅ COMPLETE

│   │   ├── tours/

│   │   │   ├── tour\_list.js             ✅ COMPLETE

│   │   │   └── tour\_detail.js           ✅ COMPLETE

│   │   ├── cars/

│   │   │   ├── car\_list.js              ✅ COMPLETE

│   │   │   └── car\_detail.js            ✅ COMPLETE

│   │   ├── bookings/

│   │   │   ├── booking\_summary.js       ✅ COMPLETE

│   │   │   ├── payment\_options.js       ✅ COMPLETE

│   │   │   └── booking\_confirmation.js  ✅ COMPLETE

│   │   ├── accounts/                    empty

│   │   ├── gallery/                     empty

│   │   ├── contact/                     empty

│   │   └── portal/                      empty

│   └── images/

│       └── favicon.png                  placeholder only

├── locale/

│   ├── en/LC\_MESSAGES/

│   ├── fr/LC\_MESSAGES/

│   └── ru/LC\_MESSAGES/

├── media/                               local dev uploads, gitignored

├── jadevine\_db.sqlite3                  dev database

├── manage.py

├── requirements.txt

├── .env                                 gitignored

└── .gitignore

```



\---



\## URL STRUCTURE (config/urls.py)

```python

\# NOT language-prefixed

/admin/                          — Django built-in admin (developer only)

/book/                           — All booking flow URLs (includes PesaPal callback)

/portal/                         — Admin portal

/i18n/                           — Django language switching



\# Booking flow URLs (mounted under /book/ — NOT language-prefixed intentionally)

/book/summary/<reference>/       — Booking summary + payment mode selection

/book/payment/<reference>/       — Payment options (PesaPal stub until Phase 6)

/book/confirm/<reference>/       — Booking confirmation

/book/pesapal/callback/          — PesaPal IPN webhook



\# Language-prefixed via i18n\_patterns (English has no prefix)

/                                — Homepage

/hotels/                         — Hotel listing

/hotels/<slug>/                  — Hotel detail

/hotels/<slug>/book/             — Hotel booking form POST (HotelBookingView)

/tours/                          — Tour listing

/tours/<slug>/                   — Tour detail

/tours/<slug>/book/              — Tour booking form POST (TourBookingView)

/cars/                           — Car listing

/cars/<slug>/                    — Car detail

/cars/<slug>/book/               — Car booking form POST (CarBookingView)

/gallery/                        — Gallery

/about/                          — About Us

/contact/                        — Contact Us

/contact/newsletter/             — Newsletter subscribe (AJAX POST)

/accounts/dashboard/             — User dashboard

/accounts/...                    — allauth URLs



\# Language-prefixed examples

/fr/hotels/                      — French hotel listing

/ru/tours/                       — Russian tour listing

```



App namespaces: `core`, `hotels`, `tours`, `cars`, `bookings`, `gallery`, `contact`, `accounts`, `portal`



\---



\## ALL DATABASE MODELS (fully migrated)



\### apps/accounts/models.py

\*\*CustomUser\*\* (extends AbstractUser)

\- `email` — login identifier for customers

\- `username` — login identifier for admin/mini-admin

\- `first\_name`, `last\_name`, `phone`, `nationality`

\- `preferred\_language` — choices: en, fr, ru

\- `profile\_photo` — ImageField

\- `is\_staff` — True for Super Admin and Mini-Admin portal access

\- `AUTH\_USER\_MODEL = 'accounts.CustomUser'`



\*\*MiniAdminProfile\*\*

\- `user` — OneToOneField → CustomUser

\- `created\_by` — ForeignKey → CustomUser

\- Check `hasattr(user, 'miniadminprofile')` to distinguish mini-admin from super admin



\### apps/hotels/models.py

\*\*Hotel\*\*

\- `name`, `slug` (auto-generated), `location` (zanzibar/dar\_es\_salaam)

\- `description\_en`, `description\_fr`, `description\_ru`

\- `stars` (1–5), `price\_per\_night` (USD), `address`, `latitude`, `longitude`

\- `tripadvisor\_url`

\- `created\_by` — ForeignKey → CustomUser (null = Super Admin)

\- `approval\_status` — pending/approved/rejected

\- `rejection\_reason`

\- `is\_active` — True only when approval\_status = approved

\- Public visibility: `is\_active=True AND approval\_status='approved'`

\- Method: `get\_description(lang='en')` — fallback to English

\- Property: `cover\_photo` — first photo with `is\_cover=True`, else first photo

\- Property: `is\_publicly\_visible`



\*\*HotelPhoto\*\*

\- `hotel`, `image`, `caption`, `is\_cover`, `order`



\*\*HotelRoomType\*\*

\- `hotel`, `name`, `description\_en/fr/ru`

\- `price\_per\_night` (overrides hotel base price if set)

\- `max\_guests`, `amenities` (JSONField list), `is\_available`

\- Method: `get\_effective\_price()` — returns room price or hotel base price



\### apps/tours/models.py

\*\*TourPackage\*\*

\- `name\_en/fr/ru`, `slug`, `tour\_type` (safari/beach/cultural/climbing/combined)

\- `description\_en/fr/ru`

\- `duration\_days`, `group\_size\_max`, `price\_per\_person` (USD)

\- `highlights\_en/fr/ru` (JSONField list)

\- `inclusions\_en/fr/ru` (JSONField list)

\- `exclusions\_en/fr/ru` (JSONField list)

\- `what\_to\_bring\_en/fr/ru`

\- `cover\_image`, `is\_active`, `is\_featured`

\- \*\*NO `created\_by` or `approval\_status`\*\* — Super Admin only, no approval workflow

\- Methods: `get\_name(lang)`, `get\_description(lang)`, `get\_highlights(lang)`, `get\_inclusions(lang)`, `get\_exclusions(lang)`



\*\*TourItineraryDay\*\*

\- `package`, `day\_number`, `title\_en/fr/ru`, `description\_en/fr/ru`

\- Methods: `get\_title(lang)`, `get\_description(lang)`

\- Ordered by `day\_number`, unique together \[package, day\_number]



\*\*TourPhoto\*\*

\- `package`, `image`, `caption`, `order`



\### apps/cars/models.py

\*\*CarRental\*\*

\- `name`, `slug`, `vehicle\_type` (sedan/suv/minibus/4x4/van)

\- `make`, `model`, `year`, `capacity`, `fuel\_type`, `transmission`

\- `price\_per\_day` (USD)

\- `offers\_self\_drive`, `offers\_driver`

\- `driver\_speaks\_en`, `driver\_speaks\_fr`

\- `pickup\_locations` (JSONField list of strings)

\- `description\_en/fr/ru`

\- `created\_by` — ForeignKey → CustomUser

\- `approval\_status` — pending/approved/rejected

\- `rejection\_reason`

\- `is\_available` — toggled by mini-admin (maintenance)

\- `is\_active` — True only when approval\_status = approved

\- Public visibility: `is\_active=True AND is\_available=True AND approval\_status='approved'`

\- Property: `is\_publicly\_visible`, `cover\_photo`

\- Method: `get\_description(lang)`



\*\*CarPhoto\*\*

\- `car`, `image`, `is\_cover`, `order`



\### apps/bookings/models.py

\*\*CancellationPolicy\*\* (seeded with default tiers)

\- `service\_type` (hotel/tour/car)

\- `days\_before\_service`, `refund\_percentage`, `label\_en`, `is\_active`

\- Default tiers: 14+ days = 100%, 7–13 days = 50%, 0–6 days = 0%

\- Configurable by Super Admin from portal



\*\*Booking\*\* (single model for all service types — polymorphic pattern)

\- `reference` — auto-generated JDV-YYYY-NNNNN

\- `user` — ForeignKey → CustomUser

\- `service\_type` — hotel/tour/car

\- `hotel`, `room\_type`, `tour\_package`, `car` — only one populated per booking

\- Date fields: `check\_in\_date`, `check\_out\_date` (hotels), `preferred\_date` (tours), `pickup\_date`, `return\_date` (cars)

\- `num\_guests`, `num\_participants`, `num\_days`

\- Car fields: `pickup\_location`, `rental\_mode` (self\_drive/with\_driver), `driver\_licence\_number`

\- Pricing: `base\_price`, `total\_price`, `currency` (USD/TZS/EUR) — \*\*SNAPSHOTTED at booking time\*\*

\- `payment\_mode` — pay\_now/pay\_on\_arrival

\- `payment\_status` — pending/paid/refunded/failed

\- `pesapal\_order\_id`, `pesapal\_tracking\_id`

\- `status` — pending\_confirmation/confirmed/cancelled/completed/no\_show

\- `special\_requests`, `cancellation\_reason`, `cancelled\_at`, `cancelled\_by`

\- Property: `service\_date` (primary date for cancellation calculation)

\- Property: `nights` (hotel bookings only)



\### apps/gallery/models.py

\*\*GalleryCategory\*\*

\- `name\_en/fr/ru`, `slug`, `order`



\*\*GalleryItem\*\*

\- `category`, `media\_type` (photo/video)

\- `image` (ImageField), `video\_url` (YouTube/Vimeo), `video\_file`

\- `caption\_en/fr/ru`

\- `is\_featured` — shown in homepage Gallery Highlights

\- `order`



\### apps/contact/models.py

\*\*ContactMessage\*\*

\- `name`, `email`, `phone`, `subject`, `message`

\- `inquiry\_type` — general/custom\_tour/partnership/press

\- `preferred\_lang`, `status` (new/in\_progress/resolved), `admin\_notes`



\*\*NewsletterSubscriber\*\*

\- `email` (unique), `is\_active`, `subscribed\_at`



\### apps/core/models.py

\*\*SavedFavourite\*\*

\- `user`, `hotel`, `tour\_package`, `car` — only one service FK populated

\- UniqueConstraints prevent duplicate favourites per user per item



\---



\## EMAIL SYSTEM



\*\*Transport:\*\* Gmail SMTP via `django.core.mail.backends.smtp.EmailBackend`

Configured in `config/settings/development.py` — reads all values from `.env`.



\*\*Sending account:\*\* `jovinjames@gmail.com` (Gmail App Password, not account password)

\*\*Admin notification recipient:\*\* `jadevinetravel@gmailcom` — stored as `ADMIN\_NOTIFICATION\_EMAIL` in `.env` and `base.py`. Never derived from `DEFAULT\_FROM\_EMAIL`.



\*\*Required `.env` entries:\*\*

```

EMAIL\_BACKEND=django.core.mail.backends.smtp.EmailBackend

EMAIL\_HOST=smtp.gmail.com

EMAIL\_PORT=587

EMAIL\_USE\_TLS=True

EMAIL\_HOST\_USER=jovinjames@gmail.com

EMAIL\_HOST\_PASSWORD=<app\_password>

DEFAULT\_FROM\_EMAIL=Jadevine Travel \& Tours <jovinjames@gmail.com>

ADMIN\_NOTIFICATION\_EMAIL=jadevinetravel@gmailcom

```



\*\*`base.py` settings entries (bottom of file):\*\*

```python

DEFAULT\_FROM\_EMAIL = os.environ.get('DEFAULT\_FROM\_EMAIL', 'noreply@jadevinetours.com')

SERVER\_EMAIL = DEFAULT\_FROM\_EMAIL

ADMIN\_NOTIFICATION\_EMAIL = os.environ.get('ADMIN\_NOTIFICATION\_EMAIL', 'jadevinetravel@gmailcom')

```



\*\*Email tasks — `apps/accounts/tasks.py` (Phase 4):\*\*

\- `send\_cancellation\_requested\_customer\_email(booking\_id, refund\_info)`

\- `send\_cancellation\_requested\_admin\_email(booking\_id, refund\_info)`

\- `send\_cancellation\_confirmed\_customer\_email(booking\_id, refund\_info)`

\- `send\_cancellation\_confirmed\_admin\_email(booking\_id, refund\_info)`

\- `cleanup\_unverified\_accounts()` — scheduled Django-Q task, runs daily



\*\*Email tasks — `apps/bookings/tasks.py` (added post-Phase 3):\*\*

\- `send\_poa\_booking\_confirmation\_customer(booking\_id)` — HTML email to customer on Pay on Arrival confirmation. Contains full booking details, reference number, and payment instructions.

\- `send\_poa\_booking\_notification\_admin(booking\_id)` — HTML email to `ADMIN\_NOTIFICATION\_EMAIL` on every Pay on Arrival booking. Contains customer details, service details, and portal link.



\*\*When tasks fire:\*\*

\- Pay on Arrival: both tasks queued via `async\_task()` immediately after `booking.status = 'confirmed'` in `BookingSummaryView.post()`

\- Pay Now: confirmation email deferred to Phase 6 — sent after PesaPal IPN confirms payment

\- All tasks use `fail\_silently=True` — a broken email never crashes a booking confirmation



\*\*Email helper pattern (established in `apps/bookings/tasks.py`):\*\*

```python

\# Always use EmailMultiAlternatives — plain text fallback + HTML version

msg = EmailMultiAlternatives(subject, text\_body, settings.DEFAULT\_FROM\_EMAIL, \[recipient])

msg.attach\_alternative(html\_body, 'text/html')

msg.send(fail\_silently=True)

```



\*\*HTML email design\*\* matches `email\_confirmation\_signup\_message.html`:

\- Green header (`#1a4d2e`) with brand name and gold tagline (`#c89666`)

\- Inline CSS only — no external stylesheets (email clients strip `<link>` tags)

\- Mobile responsive via `@media (max-width: 620px)`

\- Plain text body always included for spam filter compatibility



\---



\## BOOKING SYSTEM ARCHITECTURE (session-first, DB-on-confirm)



\*\*Flow:\*\*

1\. User submits booking form on detail page (hotel, car, or tour)

2\. View validates data server-side. On success, stores validated data + \*\*snapshotted price\*\* in `request.session\[SESSION\_BOOKING\_KEY]`. No DB write.

3\. User sees summary page rendered from session data.

4\. User selects payment mode (Pay Now or Pay on Arrival) and clicks Confirm.

5\. \*\*Only at this point\*\* is the `Booking` DB record created.

6\. Pay on Arrival → `status='confirmed'` immediately, redirect to confirmation.

7\. Pay Now → `status='pending\_confirmation'`, redirect to payment stub → Phase 6 wires PesaPal.



\*\*Session key constant:\*\* `SESSION\_BOOKING\_KEY = 'pending\_booking'` — defined in `apps/bookings/views.py`



\*\*Orphan cleanup (Phase 6 task):\*\* PAY\_NOW bookings with `payment\_status='pending'` and no `pesapal\_tracking\_id` older than 24 hours should be cancelled by a Django-Q scheduled task.



\*\*Email on booking creation:\*\*

\- Pay on Arrival → `send\_poa\_booking\_confirmation\_customer` and `send\_poa\_booking\_notification\_admin` queued via `async\_task()` immediately after `booking.status = 'confirmed'`

\- Pay Now → no email at booking creation; confirmation sent in Phase 6 after PesaPal IPN



\*\*Price snapshotting:\*\* Price is captured into the session at form validation time in each booking view — NOT at booking creation time. Prevents race conditions if listing price changes between summary and confirm.



\---



\## BOOKING FORMS (apps/bookings/forms.py)



\*\*HotelBookingForm\*\*

\- Fields: `room\_type\_id` (hidden), `check\_in\_date`, `check\_out\_date`, `num\_guests`, `special\_requests`

\- Validation: check-in not in past, check-out after check-in

\- Date format: `Y-m-d` (Flatpickr)



\*\*CarBookingForm\*\*

\- Fields: `rental\_mode`, `pickup\_location`, `pickup\_date`, `return\_date`, `driver\_licence\_number`, `special\_requests`

\- Validation: `driver\_licence\_number` required if `rental\_mode='self\_drive'` — enforced server-side in `clean()`

\- Date format: `Y-m-d`



\*\*TourBookingForm\*\* ← added in Phase 3

\- Fields: `preferred\_date`, `num\_participants`, `special\_requests`

\- Validation: preferred\_date not in past, enforced in `clean()`

\- Cross-object validation (participant count vs. `group\_size\_max`) done in `TourBookingView`, not in the form — form has no reference to the TourPackage instance

\- Date format: `Y-m-d`



\*\*PaymentModeForm\*\*

\- Fields: `payment\_mode` (pay\_now / pay\_on\_arrival)

\- Submitted on summary page to trigger DB record creation



\---



\## TOURS APP — Phase 3 Architecture Decisions



\*\*`TourListView` uses the same-URL AJAX pattern as cars and hotels:\*\*

\- Normal GET → renders `tour\_list.html` with `tour\_count` for initial display

\- GET with `X-Requested-With: XMLHttpRequest` → returns JSON `{tours: \[...], count: N}`

\- Filter params: `tour\_type`, `max\_duration`, `max\_price` (all optional GET params)

\- No separate filter endpoint URL — same path, header detection in view



\*\*`TourDetailView` serializes to context:\*\*

\- `tour\_name`, `tour\_description` — resolved with language fallback at view level

\- `highlights`, `inclusions`, `exclusions`, `what\_to\_bring` — language-resolved lists/text

\- `itinerary\_days` — queryset, ordered by `day\_number`, rendered in template accordion

\- `photos` — queryset, rendered in gallery grid

\- `photos\_json` — JSON for GLightbox

\- `price\_per\_person` — passed as string to avoid Decimal serialization issues



\*\*`TourBookingView` (in apps/bookings/views.py):\*\*

\- POST only, same session-first pattern as Hotel and Car

\- Cross-object validation: `num\_participants > tour.group\_size\_max` checked in view

\- Session payload includes: `tour\_id`, `tour\_name`, `tour\_slug`, `tour\_type`, `tour\_type\_display`, `duration\_days`, `preferred\_date`, `num\_participants`, `price\_per\_person`, `total\_price`, `currency`, `special\_requests`, `created\_at`

\- Tours ALWAYS create with `status='pending\_confirmation'` — even after payment — Jadevine must confirm date manually. This is architecturally different from hotels and cars.



\*\*`\_create\_booking()` in `BookingSummaryView` handles all three service types:\*\*

\- `service\_type='hotel'` → links Hotel + HotelRoomType, sets check\_in/out dates, num\_guests

\- `service\_type='car'` → links CarRental, sets rental\_mode, pickup details, num\_days

\- `service\_type='tour'` → links TourPackage, sets preferred\_date, num\_participants



\*\*`apps/tours/urls.py`:\*\*

```python

app\_name = 'tours'

urlpatterns = \[

&#x20;   path('', TourListView.as\_view(), name='list'),

&#x20;   path('<slug:slug>/', TourDetailView.as\_view(), name='detail'),

&#x20;   path('<slug:slug>/book/', TourBookingView.as\_view(), name='book'),

&#x20;   # TourBookingView imported from apps.bookings.views

]

```



\---



\## REVEAL ANIMATION SYSTEM (Phase 3 addition)



Two coexisting systems — do not conflate them.



\### System 1: Scroll Reveal (existing, unchanged)

\- Class: `.jd-reveal`

\- CSS: `opacity: 0; transform: translateY(32px); transition: 0.7s ease`

\- Triggered by: `IntersectionObserver` in `main.js` at `threshold: 0.12`

\- Use on: content blocks below the fold, dynamically injected cards

\- Delay utilities: `.jd-reveal-delay-1` through `.jd-reveal-delay-5` (0.1s–0.5s)



\### System 2: Page-Load Reveal (added Phase 3)

\- Class: `.jd-load-reveal` with `data-delay="N"` attribute (N = 1–6)

\- CSS: `opacity: 0; transform: translateY(24px); transition: 0.6s ease`

\- Triggered by: `triggerLoadReveals()` in `main.js` on `DOMContentLoaded`

\- Stagger: `delay \* 80ms` per step (80ms, 160ms, 240ms, 320ms, 420ms, 540ms)

\- Use on: above-fold structural elements — page header, filter bar, results count row

\- Never use on dynamically injected elements



\### JD.initReveal() — bridges both systems

\- Exposed on `window.JD` by `main.js`

\- Called by page JS (`tour\_list.js`, `car\_list.js`, `hotel\_list.js`) after injecting cards

\- Observes `.jd-reveal` elements not yet watched (guards with `data-observed` attribute)

\- Prevents duplicate observer registrations on re-renders



\### Applied pattern on list pages (tour, car, hotel):

```html

<section class="tour-list-header jd-load-reveal" data-delay="1">

<section class="tour-filters-bar jd-load-reveal" data-delay="2">

<div class="d-flex ... jd-load-reveal" data-delay="3">  <!-- results count row -->

<!-- card grid: no load-reveal, cards get .jd-reveal from JS renderCard() -->

```



\### Applied pattern on detail pages (tour, car, hotel):

```html

<div class="tour-breadcrumb jd-load-reveal" data-delay="1">

<section class="tour-gallery-section jd-load-reveal" data-delay="2">

<div class="col-lg-7 jd-load-reveal" data-delay="3">   <!-- left content column -->

<div class="col-lg-5 jd-load-reveal" data-delay="4">   <!-- booking panel column -->

<!-- content blocks inside left column keep .jd-reveal for scroll trigger -->

```



\---



\## AUTHENTICATION SYSTEM



Two completely separate auth flows:



\*\*1. Customers\*\* — email + password via django-allauth

\- Register at `/accounts/signup/`

\- Login at `/accounts/login/`

\- Email verification required (`ACCOUNT\_EMAIL\_VERIFICATION = 'mandatory'`)

\- Email backend in dev: console (prints to terminal)

\- After login, redirected to `LOGIN\_REDIRECT\_URL = '/accounts/dashboard/'`



\*\*2. Admin / Mini-Admin\*\* — username + password via Django built-in auth

\- Login at `/portal/login/`

\- `is\_staff = True` required

\- Check `hasattr(user, 'miniadminprofile')` to identify mini-admin vs super admin



\*\*Allauth settings in base.py:\*\*

```python

ACCOUNT\_LOGIN\_METHODS = {'email'}

ACCOUNT\_SIGNUP\_FIELDS = \['email\*', 'password1\*', 'password2\*']

ACCOUNT\_EMAIL\_VERIFICATION = 'mandatory'

ACCOUNT\_UNIQUE\_EMAIL = True

LOGIN\_REDIRECT\_URL = '/accounts/dashboard/'

LOGOUT\_REDIRECT\_URL = '/'

```



\---



\## DESIGN SYSTEM



\*\*Typography:\*\*

\- Headings: Cormorant Garamond (serif, elegant)

\- Body: Jost (clean sans-serif)

\- CSS variables: `--font-heading`, `--font-body`



\*\*Core colour palette (CSS variables in `static/css/main.css`):\*\*

```css

\--color-primary:        #1a4d2e   /\* deep forest green \*/

\--color-primary-dark:   #122f1c

\--color-primary-light:  #2a6b40

\--color-primary-xlight: #e8f0eb



\--color-accent:         #c89666   /\* warm gold \*/

\--color-accent-dark:    #a67a50

\--color-accent-light:   #e8c99a

\--color-accent-xlight:  #faf3ea



\--color-off-white:      #f8f5f0

\--color-light:          #f0ebe3

\--color-border:         #e0d5c8

\--color-border-dark:    #c8b89a

\--color-text:           #1e1e1e

\--color-text-light:     #5a5550

\--color-muted:          #9e8e7e

\--color-dark:           #111111

\--color-overlay:        rgba(18, 47, 28, 0.62)

\--color-overlay-dark:   rgba(0, 0, 0, 0.55)



\--color-success:        #2d7a4f

\--color-success-bg:     #edf7f1

\--color-danger:         #b03a2e

\--color-danger-bg:      #fdf0ee

\--color-warning:        #c89666

\--color-warning-bg:     #fdf6ee

\--color-info:           #2471a3

\--color-info-bg:        #eaf4fb

```



\*\*Font size scale:\*\*

```css

\--text-xs: 0.75rem  |  --text-sm: 0.875rem  |  --text-base: 1rem

\--text-md: 1.125rem |  --text-lg: 1.25rem   |  --text-xl: 1.5rem

\--text-2xl: 2rem    |  --text-3xl: 2.5rem   |  --text-4xl: 3.5rem

```



\*\*Border radius scale:\*\*

```css

\--radius-sm: 4px  |  --radius-md: 8px  |  --radius-lg: 16px

\--radius-xl: 24px |  --radius-full: 9999px

```



\*\*Shadow scale:\*\*

```css

\--shadow-xs, --shadow-sm, --shadow-md, --shadow-lg, --shadow-xl

\--shadow-card: 0 4px 24px rgba(26,77,46,0.08)

\--shadow-card-hover: 0 12px 40px rgba(26,77,46,0.16)

```



\*\*Button classes:\*\* `.btn-primary-jd`, `.btn-accent-jd`, `.btn-outline-jd`, `.btn-outline-white-jd`, `.btn-ghost-jd`



\*\*Card class:\*\* `.jd-card` with hover lift



\*\*Form classes:\*\* `.jd-form-group`, `.jd-label`, `.jd-input`, `.jd-input-icon-wrap`, `.jd-input-icon`



\*\*Badge classes:\*\* `.jd-badge`, `.jd-badge-primary`, `.jd-badge-accent`, `.jd-badge-success`, `.jd-badge-warning`, `.jd-badge-danger`



\*\*Section utilities:\*\* `.section-py` (100px), `.section-py-sm` (60px), `.section-py-lg` (140px)



\*\*Typography utilities:\*\* `.eyebrow`, `.eyebrow-white`, `.section-heading`, `.section-subheading`



\---



\## JAVASCRIPT GLOBALS (main.js)



`window.JD` object is globally available:

```javascript

JD.toast('Message', 'success')   // types: success, error, info, ''

JD.csrfToken()                   // returns CSRF token for AJAX calls

JD.initReveal()                  // observe newly injected .jd-reveal elements

```



\*\*jQuery load order in base.html:\*\*

1\. Bootstrap 5 CSS

2\. Bootstrap Icons CSS

3\. Google Fonts

4\. `main.css`

5\. `\[page CSS via block extra\_css]`

6\. Bootstrap 5 JS bundle

7\. jQuery 3.7.1

8\. `main.js`

9\. `\[page JS via block extra\_js]`



\*\*Global handlers in main.js (do NOT re-implement in page JS):\*\*

\- Navbar scroll (transparent → solid) — respects `navbar-scrolled` set by template

\- Mobile hamburger menu + ESC close

\- Active nav link detection

\- IntersectionObserver scroll reveal (`.jd-reveal`)

\- Page-load reveal (`triggerLoadReveals()` for `.jd-load-reveal`)

\- `JD.initReveal()` for dynamically injected elements

\- Toast notifications

\- CSRF helper

\- Language switcher (submits Django i18n form)

\- Smooth scroll for anchor links

\- Newsletter form AJAX (`.jd-newsletter-form` class)



\---



\## BASE TEMPLATE BLOCKS

```

{% block title %}            — page title

{% block meta\_description %} — meta description

{% block navbar\_class %}     — default: navbar-transparent. Use 'navbar-scrolled' for inner pages

{% block body\_class %}       — body CSS classes

{% block extra\_css %}        — page-specific CSS (after main.css)

{% block content %}          — main page content

{% block extra\_js %}         — page-specific JS (after main.js)

```



\*\*All inner pages (non-hero) must set:\*\*

```html

{% block navbar\_class %}navbar-scrolled{% endblock %}

```



\---



\## JS TRANSLATION PATTERN



Static `.js` files are not processed by Django's template engine. All translatable strings go in the template's `{% block extra\_js %}` before the page JS file:



```html

{% block extra\_js %}

<script>

&#x20; window.JD\_STRINGS = window.JD\_STRINGS || {};

&#x20; window.JD\_STRINGS.viewTour   = "{% trans 'View Details' %}";

&#x20; window.JD\_STRINGS.toursError = "{% trans 'Failed to load tours. Please try again.' %}";

</script>

<script src="{% static 'js/tours/tour\_list.js' %}"></script>

{% endblock %}

```



In the JS file, consume from `window.JD\_STRINGS`:

```javascript

var label = window.JD\_STRINGS.viewTour || 'View Details';

```



\---



\## DATA PASSING: DJANGO VIEW → JS



Pass model data via `window.JD\_\*` globals in a `<script>` block before the page JS:

```html

<script>

&#x20; window.JD\_TOUR\_PRICE = "{{ price\_per\_person }}";

&#x20; window.JD\_TOUR\_MAX\_PARTICIPANTS = {{ tour.group\_size\_max }};

</script>

```



Never use hidden `data-\*` attributes for complex data objects.

Use `json.dumps()` in the view and `|safe` filter in the template for JSON data.



\---



\## THIRD-PARTY LIBRARIES (CDN — detail pages only)



Load in `{% block extra\_js %}` only on pages that need them. Do not load in `base.html`.



\*\*GLightbox\*\* (photo gallery lightbox):

```html

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/glightbox/dist/css/glightbox.min.css">

<script src="https://cdn.jsdelivr.net/npm/glightbox/dist/js/glightbox.min.js"></script>

```

Note: GLightbox CSS loaded in `extra\_js` block (not `extra\_css`) — matches established pattern from car\_detail and tour\_detail.



\*\*Flatpickr\*\* (date pickers):

```html

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">

<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>

```

Config: `dateFormat: 'Y-m-d'` (submitted value), `altInput: true`, `altFormat: 'D, d M Y'` (display), `disableMobile: true`



\---



\## LISTING APPROVAL WORKFLOW



Applies to Hotels and Car Rentals created by mini-admins. Tours are Super Admin only — no approval workflow.



\- Mini-admin creates listing → `approval\_status='pending'`, `is\_active=False`, NOT publicly visible

\- Super Admin approves → `approval\_status='approved'`, `is\_active=True`, publicly visible

\- Super Admin rejects → `approval\_status='rejected'`, `rejection\_reason` saved, NOT visible

\- Mini-admin edits rejected listing and resubmits → back to `approval\_status='pending'`

\- Mini-admin edits an APPROVED listing → resets to `approval\_status='pending'`, `is\_active=False`

\- Super Admin creates listing directly → `approval\_status='approved'`, `is\_active=True` (skips queue)



\*\*Server-side enforcement helpers (use in every portal view):\*\*

```python

def get\_accessible\_hotels(user):

&#x20;   if hasattr(user, 'miniadminprofile'):

&#x20;       return Hotel.objects.filter(created\_by=user)

&#x20;   return Hotel.objects.all()



def get\_accessible\_cars(user):

&#x20;   if hasattr(user, 'miniadminprofile'):

&#x20;       return CarRental.objects.filter(created\_by=user)

&#x20;   return CarRental.objects.all()

```



\---



\## MULTILINGUAL SETUP



\*\*3 languages at launch:\*\* English (default, no URL prefix), French (`/fr/`), Russian (`/ru/`)



\*\*Pattern for all views that serve model content:\*\*

```python

lang = request.LANGUAGE\_CODE  # 'en', 'fr', or 'ru'

value = getattr(obj, f'field\_{lang}', None) or obj.field\_en

\# Always fall back to English if translated field is empty

```



\*\*In templates:\*\* All UI strings use `{% trans "..." %}` or `{% blocktrans %}...{% endblocktrans %}`



\*\*In Python code:\*\* `from django.utils.translation import gettext\_lazy as \_` then `\_("string")`



\*\*Do NOT defer translation wrapping\*\* — wrap every string as you write each template.



\---



\## BOOKING SYSTEM RULES



\- Pay on Arrival is NOT available for Expedia hotel bookings or Amadeus flights (both post-launch)

\- Prices are ALWAYS snapshotted into session at validation time, and into DB at confirm time — never recalculate

\- Tour bookings ALWAYS start as `status='pending\_confirmation'` even after payment — Jadevine must manually confirm the date. This is permanent architecture, not a stub.

\- Hotel and Car Pay Now bookings move to `status='confirmed'` in Phase 6 after PesaPal IPN confirms payment. Currently stubbed.

\- Hotel and Car Pay on Arrival bookings move to `status='confirmed'` immediately on creation

\- Cancellation refund logic: query `CancellationPolicy` by `service\_type` and `days\_before\_service` — find matching tier



\---



\## CURRENTLY WORKING

\- `python manage.py runserver` starts cleanly with zero errors and zero warnings

\- `http://jadevinetravel.com//` loads full homepage with all animations

\- `http://jadevinetravel.com//admin/` loads Django admin, superuser login works

\- `http://jadevinetravel.com//hotels/` loads hotel list with AJAX filtering, skeleton loaders, load-reveal

\- `http://jadevinetravel.com//hotels/<slug>/` loads hotel detail with GLightbox, Flatpickr, booking form

\- Hotel booking flow end-to-end: Pay Now and Pay on Arrival ✅

\- `http://jadevinetravel.com//cars/` loads car list with AJAX filtering, skeleton loaders, load-reveal

\- `http://jadevinetravel.com//cars/<slug>/` loads car detail with rental mode toggle, conditional licence field

\- Car booking flow end-to-end: Pay Now and Pay on Arrival ✅

\- `http://jadevinetravel.com//tours/` loads tour list with AJAX filtering, skeleton loaders, load-reveal ✅

\- `http://jadevinetravel.com//tours/<slug>/` loads tour detail with itinerary accordion, GLightbox, Flatpickr, participant counter, live price breakdown ✅

\- Tour booking flow end-to-end: Pay Now and Pay on Arrival, always pending\_confirmation ✅

\- Booking summary page shows correct details for all three service types (hotel, car, tour) ✅

\- Pay on Arrival confirmation email sent to customer via Gmail SMTP ✅

\- Pay on Arrival admin notification email sent to jadevinetravel@gmailcom ✅

\- Booking records verified in `/admin/` with correct service\_type, status, payment\_mode, snapshotted prices

\- Page-load reveal system working on all list and detail pages (header → filters → content stagger)

\- Scroll reveal working on content blocks and dynamically injected cards via JD.initReveal()

\- Language switcher switches EN/FR/RU on all pages

\- Newsletter subscribe endpoint works

\- All migrations applied cleanly

\- Django-Q worker runs: `python manage.py qcluster`



\---



\## PHASE 4 SCOPE — User Accounts \& Dashboard



Build in this order:



\### Authentication — backend

1\. \*\*Registration view\*\* — collects first\_name, last\_name, email, password, password\_confirmation, preferred\_language. On submit: account created with `is\_active=False`. Django-Q sends email verification link.

2\. \*\*Email verification view\*\* — activates account (`is\_active=True`) on link click. Uses django-allauth email confirmation flow.

3\. \*\*Login view\*\* — email + password. Redirects to dashboard or `?next=` URL.

4\. \*\*Logout view\*\*

5\. \*\*Password reset\*\* — request form → Django-Q sends link → reset form

6\. \*\*Password change\*\* — requires current password confirmation



\*\*Portal authentication remains separate\*\* — `/portal/login/` uses username + password, checks `is\_staff=True`. Customer accounts cannot reach the portal. Do not touch portal auth in this phase.



\### User Dashboard — backend

1\. \*\*`DashboardView`\*\* — upcoming bookings (next 3 by service\_date), recent activity summary

2\. \*\*`BookingHistoryView`\*\* — all user bookings, paginated, filterable by status

3\. \*\*`BookingDetailView`\*\* — single booking full details

4\. \*\*`CancelBookingView`\*\*:

&#x20;  - Compute days between today and `booking.service\_date`

&#x20;  - Query `CancellationPolicy` for matching `service\_type` and day range

&#x20;  - Display refund amount to customer before confirmation

&#x20;  - On confirmation: `status='cancelled'`, `cancelled\_at` set, refund flagged if applicable

&#x20;  - Django-Q queues: cancellation email to customer

&#x20;  - Django-Q queues: cancellation notification to admin

&#x20;  - PesaPal refund flagged for manual processing by Super Admin (no automated refund at launch)

5\. \*\*`ProfileView`\*\* — view and update: name, phone, nationality, preferred\_language, profile\_photo

6\. \*\*`FavouritesView`\*\* — list saved items, handle remove

7\. \*\*`ToggleFavouriteView`\*\* — AJAX endpoint, returns `{saved: true/false}`, jQuery updates heart icon without page reload



\### User Dashboard — frontend

Templates needed (each with 3 files: html + css + js):

\- `templates/accounts/dashboard.html` + `static/css/accounts/dashboard.css` + `static/js/accounts/dashboard.js`

\- `templates/accounts/booking\_history.html` + css + js

\- `templates/accounts/booking\_detail.html` + css + js

\- `templates/accounts/profile.html` + css + js

\- `templates/accounts/favourites.html` + css + js



\### Django-allauth custom templates

These override allauth's default templates:

\- `templates/account/login.html` — styled to match Jadevine design

\- `templates/account/signup.html` — styled, adds first\_name, last\_name, preferred\_language fields

\- `templates/account/email\_confirm.html`

\- `templates/account/password\_reset.html`

\- `templates/account/password\_reset\_done.html`

\- `templates/account/password\_reset\_from\_key.html`



\### PDF download

\- `BookingDetailView` includes a PDF download endpoint

\- Uses ReportLab (already installed): booking reference, service details, dates, total, Jadevine contact info

\- Served as `Content-Disposition: attachment` response



\### Key rules for Phase 4

\- `booking.service\_date` property is the authoritative date for cancellation calculation — use it, do not recalculate

\- Cancellation policy lookup: query `CancellationPolicy.objects.filter(service\_type=booking.service\_type, is\_active=True).order\_by('-days\_before\_service')` — find first row where days\_remaining >= days\_before\_service

\- The `ToggleFavouriteView` uses `SavedFavourite` model's UniqueConstraints — use `get\_or\_create` / `delete` pattern, not `create` which will raise IntegrityError on duplicate

\- Profile photo upload goes to local media in dev, S3 in prod — same `DEFAULT\_FILE\_STORAGE` setting handles this

\- Do not implement OAuth (Google/Facebook) — post-launch only

\- Do not build any portal views in this phase — portal is Phase 5



\---



\## PHASES 5–9 SUMMARY (future reference)

| Phase | Name | Key Deliverables |

|---|---|---|

| 5 | Admin Portal | Super Admin full portal, Mini-Admin restricted portal, listing approval workflow, booking management |

| 6 | PesaPal Payment | Pay Now end-to-end (sandbox), IPN callback, booking status updates, orphan cleanup task |

| 7 | Gallery, Contact, Newsletter | Gallery page with GLightbox, contact form full processing, newsletter full processing |

| 8 | i18n, SEO \& QA | .po files for FR and RU, hreflang, sitemap, GA4, full QA checklist |

| 9 | Deployment | VPS setup, PostgreSQL, AWS S3, Nginx + Gunicorn, SSL, smoke test |



\---



\## POST-LAUNCH ONLY (do not implement in any phase)

\- Domestic flights (Amadeus API) — do not install any Amadeus package

\- Expedia hotel API

\- Booking.com affiliate

\- Discover Cars API

\- TripAdvisor Content API (embeddable widget only at launch)

\- Google OAuth and Facebook OAuth for customers

\- Arabic (RTL) language

\- Dutch and Italian languages

\- Pay on Arrival deposit requirement

\- Automated PesaPal refund processing (manual flagging only at launch)

\- SMS/WhatsApp automated notifications

\- Mobile app



\---



\## KEY CONVENTIONS (apply in every phase)

1\. Every user-facing string uses `{% trans %}` or `\_()` — never hardcode English

2\. Never store card data — PesaPal handles all card processing

3\. Mini-admin access restrictions enforced in the VIEW, not just the template

4\. Every form has server-side Django validation — jQuery validation is UX only

5\. All secrets in `.env` — never commit API keys

6\. Snapshot prices at booking time — never recalculate from listing

7\. Use Django ORM only — no raw SQL unless documented reason exists

8\. Use `select\_related()` and `prefetch\_related()` to avoid N+1 queries

9\. Backup database before every production migration

10\. Test every page on mobile before moving to next phase

11\. Commit to GitHub at end of every working day

12\. Language fallback pattern: `getattr(obj, f'field\_{lang}', None) or obj.field\_en`

13\. Portal is NEVER Django's built-in `/admin/` — that is developer-only

14\. Warn mini-admins before saving edits to an approved listing

15\. JS translation strings go in `window.JD\_STRINGS` in the template — never in static `.js` files

16\. Data from Django view to JS goes via `window.JD\_\*` globals in a `<script>` block before the page JS

17\. Booking DB record is created only when user clicks Confirm on the summary page — not at form submit

18\. Tour bookings always start as `status='pending\_confirmation'` — even after payment, permanently

19\. `.jd-load-reveal` with `data-delay` for above-fold structural elements; `.jd-reveal` for scroll-triggered and dynamically injected content; call `JD.initReveal()` after injecting cards into the DOM

20\. JS files use IIFE pattern: `(function($){ 'use strict'; ... })(jQuery);`



\---



\*End of Implementation Plan Handoff — Version 3.0 | April 2026\*

\*Prepared by Fidon for Jadevine Travel \& Tours\*

\*This document supersedes versions 1.0, 1.1, 2.0 (previous phases).\*

