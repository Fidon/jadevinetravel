\# JADEVINE TRAVEL \& TOURS — PHASE HANDOFF DOCUMENT

\*\*Version 6.0 | May 2026 | End of Phase 0, 1, 2, 3, 4, 5A, 5B \& 7\*\*



\---



\## PROJECT IDENTITY

\*\*Project:\*\* Jadevine Travel \& Tours — full-stack Django booking \& marketing platform

\*\*Client:\*\* Zanzibar-based travel company

\*\*Developer:\*\* Fidon (fidonamos@gmail.com, +255 713 529 019)

\*\*Root folder:\*\* jadevinetravel/

\*\*Django version:\*\* 6.0.4

\*\*Python:\*\* 3.13 (venv)

\*\*OS:\*\* Windows (PowerShell)

\*\*Database (dev):\*\* SQLite — jadevine\_db.sqlite3

\*\*Database (prod):\*\* PostgreSQL

\*\*Media (dev):\*\* Local filesystem

\*\*Media (prod):\*\* AWS S3



\---



\## DJANGO SETTINGS MODULE

Active settings: `config.settings.development`



\*\*.env required entries:\*\*

```

DJANGO\_SETTINGS\_MODULE=config.settings.development

SECRET\_KEY=your-secret-key-here

DEFAULT\_FROM\_EMAIL=Jadevine Travel \& Tours <your-email@gmail.com>

EMAIL\_BACKEND=django.core.mail.backends.smtp.EmailBackend

EMAIL\_HOST=smtp.gmail.com

EMAIL\_PORT=587

EMAIL\_USE\_TLS=True

EMAIL\_HOST\_USER=your-gmail@gmail.com

EMAIL\_HOST\_PASSWORD=your-app-password

ADMIN\_NOTIFICATION\_EMAIL=jadevinetravel@gmailcom

DEFAULT\_SITE\_URL=http://jadevinetravel.com/

```



Settings split:

\- `config/settings/base.py` — shared

\- `config/settings/development.py` — SQLite, local media, DEBUG=True

\- `config/settings/production.py` — PostgreSQL, AWS S3, SendGrid, DEBUG=False



\*\*Key settings in `config/settings/base.py`:\*\*

```python

ACCOUNT\_ADAPTER = 'apps.accounts.adapters.AccountAdapter'

ACCOUNT\_FORMS = {'signup': 'apps.accounts.forms.CustomSignupForm'}

ACCOUNT\_PASSWORD\_CHANGE\_REDIRECT\_URL = '/accounts/password/change/'

ACCOUNT\_EMAIL\_CONFIRMATION\_HMAC = True

ADMIN\_NOTIFICATION\_EMAIL = os.environ.get('ADMIN\_NOTIFICATION\_EMAIL', 'jadevinetravel@gmailcom')

DEFAULT\_SITE\_URL = os.environ.get('DEFAULT\_SITE\_URL', 'http://jadevinetravel.com/')



TEMPLATES = \[{

&#x20;   ...

&#x20;   'OPTIONS': {

&#x20;       'context\_processors': \[

&#x20;           ...

&#x20;           'apps.portal.context\_processors.portal\_context',

&#x20;       ],

&#x20;   },

}]

```



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

| Email | Gmail SMTP (dev) → SendGrid (prod) |

| PDF Generation | ReportLab |

| Payments | PesaPal REST API 3.0 (Phase 6 — next) |

| Lightbox | GLightbox (CDN) |

| Date Pickers | Flatpickr (CDN) |

| Table Management | DataTables 1.13.8 + Buttons 2.4.2 (CDN, portal only) |

| Drag-to-reorder | jQuery UI 1.13.3 (CDN, portal only) |

| Flights | Amadeus API — POST-LAUNCH |

| Hotels API | Expedia EAN — POST-LAUNCH |

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

│   ├── accounts/         ✅ COMPLETE — CustomUser, auth, dashboard

│   ├── hotels/           ✅ COMPLETE — Hotel, HotelPhoto, HotelRoomType, public views

│   ├── tours/            ✅ COMPLETE — TourPackage, TourItineraryDay, TourPhoto, public views

│   ├── cars/             ✅ COMPLETE — CarRental, CarPhoto, public views

│   ├── bookings/         ✅ COMPLETE — Booking, CancellationPolicy, booking flow

│   ├── reviews/          ✅ COMPLETE — Review model, SubmitReviewView

│   ├── gallery/          ✅ COMPLETE — GalleryCategory, GalleryItem, GalleryView

│   ├── contact/          ✅ COMPLETE — ContactMessage, NewsletterSubscriber, ContactView

│   └── portal/           ✅ COMPLETE (Phase 5A + 5B)

│       ├── \_\_init\_\_.py

│       ├── context\_processors.py

│       ├── forms.py

│       ├── mixins.py

│       ├── tasks.py      ✅ COMPLETE — all 5 email tasks

│       ├── urls.py       ✅ COMPLETE — no stubs remaining

│       └── views/

│           ├── \_\_init\_\_.py

│           ├── auth.py           — PortalLoginView, PortalLogoutView, PortalPasswordSetView

│           ├── dashboard.py

│           ├── hotels.py

│           ├── cars.py

│           ├── tours.py

│           ├── bookings.py

│           ├── reviews.py        ✅ Phase 5B

│           ├── gallery.py        ✅ Phase 5B

│           ├── users.py          ✅ Phase 5B

│           ├── miniadmins.py     ✅ Phase 5B

│           ├── messages.py       ✅ Phase 5B

│           ├── newsletter.py     ✅ Phase 5B

│           ├── policies.py       ✅ Phase 5B

│           └── settings.py       ✅ Phase 5B

│   └── core/             ✅ COMPLETE — Homepage, About, SavedFavourite

├── templates/

│   ├── base.html                          ✅ COMPLETE

