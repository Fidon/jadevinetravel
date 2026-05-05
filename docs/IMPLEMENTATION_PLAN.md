# JADEVINE TRAVEL \& TOURS — IMPLEMENTATION PLAN

**Version 1.2 | April 2026 | Prepared by Fidon**

\---

## PART 1: PROPOSAL REVISIONS \& SCOPE DECISIONS

The following changes from the original proposal are adopted before development begins.
These are not scope cuts — they are risk mitigations that protect the launch date without
removing any core business value.

### Confirmed Scope Changes

|Original Proposal|Revised Decision|Reason|
|-|-|-|
|6 languages at launch|3 languages: English, French, Russian|Translations are Jadevine's responsibility. Launching with untranslated content is worse than launching in fewer languages. Dutch and Italian added post-launch.|
|Domestic Flights (Amadeus API)|Post-launch|Highest integration risk. Not a day-1 business need.|
|Expedia hotel API|Post-launch|Jadevine has 30–40 local partners. Local inventory is stronger at launch.|
|Pay on Arrival with configurable deposit|Pay on Arrival, no deposit at launch|Simplifies booking flow and payment states. Deposit logic added post-launch.|
|Celery + Redis|Django-Q with Django ORM broker|Simpler on a single VPS with no prior server management experience. Celery can replace it post-launch.|
|TripAdvisor Content API|Embeddable widget only at launch|Free, instant, no API approval needed. Content API applied for after launch.|
|Google OAuth + Facebook OAuth at launch|Post-launch|At launch: email/password registration with email verification for customers. Username/password for admin and mini-admins. OAuth added post-launch.|
|Car rentals: self-drive + driver|Both at launch|Confirmed by client. Booking form handles both modes with conditional fields.|
|Safari dates: slot-managed calendar|Customer picks preferred date, Jadevine confirms manually|Eliminates complex availability calendar. Admin confirms or proposes alternative via portal.|
|Super Admin assigns listings to mini-admins|Mini-admins create their own listings|Mini-admin logs in and creates hotel or car listing. Super Admin reviews and approves before it goes public. Ownership established at creation time.|
|Mini-admin listings go live immediately|Super Admin approval required|All mini-admin listings start as PENDING. Super Admin approves or rejects. Mini-admin can edit a rejected listing and resubmit.|

### What Remains Unchanged

* Django backend, Bootstrap 5 frontend, PostgreSQL (SQLite in dev)
* PesaPal payment gateway (Pay Now + Pay on Arrival, no deposit)
* Role-based admin portal: Super Admin + Mini-Admin (username/password login)
* User dashboard: bookings, cancellations, favourites, profile
* AWS S3 for media (local storage in dev)
* 4 core services at launch: Hotels, Safaris \& Tours, Car Rentals (Flights post-launch)
* SEO, Google Analytics 4, WhatsApp floating button
* 30-day post-launch support window

\---

## PART 2: SYSTEM ARCHITECTURE

### High-Level Architecture

```
Browser / Mobile
      │
      ▼
Nginx (reverse proxy + static files)
      │
      ▼
Gunicorn (WSGI server running Django)
      │
      ├── Django App
      │     ├── Public Website (Bootstrap 5 frontend)
      │     ├── Booking Engine
      │     ├── User Auth (email/password + email verification)
      │     ├── Admin Portal (/portal/) — username/password
      │     └── JSON views for async jQuery calls
      │
      ├── PostgreSQL (production database)
      │
      ├── Django-Q (async task queue)
      │     └── Booking confirmation emails
      │         Cancellation emails
      │         Admin notification emails
      │         Email verification emails
      │         Listing approval/rejection notifications
      │
      └── AWS S3 (media storage in production)
            └── Hotel photos, tour photos, gallery, videos, car photos
```

### Key Architecture Decisions \& Tradeoffs

**Django-Q instead of Celery + Redis**
Celery is the industry standard but requires Redis as a separate process, a Celery worker
process, and monitoring tools like Flower. On a first VPS, that is three things that can
fail independently. Django-Q uses the PostgreSQL database as the broker — one less service
to manage. The tradeoff is lower throughput under heavy load, which is not a concern at
Jadevine's launch-scale traffic.

**SQLite in development, PostgreSQL in production**
SQLite requires zero setup and is fine for development. PostgreSQL is non-negotiable for
production — it handles concurrent bookings correctly in a way SQLite does not. Django's
database abstraction means the switch requires only a settings change.

**Local media storage in development, AWS S3 in production**
Using django-storages with a `DEFAULT\_FILE\_STORAGE` setting means all file upload and
retrieval code is identical in dev and production. The switch is a single settings change.

**No Django REST Framework**
The frontend is server-rendered Django templates with jQuery for dynamic interactions.
Where the frontend needs async data (e.g. filtering listings), Django views return JSON.
This is simpler, faster to build, and easier to secure than a full REST API at this stage.

**Two separate authentication flows**

* Public customers: email/password via django-allauth, email verification required
* Admin/Mini-Admin: username/password via Django's built-in auth, `is\_staff` flag
checked on every portal view

This separation is intentional. It keeps customer auth and staff auth independent,
makes it impossible for a customer account to accidentally gain portal access, and
simplifies the post-launch addition of OAuth for customers without touching admin auth.

**Mini-admin ownership model**
Listings are owned by whoever created them. Mini-admins create their own listings.
Super Admin creates listings for Jadevine's directly-managed properties.
Ownership is a ForeignKey on the listing, not a ManyToMany assignment table.
This is simpler, more intuitive, and easier to enforce server-side.

\---

## PART 3: DATABASE DESIGN

### 3.1 Authentication \& Users

```
CustomUser  (extends AbstractUser)
──────────
id                  AutoField (PK)
email               EmailField (unique) — login identifier for customers
username            CharField (unique) — login identifier for admin/mini-admin only
first\_name          CharField
last\_name           CharField
phone               CharField (nullable)
nationality         CharField (nullable)
preferred\_language  CharField — choices: en, fr, ru
profile\_photo       ImageField (nullable)
is\_active           BooleanField
is\_staff            BooleanField — True for Super Admin and Mini-Admin portal access
date\_joined         DateTimeField
```

**Why CustomUser from the start?**
Django's default User uses username as the primary login identifier. We want customers
to log in with email. Django strongly recommends defining a CustomUser at the very start
of a project — switching later requires deleting all migrations and starting over.
Define it in Phase 0 and never touch the model definition again.

```
MiniAdminProfile
────────────────
id          AutoField (PK)
user        OneToOneField → CustomUser
created\_by  ForeignKey → CustomUser (the Super Admin who created this account)
created\_at  DateTimeField
```

**No ManyToMany assignment fields.**
Listing ownership is established at creation time via a `created\_by` ForeignKey on
each listing model. Mini-admins see only listings where `created\_by = request.user`.
Super Admins see all listings. This is enforced server-side on every portal view —
never only in the template.

\---

### 3.2 Hotels

```
Hotel
─────
id                  AutoField (PK)
name                CharField
slug                SlugField (unique) — used in URLs e.g. /hotels/serena-zanzibar/
location            CharField — choices: ZANZIBAR, DAR\_ES\_SALAAM
description\_en      TextField
description\_fr      TextField (nullable)
description\_ru      TextField (nullable)
stars               IntegerField — choices: 1 to 5
price\_per\_night     DecimalField — stored in USD
address             CharField
latitude            DecimalField (nullable) — for Google Maps embed
longitude           DecimalField (nullable)
tripadvisor\_url     URLField (nullable)

# Ownership and approval
created\_by          ForeignKey → CustomUser (nullable — null means Super Admin
                    created it without a mini-admin context)
approval\_status     CharField — choices: PENDING, APPROVED, REJECTED
rejection\_reason    TextField (nullable) — populated by Super Admin on rejection

# Visibility
is\_active           BooleanField — True only when approval\_status = APPROVED
                    A listing is public ONLY when is\_active=True AND
                    approval\_status=APPROVED. Both conditions must hold.

created\_at          DateTimeField
updated\_at          DateTimeField

HotelPhoto
──────────
id                  AutoField (PK)
hotel               ForeignKey → Hotel
image               ImageField
caption             CharField (nullable)
is\_cover            BooleanField — the main listing card photo
order               PositiveIntegerField — display order

HotelRoomType
─────────────
id                  AutoField (PK)
hotel               ForeignKey → Hotel
name                CharField — e.g. "Standard Double", "Ocean View Suite"
description\_en      TextField
description\_fr      TextField (nullable)
description\_ru      TextField (nullable)
price\_per\_night     DecimalField — overrides hotel base price if set
max\_guests          PositiveIntegerField
amenities           JSONField — list of strings e.g. \["WiFi", "AC", "Pool view"]
is\_available        BooleanField
```

**Why explicit `\_en`, `\_fr`, `\_ru` fields instead of a translation table?**
A separate translation table (used by packages like django-parler) is more normalized
but significantly more complex to query and manage from the admin portal. For 3 languages
with a non-technical client managing content, explicit language-suffixed fields are
simpler, clearer, and less error-prone. The tradeoff is some schema repetition, which
is acceptable at this scale.

**Approval status and is\_active relationship:**

