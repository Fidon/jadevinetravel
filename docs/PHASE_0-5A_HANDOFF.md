**JADEVINE TRAVEL \& TOURS — PHASE HANDOFF DOCUMENT**

**Version 5.0 | May 2026 | End of Phase 0, 1, 2, 3, 4 \& 5A**



**PROJECT IDENTITY**

Project: Jadevine Travel \& Tours — full-stack Django booking \& marketing platform

Client: Zanzibar-based travel company

Developer: Fidon (fidonamos@gmail.com, +255 713 529 019)

Root folder: jadevinetravel/

Django version: 6.0.4

Python: 3.13 (venv)

OS: Windows (PowerShell)

Database (dev): SQLite — jadevine\_db.sqlite3

Database (prod): PostgreSQL

Media (dev): Local filesystem

Media (prod): AWS S3



**DJANGO SETTINGS MODULE**

Active settings: config.settings.development



**.env required entries:**

DJANGO\_SETTINGS\_MODULE=config.settings.development

SECRET\_KEY=your-secret-key-here

DEFAULT\_FROM\_EMAIL=Jadevine Travel \& Tours [your-email@gmail.com](mailto:your-email@gmail.com)

EMAIL\_BACKEND=django.core.mail.backends.smtp.EmailBackend

EMAIL\_HOST=smtp.gmail.com

EMAIL\_PORT=587

EMAIL\_USE\_TLS=True

EMAIL\_HOST\_USER=your-gmail@gmail.com

EMAIL\_HOST\_PASSWORD=your-app-password

ADMIN\_NOTIFICATION\_EMAIL=fidontakakwa@gmail.com



**Settings split:**

* config/settings/base.py — shared
* config/settings/development.py — SQLite, local media, DEBUG=True
* config/settings/production.py — PostgreSQL, AWS S3, SendGrid, DEBUG=False



**Key settings in config/settings/base.py:**

ACCOUNT\_ADAPTER = 'apps.accounts.adapters.AccountAdapter'

ACCOUNT\_FORMS = {'signup': 'apps.accounts.forms.CustomSignupForm'}

ACCOUNT\_PASSWORD\_CHANGE\_REDIRECT\_URL = '/accounts/password/change/'

ACCOUNT\_EMAIL\_CONFIRMATION\_HMAC = True

ADMIN\_NOTIFICATION\_EMAIL = os.environ.get('ADMIN\_NOTIFICATION\_EMAIL', 'fidontakakwa@gmail.com')



TEMPLATES = \[{

&#x20;   ...

&#x20;   'OPTIONS': {

&#x20;       'context\_processors': \[

&#x20;           ...

&#x20;           'apps.portal.context\_processors.portal\_context',  # portal sidebar data

&#x20;       ],

&#x20;   },

}]



**TECH STACK**

Layer			Technology

Backend			Python / Django 6.0.4

Frontend			HTML5, CSS3, jQuery 3.7.1, Bootstrap 5.3.3

Icons			Bootstrap Icons 1.11.3

Fonts			Cormorant Garamond + Jost (Google Fonts)

Database			SQLite (dev) → PostgreSQL (prod)

Auth				django-allauth 65.16.0 (email/password; OAuth post-launch)

Task Queue		django-q2 with Django ORM broker

Media Storage		Local (dev) → AWS S3 via django-storages (prod)

Email			Gmail SMTP (dev) → SendGrid (prod)

PDF Generation	ReportLab

Payments			PesaPal REST API 3.0 (Phase 6)

Lightbox			GLightbox (CDN)

Date Pickers		Flatpickr (CDN)

Table Management	DataTables 1.13.8 + Buttons 2.4.2 (CDN, portal only)

Drag-to-reorder	jQuery UI 1.13.3 (CDN, portal only)

Flights			Amadeus API — POST-LAUNCH, do not implement

Hotels API		Expedia EAN — POST-LAUNCH, do not implement

Hosting			VPS: DigitalOcean or Hetzner, Nginx + Gunicorn

SSL

Let's Encrypt



**INSTALLED PACKAGES (requirements.txt)**

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



**PROJECT FOLDER STRUCTURE**

jadevinetravel/

├── apps/

│   ├── accounts/         ✅ COMPLETE — CustomUser, auth, dashboard

│   ├── hotels/           ✅ COMPLETE — Hotel, HotelPhoto, HotelRoomType, public views

│   ├── tours/            ✅ COMPLETE — TourPackage, TourItineraryDay, TourPhoto, public views

│   ├── cars/             ✅ COMPLETE — CarRental, CarPhoto, public views

│   ├── bookings/         ✅ COMPLETE — Booking, CancellationPolicy, booking flow

│   ├── reviews/          ✅ COMPLETE — Review model, SubmitReviewView

│   ├── gallery/          — models only (Phase 7)

│   ├── contact/          — models only (Phase 7)

│   └── portal/           ✅ COMPLETE (Phase 5A)

│       ├── \_\_init\_\_.py

│       ├── context\_processors.py

│       ├── forms.py

│       ├── mixins.py

│       ├── tasks.py      — stubs only (full email tasks in Phase 5B)

│       ├── urls.py

│       └── views/

│           ├── \_\_init\_\_.py

│           ├── auth.py

│           ├── dashboard.py

│           ├── hotels.py

│           ├── cars.py

│           ├── tours.py

│           └── bookings.py

│   └── core/             ✅ COMPLETE — Homepage, About stub, SavedFavourite

├── templates/

│   ├── base.html                          ✅ COMPLETE

│   ├── account/                           ✅ COMPLETE — allauth overrides

│   ├── accounts/                          ✅ COMPLETE — customer dashboard

│   ├── core/                              ✅ COMPLETE

│   ├── hotels/                            ✅ COMPLETE

│   ├── tours/                             ✅ COMPLETE

│   ├── cars/                              ✅ COMPLETE

│   ├── bookings/                          ✅ COMPLETE

│   └── portal/                            ✅ COMPLETE (Phase 5A)

│       ├── portal\_base.html

│       ├── portal\_login.html

│       ├── portal\_dashboard.html