│   ├── account/                           ✅ COMPLETE — allauth overrides

│   ├── accounts/                          ✅ COMPLETE — customer dashboard

│   ├── core/

│   │   ├── home.html                      ✅ COMPLETE

│   │   └── about.html                     ✅ COMPLETE (Phase 5B)

│   ├── hotels/                            ✅ COMPLETE

│   ├── tours/                             ✅ COMPLETE

│   ├── cars/                              ✅ COMPLETE

│   ├── bookings/                          ✅ COMPLETE

│   ├── gallery/

│   │   └── gallery.html                   ✅ COMPLETE (Phase 7)

│   ├── contact/

│   │   └── contact.html                   ✅ COMPLETE (Phase 7)

│   └── portal/                            ✅ COMPLETE (Phase 5A + 5B)

│       ├── portal\_base.html

│       ├── portal\_login.html

│       ├── portal\_set\_password.html       ✅ Phase 5B fix

│       ├── portal\_dashboard.html

│       ├── portal\_hotels\_list.html

│       ├── portal\_hotel\_form.html

│       ├── portal\_hotel\_detail.html

│       ├── portal\_cars\_list.html

│       ├── portal\_car\_form.html

│       ├── portal\_car\_detail.html

│       ├── portal\_tours\_list.html

│       ├── portal\_tour\_form.html

│       ├── portal\_tour\_detail.html

│       ├── portal\_bookings\_list.html

│       ├── portal\_booking\_detail.html

│       ├── portal\_reviews\_list.html       ✅ Phase 5B

│       ├── portal\_gallery.html            ✅ Phase 5B

│       ├── portal\_users\_list.html         ✅ Phase 5B

│       ├── portal\_user\_detail.html        ✅ Phase 5B

│       ├── portal\_miniadmins\_list.html    ✅ Phase 5B

│       ├── portal\_miniadmin\_form.html     ✅ Phase 5B

│       ├── portal\_miniadmin\_detail.html   ✅ Phase 5B

│       ├── portal\_messages\_list.html      ✅ Phase 5B

│       ├── portal\_message\_detail.html     ✅ Phase 5B

│       ├── portal\_newsletter.html         ✅ Phase 5B

│       ├── portal\_policies.html           ✅ Phase 5B

│       ├── portal\_settings.html           ✅ Phase 5B

│       └── includes/

│           ├── room\_type\_form\_fields.html

│           ├── itinerary\_day\_form\_fields.html

│           └── policy\_form\_fields.html    ✅ Phase 5B

├── static/

│   ├── css/

│   │   ├── main.css                       ✅ COMPLETE — full design system

│   │   ├── core/

│   │   │   ├── home.css                   ✅ COMPLETE

│   │   │   └── about.css                  ✅ COMPLETE (Phase 5B)

│   │   ├── hotels/                        ✅ COMPLETE

│   │   ├── tours/                         ✅ COMPLETE

│   │   ├── cars/                          ✅ COMPLETE

│   │   ├── bookings/                      ✅ COMPLETE

│   │   ├── accounts/                      ✅ COMPLETE

│   │   ├── gallery/

│   │   │   └── gallery.css                ✅ COMPLETE (Phase 7)

│   │   ├── contact/

│   │   │   └── contact.css                ✅ COMPLETE (Phase 7)

│   │   └── portal/

│   │       ├── portal\_base.css            ✅ COMPLETE

│   │       ├── portal\_dashboard.css       ✅ COMPLETE

│   │       ├── portal\_hotels.css          ✅ COMPLETE

│   │       ├── portal\_cars.css            ✅ COMPLETE

│   │       ├── portal\_tours.css           ✅ COMPLETE

│   │       ├── portal\_bookings.css        ✅ COMPLETE

│   │       ├── portal\_reviews.css         ✅ Phase 5B

│   │       ├── portal\_gallery.css         ✅ Phase 5B

│   │       ├── portal\_users.css           ✅ Phase 5B

│   │       ├── portal\_miniadmins.css      ✅ Phase 5B

│   │       ├── portal\_messages.css        ✅ Phase 5B

│   │       ├── portal\_newsletter.css      ✅ Phase 5B

│   │       ├── portal\_policies.css        ✅ Phase 5B

│   │       └── portal\_settings.css        ✅ Phase 5B

│   └── js/

│       ├── main.js                        ✅ COMPLETE

│       ├── core/

│       │   ├── home.js                    ✅ COMPLETE

│       │   └── about.js                   ✅ COMPLETE (Phase 5B)

│       ├── hotels/                        ✅ COMPLETE

│       ├── tours/                         ✅ COMPLETE

│       ├── cars/                          ✅ COMPLETE

│       ├── bookings/                      ✅ COMPLETE

│       ├── accounts/                      ✅ COMPLETE

│       ├── gallery/

│       │   └── gallery.js                 ✅ COMPLETE (Phase 7)

│       ├── contact/

│       │   └── contact.js                 ✅ COMPLETE (Phase 7)

│       └── portal/

│           ├── portal\_base.js             ✅ COMPLETE

│           ├── portal\_dashboard.js        ✅ COMPLETE

│           ├── portal\_hotels.js           ✅ COMPLETE

│           ├── portal\_cars.js             ✅ COMPLETE

│           ├── portal\_tours.js            ✅ COMPLETE

│           ├── portal\_bookings.js         ✅ COMPLETE

│           ├── portal\_reviews.js          ✅ Phase 5B

│           └── portal\_gallery.js          ✅ Phase 5B

```



\---



\## URL STRUCTURE (config/urls.py)

```python

\# NOT language-prefixed

/admin/                           — Django built-in admin (developer only)

/book/                            — All booking flow URLs

/reviews/                         — Review submission

/portal/                          — Admin portal

/portal/set-password/<uid>/<token>/ — Mini-admin password set (Django token, NOT allauth)