* Mini-admin creates listing → `approval\_status=PENDING`, `is\_active=False`
* Super Admin approves → `approval\_status=APPROVED`, `is\_active=True`
* Super Admin rejects → `approval\_status=REJECTED`, `is\_active=False`,
`rejection\_reason` populated
* Mini-admin edits rejected listing and resubmits → `approval\_status=PENDING`,
`is\_active=False`, `rejection\_reason` cleared
* Super Admin creates listing directly → `approval\_status=APPROVED`, `is\_active=True`
(Super Admin listings skip the approval queue)

\---

### 3.3 Safaris \& Tours

Tours are created and managed exclusively by the Super Admin. Mini-admins do not manage
tour packages — those represent Jadevine's own safari and tour operations, not third-party
partner listings. Therefore, TourPackage has no `created\_by` or `approval\_status` fields.

```
TourPackage
───────────
id                  AutoField (PK)
name\_en             CharField
name\_fr             CharField (nullable)
name\_ru             CharField (nullable)
slug                SlugField (unique)
tour\_type           CharField — choices: SAFARI, BEACH, CULTURAL, CLIMBING, COMBINED
description\_en      TextField
description\_fr      TextField (nullable)
description\_ru      TextField (nullable)
duration\_days       PositiveIntegerField
group\_size\_max      PositiveIntegerField
price\_per\_person    DecimalField — in USD
highlights\_en       JSONField — list of highlight strings
highlights\_fr       JSONField (nullable)
highlights\_ru       JSONField (nullable)
inclusions\_en       JSONField
inclusions\_fr       JSONField (nullable)
inclusions\_ru       JSONField (nullable)
exclusions\_en       JSONField
exclusions\_fr       JSONField (nullable)
exclusions\_ru       JSONField (nullable)
what\_to\_bring\_en    TextField (nullable)
what\_to\_bring\_fr    TextField (nullable)
what\_to\_bring\_ru    TextField (nullable)
cover\_image         ImageField
is\_active           BooleanField
is\_featured         BooleanField — shown in Featured Packages on homepage
created\_at          DateTimeField
updated\_at          DateTimeField

TourItineraryDay
────────────────
id                  AutoField (PK)
package             ForeignKey → TourPackage
day\_number          PositiveIntegerField — 1, 2, 3...
title\_en            CharField
title\_fr            CharField (nullable)
title\_ru            CharField (nullable)
description\_en      TextField
description\_fr      TextField (nullable)
description\_ru      TextField (nullable)

TourPhoto
─────────
id                  AutoField (PK)
package             ForeignKey → TourPackage
image               ImageField
caption             CharField (nullable)
order               PositiveIntegerField
```

\---

### 3.4 Car Rentals

```
CarRental
─────────
id                  AutoField (PK)
name                CharField — e.g. "Toyota Land Cruiser 4x4"
slug                SlugField (unique)
vehicle\_type        CharField — choices: SEDAN, SUV, MINIBUS, FOURX4, VAN
make                CharField
model               CharField
year                PositiveIntegerField
capacity            PositiveIntegerField — number of passengers
fuel\_type           CharField — choices: PETROL, DIESEL
transmission        CharField — choices: MANUAL, AUTOMATIC
price\_per\_day       DecimalField — in USD
offers\_self\_drive   BooleanField
offers\_driver       BooleanField
driver\_speaks\_en    BooleanField
driver\_speaks\_fr    BooleanField
pickup\_locations    JSONField — list of location name strings
description\_en      TextField (nullable)
description\_fr      TextField (nullable)
description\_ru      TextField (nullable)

# Ownership and approval — same pattern as Hotel
created\_by          ForeignKey → CustomUser (nullable)
approval\_status     CharField — choices: PENDING, APPROVED, REJECTED
rejection\_reason    TextField (nullable)

# Visibility
is\_available        BooleanField — can be toggled by mini-admin (e.g. maintenance)
is\_active           BooleanField — True only when approval\_status = APPROVED

created\_at          DateTimeField
updated\_at          DateTimeField

CarPhoto
────────
id                  AutoField (PK)
car                 ForeignKey → CarRental
image               ImageField
is\_cover            BooleanField
order               PositiveIntegerField
```

\---

### 3.5 Bookings

All three service types share a single `Booking` model with a `service\_type`
discriminator field. This is called a polymorphic booking pattern.

**Why one Booking model instead of separate HotelBooking, TourBooking, CarBooking?**
A single Booking model means one place to query all bookings, one admin view, one
payment flow, one cancellation flow, and one email notification system. The tradeoff
is some nullable fields per service type. At this scale, the simplicity wins decisively.

```
Booking
───────
id                      AutoField (PK)
reference               CharField (unique) — e.g. "JDV-2026-00142", auto-generated
user                    ForeignKey → CustomUser
service\_type            CharField — choices: HOTEL, TOUR, CAR

# Service links — only one will be populated per booking
hotel                   ForeignKey → Hotel (nullable)
room\_type               ForeignKey → HotelRoomType (nullable)
tour\_package            ForeignKey → TourPackage (nullable)
car                     ForeignKey → CarRental (nullable)

# Dates
check\_in\_date           DateField (nullable) — hotels
check\_out\_date          DateField (nullable) — hotels
preferred\_date          DateField (nullable) — tours (customer's preferred start date)
pickup\_date             DateField (nullable) — cars
return\_date             DateField (nullable) — cars

# Guests / participants
num\_guests              PositiveIntegerField (nullable) — hotels
num\_participants        PositiveIntegerField (nullable) — tours
num\_days                PositiveIntegerField (nullable) — cars, computed from dates

# Car-specific fields
pickup\_location         CharField (nullable)
rental\_mode             CharField (nullable) — choices: SELF\_DRIVE, WITH\_DRIVER
driver\_licence\_number   CharField (nullable) — required for self-drive
driver\_name             CharField (nullable) — customer's preferred driver name

# Pricing — snapshotted at booking time, never recalculated
base\_price              DecimalField
total\_price             DecimalField
currency                CharField — choices: USD, TZS, EUR

# Payment
payment\_mode            CharField — choices: PAY\_NOW, PAY\_ON\_ARRIVAL
payment\_status          CharField — choices: PENDING, PAID, REFUNDED, FAILED
pesapal\_order\_id        CharField (nullable)
pesapal\_tracking\_id     CharField (nullable)

# Booking lifecycle
status                  CharField — choices: PENDING\_CONFIRMATION, CONFIRMED,
                                    CANCELLED, COMPLETED, NO\_SHOW
# PENDING\_CONFIRMATION: awaiting Jadevine to confirm tour date, or awaiting payment
# CONFIRMED: payment received (hotels/cars) or date confirmed by admin (tours)
# CANCELLED: cancelled by customer or admin
# COMPLETED: service delivered
# NO\_SHOW: Pay on Arrival customer did not arrive

special\_requests        TextField (nullable)
cancellation\_reason     TextField (nullable)
cancelled\_at            DateTimeField (nullable)
cancelled\_by            ForeignKey → CustomUser (nullable)

created\_at              DateTimeField
updated\_at              DateTimeField

CancellationPolicy
──────────────────
id                      AutoField (PK)
service\_type            CharField — choices: HOTEL, TOUR, CAR
days\_before\_service     PositiveIntegerField — e.g. 14, 7, 0
refund\_percentage       PositiveIntegerField — e.g. 100, 50, 0
label\_en                CharField — e.g. "Full refund (14+ days before service)"
is\_active               BooleanField
```

**Default cancellation tiers to seed at setup:**

|Service|Days Before|Refund|
|-|-|-|
|HOTEL|14+ days|100%|
|HOTEL|7–13 days|50%|
|HOTEL|0–6 days|0%|
|TOUR|14+ days|100%|
|TOUR|7–13 days|50%|
|TOUR|0–6 days|0%|
|CAR|14+ days|100%|
|CAR|7–13 days|50%|
|CAR|0–6 days|0%|

These are configurable by Super Admin from the portal. They are not hardcoded.

\---

### 3.6 Gallery

```
GalleryCategory
───────────────
id          AutoField (PK)
name\_en     CharField — e.g. "Safaris", "Beaches", "Wildlife"
name\_fr     CharField (nullable)
name\_ru     CharField (nullable)
slug        SlugField
order       PositiveIntegerField

GalleryItem
───────────
id              AutoField (PK)
category        ForeignKey → GalleryCategory
media\_type      CharField — choices: PHOTO, VIDEO
image           ImageField (nullable) — for photos
video\_url       URLField (nullable) — YouTube or Vimeo embed URL
video\_file      FileField (nullable) — direct video upload
caption\_en      CharField (nullable)
caption\_fr      CharField (nullable)
caption\_ru      CharField (nullable)
is\_featured     BooleanField — shown in homepage Gallery Highlights section
order           PositiveIntegerField
created\_at      DateTimeField
```

\---

### 3.7 Supporting Models