│       ├── portal\_stub.html

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

│       └── includes/

│           ├── room\_type\_form\_fields.html

│           └── itinerary\_day\_form\_fields.html

├── static/

│   ├── css/

│   │   ├── main.css                       ✅ COMPLETE — full design system

│   │   ├── core/home.css                  ✅ COMPLETE

│   │   ├── hotels/                        ✅ COMPLETE

│   │   ├── tours/                         ✅ COMPLETE

│   │   ├── cars/                          ✅ COMPLETE

│   │   ├── bookings/                      ✅ COMPLETE

│   │   ├── accounts/                      ✅ COMPLETE

│   │   └── portal/

│   │       ├── portal\_base.css            ✅ COMPLETE

│   │       ├── portal\_dashboard.css       ✅ COMPLETE

│   │       ├── portal\_hotels.css          ✅ COMPLETE

│   │       ├── portal\_cars.css            ✅ COMPLETE

│   │       ├── portal\_tours.css           ✅ COMPLETE

│   │       └── portal\_bookings.css        ✅ COMPLETE

│   └── js/

│       ├── main.js                        ✅ COMPLETE

│       ├── core/home.js                   ✅ COMPLETE

│       ├── hotels/                        ✅ COMPLETE

│       ├── tours/                         ✅ COMPLETE

│       ├── cars/                          ✅ COMPLETE

│       ├── bookings/                      ✅ COMPLETE

│       ├── accounts/                      ✅ COMPLETE

│       └── portal/

│           ├── portal\_base.js             ✅ COMPLETE

│           ├── portal\_dashboard.js        ✅ COMPLETE

│           ├── portal\_hotels.js           ✅ COMPLETE

│           ├── portal\_cars.js             ✅ COMPLETE

│           ├── portal\_tours.js            ✅ COMPLETE

│           └── portal\_bookings.js         ✅ COMPLETE



**URL STRUCTURE**

\# NOT language-prefixed

/admin/                          — Django built-in admin (developer only)

/book/                           — All booking flow URLs

/reviews/                        — Review submission

/portal/                         — Admin portal (NOT inside i18n\_patterns)

/i18n/                           — Django language switching



\# Portal URLs (all under /portal/)

/portal/login/

/portal/logout/

/portal/                                      — dashboard

/portal/api/pending-count/                    — JSON polling endpoint (60s interval)

/portal/hotels/                               — list + filters

/portal/hotels/add/

/portal/hotels/pending/                       — Super Admin only

/portal/hotels/<pk>/

/portal/hotels/<pk>/edit/

/portal/hotels/<pk>/delete/

/portal/hotels/<pk>/approve/                  — Super Admin only

/portal/hotels/<pk>/reject/                   — Super Admin only

/portal/hotels/<pk>/resubmit/                 — Mini-Admin only

/portal/hotels/<hpk>/photos/upload/           — AJAX POST

/portal/hotels/<hpk>/photos/<pk>/delete/      — AJAX POST

/portal/hotels/<hpk>/photos/<pk>/cover/       — AJAX POST

/portal/hotels/<hpk>/photos/reorder/          — AJAX POST (JSON body)

/portal/hotels/<hpk>/rooms/add/               — modal POST

/portal/hotels/<hpk>/rooms/<pk>/edit/         — modal POST

/portal/hotels/<hpk>/rooms/<pk>/delete/       — POST

\# Cars mirrors Hotels exactly (replace hotels→cars, hpk→cpk)

\# No room type endpoints for cars

/portal/tours/                                — Super Admin only throughout

/portal/tours/add/

/portal/tours/<pk>/

/portal/tours/<pk>/edit/

/portal/tours/<pk>/delete/

/portal/tours/<pk>/toggle-featured/

/portal/tours/<tpk>/photos/upload/

/portal/tours/<tpk>/photos/<pk>/delete/

/portal/tours/<tpk>/photos/reorder/

/portal/tours/<tpk>/itinerary/add/

/portal/tours/<tpk>/itinerary/<pk>/edit/

/portal/tours/<tpk>/itinerary/<pk>/delete/

/portal/bookings/

/portal/bookings/<pk>/

/portal/bookings/<pk>/status/

/portal/bookings/<pk>/mark-paid/

\# All Phase 5B URLs registered as stubs — see stub section below



**PORTAL ARCHITECTURE**

**Authentication**

Two completely separate auth flows — they do not share sessions, views, or URLs:

**Customers** — email + password via django-allauth at /accounts/login/

**Portal staff** — username + password via Django built-in auth at /portal/login/

* Username lookup uses iexact for case-insensitive match, then passes the stored casing to authenticate()
* Requires user.is\_staff = True
* PortalLoginView in apps/portal/views/auth.py
* Session timeout: 8 hours of inactivity (set in Django session settings)



**Mixins** (apps/portal/mixins.py)

PortalRequiredMixin      # authenticated + is\_staff=True → redirects to /portal/login/

SuperAdminRequiredMixin  # extends PortalRequiredMixin + blocks mini-admins → 403



**Access control helpers (call in EVERY portal view touching listings/bookings)**

get\_accessible\_hotels(user)    # Super Admin: all / Mini-Admin: created\_by=user

get\_accessible\_cars(user)      # Super Admin: all / Mini-Admin: created\_by=user

get\_accessible\_bookings(user)  # Super Admin: all / Mini-Admin: own hotels+cars only

get\_accessible\_reviews(user)   # Super Admin: all / Mini-Admin: own hotel+car reviews

is\_mini\_admin(user)            # bool — hasattr(user, 'miniadminprofile')



**These are enforced in the VIEW, never only in the template.**

Context processor (apps/portal/context\_processors.py)

Registered in TEMPLATES\[0]\['OPTIONS']\['context\_processors'].

Injects into every portal template automatically:

* pending\_total — total pending hotel + car listings
* pending\_hotels — pending hotel count
* pending\_cars — pending car count
* unread\_messages — unread ContactMessage count
* mini\_admin — boolean



Only fires DB queries when request.user.is\_authenticated and request.user.is\_staff.



**Pending count polling**

