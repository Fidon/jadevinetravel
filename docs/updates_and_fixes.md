# JADEVINE TRAVEL & TOURS — FEATURE FIXES HANDOFF
**Version 1.1 | May 2026 | Post-Phase 5B Feature Additions**

---

## OVERVIEW

This document covers feature additions and fixes implemented after Phase 5B completion, across two dedicated conversations. All changes are incremental — no existing architecture was replaced.

---

## 1. GRANULAR GUEST / PASSENGER FIELDS ON BOOKINGS

### Models changed
**`apps/bookings/models.py`** — `Booking` model gains:
- `num_adults` (PositiveIntegerField, nullable)
- `num_children` (PositiveIntegerField, nullable) — ages 2–12
- `num_infants` (PositiveIntegerField, nullable) — under 2
- `num_pets` (PositiveIntegerField, nullable)
- `num_rooms` (PositiveIntegerField, nullable) — hotels only
- `num_guests` (PositiveIntegerField, nullable) — legacy aggregate field kept for backward compat; populated as `num_adults + num_children + num_infants` at creation
- `allows_pets` (BooleanField, default=False) — snapshotted from listing at booking time
- Property: `total_occupants` → `num_adults + num_children + num_infants`

**Old fields retained:** `num_participants` (tours), `num_days` (cars)

**`apps/hotels/models.py`** — `HotelRoomType` gains:
- `allows_pets` (BooleanField, default=False)
- `max_guests` label updated to "Max Guests Per Room"
- `cover_photo` property added: returns first `room_photos` by order

**`apps/cars/models.py`** — `CarRental` gains:
- `allows_pets` (BooleanField, default=False)

**`apps/tours/models.py`** — `TourPackage` gains:
- `allows_pets` (BooleanField, default=False)

### New model
**`apps/hotels/models.py`** — `HotelRoomTypePhoto`:
- `room_type` FK → HotelRoomType (related_name='room_photos')
- `image` (ImageField, upload_to='hotels/room_photos/')
- `caption`, `order`
- No `is_cover` — cover is first photo by order (same pattern as TourPhoto)

### Price formula change — Hotels
```
total_price = price_per_night × nights × num_rooms
```
Previously: `price_per_night × nights`

### Guest capacity validation — Hotels
```
max_occupants = room_type.max_guests × num_rooms
total_occupants = num_adults + num_children + num_infants
assert total_occupants <= max_occupants
```

### Pets enforcement
Server-side in `HotelBookingView`, `CarBookingView`, `TourBookingView`:
- If `num_pets > 0` and `listing.allows_pets == False` → reject with error message
- UI toggle alone is not sufficient — always enforce server-side

### Forms changed
**`apps/bookings/forms.py`** — all three booking forms updated:
- `HotelBookingForm`: replaces `num_guests` with `num_adults`, `num_children`, `num_infants`, `num_pets`, adds `num_rooms`
- `CarBookingForm`: replaces single count with `num_adults`, `num_children`, `num_infants`, `num_pets`
- `TourBookingForm`: replaces `num_participants` with `num_adults`, `num_children`, `num_infants`, `num_pets`; `num_participants = num_adults + num_children` (infants free)
- All optional guest fields normalise to 0 when omitted in `clean()`

### Portal forms changed
**`apps/portal/forms.py`** — `HotelRoomTypeForm`, `CarRentalForm`, `TourPackageForm` each gain `allows_pets` in `fields`, `widgets`, and `labels`.

**`templates/portal/includes/room_type_form_fields.html`** — adds `allows_pets` checkbox.

### Session data keys added
Hotel bookings: `num_rooms`, `num_adults`, `num_children`, `num_infants`, `num_pets`, `num_guests`
Car bookings: `num_adults`, `num_children`, `num_infants`, `num_pets`
Tour bookings: `num_adults`, `num_children`, `num_infants`, `num_pets`, `num_participants`

### Migrations
```
bookings: add_granular_guest_fields
hotels:   add_hotel_room_type_photo
hotels:   add_allows_pets_room_type
cars:     add_allows_pets_car
tours:    add_allows_pets_tour
```

---

## 2. ROOM TYPE PHOTOS — PORTAL MANAGEMENT