```
ContactMessage
──────────────
id              AutoField (PK)
name            CharField
email           EmailField
phone           CharField (nullable)
subject         CharField
message         TextField
inquiry\_type    CharField — choices: GENERAL, CUSTOM\_TOUR, PARTNERSHIP, PRESS
preferred\_lang  CharField — choices: en, fr, ru
status          CharField — choices: NEW, IN\_PROGRESS, RESOLVED
admin\_notes     TextField (nullable) — internal notes, never shown to customer
created\_at      DateTimeField

NewsletterSubscriber
────────────────────
id              AutoField (PK)
email           EmailField (unique)
is\_active       BooleanField
subscribed\_at   DateTimeField

SavedFavourite
──────────────
id              AutoField (PK)
user            ForeignKey → CustomUser
hotel           ForeignKey → Hotel (nullable)
tour\_package    ForeignKey → TourPackage (nullable)
car             ForeignKey → CarRental (nullable)
saved\_at        DateTimeField

class Meta:
    # Prevents duplicate favourites per user per item
    constraints = \[
        UniqueConstraint(fields=\['user', 'hotel'],
                         condition=Q(hotel\_\_isnull=False), ...),
        UniqueConstraint(fields=\['user', 'tour\_package'],
                         condition=Q(tour\_package\_\_isnull=False), ...),
        UniqueConstraint(fields=\['user', 'car'],
                         condition=Q(car\_\_isnull=False), ...),
    ]
```

\---

## PART 4: PROJECT STRUCTURE

```
jadevine/
├── config/
│   ├── \_\_init\_\_.py
│   ├── settings/
│   │   ├── base.py               ← Shared settings for all environments
│   │   ├── development.py        ← SQLite, local media, DEBUG=True
│   │   └── production.py         ← PostgreSQL, AWS S3, DEBUG=False
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/                 ← CustomUser, registration, login, user dashboard
│   ├── hotels/                   ← Hotel, HotelPhoto, HotelRoomType
│   ├── tours/                    ← TourPackage, TourItineraryDay, TourPhoto
│   ├── cars/                     ← CarRental, CarPhoto
│   ├── bookings/                 ← Booking, CancellationPolicy, payment flow
│   ├── gallery/                  ← GalleryItem, GalleryCategory
│   ├── contact/                  ← ContactMessage, NewsletterSubscriber
│   ├── portal/                   ← Admin portal: Super Admin + Mini-Admin views
│   └── core/                     ← Homepage, SavedFavourite, shared utilities
│
├── templates/
│   ├── base.html                 ← Master layout: navbar, footer, lang switcher,
│   │                                WhatsApp button
│   ├── core/
│   │   ├── home.html
│   │   └── about.html
│   ├── accounts/
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── booking\_history.html
│   │   ├── booking\_detail.html
│   │   ├── profile.html
│   │   └── favourites.html
│   ├── hotels/
│   │   ├── hotel\_list.html
│   │   └── hotel\_detail.html
│   ├── tours/
│   │   ├── tour\_list.html
│   │   └── tour\_detail.html
│   ├── cars/
│   │   ├── car\_list.html
│   │   └── car\_detail.html
│   ├── bookings/
│   │   ├── booking\_summary.html
│   │   ├── payment\_options.html
│   │   └── booking\_confirmation.html
│   ├── gallery/
│   │   └── gallery.html
│   ├── contact/
│   │   └── contact.html
│   └── portal/
│       ├── portal\_base.html      ← Portal master layout, separate from public base.html
│       ├── portal\_login.html
│       ├── portal\_dashboard.html
│       ├── portal\_hotels.html
│       ├── portal\_hotel\_form.html
│       ├── portal\_hotel\_detail.html
│       ├── portal\_hotel\_approval.html
│       ├── portal\_tours.html
│       ├── portal\_tour\_form.html
│       ├── portal\_cars.html
│       ├── portal\_car\_form.html
│       ├── portal\_car\_detail.html
│       ├── portal\_car\_approval.html
│       ├── portal\_bookings.html
│       ├── portal\_booking\_detail.html
│       ├── portal\_gallery.html
│       ├── portal\_users.html
│       ├── portal\_miniadmins.html
│       ├── portal\_miniadmin\_form.html
│       ├── portal\_messages.html
│       ├── portal\_message\_detail.html
│       ├── portal\_newsletter.html
│       ├── portal\_policies.html
│       └── portal\_settings.html
│
├── static/
│   ├── css/
│   │   └── main.css              ← Global styles and CSS variables (colour palette)
│   ├── js/
│   │   └── main.js               ← Global jQuery (navbar, WhatsApp btn, lang switcher)
│   └── images/
│       └── logo.png
│
├── static\_pages/
│   ├── css/
│   │   ├── home.css
│   │   ├── hotel\_list.css
│   │   ├── hotel\_detail.css
│   │   ├── tour\_list.css
│   │   ├── tour\_detail.css
│   │   ├── car\_list.css
│   │   ├── car\_detail.css
│   │   ├── booking\_summary.css
│   │   ├── payment\_options.css
│   │   ├── booking\_confirmation.css
│   │   ├── gallery.css
│   │   ├── contact.css
│   │   ├── about.css
│   │   ├── accounts.css          ← Shared: login, signup, dashboard pages
│   │   └── portal.css            ← Shared: all portal pages
│   └── js/
│       ├── home.js
│       ├── hotel\_list.js
│       ├── hotel\_detail.js
│       ├── tour\_list.js
│       ├── tour\_detail.js
│       ├── car\_list.js
│       ├── car\_detail.js
│       ├── booking\_summary.js
│       ├── payment\_options.js
│       ├── booking\_confirmation.js
│       ├── gallery.js
│       ├── contact.js
│       ├── signup.js
│       ├── login.js
│       ├── dashboard.js
│       ├── profile.js
│       ├── favourites.js
│       ├── portal\_dashboard.js
│       ├── portal\_hotels.js
│       ├── portal\_hotel\_form.js
│       ├── portal\_tours.js
│       ├── portal\_tour\_form.js
│       ├── portal\_cars.js
│       ├── portal\_car\_form.js
│       ├── portal\_bookings.js
│       ├── portal\_gallery.js
│       ├── portal\_users.js
│       ├── portal\_miniadmins.js
│       ├── portal\_messages.js
│       └── portal\_newsletter.js
│
├── locale/
│   ├── en/LC\_MESSAGES/django.po
│   ├── fr/LC\_MESSAGES/django.po
│   └── ru/LC\_MESSAGES/django.po
│
├── media/                        ← Local dev uploads only — gitignored
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── .env                          ← All secrets — gitignored
├── .env.example                  ← Template showing all required env var names
├── manage.py
└── README.md
```

\---

## PART 5: URL STRUCTURE

```python
# Public site — language-prefixed via i18n\_patterns
/                               → Homepage
/hotels/                        → Hotel listing
/hotels/<slug>/                 → Hotel detail
/tours/                         → Tour listing
/tours/<slug>/                  → Tour detail
/cars/                          → Car listing
/cars/<slug>/                   → Car detail
/gallery/                       → Gallery
/about/                         → About Us
/contact/                       → Contact Us

# Booking flow — login required
/book/<service\_type>/<slug>/    → Booking form + summary
/book/payment/<booking\_ref>/    → Payment options (Pay Now vs Pay on Arrival)
/book/confirm/<booking\_ref>/    → Booking confirmation page
/book/pesapal/callback/         → PesaPal IPN webhook — NOT language-prefixed

# User accounts
/accounts/register/             → Registration form
/accounts/login/                → Email + password login
/accounts/logout/
/accounts/verify-email/<key>/   → Email verification link
/accounts/dashboard/
/accounts/bookings/
/accounts/bookings/<reference>/
/accounts/bookings/<reference>/cancel/
/accounts/profile/
/accounts/favourites/
/accounts/password/change/
/accounts/password/reset/

# Language-prefixed examples
/fr/hotels/                     → French hotel listing
/ru/tours/                      → Russian tour listing
# English has no prefix (default language)

# Admin portal — NOT language-prefixed, completely separate from /admin/
/portal/                        → Portal dashboard
/portal/login/                  → Username + password login
/portal/logout/

# Listings — Super Admin full access, Mini-Admin own listings only
/portal/hotels/
/portal/hotels/add/
/portal/hotels/<id>/
/portal/hotels/<id>/edit/
/portal/hotels/<id>/delete/
/portal/hotels/<id>/approve/    → Super Admin only
/portal/hotels/<id>/reject/     → Super Admin only
/portal/hotels/pending/         → Super Admin only — pending approval queue

/portal/cars/
/portal/cars/add/
/portal/cars/<id>/
/portal/cars/<id>/edit/
/portal/cars/<id>/delete/
/portal/cars/<id>/approve/      → Super Admin only
/portal/cars/<id>/reject/       → Super Admin only
/portal/cars/pending/           → Super Admin only — pending approval queue

/portal/tours/                  → Super Admin only
/portal/tours/add/              → Super Admin only
/portal/tours/<id>/edit/        → Super Admin only

/portal/bookings/
/portal/bookings/<id>/

/portal/gallery/                → Super Admin only
/portal/users/                  → Super Admin only
/portal/users/<id>/
/portal/mini-admins/            → Super Admin only
/portal/mini-admins/add/        → Super Admin only
/portal/mini-admins/<id>/edit/  → Super Admin only
/portal/messages/               → Super Admin only
/portal/messages/<id>/
/portal/newsletter/             → Super Admin only
/portal/policies/               → Super Admin only
/portal/settings/

# Django built-in admin — developer use only, restricted in production
/admin/
```