portal\_base.js calls GET /portal/api/pending-count/ every 60 seconds.

Returns { "hotels": N, "cars": M, "total": N+M }.

Updates .pending-count-badge elements and sidebar badge without page reload.

Mini-admins: endpoint returns zeros, setInterval is skipped entirely.



**PORTAL CSS \& JS ARCHITECTURE**

**CSS structure**

portal\_base.css     — sidebar, topbar, nav links, stat cards, tables (DataTables overrides),

&#x20;                     modals, photo grid, approval badges, portal cards, forms, utility classes

portal\_hotels.css   — hotel thumbnail, room type list, field errors, btn-danger-jd

portal\_cars.css     — min-width for #cars-table

portal\_tours.css    — itinerary list, day-number badge, min-width for #tours-table

portal\_bookings.css — booking status badges, price breakdown, attention row highlight, DataTables length menu and pagination styling



**JS structure**

portal\_base.js      — sidebar toggle, active nav link (longest-match algorithm),

&#x20;                     flash message auto-dismiss, pending count polling,

&#x20;                     PORTAL.csrf() helper, shared #confirmModal system,

&#x20;                     PORTAL.initDataTable() factory, portal-autosubmit handler

portal\_dashboard.js — dashboard-specific interactions

portal\_hotels.js    — rejection modal, language tabs, edit room modal (from JSON),

&#x20;                     photo upload (AJAX sequential queue), set cover, delete photo,

&#x20;                     photo reorder (jQuery UI Sortable), portal:photo-delete-confirmed event

portal\_cars.js      — same pattern as portal\_hotels.js, no room type modal

portal\_tours.js     — language tabs, edit itinerary day modal (from JSON),

&#x20;                     photo upload/delete/reorder (no set-cover — tour cover is cover\_image field)

portal\_bookings.js  — DataTables init with CSV/Excel/PDF/Print buttons,

&#x20;                     10 per page default, lengthMenu \[10,20,50,100]