### New AJAX endpoints in `apps/portal/views/hotels.py`
| View | URL | Method |
|------|-----|--------|
| `PortalRoomTypePhotoUploadView` | `/portal/hotels/<hpk>/rooms/<rpk>/photos/upload/` | POST |
| `PortalRoomTypePhotoDeleteView` | `/portal/hotels/<hpk>/rooms/<rpk>/photos/<pk>/delete/` | POST |
| `PortalRoomTypePhotoReorderView` | `/portal/hotels/<hpk>/rooms/<rpk>/photos/reorder/` | POST |

Same upload/delete/reorder JSON contract as `PortalHotelPhotoUploadView`. No `is_cover` concept.

### URLs added to `apps/portal/urls.py`
```python
path('hotels/<int:hpk>/rooms/<int:rpk>/photos/upload/',          PortalRoomTypePhotoUploadView.as_view(),  name='room_photo_upload'),
path('hotels/<int:hpk>/rooms/<int:rpk>/photos/<int:pk>/delete/', PortalRoomTypePhotoDeleteView.as_view(),  name='room_photo_delete'),
path('hotels/<int:hpk>/rooms/<int:rpk>/photos/reorder/',         PortalRoomTypePhotoReorderView.as_view(), name='room_photo_reorder'),
```

### Portal hotel detail template
`templates/portal/portal_hotel_detail.html` — each room type item now has:
- A photo panel (`#room-photo-panel-<rt.pk>`) — hidden by default
- A toggle button (`.js-toggle-room-photos`) with a photo count badge
- Upload area + sortable photo grid inside the panel

### Portal JS — `static/js/portal/portal_hotels.js`
New sections:
- `.js-toggle-room-photos` click — slides panel open/closed (one open at a time)
- `uploadRoomFiles(roomId, files)` — sequential AJAX upload
- `.js-delete-room-photo` click — uses shared `#confirmModal` + `portal:photo-delete-confirmed` event
- `initRoomSortable(roomId)` — jQuery UI Sortable per room grid
- `updateRoomPhotoBadge(roomId)` — updates count badge after upload/delete

`portal:photo-delete-confirmed` event handler now distinguishes between hotel-level (`_pendingHotelPhotoDelete`) and room-level (`_pendingRoomPhotoDelete`) deletions.

### `window.HOTEL_URLS` additions (in portal_hotel_detail.html)
```javascript
window.HOTEL_URLS = {
  // existing hotel photo URLs...
  roomPhotoUpload:  '/portal/hotels/<pk>/rooms/__RID__/photos/upload/',
  roomPhotoDelete:  '/portal/hotels/<pk>/rooms/__RID__/photos/__ID__/delete/',
  roomPhotoReorder: '/portal/hotels/<pk>/rooms/__RID__/photos/reorder/',
};
```

### `room_types_json` additions
`PortalHotelDetailView.get()` serializes `allows_pets` and `photos` (array of `{id, url, caption}`) into `window.HOTEL_ROOM_TYPES`. JS edit modal populates `allows_pets` checkbox.

### Public hotel detail — inline room photo strip
`templates/hotels/hotel_detail.html` — each `.room-type-card` has a `.room-photo-strip` div below it (hidden by default). Clicking a room card slides the strip open and reinitialises GLightbox to include the newly visible photo links.

`apps/hotels/views.py` `HotelDetailView.get_context_data()` — room type JSON now includes:
```python
'photos': [{'url': p.image.url, 'caption': p.caption or ''} for p in rt.room_photos.all()]
```
Queryset uses `.prefetch_related('room_photos')`.

`static/js/hotels/hotel_detail.js` — on room card click, shows `#room-strip-<id>`, calls `initLightbox()` to reinitialise GLightbox.

---

## 3. FAVOURITE / SAVE BUTTONS

### Toggle endpoint
**`apps/core/views.py`** — `FavouriteToggleView`:
- URL: `/favourites/toggle/` (POST only)
- Body: `item_type=hotel|tour|car`, `item_id=<int>`
- Returns `{"saved": true|false}` on success
- Returns `{"requires_login": true}` (HTTP 401) for unauthenticated users
- Enforces that the item is publicly visible before toggling

**`apps/core/urls.py`** — adds:
```python
path('favourites/toggle/', views.FavouriteToggleView.as_view(), name='favourite_toggle'),
```