/i18n/                            — Django language switching



\# Portal URLs

/portal/login/

/portal/logout/

/portal/                                       — dashboard

/portal/api/pending-count/                     — JSON polling (60s)

/portal/hotels/                                — list

/portal/hotels/add/

/portal/hotels/pending/                        — Super Admin only

/portal/hotels/<pk>/

/portal/hotels/<pk>/edit/

/portal/hotels/<pk>/delete/

/portal/hotels/<pk>/approve/                   — Super Admin only

/portal/hotels/<pk>/reject/                    — Super Admin only

/portal/hotels/<pk>/resubmit/                  — Mini-Admin only

/portal/hotels/<hpk>/photos/upload/

/portal/hotels/<hpk>/photos/<pk>/delete/

/portal/hotels/<hpk>/photos/<pk>/cover/

/portal/hotels/<hpk>/photos/reorder/

/portal/hotels/<hpk>/rooms/add/

/portal/hotels/<hpk>/rooms/<pk>/edit/

/portal/hotels/<hpk>/rooms/<pk>/delete/

\# Cars mirrors Hotels

/portal/tours/                                 — Super Admin only throughout

/portal/bookings/

/portal/bookings/<pk>/

/portal/bookings/<pk>/status/

/portal/bookings/<pk>/mark-paid/

/portal/reviews/

/portal/reviews/<pk>/approve/

/portal/reviews/<pk>/reject/

/portal/gallery/

/portal/gallery/upload/

/portal/gallery/reorder/

/portal/gallery/<pk>/delete/

/portal/gallery/<pk>/toggle-featured/

/portal/gallery/categories/add/

/portal/gallery/categories/<pk>/edit/

/portal/gallery/categories/<pk>/delete/

/portal/users/

/portal/users/<pk>/

/portal/users/<pk>/deactivate/

/portal/users/<pk>/reset-password/

/portal/mini-admins/

/portal/mini-admins/add/

/portal/mini-admins/<pk>/

/portal/mini-admins/<pk>/edit/

/portal/mini-admins/<pk>/deactivate/

/portal/mini-admins/<pk>/reset-password/

/portal/messages/

/portal/messages/<pk>/

/portal/messages/<pk>/reply/

/portal/messages/<pk>/status/

/portal/newsletter/

/portal/newsletter/<pk>/toggle/

/portal/policies/

/portal/policies/add/

/portal/policies/<pk>/edit/

/portal/policies/<pk>/delete/

/portal/settings/



\# Language-prefixed public URLs (English has no prefix)

/                                 — Homepage

/hotels/                          — Hotel listing

/hotels/<slug>/                   — Hotel detail

/hotels/<slug>/book/              — Hotel booking POST

/tours/                           — Tour listing

/tours/<slug>/                    — Tour detail

/tours/<slug>/book/               — Tour booking POST

/cars/                            — Car listing

/cars/<slug>/                     — Car detail

/cars/<slug>/book/                — Car booking POST

/gallery/                         — Gallery ✅ Phase 7

/about/                           — About Us ✅ Phase 5B

/contact/                         — Contact Us ✅ Phase 7

/contact/newsletter/              — Newsletter subscribe (AJAX POST)

/accounts/dashboard/

/accounts/bookings/

/accounts/bookings/<reference>/

/accounts/bookings/<reference>/cancel/

/accounts/bookings/<reference>/pdf/

/accounts/bookings/<reference>/review/

/accounts/profile/

/accounts/favourites/

/accounts/favourites/toggle/

/accounts/resend-verification/

/accounts/login/

/accounts/signup/

/accounts/logout/

/accounts/confirm-email/<key>/

/accounts/password/reset/

/accounts/password/change/