\---

## PART 6: PAYMENT FLOW (PESAPAL)

### Pay Now Flow

```
Step 1 — Customer submits booking form
  → Booking saved: status=PENDING\_CONFIRMATION, payment\_status=PENDING,
    payment\_mode=PAY\_NOW
  → Customer redirected to /book/payment/<ref>/

Step 2 — Payment options page
  → Django calls PesaPal API: submit\_order\_request
  → PesaPal returns a redirect URL
  → Customer redirected to PesaPal hosted payment page

Step 3 — Customer completes payment on PesaPal
  → Visa / Mastercard / M-Pesa / Airtel Money / etc.

Step 4 — PesaPal sends IPN to /book/pesapal/callback/
  → Django receives the notification
  → Django calls PesaPal API: get\_transaction\_status (independent verification)
  → If payment confirmed:
      booking.payment\_status = PAID
      booking.status = CONFIRMED        (hotels and cars)
      booking.status = PENDING\_CONFIRMATION  (tours — Jadevine must confirm date)
  → If payment failed:
      booking.payment\_status = FAILED
  → Django-Q queues: confirmation email to customer
  → Django-Q queues: new booking notification to Jadevine admin

Step 5 — Customer lands on /book/confirm/<ref>/
  → Shows booking reference, status, and next steps
  → For tours: message explains Jadevine will confirm the date within 24–48 hours
```

### Pay on Arrival Flow

```
Step 1 — Customer submits booking form, selects Pay on Arrival
  → Booking saved: status=PENDING\_CONFIRMATION, payment\_status=PENDING,
    payment\_mode=PAY\_ON\_ARRIVAL
  → No PesaPal redirect

Step 2 — Customer goes directly to /book/confirm/<ref>/
  → Shows booking reference and pay-on-arrival instructions
  → Django-Q queues: confirmation email (with arrival payment instructions)
  → Django-Q queues: notification to Jadevine admin

Step 3 — Admin action in portal
  → Admin reviews and confirms the booking: status=CONFIRMED
  → When customer pays on arrival: admin marks payment\_status=PAID
  → System flags no-shows if service date passes with no payment recorded
```

**Development note on PesaPal IPN:**
PesaPal's callback must be reachable from the public internet during development.
Use ngrok (`ngrok http 8000`) to expose your local server.
Configure the ngrok URL as the IPN callback URL in PesaPal sandbox settings.
This is a required step — do not skip it when testing payments.

\---

## PART 7: LISTING APPROVAL WORKFLOW

This workflow applies to hotels and car rentals created by mini-admins.
Tours are Super Admin only and skip this workflow entirely.
Super Admin listings also skip this workflow — they are approved on creation.

```
Step 1 — Super Admin creates mini-admin account
  → Sets username, email, temporary password
  → Django-Q sends welcome email with login credentials and portal URL
  → MiniAdminProfile record created, linked to the new CustomUser

Step 2 — Mini-admin logs in and creates a listing
  → Fills in all hotel or car details, uploads photos
  → On save:
      created\_by = request.user
      approval\_status = PENDING
      is\_active = False
  → Listing is NOT visible on the public site
  → Django-Q notifies Super Admin: new listing pending review

Step 3 — Super Admin reviews the listing
  → Pending listings appear in the portal dashboard as a count badge
    and in a dedicated "Pending Approvals" queue
  → Super Admin can view full listing detail before deciding
  → Super Admin can edit the listing before approving if minor corrections needed

Step 4a — Super Admin approves
  → approval\_status = APPROVED
  → is\_active = True
  → Listing appears on the public site immediately
  → Django-Q notifies mini-admin: listing approved and live

Step 4b — Super Admin rejects
  → approval\_status = REJECTED
  → is\_active = False (remains hidden)
  → rejection\_reason saved (required — Super Admin must provide a reason)
  → Django-Q notifies mini-admin: listing rejected with reason

Step 5 — Mini-admin edits and resubmits (after rejection)
  → Mini-admin sees rejection reason on their listing in the portal
  → Mini-admin edits the listing and clicks Resubmit for Approval
  → approval\_status = PENDING
  → rejection\_reason = cleared
  → Django-Q notifies Super Admin: listing resubmitted, pending review again
  → Flow returns to Step 3
```

**Access control rules for the approval flow:**

* Only Super Admin can access `/portal/hotels/pending/`,
`/portal/hotels/<id>/approve/`, and `/portal/hotels/<id>/reject/`
* Mini-admin attempting to access these URLs receives a 403 Forbidden response
* Mini-admin can see their own listing's approval status in their portal view
* Mini-admin can edit a PENDING or REJECTED listing, but not an APPROVED one
(edits to an approved listing reset it to PENDING and remove it from the
public site until re-approved — this prevents mini-admins from publishing
unapproved changes to a live listing)

\---

## PART 8: COLOUR PALETTE \& DESIGN SYSTEM

All colours defined as CSS variables in `static/css/main.css`.
Every template and page file references these variables — never hardcode hex values.

```css
:root {
  /\* Primary brand colours \*/
  --color-primary:        #1a4d2e;   /\* Deep forest green — main brand colour \*/
  --color-primary-dark:   #122f1c;   /\* Darker green — hover states, headings \*/
  --color-primary-light:  #2a6b40;   /\* Lighter green — secondary buttons, accents \*/

  /\* Gold / warm accent \*/
  --color-accent:         #c89666;   /\* Warm gold — CTAs, highlights, borders \*/
  --color-accent-dark:    #a67a50;   /\* Darker gold — hover on accent elements \*/
  --color-accent-light:   #e0b88a;   /\* Light gold — backgrounds, badges \*/

  /\* Neutrals \*/
  --color-white:          #ffffff;
  --color-off-white:      #f8f5f0;   /\* Warm off-white — page backgrounds \*/
  --color-light:          #f0ebe3;   /\* Warm light — card backgrounds, section fills \*/
  --color-border:         #e0d5c8;   /\* Warm border — card borders, dividers \*/
  --color-muted:          #9e8e7e;   /\* Muted brown-grey — secondary text, captions \*/
  --color-text:           #2c2c2c;   /\* Near-black — primary body text \*/
  --color-text-light:     #5a5a5a;   /\* Medium grey — subtext, meta info \*/

  /\* Dark / overlay \*/
  --color-dark:           #1a1a1a;   /\* Deep dark — footer background \*/
  --color-overlay:        rgba(26, 77, 46, 0.55);  /\* Green overlay on hero images \*/
  --color-overlay-dark:   rgba(0, 0, 0, 0.45);     /\* Dark overlay for card hover \*/

  /\* Status colours \*/
  --color-success:        #2d7a4f;   /\* Confirmed bookings, success messages \*/
  --color-warning:        #c89666;   /\* Pending states — reuses accent gold \*/
  --color-danger:         #c0392b;   /\* Cancellations, errors, rejections \*/
  --color-info:           #2980b9;   /\* Information notices \*/

  /\* Typography \*/
  --font-heading:         'Playfair Display', Georgia, serif;
  --font-body:            'Inter', 'Segoe UI', sans-serif;

  /\* Spacing \*/
  --section-padding:      80px 0;
  --card-radius:          12px;
  --btn-radius:           6px;

  /\* Shadows \*/
  --shadow-card:          0 4px 20px rgba(0, 0, 0, 0.08);
  --shadow-card-hover:    0 8px 32px rgba(0, 0, 0, 0.14);
  --shadow-dropdown:      0 4px 16px rgba(0, 0, 0, 0.12);
}
```

**Google Fonts to load in base.html:**

```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700
\&family=Inter:wght@300;400;500;600\&display=swap" rel="stylesheet">
```

\---

## PART 9: MULTILINGUAL IMPLEMENTATION

### How Django i18n Works

In every template, instead of `<h1>Welcome</h1>` write `<h1>{% trans "Welcome" %}</h1>`.
In Python code, instead of `label = "Book Now"` write `label = \_("Book Now")`.

Django's `makemessages` command scans all templates and Python files, collects every
string wrapped in `{% trans %}` or `\_()`, and writes them into `.po` files in `locale/`.
A translator fills in French and Russian. Then `compilemessages` compiles them to `.mo`
binary files that Django reads at runtime.

### What Gettext Covers vs. What Field Suffixes Cover

**Gettext (.po files):** All UI strings — button labels, navigation items, form labels,
error messages, page headings, email subjects, status messages, system notifications.

**Database field suffixes (\_en, \_fr, \_ru):** All content entered by Jadevine staff —
hotel descriptions, tour names, itinerary text, car descriptions, gallery captions.
The view selects the correct field based on `request.LANGUAGE\_CODE`.

### Language Field Selection Pattern

Use this pattern consistently in every view that renders multilingual model content:

```python
lang = request.LANGUAGE\_CODE  # 'en', 'fr', or 'ru'
description = getattr(hotel, f'description\_{lang}') or hotel.description\_en
```

Always fall back to English if the translated field is empty. Never let a page
render a blank description because a translation has not been provided yet.

### Translation Workflow Per Phase