### Shared JS module
**`static/js/core/favourites.js`** — exposes `window.JD_FAV`:
- `JD_FAV.buildCardBtn(itemType, itemId, isSaved)` → HTML string for card overlay button
- `JD_FAV.buildDetailBtn(itemType, itemId, isSaved, toggleUrl)` → HTML string for detail page pill button
- `JD_FAV.applyState($btn, saved)` → updates icon, class, label in place
- Delegated click handler on `.jd-fav-btn` — handles optimistic UI, AJAX toggle, error revert, login redirect

**Load order requirement:** `favourites.js` MUST load before any list JS file that calls `JD_FAV.buildCardBtn()`.

### Card button design
- `.jd-fav-btn` — absolute positioned, `bottom:12px; right:12px` (via `.hotel-card .jd-fav-btn`, `.tour-card .jd-fav-btn`, `.car-card .jd-fav-btn` overrides in `main.css`)
- Frosted white circle, 36×36px, heart icon
- Filled red heart (`jd-fav-btn--saved`) when saved

### Detail page button design
- `.jd-fav-btn--detail` — pill button, `position:static`, placed in `.jd-fav-detail-wrap` div below the listing header divider
- Shows flag + label "Save" / "Saved"
- Present on `hotel_detail.html`, `tour_detail.html`, `car_detail.html`

### Backend `is_saved` in AJAX responses
All three list views pass `is_saved: bool` and `item_type: str` per item in the AJAX JSON:
- `HotelListView._ajax_filter()` — single query: `SavedFavourite.objects.filter(user=request.user, hotel__in=qs).values_list('hotel_id', flat=True)`
- `CarListView._ajax_filter()` — same pattern with `car__in`
- `TourListView.get()` — same pattern with `tour_package__in`
- All return empty set for anonymous users (no query)

### `is_saved` in detail view contexts
`HotelDetailView`, `CarDetailView`, `TourDetailView` each pass:
```python
context['is_saved'] = (
    request.user.is_authenticated and
    SavedFavourite.objects.filter(user=request.user, hotel=hotel).exists()
)
context['favourite_toggle_url'] = '/favourites/toggle/'
```

### Required `JD_STRINGS` keys
```javascript
window.JD_STRINGS.saveToFavourites      = "Save";
window.JD_STRINGS.savedToFavourites     = "Saved";
window.JD_STRINGS.addedToFavourites     = "Added to favourites";
window.JD_STRINGS.removedFromFavourites = "Removed from favourites";
window.JD_STRINGS.favouriteError        = "Could not update favourites. Try again.";
```
Must be set in every list template's `{% block extra_js %}` BEFORE `favourites.js` loads.

---

## 4. SEARCH ON LISTING PAGES

### Backend — `q` parameter support
**`apps/hotels/views.py`** `_ajax_filter()`:
```python
search_q = request.GET.get('q', '').strip()
if search_q:
    qs = qs.filter(name__icontains=search_q)
```

**`apps/cars/views.py`** `_ajax_filter()`:
```python
search_q = request.GET.get('q', '').strip()
if search_q:
    qs = qs.filter(name__icontains=search_q)
```

**`apps/tours/views.py`** `TourListView.get()`:
```python
search_q = request.GET.get('q', '').strip()
if search_q:
    qs = qs.filter(name_en__icontains=search_q)
```
Note: tours filter on `name_en` only (multilingual names not searched).

### Frontend — search bar HTML
All three list templates (`hotel_list.html`, `tour_list.html`, `car_list.html`) — above the filter dropdowns row:
```html
<div class="listing-search-wrap">
  <div class="listing-search-input-wrap">
    <i class="bi bi-search listing-search-icon"></i>
    <input type="text" id="search-input" class="jd-input listing-search-input"
           placeholder="Search ... by name..." autocomplete="off">
    <button type="button" class="listing-search-clear" id="btn-search-clear"
            style="display:none;">
      <i class="bi bi-x-lg"></i>
    </button>
  </div>
</div>
```

### Frontend — JS wiring (all three list JS files)
- `q: $("#search-input").val().trim()` added to AJAX params
- `$("#search-input").on("input", onFilterChange)` — live search with 300ms debounce
- `#btn-search-clear` shown/hidden based on input value; click clears + re-fetches
- `clearFilters()` also clears `#search-input` and hides `#btn-search-clear`
- URL param `q` pre-fills the search input on page load (enables homepage widget → listing page with text search)