```



App namespaces: `core`, `hotels`, `tours`, `cars`, `bookings`, `reviews`, `gallery`, `contact`, `accounts`, `portal`



\---



\## ALL DATABASE MODELS (fully migrated)



\### apps/accounts/models.py

\*\*CustomUser\*\* (extends AbstractUser)

\- `email` — customer login identifier

\- `username` — admin/mini-admin login identifier (stored lowercase, matched iexact)

\- `first\_name`, `last\_name`, `phone`, `nationality`

\- `preferred\_language` — en/fr/ru

\- `profile\_photo` — ImageField (upload\_to='profiles/')

\- `is\_staff` — True for Super Admin and Mini-Admin

\- `AUTH\_USER\_MODEL = 'accounts.CustomUser'`

\- Property: `full\_name`



\*\*MiniAdminProfile\*\*

\- `user` — OneToOneField → CustomUser

\- `created\_by` — ForeignKey → CustomUser

\- Detect mini-admin: `hasattr(user, 'miniadminprofile')`



\### apps/hotels/models.py

\*\*Hotel\*\* — name, slug (auto), location, description\_en/fr/ru, stars, price\_per\_night, address, latitude, longitude, tripadvisor\_url, created\_by, approval\_status (pending/approved/rejected), rejection\_reason, is\_active

\- Public: `is\_active=True AND approval\_status='approved'`

\- `cover\_photo` property, `is\_publicly\_visible` property, `get\_description(lang)` method



\*\*HotelPhoto\*\* — hotel, image, caption, is\_cover, order



\*\*HotelRoomType\*\* — hotel, name, description\_en/fr/ru, price\_per\_night (nullable), max\_guests, amenities (JSONField), is\_available, discount\_percent, discount\_expires\_at, is\_refundable, allows\_pay\_on\_arrival

\- `get\_effective\_price()`, `get\_discounted\_price()`, `get\_display\_price()`, `has\_active\_discount`



\### apps/tours/models.py

\*\*TourPackage\*\* — name\_en/fr/ru, slug, tour\_type, description\_en/fr/ru, duration\_days, group\_size\_max, price\_per\_person, highlights/inclusions/exclusions\_en/fr/ru (JSONField), what\_to\_bring\_en/fr/ru, cover\_image, is\_active, is\_featured, discount\_percent, discount\_expires\_at, is\_refundable, allows\_pay\_on\_arrival

\- NO created\_by or approval\_status — Super Admin only

\- `get\_name(lang)`, `get\_description(lang)`, `get\_display\_price()`, `has\_active\_discount`



\*\*TourItineraryDay\*\* — package, day\_number, title\_en/fr/ru, description\_en/fr/ru



\*\*TourPhoto\*\* — package, image, caption, order

\- \*\*No `is\_cover` field\*\* — tour cover is `TourPackage.cover\_image` (direct ImageField)



\### apps/cars/models.py

\*\*CarRental\*\* — name, slug, vehicle\_type, make, model, year, capacity, fuel\_type, transmission, price\_per\_day, offers\_self\_drive, offers\_driver, driver\_speaks\_en/fr, pickup\_locations (JSONField), description\_en/fr/ru, created\_by, approval\_status, rejection\_reason, is\_available, is\_active, discount\_percent, discount\_expires\_at, is\_refundable, allows\_pay\_on\_arrival

\- Public: `is\_active=True AND is\_available=True AND approval\_status='approved'`

\- `cover\_photo` property, `get\_display\_price()`, `has\_active\_discount`



\*\*CarPhoto\*\* — car, image, is\_cover, order



\### apps/bookings/models.py

\*\*CancellationPolicy\*\* — service\_type, days\_before\_service, refund\_percentage, label\_en, is\_active

\- Default tiers seeded: 14+ days=100%, 7-13 days=50%, 0-6 days=0%

\- `SERVICE\_TYPE\_CHOICES` defined as class-level attribute



\*\*Booking\*\* — reference (JDV-YYYY-NNNNN auto), user, service\_type, hotel, room\_type, tour\_package, car, date fields, num\_guests/participants/days, car-specific fields, base\_price, total\_price, currency, payment\_mode, payment\_status, pesapal\_order\_id/tracking\_id, status, special\_requests, is\_refundable (snapshotted), cancellation\_reason, cancelled\_at, cancelled\_by

\- STATUS\_CHOICES includes `cancellation\_requested`

\- `service\_date` property, `nights` property



\### apps/reviews/models.py

\*\*Review\*\* — user, booking (OneToOneField), service\_type, hotel/tour\_package/car (nullable FKs), rating (1-10), comment, status (pending/approved/rejected), rejection\_reason, moderated\_by, moderated\_at

\- Display threshold: only show when listing has ≥ 3 approved reviews



\### apps/gallery/models.py

\*\*GalleryCategory\*\* — name\_en/fr/ru, slug (auto-generated in save()), order



\*\*GalleryItem\*\* — category, media\_type (photo/video), image, video\_url, video\_file, caption\_en/fr/ru, is\_featured, order



\### apps/contact/models.py

\*\*ContactMessage\*\* — name, email, phone, subject, message, inquiry\_type, preferred\_lang, status (new/in\_progress/resolved), admin\_notes

\- `STATUS\_CHOICES` and `INQUIRY\_TYPE\_CHOICES` defined as class-level attributes



\*\*NewsletterSubscriber\*\* — email (unique), is\_active, subscribed\_at



\### apps/core/models.py

\*\*SavedFavourite\*\* — user, hotel, tour\_package, car (one FK populated), UniqueConstraints per user per item



\---



\## AUTHENTICATION SYSTEM



\*\*Customer auth (django-allauth)\*\*

```python

ACCOUNT\_LOGIN\_METHODS = {'email'}

ACCOUNT\_SIGNUP\_FIELDS = \['email\*', 'password1\*', 'password2\*']

ACCOUNT\_EMAIL\_VERIFICATION = 'mandatory'

ACCOUNT\_UNIQUE\_EMAIL = True

LOGIN\_REDIRECT\_URL = '/accounts/dashboard/'

LOGOUT\_REDIRECT\_URL = '/'

ACCOUNT\_ADAPTER = 'apps.accounts.adapters.AccountAdapter'

ACCOUNT\_FORMS = {'signup': 'apps.accounts.forms.CustomSignupForm'}

```



\*\*Portal auth (Django built-in)\*\*

\- Login at `/portal/login/` — `PortalLoginView` in `apps/portal/views/auth.py`

\- Case-insensitive username lookup: `CustomUser.objects.get(username\_\_iexact=username\_raw)`

\- `is\_staff=True` required

\- Customer accounts cannot access portal



\*\*Mini-admin password reset — CRITICAL\*\*

\- Welcome email and reset-password emails send to `/portal/set-password/<uid>/<token>/`

\- This uses Django's `default\_token\_generator` and `PasswordResetConfirmView`

\- \*\*NEVER use allauth's URL pattern\*\* (`/accounts/password/reset/key/<uid>-<token>/`) for staff users — allauth rejects tokens generated by `default\_token\_generator`

\- `PortalPasswordSetView` in `apps/portal/views/auth.py` extends Django's `PasswordResetConfirmView`



\---



\## PORTAL ARCHITECTURE



\*\*Mixins\*\* (`apps/portal/mixins.py`)

```python

PortalRequiredMixin      # authenticated + is\_staff=True

SuperAdminRequiredMixin  # extends PortalRequiredMixin + blocks mini-admins → 403

```



\*\*Access control helpers (call in EVERY portal view touching listings/bookings)\*\*

```python

get\_accessible\_hotels(user)    # Super Admin: all / Mini-Admin: created\_by=user

get\_accessible\_cars(user)      # Super Admin: all / Mini-Admin: created\_by=user

get\_accessible\_bookings(user)  # Super Admin: all / Mini-Admin: own hotels+cars only