1. Wrap all strings in `{% trans %}` / `\_()` as you write each template
2. After each phase: `python manage.py makemessages -l fr -l ru`
3. Share `.po` files with Jadevine for translation
4. On receipt: update `.po` files, run `python manage.py compilemessages`, test
5. Test all 3 language versions of all completed pages before moving on

**Do not defer translation wrapping to Phase 8.**
Wrapping strings retroactively across 50+ templates is error-prone and slow.
Wrap every string as you write each template throughout every phase.

\---

## PART 10: PHASED IMPLEMENTATION PLAN

### Timeline Summary

|Phase|Name|Duration|Cumulative Week|
|-|-|-|-|
|0|Environment \& Project Setup|3–4 days|Week 1|
|1|Foundation: Models, Base Templates, Static Pages|1.5–2 weeks|Week 3|
|2|Hotels \& Cars: Listings + Booking Flow|2–2.5 weeks|Week 5–6|
|3|Safaris \& Tours: Listings + Booking Flow|1.5 weeks|Week 7–8|
|4|User Accounts \& Dashboard|1.5 weeks|Week 9–10|
|5|Admin Portal|2 weeks|Week 11–12|
|6|PesaPal Payment Integration|1 week|Week 13|
|7|Gallery, Contact \& Newsletter|1 week|Week 14|
|8|i18n Completion, SEO \& QA|1–1.5 weeks|Week 15|
|9|Deployment \& Launch|3–4 days|Week 15–16|

**Total: 14–16 weeks solo.**

\---

### PHASE 0 — Environment \& Project Setup (3–4 days)

**Goal:** A working, version-controlled Django project with the correct structure,
settings split, all dependencies installed, and CustomUser defined and migrated.

**Why this phase exists separately:**
Several decisions cannot be changed later without severe pain. CustomUser must be defined
before any other model. The settings split must exist before any configuration is written.
Getting these right on day one saves days of remediation later.

**Deliverables:**

* GitHub repository created with `.gitignore`:
Exclude `.env`, `media/`, `\_\_pycache\_\_/`, `\*.pyc`, `db.sqlite3`, `staticfiles/`
* Django project created using the `config/` and `apps/` structure defined in Part 4
* `CustomUser` model defined in `apps/accounts/models.py`, migrated,
set as `AUTH\_USER\_MODEL = 'accounts.CustomUser'` in `base.py`
* Settings split working: `base.py`, `development.py`, `production.py`
* `DJANGO\_SETTINGS\_MODULE` managed via `.env`
* All base dependencies installed and pinned in `requirements/base.txt`
* `django-allauth` installed, configured for email-only auth (no social providers yet)
* `django-q2` installed and configured with Django ORM as broker
* `django-storages` + `boto3` installed (local storage active in dev settings)
* `Pillow` installed for ImageField support
* `python-dotenv` installed and loading `.env` on startup
* WhiteNoise installed for static file serving in production
* `.env.example` created listing all required variable names with placeholder values
* `base.html` created: Bootstrap 5 CDN, Google Fonts, CSS variables loaded,
navbar placeholder, footer placeholder
* `main.css` created with the full colour palette as CSS variables (see Part 8)
* `main.js` created as the global jQuery file
* Development server confirmed running: `python manage.py runserver`
* Django built-in `/admin/` confirmed accessible with a superuser account

**requirements/base.txt:**

```
Django>=4.2,<5.0
django-allauth
django-q2
django-storages
boto3
Pillow
psycopg2-binary
python-dotenv
gunicorn
whitenoise
requests
reportlab
```

**Critical warning — CustomUser:**
Create the `accounts` app first.
Define `CustomUser` extending `AbstractUser`.
Set `AUTH\_USER\_MODEL = 'accounts.CustomUser'` in `base.py`.
Run the initial migration.
Only then create any other app or model.
If any other app is migrated before this step, you must delete all migrations
across the entire project and start over. There is no patch for this.

\---

### PHASE 1 — Foundation: Models, Base Templates \& Static Pages (1.5–2 weeks)

**Goal:** All database models defined and migrated. Base templates complete.
Homepage, About, and Contact pages are live.

**Backend deliverables:**

* All models defined across all apps and migrated:
Hotel, HotelPhoto, HotelRoomType, TourPackage, TourItineraryDay, TourPhoto,
CarRental, CarPhoto, Booking, CancellationPolicy, GalleryCategory, GalleryItem,
ContactMessage, NewsletterSubscriber, SavedFavourite, MiniAdminProfile
* `approval\_status` and `created\_by` fields confirmed on Hotel and CarRental
* Auto-slug generation on save for Hotel, TourPackage, CarRental
* Booking reference auto-generation on save: format `JDV-YYYY-NNNNN`
* Default CancellationPolicy rows seeded via a Django data migration
* All models registered in Django's built-in `/admin/` for developer use
* Django-Q worker confirmed running: `python manage.py qcluster`

**Frontend deliverables:**

* `base.html` complete:

  * Navbar: logo, main navigation links, language switcher (EN / FR / RU),
user account dropdown (login / register if anonymous,
dashboard / logout if authenticated)
  * Mobile hamburger menu — responsive at all Bootstrap breakpoints
  * WhatsApp floating button — bottom-right, links to Jadevine WhatsApp Business
  * Footer: logo, description, service links, social links, contact info, copyright
  * Google Fonts and CSS variables applied throughout
* Homepage (`home.html`, `home.js`, `home.css`):

  * Full-width hero: high-quality photo with `--color-overlay`, tagline,
booking search widget with tabs (Hotels / Tours / Cars)
  * Our Services section: four service cards (Flights card shows "Coming Soon")
  * Featured Packages: pulls `TourPackage` where `is\_featured=True`
  * Why Choose Us section
  * TripAdvisor embeddable widget
  * Gallery Highlights: pulls `GalleryItem` where `is\_featured=True` (6–9 items)
  * Newsletter form — jQuery AJAX submit, inline success/error message
  * All strings wrapped in `{% trans %}`
* About Us page (`about.html`, `about.js`, `about.css`):

  * Company story, mission, vision
  * Team section (placeholder until Jadevine provides content)
  * Certifications and partnerships
  * Google Maps embed for office location
* Contact Us page (`contact.html`, `contact.js`, `contact.css`):

  * Contact form with jQuery validation (UX) + Django form validation (authoritative)
  * Inquiry type selector: General / Custom Tour / Partnership / Press
  * Direct phone and WhatsApp links (click-to-call on mobile)
  * Google Maps embed
  * On submit: saves ContactMessage to DB, Django-Q sends acknowledgment to customer
and notification to admin
* Custom 404 and 500 error pages styled to match the brand
* i18n skeleton:

  * `i18n\_patterns()` configured in `config/urls.py`
  * `LocaleMiddleware` in `MIDDLEWARE` in `base.py`
  * Language switcher in navbar functional
  * All strings in base templates and Phase 1 pages wrapped in `{% trans %}`
  * `.po` files generated for fr and ru (empty translations acceptable at this stage)

**Content Jadevine must provide by end of Phase 1:**

* Hero photograph (high resolution)
* Company tagline in English, French, Russian
* WhatsApp Business number
* Office address and coordinates
* Social media URLs
* Team member names, titles, and photos

\---

### PHASE 2 — Hotels \& Cars: Listings + Booking Flow (2–2.5 weeks)

**Goal:** A tourist can find a hotel or car, view its detail page, and complete
a booking through to the confirmation page. Payment is stubbed (completed in Phase 6).

**Hotels — backend:**

* `HotelListView`: queryset filtered by GET parameters using Django ORM.
Public queryset always filters: `is\_active=True` AND `approval\_status=APPROVED`.
An AJAX endpoint returns filtered results as JSON for jQuery to update the grid.
* `HotelDetailView`: retrieves hotel, photos, room types. Serves correct language
field based on `request.LANGUAGE\_CODE` with English fallback.
* `HotelBookingView`: validates booking form, creates Booking with
`payment\_status=PENDING`, redirects to booking summary. Requires login.
* `BookingSummaryView`: full booking review before payment
* `PaymentOptionsView`: Pay Now / Pay on Arrival choice
(PesaPal call stubbed — completed in Phase 6)
* `BookingConfirmationView`: confirmation page

**Hotels — frontend:**

* `hotel\_list.html` + `hotel\_list.js` + `hotel\_list.css`:

  * Search bar and filters (location, dates, guests, stars, price range)
  * jQuery sends AJAX request on filter change, updates listing grid
  * Loading spinner during AJAX request
  * Hotel cards: cover photo, name, stars, location, price per night, Book Now
* `hotel\_detail.html` + `hotel\_detail.js` + `hotel\_detail.css`:

  * Photo gallery with GLightbox lightbox
  * Room type selector with jQuery price update on selection
  * Amenities list, Google Maps embed, TripAdvisor link
  * Booking form: flatpickr date pickers, guest count, room type, special requests
  * Login redirect if unauthenticated on form submit

**Cars — backend:**

* `CarListView`: filtered by vehicle type, self-drive flag, pickup location.
Public queryset always filters: `is\_active=True`, `is\_available=True`,
`approval\_status=APPROVED`.
* `CarDetailView`: retrieves car and photos
* `CarBookingView`:

  * Conditional validation: `driver\_licence\_number` required if `SELF\_DRIVE`
  * Computes `num\_days` from pickup and return dates
  * Creates Booking, redirects to summary