### CSS
`.listing-search-wrap`, `.listing-search-input-wrap`, `.listing-search-icon`, `.listing-search-input`, `.listing-search-clear` — added to `static/css/main.css`. Full-width at all screen sizes.

### Homepage search widget
No backend changes. `home.js` already builds URL params and redirects to listing pages. Listing page JS reads `?q=` from URL params on load and pre-fills the search input.

---

## 5. LANGUAGE SWITCHER REDESIGN

### Design
Floating pill fixed `bottom:28px; left:28px` — above WhatsApp button. Shows current language flag image + code (e.g. 🇬🇧 EN). Click opens a dropdown above the pill listing all languages with flag + full name. Clicking a language submits the `/i18n/setlang/` Django form (same mechanism as before).

### Flag images
Uses `flagcdn.com/w40/<code>.png` via CSS `background-image`. No library required.
```css
.jd-float-lang-flag[data-flag="en"] { background-image: url('https://flagcdn.com/w40/gb.png'); }
.jd-float-lang-flag[data-flag="fr"] { background-image: url('https://flagcdn.com/w40/fr.png'); }
.jd-float-lang-flag[data-flag="ru"] { background-image: url('https://flagcdn.com/w40/ru.png'); }
```
Flag spans use `data-flag="en|fr|ru"` attribute — NOT emoji.

### Template changes — `templates/base.html`
- Removed: `jd-lang-btn` + `jd-lang-separator` from desktop navbar and mobile menu
- Added: `#jd-float-lang` floating widget just before `jd-whatsapp-btn`
- Mobile menu: `jd-mobile-menu-lang` now uses `.jd-lang-option` buttons (full-width pills) with flag images instead of text-only buttons

### JS changes — `static/js/main.js`
Old section 6 (`.jd-lang-btn` click handler) replaced with:
- `submitLang(lang)` — shared function that builds and submits the i18n form
- `#jd-float-lang-pill` click — toggles `.open` class on `#jd-float-lang`
- `.jd-float-lang-item` click — calls `submitLang()`
- Click outside / ESC — closes dropdown
- `.jd-lang-option` click (mobile menu) — calls `submitLang()`

Also added: longest-match algorithm for nav active state (replaces `startsWith` prefix match that caused false multi-activation).

### CSS additions — `static/css/main.css`
Classes: `.jd-float-lang`, `.jd-float-lang-pill`, `.jd-float-lang-dropdown`, `.jd-float-lang-item`, `.jd-float-lang-flag`, `.jd-float-lang-code`, `.jd-float-lang-chevron`, `.jd-float-lang-name`, `.jd-lang-option`

`.jd-lang-separator` and `.jd-lang-btn` set to `display:none` (kept for safety, no longer in markup).

---

## 6. CARD BADGE LAYOUT — ALL THREE LISTING PAGES

Consistent badge layout across hotels, tours, and cars list cards:
| Position | Content |
|---|---|
| Top-left | Hotel: location badge (`.hotel-card-location-badge`). Tours: type badge (`.tour-card-type-badge`). Cars: type badge (`.car-card-type-badge-img`) |
| Top-right | Discount badge (`.jd-discount-badge`) — only when `has_discount` |
| Bottom-right | Favourite heart button (`.jd-fav-btn`) |

### Car type badge on image
New class `.car-card-type-badge-img` (frosted white pill) used for the image overlay — distinct from `.car-card-type-badge` used in the card body specs row.

### Tour type badge
`.tour-card-type-badge` CSS updated: removed coloured variant backgrounds (`rgba(26,77,46,0.85)` etc.), now uses frosted white pill (`rgba(255,255,255,0.92)`) matching hotel location badge style.

### Tour card img-wrap overflow
`.tour-card-img-wrap` changed from `overflow: hidden` to `overflow: visible` to prevent heart button clipping. The `<a>` tag inside gets `overflow: hidden; border-radius: var(--radius-lg) var(--radius-lg) 0 0` to maintain image masking.

### Featured badge removed
`is_featured` badge removed from tour list cards entirely. `is_featured` field and homepage display unchanged.

---

## 7. HOMEPAGE FEATURED PACKAGES — DISCOUNT BADGE