get\_accessible\_reviews(user)   # Super Admin: all / Mini-Admin: own hotel+car reviews only

is\_mini\_admin(user)            # bool

```



\*\*Context processor\*\* (`apps/portal/context\_processors.py`)

Registered in `TEMPLATES\[0]\['OPTIONS']\['context\_processors']`.

Injects into every portal template:

\- `pending\_total`, `pending\_hotels`, `pending\_cars`

\- `unread\_messages`, `pending\_reviews`

\- `mini\_admin` (boolean)



Only fires DB queries when `request.user.is\_authenticated and request.user.is\_staff`.



\*\*Pending count polling\*\*

`portal\_base.js` calls `GET /portal/api/pending-count/` every 60 seconds.

Returns `{"hotels": N, "cars": M, "total": N+M}`.

Mini-admins: endpoint returns zeros, setInterval is skipped.



\---



\## PORTAL CSS \& JS ARCHITECTURE



\*\*CSS files (one shared base + per-section)\*\*

```

portal\_base.css     — sidebar, topbar, nav, stat cards, tables, modals,

&#x20;                     photo grid, approval badges, portal cards, forms

portal\_hotels.css   — hotel thumbnail, room type list, btn-danger-jd

portal\_cars.css     — min-width for #cars-table

portal\_tours.css    — itinerary list, day-number badge

portal\_bookings.css — booking status badges, price breakdown

portal\_reviews.css  — service badges, rating colour scale, detail modal

portal\_gallery.css  — two-column layout, category sidebar, item grid

portal\_users.css    — list table, detail profile card, booking stats

portal\_miniadmins.css — partner profile card, stat grid

portal\_messages.css — filter row, sender cell, message body, reply history

portal\_newsletter.css — table min-width only

portal\_policies.css — days badge, refund badge colour variants

portal\_settings.css — two-column grid (side by side lg+, stacked sm), pw toggle

```



\*\*JS files\*\*

```

portal\_base.js      — sidebar, active nav (longest-match), flash dismiss,

&#x20;                     pending count polling, PORTAL.csrf(), #confirmModal,

&#x20;                     PORTAL.initDataTable() factory, portal-autosubmit

portal\_dashboard.js — dashboard interactions

portal\_hotels.js    — rejection modal, language tabs, room modal, photo AJAX

portal\_cars.js      — same pattern as hotels, no room type modal

portal\_tours.js     — language tabs, itinerary day modal, photo AJAX (no set-cover)

portal\_bookings.js  — DataTables, CSV/Excel/PDF/Print

portal\_reviews.js   — approve AJAX, reject modal AJAX, detail modal

portal\_gallery.js   — photo upload queue, video URL, delete, featured toggle, reorder

```



\*\*PORTAL globals (window.PORTAL)\*\*

```javascript

PORTAL.csrfToken       // string

PORTAL.isMiniAdmin     // boolean

PORTAL.pendingTotal    // integer

PORTAL.pendingReviews  // integer

PORTAL.urls.pendingCount

PORTAL.urls.dashboard

PORTAL.csrf()          // function

PORTAL.initDataTable(selector, overrides)  // DataTables factory

```



\---



\## MODAL STRUCTURE PATTERN

All portal modals use `form { display: contents }` so the form is transparent to Bootstrap's flex column:

```html

<div class="modal-content">

&#x20; <form method="post" action="...">

&#x20;   {% csrf\_token %}

&#x20;   <div class="modal-header">...</div>

&#x20;   <div class="modal-body">...</div>

&#x20;   <div class="modal-footer">...</div>

&#x20; </form>

</div>

```

CSS in `portal\_base.css`:

```css

.portal-modal .modal-dialog-scrollable { max-height: calc(100% - 3.5rem); }

.portal-modal .modal-content { max-height: 100%; display: flex; flex-direction: column; }

.portal-modal form { display: contents; }

.portal-modal .modal-header .modal-title,