**Cars — frontend:**

* `car\_list.html` + `car\_list.js` + `car\_list.css`:

  * Filter tabs: vehicle type, self-drive toggle, pickup location
  * Car cards: cover photo, make/model, capacity, transmission, price per day
* `car\_detail.html` + `car\_detail.js` + `car\_detail.css`:

  * Photo gallery with lightbox
  * Rental mode selector: Self Drive / With Driver
  * jQuery shows and hides conditional fields based on rental mode:
Self Drive → show licence number field
With Driver → show driver language preference field
  * Flatpickr date range picker

**Shared booking pages:**

* `booking\_summary.html` + `booking\_summary.js`:

  * Full review: service, dates, pricing breakdown, total
  * Edit button returns to detail page
  * Proceed to Payment (stubbed in this phase)
* `booking\_confirmation.html` + `booking\_confirm.js`:

  * Booking reference, status badge, next steps
  * Different message for PAY\_NOW vs PAY\_ON\_ARRIVAL
  * Link to user dashboard

**Seed data for testing (via Django built-in admin):**

* 3–5 sample hotels with photos, room types, amenities
Set `approval\_status=APPROVED`, `is\_active=True` manually for test records
* 3–5 sample cars with photos and pickup locations
Same approval override for test records

\---

### PHASE 3 — Safaris \& Tours: Listings + Booking Flow (1.5 weeks)

**Goal:** A tourist can browse tour packages, read full itineraries, and submit
a booking request with a preferred date.

**Backend:**

* `TourListView`: filtered by tour type, duration, price range.
Public queryset filters: `is\_active=True`.
* `TourDetailView`: retrieves package, ordered itinerary days, photos.
Serves correct language field with English fallback.
* `TourBookingView`:

  * Preferred start date, number of participants, special requests
  * Creates Booking with `status=PENDING\_CONFIRMATION` — always for tours,
even after payment, because Jadevine must confirm the date
  * Django-Q notifies Jadevine admin of new tour booking request

**Frontend:**

* `tour\_list.html` + `tour\_list.js` + `tour\_list.css`:

  * Filter tabs: All / Safari / Beach / Cultural / Climbing / Combined
  * Tour cards: cover image, name, type badge, duration, group size, price,
2–3 highlights, Book Now button
  * jQuery AJAX filtering
* `tour\_detail.html` + `tour\_detail.js` + `tour\_detail.css`:

  * Hero image with overlay
  * Package overview: duration, group size, price, tour type badge
  * Itinerary: Bootstrap accordion, one panel per day
  * Inclusions and exclusions: two-column checklist
  * What to Bring section
  * Photo gallery with GLightbox
  * Booking form:

    * Flatpickr date picker for preferred start date
    * Participant count with running total price update (jQuery)
    * Special requests textarea
    * Informational note: "We will confirm your preferred date within 24–48 hours"
    * Pay Now and Pay on Arrival options clearly explained

**Seed data for testing:**

* Serengeti National Park Safari (5 days)
* Ngorongoro Crater Tour (2 days)
* Zanzibar Beach \& Snorkeling Package (3 days)
* Zanzibar Spice Tour (1 day)
* Stone Town Cultural Walking Tour (1 day)

\---

### PHASE 4 — User Accounts \& Dashboard (1.5 weeks)

**Goal:** Complete customer authentication system and personal dashboard.

**Authentication — backend:**

* Registration view: form collects first name, last name, email, password,
password confirmation, preferred language
* On registration: account created with `is\_active=False`. Django-Q sends
email verification link via django-allauth email confirmation flow.
* Email verification view: activates account (`is\_active=True`) on link click
* Login view: email + password. Redirects to dashboard or to `next` URL.
* Logout view
* Password reset: request form → Django-Q sends link → reset form
* Password change: requires current password confirmation

**Portal authentication (separate):**

* `/portal/login/` uses username + password
* Checks `user.is\_staff = True`
* Completely independent from customer login
* Customer accounts cannot reach the portal

**User dashboard — backend:**

* `DashboardView`: upcoming bookings (next 3), recent activity summary
* `BookingHistoryView`: all user bookings, paginated, filterable by status
* `BookingDetailView`: single booking details
* `CancelBookingView`:

  1. Compute days between today and service date
  2. Find matching `CancellationPolicy` row for service type and day count
  3. Display refund amount to customer before confirmation
  4. On confirmation: `status=CANCELLED`, `cancelled\_at` set,
refund flagged if applicable
  5. Django-Q sends cancellation email to customer
  6. Django-Q sends cancellation notification to Jadevine admin
  7. PesaPal refund processed manually by Super Admin in portal
* `ProfileView`: view and update personal details, profile photo
* `FavouritesView`: list saved items, handle remove
* `ToggleFavouriteView`: AJAX endpoint, returns `{saved: true/false}`,
jQuery updates heart icon without page reload

**User dashboard — frontend:**

* `dashboard.html` + `dashboard.js`:

  * Welcome with customer's first name
  * Upcoming bookings summary cards (max 3)
  * Quick links to all dashboard sections
* `booking\_history.html` + `booking\_history.js`:

  * Paginated booking table with colour-coded status badges
  * Filter by status dropdown
  * Each row links to booking detail
* `booking\_detail.html` + `booking\_detail.js`:

  * Full booking card: service, dates, pricing, payment method, statuses
  * Download confirmation PDF (ReportLab: reference, dates, total, contact info)
  * Cancel Booking button — visible only when booking is cancellable
(not already cancelled, not completed, service date in the future)
  * Cancellation modal: shows refund amount, requires explicit confirmation
* `profile.html` + `profile.js`:

  * Edit: name, phone, nationality, preferred language, profile photo
  * Password change section
* `favourites.html` + `favourites.js`:

  * Grid of saved hotels, tours, cars
  * Remove button on each card (AJAX, no reload)

\---

### PHASE 5 — Admin Portal (2 weeks)

**Goal:** A fully functional, role-separated portal for Jadevine staff.
Includes the complete listing approval workflow for mini-admin submissions.

**Portal authentication:**

* Login at `/portal/login/`: username + password
* Custom `@portal\_required` decorator on every portal view:

  * Checks `request.user.is\_authenticated`
  * Checks `request.user.is\_staff`
  * Redirects to `/portal/login/` if either fails
* Custom `@superadmin\_required` decorator for Super Admin-only views:

  * Checks `not hasattr(request.user, 'miniadminprofile')`
  * Returns 403 Forbidden if a mini-admin attempts access
* Access control helper for listings and bookings:

```python
  def get\_accessible\_hotels(user):
      if hasattr(user, 'miniadminprofile'):
          return Hotel.objects.filter(created\_by=user)
      return Hotel.objects.all()

  def get\_accessible\_cars(user):
      if hasattr(user, 'miniadminprofile'):
          return CarRental.objects.filter(created\_by=user)
      return CarRental.objects.all()
```

Called in the view, not in the template. Never rely on template logic alone.

* Portal session timeout: 8 hours of inactivity
* `portal\_base.html` is the portal master layout, separate from public `base.html`

**Super Admin — Portal Dashboard:**

* Booking counts: today / this week / this month (confirmed paid)
* Revenue summary: total from confirmed paid bookings
* Bookings by status: count cards (Confirmed, Pending, Cancelled, Completed)
* **Pending Approvals section — prominent, at the top of the dashboard:**

  * Count badge showing total listings awaiting approval
  * Split by type: "X Hotels pending" and "Y Cars pending"
  * Quick links to `/portal/hotels/pending/` and `/portal/cars/pending/`
  * If count is zero, section shows a green "All listings reviewed" state
* Recent bookings table (last 10 across all services)
* Unread contact messages count with link to messages
* Recent mini-admin activity (new listings submitted in the last 7 days)

**Super Admin — Hotels Management:**

* Listing table: name, location, stars, owner (created\_by), approval status badge,
active status, created date, actions (view, edit, delete)
* Filter table by: approval status, location, created\_by
* **Pending Approvals queue (`/portal/hotels/pending/`):**

  * Lists all hotels where `approval\_status=PENDING`
  * Each row shows: hotel name, mini-admin who submitted, submission date,
preview link, Approve button, Reject button
  * Approve action: sets `approval\_status=APPROVED`, `is\_active=True`,
Django-Q notifies mini-admin
  * Reject action: opens modal requiring rejection reason text before confirming.