In `templates/core/home.html` inside the featured packages loop, the price tag now shows:
- Discount badge (`jd-discount-badge`) top-right of card image when `package.has_active_discount`
- Strikethrough original price + discounted price when active
- "From $X" label when no discount

Uses `package.has_active_discount` and `package.get_display_price` from `TourPackage` model methods.

---

## 8. NEWSLETTER UNSUBSCRIBE IN CUSTOMER DASHBOARD

### Summary
Logged-in customers can subscribe or unsubscribe from the newsletter directly from their profile page. No model changes — the link between a user and a `NewsletterSubscriber` record is their email address.

### Backend changes

**`apps/accounts/urls.py`**
Added:
```python
path('profile/newsletter-toggle/', views.NewsletterToggleView.as_view(), name='newsletter_toggle'),
```

**`apps/accounts/views.py`**
- Import added: `from apps.contact.models import NewsletterSubscriber`
- `ProfileView.get()` and `ProfileView.post()` — both now pass `newsletter_subscribed: bool` into context. Resolved via `NewsletterSubscriber.objects.filter(email__iexact=request.user.email).first()`.
- New view `NewsletterToggleView` (AJAX POST, `LoginRequiredMixin`):
  - Calls `get_or_create` on `NewsletterSubscriber` by `email__iexact=request.user.email`
  - If created (record didn't exist), sets `is_active=True` immediately
  - If existing, toggles `is_active`
  - Returns `{"subscribed": true|false}`

### Frontend changes

**`templates/accounts/profile.html`**
Added a "Newsletter" card in the `col-lg-4` right column, below the Security card:
- Shows current subscription state with icon (`bi-check-circle-fill` / `bi-x-circle-fill`)
- Toggle button swaps between `btn-primary-jd` (Subscribe) and `btn-outline-jd` (Unsubscribe)
- `data-subscribed` attribute drives initial JS state
- `#newsletterFeedback` div for inline confirmation text

**`templates/accounts/dashboard_base.html`**
- Added to `window.JD_URLS`: `newsletterToggle`
- Added to `window.JD_STRINGS`: `subscribe`, `unsubscribe`, `subscribed`, `notSubscribed`, `newsletterSubscribedMsg`, `newsletterUnsubscribedMsg`, `genericError`

**`static/js/accounts/profile.js`**
Added newsletter toggle handler:
- AJAX POST to `window.JD_URLS.newsletterToggle`
- On success: swaps button class/label and status label text from `JD_STRINGS`
- On error: shows `JD_STRINGS.genericError` in `#newsletterFeedback`
- Button disabled during request to prevent double-submit

### Edge case
`get_or_create` uses `email__iexact` as the lookup (catches case variants already in the DB). On create, `defaults` sets `email=request.user.email` and `is_active=False`, then the view immediately flips `is_active=True`. Do not switch the lookup to `email=` exact — case variants would create duplicates.

---

## 9. SUPER ADMIN LISTING EDIT — MINI-ADMIN EMAIL NOTIFICATION

### Summary
When a Super Admin edits a hotel or car listing that belongs to a mini-admin, the mini-admin now receives a branded HTML email notifying them of the change. Does not fire when a mini-admin edits their own listing (that path already triggers the approval-reset flow).

### Trigger condition
Both edit views check, inside the `else` branch of `was_reset` (i.e. a clean save, not an approval reset):
```python
if (
    not is_mini_admin(request.user)
    and listing.created_by
    and hasattr(listing.created_by, 'miniadminprofile')
):
    async_task(
        'apps.portal.tasks.send_listing_edited_by_admin_email',
        'hotel'|'car', listing.pk, request.user.pk,
    )
```
Placed inside `else` to be mutually exclusive with the approval-reset notification path.

### Backend changes

**`apps/portal/views/hotels.py`** — `PortalHotelEditView.post()`
Added async task dispatch in the `else` branch (clean save by Super Admin).

**`apps/portal/views/cars.py`** — `PortalCarEditView.post()`
Same change as hotels.

**`apps/portal/tasks.py`** — new task `send_listing_edited_by_admin_email(listing_type, listing_id, edited_by_id)`:
- Fetches listing via `_get_listing()` (existing helper)
- Guards: returns early if `listing.created_by` is None or has no `miniadminprofile`
- Fetches editor `CustomUser` by `edited_by_id`
- Sends branded HTML email to mini-admin with listing name, editor name, timestamp, and portal link button
- Uses all existing shared chrome: `_email_header()`, `_email_footer()`, `_detail_row()`, `_portal_button()`, `_section_title()`

### Email content
Subject: `Your {label} listing has been updated — {listing_name}`
Body conveys: listing is still live, who made the change, date/time (UTC), link to review in portal.

---

## 10. MOBILE MENU — REGISTER LINK + LANGUAGE BLOCK REMOVED

### Summary
On small screens the mobile nav menu was missing the Register link and showing redundant language switcher buttons (duplicating the floating pill already present on all screen sizes).

### Changes — `templates/base.html` only

**Inside `.jd-mobile-menu-links`:**
- Added `Sign Out` link for authenticated users (was missing entirely)
- Added `Register` link for unauthenticated users, after Sign In

Before:
```html
{% if user.is_authenticated %}
  <a ... >Dashboard</a>
{% else %}
  <a ... >Sign In</a>
{% endif %}
```

After:
```html
{% if user.is_authenticated %}
  <a ... >Dashboard</a>
  <a ... >Sign Out</a>
{% else %}
  <a ... >Sign In</a>
  <a ... >Register</a>
{% endif %}
```

**`jd-mobile-menu-lang` block removed entirely** — the floating language switcher (`#jd-float-lang`) handles language switching on all screen sizes including mobile. The inline language block in the mobile menu was redundant.

### CSS housekeeping — `static/css/main.css` (optional)
The following blocks are now dead CSS and can be removed:
- `.jd-mobile-menu-lang` (first occurrence — old `margin-top: 28px` version)
- `.jd-mobile-menu-lang` (second occurrence — `flex-direction: column` version inside floating lang switcher section)
- `.jd-lang-option` and its variants (`.jd-lang-option:hover`, `.jd-lang-option.active`)

Leaving them in place has no functional impact.

---

## ESTABLISHED PATTERNS (additions to project-wide patterns)

### Guest counter UI
`.guests-breakdown` container with `.guest-row` items — each row has a label column and a `.guest-counter-sm` column. Used on hotel, tour, car detail booking forms. CSS in `static/css/hotels/hotel_detail.css`, `tours/tour_detail.css`, `cars/car_detail.css` (identical rules — consider extracting to `main.css` in future).

### Room photo strip (public site)
No `is_cover` on room type photos. Cover shown to customer = first photo by `order`. Strip hidden by default, revealed on room card click. GLightbox reinitialised after reveal via `initLightbox()`.

### Favourite button — card vs detail
Two variants from `JD_FAV`:
- Card: `buildCardBtn()` — absolute positioned circle, no label
- Detail: `buildDetailBtn()` — static pill with label, placed in `.jd-fav-detail-wrap`

Both use the same delegated click handler on `.jd-fav-btn`. Never attach separate click handlers.

### `favourites.js` load order
Must be loaded **before** any list JS file in every listing template's `{% block extra_js %}`. Failure to do so results in `typeof JD_FAV !== "undefined"` being false and silent empty buttons.

### Search `q` parameter
Sent in all three listing AJAX calls. Backend filters: hotels → `name__icontains`, cars → `name__icontains`, tours → `name_en__icontains`. URL param `?q=` pre-fills the search input on page load.

### Flag images
Use `data-flag="en|fr|ru"` attribute on `.jd-float-lang-flag` spans. CSS applies `background-image` from `flagcdn.com`. Never use emoji for flags — rendering varies by OS.

### Newsletter toggle — email-based user lookup
`NewsletterSubscriber` has no FK to `CustomUser`. Always look up by `email__iexact=request.user.email`. Using exact `email=` match risks missing case-variant records already in the DB and creating duplicates.

### Super Admin listing edit notification
Fires only when `not is_mini_admin(request.user)` AND `hasattr(listing.created_by, 'miniadminprofile')`. Placed inside the `else` branch of `was_reset` to be mutually exclusive with the approval-reset notification. Never attach to the `was_reset=True` path.

---

*End of Feature Fixes Handoff — Version 1.1 | May 2026*
*Prepared by Fidon for Jadevine Travel & Tours*
*Covers post-Phase 5B feature additions implemented across two dedicated conversations.*