.portal-modal .modal-header .modal-title i { color: #fff; }

```



\---



\## PHOTO MANAGEMENT PATTERN (Hotels, Cars, Tours)

AJAX contract (all three use identical pattern):

```

Upload:    POST /portal/{type}/{pk}/photos/upload/  — multipart, one image per call

Delete:    POST /portal/{type}/{pk}/photos/{photo\_pk}/delete/

Set Cover: POST /portal/{type}/{pk}/photos/{photo\_pk}/cover/ — Hotels/Cars only

Reorder:   POST /portal/{type}/{pk}/photos/reorder/ — JSON body {"order": \[id, id, ...]}

```



\*\*TourPhoto has no `is\_cover` field\*\* — no set-cover button in tour photo grids.

Tour cover is `TourPackage.cover\_image` (direct ImageField on the model).



Upload area click fix (prevents browser loop):

```javascript

$area.on('click', function(e) {

&#x20; if (!$(e.target).is($input)) { $input.trigger('click'); }

});

$input.on('click', function(e) { e.stopPropagation(); });

```



Photo delete uses shared `#confirmModal` + `window.\_photoDeletePending` flag + `portal:photo-delete-confirmed` jQuery event.



\---



\## EMAIL SYSTEM



\*\*Transport:\*\* Gmail SMTP (dev), SendGrid (prod)

Admin emails always go to: `settings.ADMIN\_NOTIFICATION\_EMAIL`



\*\*Email tasks by app:\*\*



`apps/portal/tasks.py` — 5 tasks:

1\. `notify\_superadmin\_new\_listing(listing\_type, listing\_id)`

2\. `send\_listing\_approved\_email(listing\_type, listing\_id)`

3\. `send\_listing\_rejected\_email(listing\_type, listing\_id)` — reads `listing.rejection\_reason`

4\. `send\_miniadmin\_welcome\_email(user\_id)` — sends to `/portal/set-password/<uid>/<token>/`

5\. `send\_contact\_reply\_email(message\_id, reply\_text)` — reply to contact form sender



`apps/bookings/tasks.py` — 2 tasks:

\- `send\_poa\_booking\_confirmation\_customer(booking\_id)`

\- `send\_poa\_booking\_notification\_admin(booking\_id)`



`apps/accounts/tasks.py` — 4 tasks + 1 scheduled:

\- `send\_cancellation\_requested\_customer\_email(booking\_id, refund\_info)`

\- `send\_cancellation\_requested\_admin\_email(booking\_id, refund\_info)`

\- `send\_cancellation\_confirmed\_customer\_email(booking\_id, refund\_info)`

\- `send\_cancellation\_confirmed\_admin\_email(booking\_id, refund\_info)`

\- `cleanup\_unverified\_accounts()` — daily Django-Q scheduled task



`apps/contact/tasks.py` — 2 tasks:

\- `send\_contact\_acknowledgement\_customer(message\_id)`

\- `send\_contact\_notification\_admin(message\_id)`



\*\*Email HTML rules (never violate):\*\*

\- Never use `display:flex` or `display:grid` — Gmail strips these

\- Use `<table>` for all multi-column layouts and amount rows

\- Inline CSS only — no `<link>` tags

\- Always include plain-text body

\- Mobile responsive via `@media (max-width: 620px)`

\- Green header `#1a4d2e`, gold accent `#c89666`

\- Footer: `Jadevine Travel \& Tours | Zanzibar, Tanzania | info@jadevinetravel.com`



\---



\## LISTING APPROVAL WORKFLOW

Applies to Hotels and Car Rentals. Tours skip this entirely — Super Admin only.



```

Mini-Admin creates  → approval\_status='pending', is\_active=False (not public)

&#x20;                   → async\_task: notify\_superadmin\_new\_listing



Super Admin approves → approval\_status='approved', is\_active=True (goes live)

&#x20;                    → async\_task: send\_listing\_approved\_email



Super Admin rejects  → approval\_status='rejected', rejection\_reason saved

&#x20;                    → async\_task: send\_listing\_rejected\_email



Mini-Admin resubmits rejected → approval\_status='pending', reason cleared

&#x20;                             → async\_task: notify\_superadmin\_new\_listing



Mini-Admin edits APPROVED     → approval\_status='pending', is\_active=False

&#x20;                             → async\_task: notify\_superadmin\_new\_listing

&#x20;                             → WARNING shown in UI before save



Super Admin creates directly  → approval\_status='approved', is\_active=True (skips queue)

Super Admin edits any listing → no approval state change (trusted)

```



State machine enforced in `form\_valid()`, not in `model.save()`.



\---



\## BOOKING SYSTEM ARCHITECTURE



\*\*Session-first, DB-on-confirm pattern:\*\*

1\. User submits booking form → validated data + snapshotted price stored in `request.session\['pending\_booking']`. No DB write.

2\. User sees summary rendered from session.

3\. User clicks Confirm → `Booking` DB record created at this point only.

4\. Pay on Arrival → `status='confirmed'` immediately.

5\. Pay Now → `status='pending\_confirmation'` → Phase 6 wires PesaPal.



\*\*Price snapshotting:\*\* Always call `get\_display\_price()` — never read `price\_per\_night`, `price\_per\_day`, or `price\_per\_person` directly for display or booking.



\*\*`is\_refundable` snapshotted\*\* at booking creation from listing's current value. Never retroactively affected by listing changes.



\*\*`allows\_pay\_on\_arrival=False` enforced server-side\*\* in `BookingSummaryView.\_create\_booking()` — UI suppression alone is not sufficient.



\*\*Tour bookings always\*\* `status='pending\_confirmation'` — even after payment. Permanent architecture.



\*\*Orphan cleanup (Phase 6 task):\*\* PAY\_NOW bookings with `payment\_status='pending'` and no `pesapal\_tracking\_id` older than 24 hours should be cancelled by a Django-Q scheduled task.



\---



\## PORTAL FORMS (apps/portal/forms.py)

\- `HotelForm` — Hotel create/edit

\- `HotelRoomTypeForm` — Room type modal (amenities textarea → JSONField)

\- `HotelRejectionForm` — rejection\_reason (required, min 10 chars)

\- `CarRentalForm` — Car create/edit (pickup\_locations textarea → JSONField)

\- `CarRejectionForm`

\- `TourPackageForm` — Tour create/edit (highlights/inclusions/exclusions textarea → JSONField)

\- `TourItineraryDayForm`

\- `BookingStatusForm` — choices filtered to valid transitions only

\- `BookingMarkPaidForm`

\- `STATUS\_TRANSITIONS` dict — valid next states per current status



\*\*Mini-admin forms\*\* (in `apps/portal/views/miniadmins.py`):

\- `MiniAdminCreateForm` — username validation regex: `^\[a-z]\[a-z0-9\_]\*\[a-z0-9]$`

&#x20; - Starts and ends with letter or digit

&#x20; - No underscore at start or end

&#x20; - Min 2 characters

&#x20; - Stored as lowercase

\- `MiniAdminEditForm` — ModelForm, excludes username



\*\*Portal settings forms\*\* (in `apps/portal/views/settings.py`):

\- `PortalUsernameForm` — same regex as MiniAdminCreateForm

\- `PortalPasswordChangeForm` — wraps Django's PasswordChangeForm with jd-input class



\---



\## GALLERY APP (Phase 7)



\*\*`apps/gallery/views.py` — `GalleryView`:\*\*

\- Resolves category names and item captions per language with English fallback

\- Filters by `?category=<slug>` GET param

\- Passes resolved dicts to template (not raw model instances) to avoid template-level language fallback logic



\*\*`apps/gallery/models.py` — `GalleryCategory.save()`:\*\*

Auto-slug generation on save — slug is generated from `name\_en` if not already set. Uniqueness ensured with counter suffix.



\---



\## CONTACT APP (Phase 7)



\*\*`apps/contact/views.py` — `ContactView`:\*\*

\- GET: renders form

\- POST: server-side validation → creates `ContactMessage` → queues two email tasks → returns JSON

\- Returns `{'success': True, 'message': '...'}` or `{'success': False, 'errors': {...}}`



\*\*`apps/contact/tasks.py`:\*\*

\- `send\_contact\_acknowledgement\_customer(message\_id)` — to sender

\- `send\_contact\_notification\_admin(message\_id)` — to `ADMIN\_NOTIFICATION\_EMAIL`



\*\*Newsletter:\*\* `NewsletterSubscribeView` is unchanged from Phase 1. The `.jd-newsletter-form` class on any form triggers the global handler in `main.js`. Do NOT duplicate this handler in `contact.js`.



\---



\## PORTAL SETTINGS PAGE

Two forms on one page, distinguished by `form\_action` hidden field:

\- `form\_action=username` → `PortalUsernameForm`

\- `form\_action=password` → `PortalPasswordChangeForm`



Password change calls `update\_session\_auth\_hash(request, user)` after save — without this, Django invalidates the session and logs the user out.



Side-by-side layout: `settings-grid` with `grid-template-columns: 1fr 1fr` on lg+, stacks on smaller screens.



Password field eye/slash-eye toggle implemented in inline `<script>` in the template.



\---



\## DESIGN SYSTEM



\*\*Typography:\*\* Cormorant Garamond (headings) + Jost (body)



\*\*Core CSS variables (in `static/css/main.css`):\*\*

```css

\--color-primary:        #1a4d2e

\--color-primary-dark:   #122f1c

\--color-primary-light:  #2a6b40

\--color-primary-xlight: #e8f0eb

\--color-accent:         #c89666

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

\--color-success:        #2d7a4f    --color-success-bg: #edf7f1

\--color-danger:         #b03a2e    --color-danger-bg:  #fdf0ee

\--color-warning:        #c89666    --color-warning-bg: #fdf6ee

\--color-info:           #2471a3    --color-info-bg:    #eaf4fb

\--font-heading: 'Cormorant Garamond', Georgia, serif

\--font-body:    'Jost', 'Segoe UI', sans-serif

\--radius-sm: 4px  --radius-md: 8px  --radius-lg: 16px  --radius-full: 9999px

```



\*\*Public site JS globals (window.JD):\*\*

```javascript

JD.toast('Message', 'success')   // success, error, info, ''

JD.csrfToken()                   // returns CSRF token

JD.initReveal()                  // observe newly injected .jd-reveal elements

```



\*\*Reveal systems:\*\*

\- `.jd-reveal` + `.jd-reveal-delay-N` — scroll-triggered (IntersectionObserver)

\- `.jd-load-reveal` + `data-delay="N"` — above-fold stagger on DOMContentLoaded

\- Call `JD.initReveal()` after injecting cards dynamically



\---



\## MULTILINGUAL SETUP

3 languages: English (default, no prefix), French (`/fr/`), Russian (`/ru/`)



Language fallback pattern (use in every view serving model content):

```python

lang = request.LANGUAGE\_CODE  # 'en', 'fr', or 'ru'

value = getattr(obj, f'field\_{lang}', None) or obj.field\_en

\# Always fall back to English

```



JS translation strings → `window.JD\_STRINGS` in template — never in static `.js` files.

Django → JS data → `window.JD\_\*` globals in `<script>` block before page JS.



\---



\## DJANGO-Q SCHEDULED TASKS

```python

\# Registered via migration accounts/0002\_seed\_cleanup\_schedule

Schedule(

&#x20;   name='Cleanup unverified accounts',

&#x20;   func='apps.accounts.tasks.cleanup\_unverified\_accounts',

&#x20;   schedule\_type='D',

&#x20;   repeats=-1,

)

```

Run worker: `python manage.py qcluster`



\---



\## CURRENTLY WORKING (end of Phase 5B + Phase 7)



\*\*Public site:\*\*

\- Homepage, hotels, tours, cars — list and detail with full booking flow

\- Hotel/car/tour: Pay Now (stub) and Pay on Arrival end-to-end

\- User dashboard: history, cancellations, favourites, profile, PDF download

\- Email: POA confirmation, cancellation, verification emails

\- About Us page — full static page with sections

\- Gallery page — masonry grid, GLightbox lightbox, category filter tabs

\- Contact page — AJAX form, inquiry type selector, FAQ section, map embed

\- Newsletter: AJAX subscribe via `.jd-newsletter-form` class globally



\*\*Portal (Phase 5A + 5B):\*\*

\- `/portal/login/` — case-insensitive username, is\_staff check

\- `/portal/` — dashboard with pending approvals, stats, revenue

\- `/portal/hotels/` — full CRUD, approval workflow, photo/room management

\- `/portal/cars/` — same structure as hotels

\- `/portal/tours/` — Super Admin only, itinerary days, photos

\- `/portal/bookings/` — DataTables, status updates, mark POA paid

\- `/portal/reviews/` — AJAX approve/reject, both roles scoped

\- `/portal/gallery/` — categories, photo upload, video URL, reorder, featured

\- `/portal/users/` — list, detail, deactivate, password reset

\- `/portal/mini-admins/` — create, welcome email, detail, deactivate

\- `/portal/messages/` — list, detail, reply (email task), status update

\- `/portal/newsletter/` — DataTables with export, toggle active

\- `/portal/policies/` — grouped by service type, add/edit/delete modals

\- `/portal/settings/` — side-by-side cards, eye toggle on password fields

\- `/portal/set-password/<uid>/<token>/` — mini-admin password set via Django token



\---



\## PHASE 6 SCOPE — PesaPal Payment Integration (next phase)



Build in a new conversation. Key points:



\*\*PesaPal credentials in `.env`:\*\*

```

PESAPAL\_CONSUMER\_KEY=...

PESAPAL\_CONSUMER\_SECRET=...

PESAPAL\_ENVIRONMENT=sandbox

```



\*\*Service module:\*\* `apps/bookings/pesapal.py`

\- `get\_auth\_token()` — authenticates, returns bearer token

\- `submit\_order\_request(booking)` — submits order, returns PesaPal redirect URL

\- `get\_transaction\_status(order\_tracking\_id)` — independent verification



\*\*Views to update:\*\*

\- `PaymentOptionsView` — calls `submit\_order\_request()`, redirects to PesaPal

\- IPN callback view at `/book/pesapal/callback/`

\- `BookingConfirmationView` — reads actual DB state, not URL parameters



\*\*IPN callback:\*\*

\- POST from PesaPal → call `get\_transaction\_status()` to verify independently

\- If confirmed: `booking.payment\_status='paid'`, update `booking.status`

&#x20; - Hotels/Cars: `status='confirmed'`

&#x20; - Tours: stays `status='pending\_confirmation'` (Jadevine must confirm date)

\- Queue: confirmation email to customer + notification to admin



\*\*Orphan cleanup task:\*\* Django-Q scheduled task cancels PAY\_NOW bookings with `payment\_status='pending'` and no `pesapal\_tracking\_id` older than 24 hours.



\*\*Development:\*\* Use ngrok to expose local server for PesaPal IPN callback.

```

ngrok http 8000

```

Register the ngrok URL in PesaPal sandbox settings as the IPN callback URL.



\*\*IMPORTANT:\*\* Submit PesaPal merchant account for production activation during Phase 6 — not at deployment. Approval takes 3–7 business days.



\---



\## POST-LAUNCH ONLY (do not implement)

\- Domestic flights (Amadeus API)

\- Expedia hotel API / Booking.com

\- Discover Cars API

\- TripAdvisor Content API (widget only)

\- Google OAuth / Facebook OAuth

\- Arabic (RTL), Dutch, Italian languages

\- Pay on Arrival deposit requirement

\- Automated PesaPal refund processing

\- SMS/WhatsApp automated notifications

\- Mobile app



\---



\## KEY CONVENTIONS (apply in every phase)

1\. Every user-facing string: `{% trans %}` or `\_()` — never hardcode English

2\. Never store card data — PesaPal handles all card processing

3\. Mini-admin restrictions enforced in VIEW — never only in template

4\. Server-side Django validation is authoritative — jQuery is UX only

5\. All secrets in `.env`

6\. Snapshot prices via `get\_display\_price()` — never use raw price fields directly

7\. Snapshot `is\_refundable` at booking time — never retroactively changed

8\. Django ORM only — no raw SQL

9\. `select\_related()` and `prefetch\_related()` — avoid N+1

10\. DB backup before every production migration

11\. Test mobile before moving to next phase

12\. Commit to GitHub daily

13\. Language fallback: `getattr(obj, f'field\_{lang}', None) or obj.field\_en`

14\. Portal ≠ Django `/admin/` — `/admin/` is developer-only

15\. Warn mini-admins before saving edits to approved listing

16\. JS strings → `window.JD\_STRINGS` in template — never in static `.js` files

17\. Django → JS data: `window.JD\_\*` globals in `<script>` block before page JS

18\. Booking DB record created only at Confirm click — not at form submit

19\. Tour bookings always `status='pending\_confirmation'` — permanent

20\. `.jd-load-reveal` for above-fold; `.jd-reveal` for scroll-triggered

21\. JS files: IIFE pattern `(function($){ 'use strict'; ... })(jQuery);`

22\. `templates/account/` (singular) = allauth; `templates/accounts/` (plural) = dashboard

23\. Profile photo: raw `<input type="file" name="profile\_photo">` — never `{{ form.profile\_photo }}`

24\. Never call Python methods with args from Django templates — resolve in view

25\. Never use `display:flex` or `display:grid` in email HTML — use `<table>`

26\. Refund info hidden when `payment\_status != 'paid'` OR `booking.is\_refundable == False`

27\. PDF headers: flat Table only — no nested tables (ReportLab clips nested content)

28\. Rating badges only shown when listing has ≥ 3 approved reviews

29\. Review eligibility: `booking.status == 'completed'` AND `booking.user == request.user`

30\. `get\_display\_price()` is single source of truth for any price shown or snapshotted

31\. `allows\_pay\_on\_arrival=False` enforced server-side — UI suppression alone is not sufficient

32\. `form { display: contents }` inside `.modal-content` — form transparent to flex column

33\. Table horizontal scroll: `overflow-x: auto` on `.portal-table-wrap` + `table-responsive` class

34\. Active nav link: longest-match algorithm in `portal\_base.js` — not set in template blocks

35\. TourPhoto has no `is\_cover` field — no set-cover in tour photo grids

36\. Username regex: `^\[a-z]\[a-z0-9\_]\*\[a-z0-9]$` — starts/ends letter or digit, no leading/trailing underscore

37\. Mini-admin password reset uses `/portal/set-password/<uid>/<token>/` — NOT allauth's URL

38\. `GalleryCategory.slug` auto-generated in model `save()` — not in views

39\. Contact form POST returns JSON — contact.js handles success/error states without page reload

40\. Newsletter subscribe handler lives in `main.js` (`.jd-newsletter-form` class) — never duplicate in page JS



\---



\*End of Handoff — Version 6.0 | May 2026\*

\*Prepared by Fidon for Jadevine Travel \& Tours\*

\*Supersedes versions 1.0, 1.1, 1.2, 2.0, 3.0, 4.0, 4.1, 4.2, 5.0\*