Sets `approval\_status=REJECTED`, `rejection\_reason` saved,
Django-Q notifies mini-admin with reason
* Create hotel form: all fields, multilingual descriptions, photo upload
Super Admin listings saved with `approval\_status=APPROVED`, `is\_active=True`
(skips the queue — Super Admin's own listings are trusted)
* Edit hotel: all fields editable. If editing a mini-admin's approved listing,
`approval\_status` is not changed (Super Admin edits are trusted)
* Inline photo management: upload, set cover, reorder, delete
* Inline room type management: add, edit, delete
* Toggle hotel active/hidden independently of approval status

**Super Admin — Cars Management:**
Same structure as Hotels Management, including pending approvals queue.

**Super Admin — Tours Management (Super Admin only):**

* Full CRUD for tour packages
* Inline itinerary day management: add, edit, delete days with ordering
* Inline photo management
* Featured package toggle
* No approval workflow — tours are Jadevine's own content

**Super Admin — Bookings Management:**

* Filterable table: service type, status, payment status, date range
* Booking detail: full customer and service info
* Status updates:

  * Confirm tour date → `status=CONFIRMED`
  * Mark as completed → `status=COMPLETED`
  * Mark as no-show → `status=NO\_SHOW`
  * Mark Pay on Arrival as fully paid → `payment\_status=PAID`
* Cancellation exception: override standard refund policy with written reason
* Export filtered results to CSV

**Super Admin — Gallery Management:**

* Upload photos and videos with category assignment
* Drag-to-reorder within category (jQuery UI sortable)
* Set and unset featured flag (controls homepage Gallery Highlights)
* Delete media

**Super Admin — User Accounts Management:**

* Search by name or email
* View profile and full booking history
* Deactivate and reactivate accounts
* Trigger password reset email

**Super Admin — Mini-Admin Management:**

* Create mini-admin account: username, email, first name, last name
* On creation: Django-Q sends welcome email with login credentials and portal URL
* View mini-admin profile: account details, listings created, approval statuses
* Edit account details
* Deactivate account (listings remain but mini-admin can no longer log in)
* Trigger password reset email

**Super Admin — Contact Messages:**

* Table filtered by inquiry type and status (New, In Progress, Resolved)
* Update status
* Reply form: sends email to customer via Django-Q, saves reply in `admin\_notes`

**Super Admin — Newsletter:**

* Subscriber list with date and active status
* Toggle active/inactive per subscriber
* Export to CSV

**Super Admin — Cancellation Policies:**

* Edit policy tiers per service type: days, refund percentage, label
* Add new tiers, toggle active/inactive
* Changes apply to new bookings immediately
(existing bookings retain the policy active at their creation time)

**Super Admin — Portal Settings:**

* Change own username
* Change own password

**Mini-Admin — Portal View:**

* Dashboard: own listings summary (Approved, Pending, Rejected counts),
recent bookings for own listings
* My Listings (Hotels and/or Cars):

  * Lists only own listings with approval status badges
  * PENDING: shows "Awaiting review" — can edit but not resubmit until rejected
  * APPROVED: shows "Live" — edit button opens edit form, saving resets to PENDING
and removes from public site until re-approved
  * REJECTED: shows rejection reason prominently — edit button opens edit form,
saving resets to PENDING and notifies Super Admin
  * Create new listing button: opens full hotel or car form
* My Bookings: read-only table of bookings for own listings only
* Change Password

**Mini-Admin access control — enforced server-side:**
Every view in the portal that touches listings or bookings calls the appropriate
`get\_accessible\_\*` helper. If a mini-admin crafts a direct URL to another
mini-admin's listing or to a Super Admin-only page, they receive 403 Forbidden.
This is not a UI restriction — it is a server-side check on every request.

\---

### PHASE 6 — PesaPal Payment Integration (1 week)

**Goal:** Pay Now flow working end-to-end in sandbox. Pay on Arrival complete.

**Backend:**

* PesaPal credentials in `.env`:
`PESAPAL\_CONSUMER\_KEY`, `PESAPAL\_CONSUMER\_SECRET`, `PESAPAL\_ENVIRONMENT=sandbox`
* PesaPal service module at `apps/bookings/pesapal.py`:

  * `get\_auth\_token()`: authenticates, returns bearer token
  * `submit\_order\_request(booking)`: submits order, returns PesaPal redirect URL
  * `get\_transaction\_status(order\_tracking\_id)`: independent payment verification
* `PaymentOptionsView` updated: calls `submit\_order\_request()`, redirects to PesaPal
* IPN callback view at `/book/pesapal/callback/`:

  * Receives PesaPal POST notification
  * Calls `get\_transaction\_status()` to verify independently
  * Updates `booking.payment\_status` and `booking.status`
  * Triggers Django-Q email tasks
* `BookingConfirmationView`: reads actual DB state, not URL parameters

**Testing checklist:**

* \[ ] Pay Now — Visa test card: confirmed, email received, DB updated correctly
* \[ ] Pay Now — M-Pesa sandbox: same verification
* \[ ] Pay Now — failed payment: booking stays PENDING, failure page shown
* \[ ] Pay on Arrival: booking created, confirmation email sent, no PesaPal call
* \[ ] IPN received via ngrok, status verified, DB updated
* \[ ] Confirmation page correct for all scenarios
* \[ ] Admin receives notification for all new bookings
* \[ ] Tour booking stays PENDING\_CONFIRMATION after payment (correct)
* \[ ] Hotel/car booking moves to CONFIRMED after successful payment (correct)

**Amadeus reminder:**
Flights are post-launch. Do not install, configure, or reference any Amadeus
package, credentials, or code during this project.

\---

### PHASE 7 — Gallery, Contact \& Newsletter (1 week)

**Goal:** Gallery fully functional. Contact and newsletter flows complete.

**Gallery — backend:**

* `GalleryView`: all active categories and their items, ordered by `order` field
* Featured items JSON endpoint: returns `is\_featured=True` items for homepage

**Gallery — frontend:**

* `gallery.html` + `gallery.js` + `gallery.css`:

  * Category tab navigation
  * Photo grid with `loading="lazy"` on all images
  * GLightbox fullscreen lightbox on photo click
  * Video items: YouTube/Vimeo embed in lightbox or direct video player
  * jQuery tab switching filters visible items by category without page reload
  * Responsive: 1 column mobile, 2 tablet, 3–4 desktop

**Contact — backend (completing the stub from Phase 1):**

* Full form processing: saves ContactMessage, Django-Q sends acknowledgment to
customer and notification to admin, returns `{success: true}` JSON

**Newsletter — backend:**

* `NewsletterSubscribeView` AJAX endpoint:

  * Validates email
  * Creates `NewsletterSubscriber` or reactivates if inactive
  * Django-Q sends welcome email
  * Returns `{success: true}` or `{error: "already subscribed"}`

\---

### PHASE 8 — i18n Completion, SEO \& QA (1–1.5 weeks)

**Goal:** French and Russian translations integrated. SEO configured.
All flows tested end-to-end on all devices and browsers.

**i18n completion:**

* Audit all templates and Python files: every user-facing string in `{% trans %}`
or `\_()`. No hardcoded English strings anywhere.
* `python manage.py makemessages -l fr -l ru` — generate final `.po` files
* Submit to Jadevine for translation
* On receipt: integrate, `compilemessages`, test all 3 languages
* Verify multilingual database fields served correctly across all listing pages
* Translate all email templates: booking confirmation, cancellation,
contact acknowledgment, newsletter welcome, email verification,
listing approval notification, listing rejection notification

**SEO:**

* Meta title and description in every public page template using actual content
* `hreflang` tags for all 3 language versions of each page
* `sitemap.xml` via Django's sitemaps framework:

  * Static pages, hotel detail pages, tour detail pages, car detail pages
  * One URL per listing per language
* `robots.txt`: allow public pages, disallow `/portal/`, `/accounts/`, `/admin/`
* Google Analytics 4: `gtag.js` in `base.html`
* Google Search Console: verification meta tag in `base.html`
* Schema.org structured data:

  * `LodgingBusiness` for hotels
  * `TouristAttraction` or `Product` for tour packages
  * `LocalBusiness` for the main site

**QA checklist:**

Booking flows:

* \[ ] Hotel: Pay Now end-to-end (sandbox Visa, sandbox M-Pesa)
* \[ ] Hotel: Pay on Arrival end-to-end
* \[ ] Tour: Pay Now — stays PENDING\_CONFIRMATION after payment
* \[ ] Tour: Pay on Arrival end-to-end
* \[ ] Car: Pay Now with self-drive (licence number required)
* \[ ] Car: Pay Now with driver option
* \[ ] Car: Pay on Arrival end-to-end
* \[ ] Cancellation: 14+ days → 100% refund flagged correctly
* \[ ] Cancellation: 7–13 days → 50% refund flagged correctly
* \[ ] Cancellation: 0–6 days → 0% refund, booking cancelled
* \[ ] All confirmation emails received by customer
* \[ ] All admin notification emails received

Listing approval workflow:

* \[ ] Mini-admin creates hotel → approval\_status=PENDING, not visible publicly
* \[ ] Super Admin sees pending count on dashboard
* \[ ] Super Admin approves → listing appears publicly, mini-admin notified
* \[ ] Super Admin rejects with reason → listing hidden, mini-admin notified with reason
* \[ ] Mini-admin edits rejected listing and resubmits → back to PENDING
* \[ ] Mini-admin edits approved listing → resets to PENDING, removed from public site
* \[ ] Mini-admin direct URL to another's listing → 403 Forbidden
* \[ ] Mini-admin direct URL to Super Admin-only page → 403 Forbidden

User accounts:

* \[ ] Registration: verification email received, link activates account
* \[ ] Login: email + password, redirects correctly
* \[ ] Wrong password: error shown, does not reveal whether email exists
* \[ ] Password reset: link received, new password works, old does not
* \[ ] Booking history shows correct records for logged-in user only
* \[ ] Favourite add and remove via AJAX
* \[ ] Profile updates saved including photo

Admin portal:

* \[ ] Super Admin login and access to all sections
* \[ ] Super Admin creates hotel, tour, car with photos
* \[ ] Super Admin views and updates all bookings
* \[ ] Super Admin creates mini-admin, welcome email received
* \[ ] Mini-admin login: sees only own sections
* \[ ] Export bookings CSV downloads correctly
* \[ ] Gallery upload: appears on gallery page

i18n:

* \[ ] Language switcher changes UI text on every page
* \[ ] Hotel descriptions in correct language with English fallback
* \[ ] Tour itinerary in correct language
* \[ ] Confirmation email in customer's preferred language
* \[ ] /fr/ and /ru/ URL prefixes work on all public pages

Responsive and cross-browser:

* \[ ] Mobile 375px: all pages usable, forms submittable
* \[ ] Tablet 768px: layout correct
* \[ ] Desktop 1280px+: full layout
* \[ ] Chrome, Firefox, Safari, Edge: no layout breakage
* \[ ] iOS Safari: flatpickr date pickers work
* \[ ] Android Chrome: same

\---

### PHASE 9 — Deployment \& Launch (3–4 days)

**Goal:** Live website on production VPS with HTTPS, PostgreSQL, and AWS S3.

**Step-by-step server setup:**

```
1.  Provision VPS: DigitalOcean or Hetzner, Ubuntu 22.04 LTS, 2GB RAM / 2 vCPU minimum
2.  SSH as root. Create non-root sudo user. Disable root SSH login.
3.  sudo apt update \&\& sudo apt upgrade -y
4.  Install: python3.11, python3-pip, python3-venv, git, nginx, certbot,
    python3-certbot-nginx, postgresql, postgresql-contrib
5.  Create PostgreSQL database and user. Grant all privileges on database to user.
6.  git clone <repo> /var/www/jadevine/
7.  python3 -m venv /var/www/jadevine/venv
8.  Activate venv. pip install -r requirements/production.txt
9.  Create /var/www/jadevine/.env with all production secrets
10. python manage.py migrate
11. python manage.py collectstatic --noinput
12. python manage.py createsuperuser (developer account for Django /admin/)
13. Create /etc/systemd/system/jadevine.service (Gunicorn)
14. Create /etc/systemd/system/jadevine-qcluster.service (Django-Q worker)
15. systemctl enable jadevine jadevine-qcluster
    systemctl start jadevine jadevine-qcluster
16. Configure Nginx:
    - HTTP server block: redirect all to HTTPS
    - HTTPS server block: proxy\_pass to Gunicorn socket
    - Serve /static/ directly from staticfiles/ directory (bypasses Django)
17. Register domain. Point DNS A record to VPS IP. Wait for propagation.
18. certbot --nginx -d yourdomain.com -d www.yourdomain.com
19. Configure AWS S3:
    - Create S3 bucket with appropriate public read policy for media
    - Create IAM user with S3 full access, save access key and secret key
    - Add S3 credentials to .env
    - Set DEFAULT\_FILE\_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
      in production.py
20. Smoke test on live domain:
    - Homepage loads with HTTPS (green padlock)
    - Hotel listing and detail pages load
    - Booking flow completes
    - PesaPal production credentials active (switch PESAPAL\_ENVIRONMENT=production)
    - Update IPN callback URL in PesaPal merchant dashboard to live domain
    - Admin portal accessible at /portal/
    - Confirmation emails arrive
    - Gallery photos served from S3 URLs
```

**PesaPal production note:**
Submit PesaPal merchant account for production activation during Phase 6 — not
at deployment time. Approval takes 3–7 business days. Do not wait until Phase 9
to submit or the launch will be blocked.

**Pre-launch checklist:**

* \[ ] `DEBUG = False` in production settings
* \[ ] `ALLOWED\_HOSTS` set to live domain
* \[ ] `SECRET\_KEY` is a long unique random string
* \[ ] All `.env` values are production credentials, not sandbox
* \[ ] HTTPS confirmed working
* \[ ] Static files served by Nginx directly
* \[ ] Media files served from S3
* \[ ] Email sending confirmed with a real test booking
* \[ ] Django-Q worker confirmed running: `systemctl status jadevine-qcluster`
* \[ ] Database backup taken before any post-launch changes

\---

## PART 11: RISKS \& HONEST ASSESSMENTS

|Risk|Likelihood|Mitigation|
|-|-|-|
|Jadevine does not deliver translations on time|High|Build English throughout. French/Russian are content dependencies. Launch in English if translations are not ready — do not delay the entire launch.|
|Jadevine does not deliver photos on time|High|Build with quality placeholder images (Unsplash). Real photos are a content swap, not a rebuild.|
|PesaPal merchant production approval delayed|Medium|Submit for approval at the start of Phase 6. Approval takes 3–7 days. Do not wait until Phase 9.|
|PesaPal IPN not received in development|Medium|Use ngrok. Document the setup step explicitly. This is a required step, not optional.|
|Timeline slips due to scope creep|Medium|This document is the scope contract. New features requested mid-development require a written estimate and approval before work starts.|
|Mini-admin security misconfiguration|Low but high impact|Test explicitly in QA: log in as mini-admin and attempt direct URL attacks to other listings. Add this to the QA checklist and do not skip it.|
|Mini-admin edits approved listing causing unexpected downtime|Medium|The plan sets PENDING on edit of an approved listing. Mini-admin must be clearly warned in the portal UI before they save: "Saving changes will remove this listing from the public site until re-approved."|
|Google/Facebook OAuth complexity at post-launch|Medium|Document the exact setup steps (Google Cloud Console, Facebook Developer App, callback URLs) before starting that work. Known complexity.|
|Production migration errors|Medium|Take a full database backup before every migration on production. No exceptions.|
|First-time VPS management errors|Medium|Follow Phase 9 steps in exact order. Do not skip steps. All commands are explicit for this reason.|

\---

## PART 12: WHAT IS EXPLICITLY POST-LAUNCH

The following are not part of this implementation plan. Any request to add them
during development requires a written estimate and approval before work starts.

* Domestic flights (Amadeus API) — do not install any Amadeus package or credentials
* Expedia hotel API integration
* Booking.com affiliate integration
* Discover Cars API
* TripAdvisor Content API (widget only at launch)
* Google OAuth login for customers
* Facebook OAuth login for customers
* Arabic (RTL) language support
* Dutch language support
* Italian language support
* Pay on Arrival deposit requirement
* Automated PesaPal refund processing (manual flagging only at launch)
* SMS or WhatsApp automated notifications
* Mobile app (iOS or Android)
* Live chat integration

\---

## PART 13: DEVELOPMENT CONVENTIONS (APPLY THROUGHOUT ALL PHASES)

1. **Never hardcode strings in templates or Python code.**
Every user-facing string uses `{% trans "..." %}` in templates and `\_("...")` in Python.
2. **Never store card data.**
PesaPal handles all card processing. Store only PesaPal's `order\_id` and `tracking\_id`.
3. **Never enforce Mini-Admin restrictions only in the template.**
Always enforce in the view using the `get\_accessible\_\*` helper functions.
A hidden menu item is not access control.
4. **Every form has server-side validation.**
jQuery validation is for UX only and can be bypassed. Django form validation
is the final and only authority.
5. **All secrets in `.env`.**
No API keys, database passwords, or secret keys in the codebase or in any
file committed to Git.
6. **Snapshot prices at booking time.**
Store `base\_price` and `total\_price` on the Booking record at creation.
Never recalculate from the current listing price after a booking is made.
7. **Use Django ORM only.**
No raw SQL unless there is a specific documented performance reason.
Use `select\_related()` and `prefetch\_related()` to avoid N+1 queries.
8. **Database backup before every production migration.**
No exceptions, regardless of how minor the migration appears.
9. **Every page tested on mobile before moving to the next phase.**
Do not accumulate responsive debt. Fix it in the phase it is built.
10. **Commit to GitHub at the end of every working day.**
Descriptive commit messages. Never commit directly to `main`.
Use feature branches and merge via pull requests.
11. **Language field selection pattern — use consistently in every view:**

```python
    lang = request.LANGUAGE\_CODE  # 'en', 'fr', or 'ru'
    description = getattr(hotel, f'description\_{lang}') or hotel.description\_en
```

&#x20;   Always fall back to English if the translated field is empty or null.


12. **Portal is never the Django built-in `/admin/`.**
The built-in admin is for developer use only during development.
Restrict it to `127.0.0.1` in production. The client portal is entirely
custom at `/portal/`.
13. **Warn mini-admins before they edit an approved listing.**
The portal must display a clear warning before saving: "Saving changes will
remove this listing from the public site until it is re-approved by the admin."
This prevents accidental unintended downtime of live listings.
14. **Super Admin listings skip the approval queue.**
When a Super Admin creates or edits a listing, set `approval\_status=APPROVED`
and `is\_active=True` automatically. Super Admin content is trusted by definition.

\---

*End of Implementation Plan — Version 1.2 | April 2026
Prepared by Fidon for Jadevine Travel \& Tours
This document supersedes versions 1.0 (March 2026) and 1.1 (April 2026).
Any changes to agreed scope require written agreement from both parties before work starts.*