**Shared confirm modal (#confirmModal in portal\_base.html)**

All destructive actions use this modal — no window.confirm() anywhere.



**Usage on standard form submit buttons:**

<button type="submit"

&#x20;       data-confirm="Are you sure?"

&#x20;       data-confirm-title="Delete Hotel">



**Usage for photo delete (AJAX — not a form submit):** Photo delete sets window.\_photoDeletePending = true and fires $('#confirmModal').modal('show'). The portal:photo-delete-confirmed jQuery event is triggered on proceed.

Each page JS (portal\_hotels.js, portal\_cars.js, portal\_tours.js) listens for this event.



**Modal structure pattern (applies to ALL modals in portal)**

The form { display: contents } trick makes the form element transparent to Bootstrap's flex column, so header/body/footer participate correctly in scrollable modal layout:



<div class="modal fade portal-modal" ...>

&#x20; <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">

&#x20;   <div class="modal-content">

&#x20;     <form method="post" action="...">

&#x20;       {% csrf\_token %}

&#x20;       <div class="modal-header">...</div>

&#x20;       <div class="modal-body">...</div>

&#x20;       <div class="modal-footer">...</div>

&#x20;     </form>

&#x20;   </div>

&#x20; </div>

</div>



**CSS in portal\_base.css:**

.portal-modal .modal-dialog-scrollable { max-height: calc(100% - 3.5rem); }

.portal-modal .modal-content { max-height: 100%; display: flex; flex-direction: column; }

.portal-modal form { display: contents; }

.portal-modal .modal-header .modal-title,

.portal-modal .modal-header .modal-title i { color: #fff; }



**Active nav link algorithm**

Longest-match: collects all .portal-nav-link elements, finds the one whose href is the longest prefix matching window.location.pathname at a path segment boundary. Prevents /portal/hotels/ matching as active when on /portal/hotels/pending/.



**DataTables pattern**

// In page JS files — call the factory, override only what differs:

PORTAL.initDataTable('#my-table', {

&#x20; pageLength: 25,

&#x20; searching: false,          // when server-side filtering handles search

&#x20; columnDefs: \[{ orderable: false, targets: -1 }],

&#x20; exportOptions: { columns: ':not(:last-child)' }  // exclude Actions column

});



DataTables CDN (loaded in portal\_base.html only, not base.html):

* datatables.min.css + dataTables.bootstrap5.min.js
* buttons.bootstrap5.min.js + buttons.html5.min.js + buttons.print.min.js
* jszip.min.js (Excel) + pdfmake.min.js + vfs\_fonts.js (PDF)



jQuery UI CDN (for Sortable drag-to-reorder in photo grids):

<script src="https://code.jquery.com/ui/1.13.3/jquery-ui.min.js"></script>



**ALL DATABASE MODELS**

**apps/accounts/models.py**

**CustomUser** (extends AbstractUser)

* email — customer login identifier
* username — admin/mini-admin login identifier (stored lowercase, matched iexact)
* first\_name, last\_name, phone, nationality
* preferred\_language — en/fr/ru
* profile\_photo — ImageField (upload\_to='profiles/')
* is\_staff — True for Super Admin and Mini-Admin
* AUTH\_USER\_MODEL = 'accounts.CustomUser'



**MiniAdminProfile**

* user — OneToOneField → CustomUser
* created\_by — ForeignKey → CustomUser (the Super Admin who created it)
* Detect mini-admin: hasattr(user, 'miniadminprofile')



**apps/hotels/models.py**

**Hotel** — name, slug (auto), location, description\_en/fr/ru, stars, price\_per\_night, address, latitude, longitude, tripadvisor\_url, created\_by, approval\_status (pending/approved/rejected), rejection\_reason, is\_active

* Public visibility: is\_active=True AND approval\_status='approved'
* cover\_photo property, is\_publicly\_visible property, get\_description(lang) method



**HotelPhoto** — hotel, image, caption, is\_cover, order

**HotelRoomType** — hotel, name, description\_en/fr/ru, price\_per\_night (nullable, overrides hotel base), max\_guests, amenities (JSONField list), is\_available, discount\_percent, discount\_expires\_at, is\_refundable, allows\_pay\_on\_arrival

* get\_effective\_price(), get\_discounted\_price(), get\_display\_price(), has\_active\_discount



**apps/tours/models.py**

**TourPackage** — name\_en/fr/ru, slug, tour\_type, description\_en/fr/ru, duration\_days, group\_size\_max, price\_per\_person, highlights/inclusions/exclusions\_en/fr/ru (JSONField lists), what\_to\_bring\_en/fr/ru, cover\_image, is\_active, is\_featured, discount\_percent, discount\_expires\_at, is\_refundable, allows\_pay\_on\_arrival

* NO created\_by or approval\_status — Super Admin only, no approval workflow
* get\_name(lang), get\_description(lang), get\_display\_price(), has\_active\_discount



**TourItineraryDay** — package, day\_number, title\_en/fr/ru, description\_en/fr/ru

* Unique together: \[package, day\_number]



**TourPhoto** — package, image, caption, order

* No is\_cover field — tour cover is TourPackage.cover\_image (direct ImageField)
* Therefore: no set-cover button in tour photo grid



**apps/cars/models.py**

**CarRental** — name, slug, vehicle\_type, make, model, year, capacity, fuel\_type, transmission, price\_per\_day, offers\_self\_drive, offers\_driver, driver\_speaks\_en/fr, pickup\_locations (JSONField list), description\_en/fr/ru, created\_by, approval\_status, rejection\_reason, is\_available, is\_active, discount\_percent, discount\_expires\_at, is\_refundable, allows\_pay\_on\_arrival

* Public visibility: is\_active=True AND is\_available=True AND approval\_status='approved'
* cover\_photo property, get\_display\_price(), has\_active\_discount



**CarPhoto** — car, image, is\_cover, order



**apps/bookings/models.py**

**CancellationPolicy** — service\_type, days\_before\_service, refund\_percentage, label\_en, is\_active

**Booking** — reference (JDV-YYYY-NNNNN auto), user, service\_type, hotel, room\_type, tour\_package, car, date fields, num\_guests/participants/days, car-specific fields, base\_price, total\_price, currency, payment\_mode, payment\_status, pesapal\_order\_id/tracking\_id, status, special\_requests, is\_refundable (snapshotted), cancellation\_reason, cancelled\_at, cancelled\_by

* service\_date property (primary date for cancellation calc)
* nights property (hotel bookings)
* STATUS\_CHOICES: pending\_confirmation, confirmed, cancellation\_requested, cancelled, completed, no\_show



**apps/reviews/models.py**

**Review** — user, booking (OneToOneField — enforces one review per booking), service\_type, hotel/tour\_package/car (nullable FKs), rating (1–10), comment, status (pending/approved/rejected), rejection\_reason, moderated\_by, moderated\_at

* Display threshold: only show ratings when listing has ≥ 3 approved reviews



**apps/gallery/models.py**

**GalleryCategory** — name\_en/fr/ru, slug, order

GalleryItem — category, media\_type (photo/video), image, video\_url, video\_file, caption\_en/fr/ru, is\_featured, order



**apps/contact/models.py**

**ContactMessage** — name, email, phone, subject, message, inquiry\_type, preferred\_lang, status (new/in\_progress/resolved), admin\_notes

**NewsletterSubscriber** — email (unique), is\_active, subscribed\_at



**apps/core/models.py**

**SavedFavourite** — user, hotel, tour\_package, car (one FK populated), UniqueConstraints per user per item



**AUTHENTICATION SYSTEM**

**Customer auth (django-allauth)**

ACCOUNT\_LOGIN\_METHODS = {'email'}

ACCOUNT\_SIGNUP\_FIELDS = \['email\*', 'password1\*', 'password2\*']

ACCOUNT\_EMAIL\_VERIFICATION = 'mandatory'

ACCOUNT\_UNIQUE\_EMAIL = True

LOGIN\_REDIRECT\_URL = '/accounts/dashboard/'

LOGOUT\_REDIRECT\_URL = '/'

ACCOUNT\_ADAPTER = 'apps.accounts.adapters.AccountAdapter'

ACCOUNT\_FORMS = {'signup': 'apps.accounts.forms.CustomSignupForm'}



AccountAdapter responsibilities: saves extra signup fields, strips \[Site Name] from email subjects, suppresses allauth system messages, forces HTML+plain multipart emails.



**Portal auth (Django built-in)**

Login at /portal/login/ — PortalLoginView in apps/portal/views/auth.py.

Case-insensitive lookup: CustomUser.objects.get(username\_\_iexact=username\_raw) then pass actual stored username to authenticate().

is\_staff=True required. Customer accounts cannot access portal.



**LISTING APPROVAL WORKFLOW**

Applies to Hotels and Car Rentals. Tours skip this entirely — Super Admin only.

Mini-Admin creates listing:

&#x20; approval\_status = 'pending', is\_active = False (not public)

&#x20; → async\_task: notify Super Admin



Super Admin approves:

&#x20; approval\_status = 'approved', is\_active = True (goes live)

&#x20; rejection\_reason = ''

&#x20; → async\_task: send\_listing\_approved\_email to mini-admin



Super Admin rejects:

&#x20; approval\_status = 'rejected', is\_active = False, rejection\_reason saved

&#x20; → async\_task: send\_listing\_rejected\_email to mini-admin with reason



Mini-Admin edits REJECTED listing → resubmit button:

&#x20; approval\_status = 'pending', rejection\_reason = '', is\_active = False

&#x20; → async\_task: notify Super Admin (same as create)



Mini-Admin edits APPROVED listing → saves:

&#x20; approval\_status = 'pending', is\_active = False (REMOVED FROM PUBLIC SITE)

&#x20; → async\_task: notify Super Admin

&#x20; Warning shown in portal UI before save



Super Admin creates listing directly:

&#x20; approval\_status = 'approved', is\_active = True (skips queue)



Super Admin edits any listing:

&#x20; No approval state change (trusted)



**State machine enforced in view form\_valid(), not in model save().**

**PORTAL FORMS (apps/portal/forms.py)**

HotelForm              — Hotel create/edit (excludes created\_by, approval\_status, rejection\_reason, is\_active, slug)

HotelRoomTypeForm      — Room type modal (amenities as textarea → JSONField via save())

HotelRejectionForm     — rejection\_reason (required, min 10 chars)

CarRentalForm          — Car create/edit (pickup\_locations as textarea → JSONField via save())

CarRejectionForm       — same pattern as HotelRejectionForm

TourPackageForm        — Tour create/edit (highlights/inclusions/exclusions as textarea → JSONField via save())

&#x20;                        enctype="multipart/form-data" required (cover\_image)

TourItineraryDayForm   — Itinerary day modal

BookingStatusForm      — Status update (choices filtered to valid transitions for current status)

BookingMarkPaidForm    — Simple confirmation for POA mark-as-paid



**STATUS\_TRANSITIONS dict** (in portal/forms.py, imported by views/bookings.py):

STATUS\_TRANSITIONS = {

&#x20;   'pending\_confirmation': \['confirmed', 'cancelled'],

&#x20;   'confirmed':            \['completed', 'no\_show', 'cancelled'],

&#x20;   'cancellation\_requested': \['cancelled', 'confirmed'],

&#x20;   'cancelled':            \[],

&#x20;   'completed':            \[],

&#x20;   'no\_show':              \[],

}



**PHOTO MANAGEMENT PATTERN (Hotels, Cars, Tours)**

All three use identical AJAX contract:

Upload: POST /portal/{type}/{pk}/photos/upload/ — multipart, single image per call, sequential queue in JS

Delete: POST /portal/{type}/{pk}/photos/{photo\_pk}/delete/

Set Cover: POST /portal/{type}/{pk}/photos/{photo\_pk}/cover/ — Hotels and Cars only. Tours have no is\_cover field.

Reorder: POST /portal/{type}/{pk}/photos/reorder/ — JSON body { "order": \[id, id, id] }



Upload area click fix (prevents browser loop):

$area.on('click', function (e) {

&#x20;   if (!$(e.target).is($input)) { $input.trigger('click'); }

});

$input.on('click', function (e) { e.stopPropagation(); });



Photo delete uses shared #confirmModal + window.\_photoDeletePending flag + portal:photo-delete-confirmed jQuery event. The page JS listens for this event and executes the AJAX call.

URL templates for JS (set in {% block extra\_js %} of each detail template):

window.HOTEL\_URLS = {

&#x20;   photoUpload:   '{% url "portal:hotel\_photo\_upload" hotel.pk %}',

&#x20;   photoDelete:   '/portal/hotels/{{ hotel.pk }}/photos/\_\_ID\_\_/delete/',

&#x20;   photoSetCover: '/portal/hotels/{{ hotel.pk }}/photos/\_\_ID\_\_/cover/',

&#x20;   photoReorder:  '{% url "portal:hotel\_photo\_reorder" hotel.pk %}',

};

// CAR\_URLS and TOUR\_URLS follow same pattern



**ROOM TYPE \& ITINERARY DAY MODAL PATTERN**

Room types (Hotels) and itinerary days (Tours) use modal POST (not AJAX):

1. Form HTML is pre-rendered in the detail template via {% include %} partial
2. Add modal: form POSTs to /portal/hotels/<hpk>/rooms/add/
3. Edit modal: JS populates fields from window.HOTEL\_ROOM\_TYPES JSON (set in template), sets form action to rt.edit\_url
4. View processes POST, redirects back to detail page with Django messages toast
5. Edit and Add modals share the same form partial (room\_type\_form\_fields.html)



Amenities / pickup\_locations prepopulation fix:

Never use data-\* attributes for multi-line text. Pass as JSON global:

\# In view context:

context\['room\_types\_json'] = json.dumps(room\_types\_data, cls=DjangoJSONEncoder)



// In JS edit handler:

$modal.find('\[name="amenities\_text"]').val(rt.amenities.join('\\n'));



**EMAIL SYSTEM**

**Transport**: Gmail SMTP in dev, SendGrid in prod.

Admin emails always go to: settings.ADMIN\_NOTIFICATION\_EMAIL



**Branded HTML email pattern (inline CSS only, table-based layout):**

msg = EmailMultiAlternatives(subject, text\_body, settings.DEFAULT\_FROM\_EMAIL, \[recipient])

msg.attach\_alternative(html\_body, 'text/html')

msg.send(fail\_silently=True)



Never use display:flex or display:grid in email HTML. Gmail strips these. Use <table> for all multi-column layouts.

Email tasks in apps/portal/tasks.py (stubs — full implementation in Phase 5B):

notify\_superadmin\_new\_listing(listing\_type, listing\_id)  # → stub

send\_listing\_approved\_email(listing\_type, listing\_id)    # → stub

send\_listing\_rejected\_email(listing\_type, listing\_id)    # → stub



Email tasks in apps/bookings/tasks.py:

send\_poa\_booking\_confirmation\_customer(booking\_id)  # → HTML email ✅ COMPLETE

send\_poa\_booking\_notification\_admin(booking\_id)     # → HTML email ✅ COMPLETE



Email tasks in apps/accounts/tasks.py:

send\_cancellation\_requested\_customer\_email(booking\_id, refund\_info)  # ✅

send\_cancellation\_requested\_admin\_email(booking\_id, refund\_info)     # ✅

send\_cancellation\_confirmed\_customer\_email(booking\_id, refund\_info)  # ✅

send\_cancellation\_confirmed\_admin\_email(booking\_id, refund\_info)     # ✅

cleanup\_unverified\_accounts()  # scheduled daily Django-Q task ✅



**BOOKING SYSTEM ARCHITECTURE**

**Session-first, DB-on-confirm pattern:**

1. User submits booking form → view validates and stores data + snapshotted price in request.session\['pending\_booking']. No DB write.
2. User sees summary page rendered from session.
3. User clicks Confirm → Booking DB record created at this point only.
4. Pay on Arrival → status='confirmed' immediately.
5. Pay Now → status='pending\_confirmation' → Phase 6 wires PesaPal.



**Price snapshotting:** Always call get\_display\_price() — never read price\_per\_night, price\_per\_day, or price\_per\_person directly for display or booking.

is\_refundable **snapshotted** at booking creation from the listing's current value. Never retroactively affected by future listing changes.

allows\_pay\_on\_arrival=False enforced server-side in BookingSummaryView.\_create\_booking() — UI suppression alone is not sufficient.

**Tour bookings always** status='pending\_confirmation' — even after payment. Jadevine must manually confirm the date. Permanent architecture.



**DESIGN SYSTEM**

**Typography:**

* Headings: Cormorant Garamond (serif)
* Body: Jost (sans-serif)



**Core CSS variables (defined in static/css/main.css, referenced everywhere):**

\--color-primary: #1a4d2e      --color-primary-dark: #122f1c

\--color-primary-light: #2a6b40  --color-primary-xlight: #e8f0eb

\--color-accent: #c89666        --color-accent-dark: #a67a50

\--color-accent-light: #e8c99a  --color-accent-xlight: #faf3ea

\--color-off-white: #f8f5f0     --color-light: #f0ebe3

\--color-border: #e0d5c8        --color-border-dark: #c8b89a

\--color-text: #1e1e1e          --color-text-light: #5a5550

\--color-muted: #9e8e7e         --color-dark: #111111

\--color-success: #2d7a4f       --color-success-bg: #edf7f1

\--color-danger: #b03a2e        --color-danger-bg: #fdf0ee

\--color-warning: #c89666       --color-warning-bg: #fdf6ee

\--color-info: #2471a3          --color-info-bg: #eaf4fb

\--font-heading: 'Cormorant Garamond', Georgia, serif

\--font-body: 'Jost', 'Segoe UI', sans-serif

\--radius-sm: 4px  --radius-md: 8px  --radius-lg: 16px  --radius-full: 9999px



**Portal-specific classes (in portal\_base.css):**

* .portal-card, .portal-card-header, .portal-card-title
* .portal-stat-card, .portal-stat-icon--primary/accent/success/danger
* .approval-badge--approved/pending/rejected
* .portal-table-wrap — overflow-x: auto + table-responsive class on div
* .portal-row-actions, .portal-icon-btn, .portal-icon-btn--danger/accent
* .portal-empty-state
* .portal-edit-warning — yellow banner before mini-admin edits approved listing
* .portal-alert--success/error/warning/info
* .photo-grid, .photo-item, .photo-upload-area, .photo-cover-badge
* .portal-nav-link.active — set via longest-match JS algorithm, not in template
* .btn-danger-jd — defined in portal\_hotels.css



**window.JD globals (public site, main.js):**

JD.toast('Message', 'success')

JD.csrfToken()

JD.initReveal()



**window.PORTAL globals (portal, portal\_base.html):**

PORTAL.csrfToken    // string

PORTAL.isMiniAdmin  // boolean

PORTAL.pendingTotal // integer

PORTAL.urls.pendingCount

PORTAL.urls.dashboard

PORTAL.csrf()       // function, returns token

PORTAL.initDataTable(selector, overrides)  // DataTables factory



**MULTILINGUAL SETUP**

3 languages at launch: English (default, no prefix), French (/fr/), Russian (/ru/)

Language fallback pattern (use in every view serving model content):

lang = request.LANGUAGE\_CODE  # 'en', 'fr', or 'ru'

value = getattr(obj, f'field\_{lang}', None) or obj.field\_en



**JS translation strings** go in window.JD\_STRINGS in the template {% block extra\_js %} — never in static .js files.

**Django → JS data** passed via window.JD\_\* globals in <script> block before page JS.



**KEY CONVENTIONS (apply in every phase)**

1. Every user-facing string: {% trans %} or \_() — never hardcode English
2. Never store card data — PesaPal handles all card processing
3. Mini-admin access restrictions enforced in VIEW — never only in template
4. Server-side Django validation is authoritative — jQuery is UX only
5. All secrets in .env
6. Snapshot prices via get\_display\_price() — never read raw price fields
7. Snapshot is\_refundable at booking time — never retroactively changed
8. Django ORM only — no raw SQL
9. select\_related() and prefetch\_related() — avoid N+1
10. DB backup before every production migration
11. Test mobile before moving to next phase
12. Commit to GitHub daily
13. Language fallback: getattr(obj, f'field\_{lang}', None) or obj.field\_en
14. Portal ≠ Django /admin/ — /admin/ is developer-only
15. Warn mini-admins before saving edits to approved listing (UI + server-side)
16. JS strings → window.JD\_STRINGS in template — never in static .js files
17. Django → JS data: window.JD\_\* globals in <script> block before page JS
18. Booking DB record created only at Confirm click — not at form submit
19. Tour bookings always status='pending\_confirmation' — permanent
20. .jd-load-reveal for above-fold; .jd-reveal for scroll-triggered
21. JS files: IIFE pattern (function($){ 'use strict'; ... })(jQuery);
22. templates/account/ (singular) = allauth; templates/accounts/ (plural) = dashboard
23. Profile photo: raw <input type="file" name="profile\\\_photo"> — never {{ form.profile\_photo }}
24. Never call Python methods with args from Django templates — resolve in view
25. allauth email prefixes: verify with logging before creating templates
26. Never use display:flex/display:grid in email HTML — use <table>
27. Refund info hidden when payment\_status != 'paid' OR booking.is\_refundable == False
28. PDF headers: flat Table only — no nested tables (ReportLab clips nested content)
29. Rating badges only shown when listing has ≥ 3 approved reviews
30. Review eligibility: booking.status == 'completed' AND booking.user == request.user
31. get\_display\_price() is the single source of truth for any price shown or snapshotted
32. allows\_pay\_on\_arrival=False enforced server-side — UI suppression alone is not sufficient
33. form { display: contents } inside .modal-content — makes form transparent to flex column
34. Modal footer always visible: modal-dialog-scrollable + CSS max-height constraints
35. Table horizontal scroll: overflow-x: auto on .portal-table-wrap + table-responsive class + min-width on table
36. Active nav link: longest-match algorithm in portal\_base.js — not set in template blocks
37. Photo upload click loop fix: stop $input click from propagating to upload area
38. DataTables export: exportOptions: { columns: ':not(:last-child)' } to exclude Actions column
39. TourPhoto has no is\_cover field — no set-cover button in tour photo grids
40. Username login: .lower() applied on input; stored as lowercase; iexact lookup





**CURRENTLY WORKING (end of Phase 5A)**

**Portal:**

/portal/login/ — username + password, case-insensitive, is\_staff check

/portal/ — dashboard with pending approvals, booking stats, revenue, recent bookings

/portal/api/pending-count/ — JSON polling, 60s interval in sidebar

/portal/hotels/ — list, filters (search/status/location), DataTables

/portal/hotels/add/ — create with correct approval state per role

/portal/hotels/<pk>/ — detail with photo grid (upload/delete/reorder/cover), room type modals

/portal/hotels/<pk>/edit/ — edit with mini-admin warning for approved listings

/portal/hotels/pending/ — Super Admin pending queue

Hotel approve/reject/resubmit flows with Django messages

/portal/cars/ — same structure as hotels

/portal/tours/ — list, form, detail with itinerary day modals and photo grid

/portal/bookings/ — DataTables with CSV/Excel/PDF/Print, 10/page default, server-side filters

/portal/bookings/<pk>/ — detail with status update form, mark POA as paid

All Phase 5B sections render as stub pages (no errors)

Shared #confirmModal for all destructive actions

Mini-Admin scoped access: hotels/cars/bookings filtered by created\_by



**Public site (Phases 0–4):**

* Homepage, hotels, tours, cars — list and detail with booking flow
* Hotel/car/tour booking: Pay Now (stub) and Pay on Arrival end-to-end
* User dashboard: history, cancellations, favourites, profile, PDF download
* Email: POA confirmation, cancellation emails, verification emails



**PHASE 5B SCOPE — WHAT TO IMPLEMENT**

Phase 5B implements content management and supporting features. All URLs are already registered as stubs in apps/portal/urls.py — they render portal\_stub.html. Each stub just needs a real view replacing it.



**Build Phase 5B in this order:**

**1. Portal email tasks** — apps/portal/tasks.py

Replace the three stubs with full branded HTML email implementations. Follow the established email pattern exactly (green header, gold accents, inline CSS, <table> layout, plain text fallback, mobile responsive).

notify\_superadmin\_new\_listing(listing\_type, listing\_id)

* Recipient: settings.ADMIN\_NOTIFICATION\_EMAIL
* Subject: New \[Hotel/Car] listing pending review — \[listing name]
* Body: listing name, mini-admin name, link to /portal/hotels/<pk>/ or /portal/cars/<pk>/



send\_listing\_approved\_email(listing\_type, listing\_id)

* Recipient: listing.created\_by.email (the mini-admin)
* Subject: Your \[Hotel/Car] listing is now live — \[listing name]
* Body: listing name, confirmation it's live, link to portal



send\_listing\_rejected\_email(listing\_type, listing\_id)

* Recipient: listing.created\_by.email
* Subject: Your \[Hotel/Car] listing needs attention — \[listing name]
* Body: listing name, rejection reason, link to edit in portal



send\_miniadmin\_welcome\_email(user\_id) — new task for Phase 5B

* Recipient: the new mini-admin's email
* Subject: Welcome to Jadevine Staff Portal
* Body: their username, portal URL, password reset link (use Django's default\_token\_generator to generate), instructions



**2. Reviews moderation** — apps/portal/views/reviews.py

Use get\_accessible\_reviews(user) from mixins.py — Super Admin sees all, Mini-Admin sees only reviews for their own hotel and car listings. Mini-Admin cannot moderate tour reviews.



**URLs to implement (replace stubs):**

/portal/reviews/              → list: all pending reviews + recent (paginated)

/portal/reviews/<pk>/approve/ → POST: set status='approved', moderated\_by, moderated\_at

/portal/reviews/<pk>/reject/  → POST: requires rejection\_reason, set status='rejected'



**Template:** portal\_reviews\_list.html

* Table: reviewer name, service, rating (1–10), comment preview, submission date, status, actions
* Filter by status (pending/approved/rejected) and service type
* Pending count badge shown in sidebar — add pending\_reviews to context processor



**Rejection modal:** Same form { display: contents } pattern. Rejection reason required and stored in Review.rejection\_reason — shown to customer on their booking detail page.

**Super Admin dashboard update:** Add pending reviews count card alongside pending listings.



**3. Gallery management** — apps/portal/views/gallery.py

Super Admin only throughout (SuperAdminRequiredMixin).

**Models:** GalleryCategory, GalleryItem (already defined, already migrated)



**URLs to implement:**

/portal/gallery/                      → main page (categories + items)

/portal/gallery/upload/               → AJAX POST (photo file or video URL)

/portal/gallery/<pk>/delete/          → AJAX POST

/portal/gallery/<pk>/toggle-featured/ → AJAX POST (flips is\_featured)

/portal/gallery/reorder/              → AJAX POST (JSON order array)

/portal/gallery/categories/add/       → modal POST

/portal/gallery/categories/<pk>/edit/ → modal POST

/portal/gallery/categories/<pk>/delete/ → POST



**Template:** portal\_gallery.html

* Left: category list (tabs or sidebar within page)
* Right: item grid for selected category — drag-to-reorder (jQuery UI Sortable)
* Upload area: same AJAX pattern as hotel/car/tour photos for images; separate URL input for YouTube/Vimeo
* Featured toggle: AJAX, updates button state without reload
* Photo grid has no cover concept — just order and featured flag
* is\_featured=True items appear in homepage Gallery Highlights section



**4. User accounts management** — apps/portal/views/users.py

Super Admin only.

**URLs to implement:**

/portal/users/                  → searchable + filterable list

/portal/users/<pk>/             → profile detail + full booking history

/portal/users/<pk>/deactivate/  → POST: toggle is\_active

/portal/users/<pk>/reset-password/ → POST: trigger allauth password reset email



**Template:** portal\_users\_list.html, portal\_user\_detail.html

* List: name, email, registration date, booking count, active status, actions
* Detail: full profile, all bookings in a DataTable
* Password reset uses allauth's send\_email\_confirmation or default\_token\_generator — do not create a custom password reset flow



**5. Mini-Admin management** — apps/portal/views/miniadmins.py

Super Admin only.

**URLs to implement:**

/portal/mini-admins/                   → list all mini-admin accounts

/portal/mini-admins/add/               → create account form

/portal/mini-admins/<pk>/              → profile + listings + activity

/portal/mini-admins/<pk>/edit/         → edit account details

/portal/mini-admins/<pk>/deactivate/   → POST: toggle is\_active

/portal/mini-admins/<pk>/reset-password/ → POST: trigger password reset email



**Create mini-admin flow:**

\# In PortalMiniAdminCreateView.post():

user = CustomUser.objects.create\_user(

&#x20;   username=form.cleaned\_data\['username'].lower(),  # always stored lowercase

&#x20;   email=form.cleaned\_data\['email'],

&#x20;   first\_name=form.cleaned\_data\['first\_name'],

&#x20;   last\_name=form.cleaned\_data\['last\_name'],

&#x20;   is\_staff=True,

&#x20;   is\_active=True,

)

user.set\_unusable\_password()  # cannot log in until they set their own password

user.save()

MiniAdminProfile.objects.create(user=user, created\_by=request.user)

async\_task('apps.portal.tasks.send\_miniadmin\_welcome\_email', user.pk)



The welcome email contains a Django password reset link (generated via default\_token\_generator). The mini-admin clicks it, sets their own password, and can then log in. **Never send a plaintext password in email.**

**Template:** portal\_miniadmins\_list.html, portal\_miniadmin\_form.html



**6. Contact messages** — apps/portal/views/messages.py

Super Admin only.

**URLs to implement:**

/portal/messages/           → list, filterable by inquiry\_type and status

/portal/messages/<pk>/      → full message detail + reply form

/portal/messages/<pk>/reply/ → POST: sends reply email via Django-Q, saves in admin\_notes

/portal/messages/<pk>/status/ → POST: update status (new/in\_progress/resolved)



**Reply email task** (new in apps/portal/tasks.py):

def send\_contact\_reply\_email(message\_id, reply\_text):

&#x20;   # Branded HTML email to message.email

&#x20;   # Subject: Re: \[original subject]

&#x20;   # Body: reply\_text + original message quoted below



**Template:** portal\_messages\_list.html, portal\_message\_detail.html



**7. Newsletter** — apps/portal/views/newsletter.py

Super Admin only.

**URLs to implement:**

/portal/newsletter/             → subscriber list with DataTables (CSV/Excel/PDF/Print)

/portal/newsletter/<pk>/toggle/ → POST: toggle is\_active



**Template:** portal\_newsletter.html

* DataTables with export buttons (same pattern as bookings)
* Email, subscription date, active status, toggle action



**8. Cancellation policies** — apps/portal/views/policies.py

Super Admin only.

**URLs to implement:**

/portal/policies/               → list all tiers, grouped by service type

/portal/policies/add/           → modal POST: create new tier

/portal/policies/<pk>/edit/     → modal POST: edit tier

/portal/policies/<pk>/delete/   → POST with confirm modal



**Template:** portal\_policies.html

* Three sections: Hotel, Tour, Car — each showing active tiers
* Each tier: days\_before\_service, refund\_percentage, label\_en, is\_active toggle
* Important info notice on page: "Changes apply to new bookings only. Existing bookings retain the policy active at their creation time."



**9. Portal settings** — apps/portal/views/settings.py

Both roles (no SuperAdminRequiredMixin — just PortalRequiredMixin).

**URL to implement:**

/portal/settings/  → own username + password change



**Username change:** ModelForm on CustomUser, field username only. Validate uniqueness, save as .lower().

**Password change:** Django's built-in PasswordChangeForm. Call update\_session\_auth\_hash(request, user) after save to keep portal session alive — without this Django logs the user out on password change.

**Template:** portal\_settings.html



**10. About Us page (public site) — apps/core/**

The templates/core/about.html is currently a stub. Implement it as a static server-rendered page. View in apps/core/views.py, CSS in static/css/core/about.css, JS in static/js/core/about.js. No model required — static content with translations.



**STUB URLS STILL IN** apps/portal/urls.py

These URL names are registered and resolve (render portal\_stub.html) but have no real views yet. Replace each as Phase 5B is built:

portal:review\_list, portal:review\_approve, portal:review\_reject

portal:gallery, portal:gallery\_upload, portal:gallery\_delete,

portal:gallery\_toggle\_featured, portal:gallery\_reorder,

portal:gallery\_category\_add, portal:gallery\_category\_edit, portal:gallery\_category\_delete

portal:user\_list, portal:user\_detail, portal:user\_deactivate, portal:user\_reset\_password

portal:miniadmin\_list, portal:miniadmin\_add, portal:miniadmin\_detail,

portal:miniadmin\_edit, portal:miniadmin\_deactivate, portal:miniadmin\_reset\_password

portal:message\_list, portal:message\_detail, portal:message\_reply, portal:message\_status

portal:newsletter, portal:newsletter\_toggle

portal:policies, portal:policy\_add, portal:policy\_edit, portal:policy\_delete

portal:settings



**POST-LAUNCH ONLY (do not implement in any phase)**

Domestic flights (Amadeus API)

Expedia hotel API / Booking.com

Discover Cars API

TripAdvisor Content API (embeddable widget only at launch)

Google OAuth / Facebook OAuth for customers

Arabic (RTL), Dutch, Italian languages

Pay on Arrival deposit requirement

Automated PesaPal refund processing

SMS/WhatsApp automated notifications

Mobile app





*End of Handoff — Version 5.0 | May 2026*

*Prepared by Fidon for Jadevine Travel \& Tours*

*Supersedes versions 1.0, 1.1, 1.2, 2.0, 3.0, 4.0, 4.1, 4.2.*

