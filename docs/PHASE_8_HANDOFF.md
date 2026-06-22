# Jadevine Travel & Tours — Phase 8 Handoff
**i18n Completion · SEO Infrastructure · GA4 / Search Console · Accessibility QA**

*June 2026 — Fidon / Jadevine Travel & Tours*
*Source of truth for Phase 9 (AWS S3 media) — read this before starting.*

---

## Overview

Phase 8 closes out the public-site readiness work: a full SEO foundation built from scratch, analytics/Search-Console provisioning, the French + Russian translation catalogues brought to 100 %, and a multi-stage accessibility audit across every public page.

| # | Work stream | Surface area | Status |
|---|-------------|--------------|--------|
| 1 | SEO infrastructure | `apps/core/*`, `base.html`, listing views + detail templates, settings | **Complete & verified** (Rich Results, robots, sitemap) |
| 2 | GA4 + Google Search Console | settings, DNS | **Complete** (sitemap submission deferred to post-deploy) |
| 3 | i18n completion (fr / ru) | `locale/fr`, `locale/ru` | **Complete** — 100 % translated, 0 fuzzy |
| 4 | Accessibility / alt-text QA | list, detail, home, gallery, contact templates + their JS | **Complete** |
| 4b | Detail-page JS i18n leak fix | `*_detail.js` + detail templates | **Complete** |

Nothing in Phase 8 touched models, migrations, the booking pipeline, the portal, or payments. It is deployable as a unit.

---
---

# PART 1 — SEO INFRASTRUCTURE

Built clean this phase (no prior SEO existed despite stale notes suggesting otherwise).

## Files

| File | Role |
|------|------|
| `apps/core/seo.py` *(new)* | Helpers: `get_site_url()`, `absolute_url()`, `is_public_i18n_path()`, `clean_text()`, `breadcrumb_schema()`, `jsonld_safe()` (escapes `<>&` to `\uXXXX` for safe inline `<script type="application/ld+json">`). `NON_PUBLIC_PREFIXES` drives `noindex`. |
| `apps/core/context_processors.py` *(new)* | `seo()` → `{site_url, canonical_url, hreflang_alternates (+x-default), robots_index, og_locale}` plus `GA4_MEASUREMENT_ID`, `GSC_VERIFICATION`. OG locale map en→en_US / fr→fr_FR / ru→ru_RU. |
| `apps/core/sitemaps.py` *(new)* | `StaticViewSitemap` (home 1.0, rest 0.7) + `Hotel/Tour/CarSitemap` (0.9, `lastmod=updated_at`). All `i18n=True`, `alternates=True`, `x_default=True`, `protocol='https'`. `location()` uses `reverse()` — **required** for i18n alternates to emit. |
| `templates/robots.txt` *(new)* | Disallows `/portal/ /admin/ /accounts/ /book/ /reviews/ /favourites/ /i18n/`. **No** `Disallow: /*?` — query pages are handled by `meta noindex`, not robots (the two are mutually exclusive; robots-blocked URLs can't have their noindex read). |
| `templates/base.html` *(rewrite)* | Canonical, hreflang + x-default, OG/Twitter, GA4 gtag (gated on ID), GSC meta, site-wide `TravelAgency` + `WebSite` JSON-LD, `{% block structured_data %}`. |
| `config/urls.py` | `sitemap.xml` + `robots.txt` registered at root, **outside** `i18n_patterns`. Favicon `/favicon.ico` → `RedirectView` (302, hardcoded path) also outside i18n_patterns. |
| `apps/{hotels,cars,tours}/views.py` | Per-listing SEO context (`seo_title`, `seo_description`, `seo_image`, `structured_data`) + **AJAX card-URL fix** (see Learnings). |
| `templates/{hotels,cars,tours}/*_detail.html` | `{% block title %}` / `{% block meta_description %}` removed (view is single source); `{% block structured_data %}` added. |
| `config/settings/base.py` | Registered `apps.core.context_processors.seo`; `DEFAULT_SITE_URL` / `SITE_URL` env split (SITE_URL inherits the ngrok DEFAULT_SITE_URL in dev so PesaPal IPN is unaffected); `GA4_MEASUREMENT_ID` / `GSC_VERIFICATION` env defaults `''`. |
| `config/settings/production.py` | `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` before HSTS — Nginx must send `proxy_set_header X-Forwarded-Proto $scheme;` for canonical URLs to resolve as `https`. |

## Schema types (must match Google Business Profile exactly)

- Hotel detail → `Hotel` schema; Tours & Cars → `Product` + `Offer` (USD). `aggregateRating` emitted only when `review_count ≥ 1`. `BreadcrumbList` on all three.
- Organization `PostalAddress` (NAP): streetAddress "Welezo Street, Amani", addressLocality "Stone Town", addressRegion "Zanzibar Urban/West", postalCode "11000", addressCountry "TZ"; geo lat **-6.1631323** lng **39.2273077**; telephone **+255683956372**; `sameAs` = [instagram, facebook, tripadvisor] (not WhatsApp).

## Verified
- robots.txt + sitemap.xml render correctly; all 7 static pages × en/fr/ru with `xhtml:link` hreflang alternates + x-default confirmed in view-source.
- Rich Results Test on a hotel detail page: 5 valid items, 0 errors.
- **Still to validate:** one tour + one car detail page (Product/Offer) in Rich Results Test.

---
---

# PART 2 — GA4 + GOOGLE SEARCH CONSOLE

- **GA4 Measurement ID `G-708XM26EPW`** → set as `GA4_MEASUREMENT_ID` in **production `.env` only** (leave empty in dev — no GA4 sandbox; the gtag block is gated on a non-empty ID). Property: "Jadevine Travel & Tours", Tanzania timezone, USD.
- **GSC**: domain property **verified via DNS TXT in DigitalOcean** — keep that TXT record permanently.
- **Deferred to post-deploy (Phase 10):** submit `sitemap.xml` in GSC once live.
- **Flagged post-launch:** EEA/GDPR cookie-consent gating for GA4.

---
---

# PART 3 — i18n COMPLETION (fr / ru)

Both `fr` and `ru` `django.po` / `.mo` are 100 % translated, 0 untranslated, 0 fuzzy, no venv/portal pollution. Place at `locale/{fr,ru}/LC_MESSAGES/` and restart.

### The canonical makemessages command (use this every time)
```
python manage.py makemessages -l fr -l ru --ignore="venv/*" --ignore="staticfiles/*" --ignore="apps/portal/*" --ignore="templates/portal/*" --no-obsolete
```

### Behaviours confirmed this phase (so they don't surprise the next session)
- **makemessages is incremental.** Re-running preserves every existing `msgstr`; it only adds new empty msgids and (with `--no-obsolete`) drops dead ones. You never re-translate the catalogue.
- **Fuzzy pre-fills.** When a new msgid resembles an existing one, gettext copies the old translation across and flags it `#, fuzzy`. **Fuzzy entries are skipped by `compilemessages`** — they fall back to English at runtime. You must verify the text and delete both the `#, fuzzy` line and the `#| msgid "…"` line.
- **Multi-line msgids** (gettext word-wrap) concatenate the quoted segments — mind the trailing space at each break. The `msgstr` does **not** need to mirror the wrapping; put the whole translation on one line. Keep `{placeholders}` exact — `#, python-brace-format` makes `compilemessages` validate them.
- Harmless warnings to ignore: `requirements.txt` UnicodeDecodeError (skipped, no effect). Real-but-minor: `login.html:67` has an email inside a translatable string — pull it out of the `{% trans %}` eventually.

---
---

# PART 4 — ACCESSIBILITY / ALT-TEXT QA

A WCAG-oriented pass over every public page. **`about.html` / `about.js` audited clean — no changes.**

## Stage 1 — list pages + global
- `static/js/{hotels,cars}/*_list.js`: HTML-escaping on injected card markup (was XSS-exposed), alt-safe images, star rating `role="img"` + `aria-label`, decorative `<i>` `aria-hidden`. `tour_list.js` already safe.
- `static/js/core/favourites.js`: **`aria-pressed`** added to both button builders and synced in `applyState()`; heart icon `aria-hidden`. Fixes the favourite toggle on list cards **and** detail pages in one file.
- List templates (`hotel/car/tour_list.html`): `aria-label` on search input, `for=` on filter labels, visually-hidden `<h2>` before each grid.

## Stage 2 — detail pages
- Counter `+/−` buttons (rooms/adults/children/infants/pets) were icon-only with **no accessible name** (WCAG fail) → `aria-label` (Decrease/Increase) + `aria-hidden` icons.
- Readonly counter inputs were unlabelled → `aria-label` reusing existing field strings.
- Detail favourite button is server-rendered → added `aria-pressed` on initial render.
- **Hotel only:** map iframe `title`; header stars `role="img"` + `aria-label`; duplicate panel stars `aria-hidden`; `Choose Your <em>Room</em>` switched `{% trans %}` → `{% blocktrans %}` (the `<em>` was rendering as literal text under autoescape).
- Breadcrumb nav `aria-label` made translatable on hotel/car (tour already was).

## Stage 2b — home / gallery / contact
- **contact:** validated fields associated to error regions via `aria-describedby`; error `<div>`s `role="alert"`; `contact.js` toggles `aria-invalid`; inquiry tabs `aria-pressed`; char count `aria-live="polite"`.
- **gallery:** photo/video links given accessible names (caption → fallback "View photo"/"Play video"); decorative zoom/play/star icons `aria-hidden`.
- **home:** gallery tiles were click-only `<div>`s (keyboard-unreachable) → `role="button" tabindex="0"` + Enter/Space handler in `home.js`; injected modal close button + image alt fixed; booking-widget selects + newsletter input `aria-label`led (reusing visible-label strings); disabled Flights tab `aria-disabled`.

## Stage 4b — detail-page JS i18n leak (fixed alongside)
`*_detail.js` were hardcoding user-facing English (validation toasts, "night/nights", "room/rooms", the guest-capacity note, the occupancy error). All now route through `window.JD_STRINGS`, with the new keys declared in each detail template's `<script>` block.

---
---

# NEW TRANSLATABLE STRINGS INTRODUCED THIS PHASE

After placing the Phase 8 files, re-run makemessages, de-fuzz, fill, `compilemessages`. (Booking-widget `aria-label`s reuse existing msgids, so they're not listed.)

| msgid | fr | ru |
|---|---|---|
| `star rating` | étoiles | звёзд |
| `Search results` | Résultats de recherche | Результаты поиска |
| `Toggle menu` | Afficher/masquer le menu | Открыть меню |
| `Chat on WhatsApp` | Discuter sur WhatsApp | Написать в WhatsApp |
| `Decrease` | Diminuer | Уменьшить |
| `Increase` | Augmenter | Увеличить |
| `Map showing hotel location` | Carte indiquant l'emplacement de l'hôtel | Карта расположения отеля |
| `Please select a pickup location` | Veuillez sélectionner un lieu de prise en charge | Пожалуйста, выберите место получения |
| `Please select a pickup date` | Veuillez sélectionner une date de prise en charge | Пожалуйста, выберите дату получения |
| `Please select a return date` | Veuillez sélectionner une date de retour | Пожалуйста, выберите дату возврата |
| `Licence number is required for self-drive` | Le numéro de permis est requis pour la conduite sans chauffeur | Для аренды без водителя требуется номер водительского удостоверения |
| `day (transfer)` | jour (transfert) | день (трансфер) |
| `days` | jours | дней |
| `Please select a check-in date` | Veuillez sélectionner une date d'arrivée | Пожалуйста, выберите дату заезда |
| `Please select a check-out date` | Veuillez sélectionner une date de départ | Пожалуйста, выберите дату выезда |
| `Please select a room type` | Veuillez sélectionner un type de chambre | Пожалуйста, выберите тип номера |
| `night` | nuit | ночь |
| `nights` | nuits | ночей |
| `room` | chambre | номер |
| `rooms` | chambres | номеров |
| `Max {max} adults/children per room × {rooms} {roomWord} = {total} total. Infants & pets excluded.` | Max {max} adultes/enfants par chambre × {rooms} {roomWord} = {total} au total. Nourrissons et animaux exclus. | Макс. {max} взрослых/детей на номер × {rooms} {roomWord} = {total} всего. Младенцы и питомцы не учитываются. |
| `Max {max} adults/children for {rooms} room(s). Infants and pets are not counted.` | Max {max} adultes/enfants pour {rooms} chambre(s). Les nourrissons et animaux ne sont pas comptés. | Макс. {max} взрослых/детей на {rooms} номер(ов). Младенцы и питомцы не учитываются. |
| `Please select a preferred start date.` | Veuillez sélectionner une date de début préférée. | Пожалуйста, выберите предпочтительную дату начала. |
| `View photo` | Voir la photo | Посмотреть фото |
| `Play video` | Lire la vidéo | Воспроизвести видео |
| `Close` | Fermer | Закрыть |

> Note: `days` may already exist (tour cards). The `{roomWord}` placeholder carries a 2-form plural, so Russian's 3-form grammar is approximate there — acceptable for a helper note.

---
---

# KEY LEARNINGS (consolidated)

- **Canonical/hreflang are built from `settings.SITE_URL`, never the request host** — prevents ngrok/preview hosts from poisoning canonical tags.
- **Sitemap i18n alternates require `reverse()` in `location()`** — hardcoded paths silently drop the `xhtml:link` alternates.
- **robots `Disallow` and meta `noindex` are mutually exclusive** — never block a URL you need de-indexed; the crawler must reach it to read the noindex.
- **AJAX list cards must build URLs with `reverse()`**, not f-strings — hardcoded paths lose the `/fr/` `/ru/` language prefix. (Server-rendered `{% url %}` cards were already fine.)
- **`{% trans %}` autoescapes**; embedded HTML (`<em>`) renders as literal text. Use `{% blocktrans %}` when markup must survive, or split the markup out of the tag.
- **Django `{# #}` comments are single-line only**; `_()` cannot be used inside a Django filter argument — both throw `TemplateSyntaxError`.
- **Icon-only controls need an accessible name** (`aria-label`) and their `<i>` should be `aria-hidden`. Toggles (favourite, tabs) need `aria-pressed` kept in sync by the JS that flips visual state.
- **Click-only `<div>`s are not keyboard-operable** — add `role="button" tabindex="0"` + a keydown (Enter/Space) handler, or use a real `<button>`.
- **JS user-facing strings go through `window.JD_STRINGS`** declared in the template `<script>` block — never hardcoded in `.js` files (they bypass gettext).
- **Fixed-height image wraps + `object-fit: cover` already reserve layout space** → card CLS ≈ 0; no `aspect-ratio`/width-height needed (Lighthouse's "explicit width/height" lint is cosmetic in that case).

---
---

# PENDING — before Phase 8 can be called "shipped"

These are run/verify tasks (no code owed):

1. **Place the files, run makemessages, fill the new strings, `compilemessages`, restart.** Confirm 0 fuzzy on the new msgids.
2. **Validate one tour + one car detail page** in Google Rich Results Test (Product/Offer).
3. **Booking-flow regression:** hotels/cars/tours × Pay Now + Pay on Arrival × fr/ru; price snapshot intact. ⚠️ **PesaPal is still in PRODUCTION mode in the dev `.env` — live charges. Switch to sandbox or test with care.**
4. **Mobile Lighthouse** on home + a detail page — trust SEO/Accessibility scores, **not** Performance (dev server is unreliable; real CWV via pagespeed.web.dev post-deploy).
5. **NAP reconciliation** — one phone + address everywhere, matching the Google Business Profile.
6. **Credential rotation before go-live** — AWS / Brevo / PesaPal keys were exposed in earlier screenshots/`.env` uploads. **Still outstanding.**

---

# NEXT — Phase 9: AWS S3 Media Storage

Pre-reqs already in place (and gotchas to respect):
- Bucket `jadevine-media-926634327396-eu-west-1-an` (eu-west-1), IAM user `jadevine-django`.
- **Rotate the IAM credentials first** (prior screenshot exposure).
- **Do not set `AWS_DEFAULT_ACL = 'public-read'`** — it breaks on modern (ACL-disabled) buckets. Use a **bucket policy** for public read instead.
- Stack: `django-storages` + `boto3`, public-read media via bucket policy, `MEDIA_URL` → bucket/CloudFront, `collectstatic` strategy unchanged (static already handled).
- One-time `Site` framework update still pending: set domain to `jadevinetravel.com` (`Site.objects.get(pk=1)` → domain + name) — fixes allauth email links.

---

# FILE MANIFEST — changed/added in Phase 8

**SEO / settings**
`apps/core/seo.py` *(new)* · `apps/core/context_processors.py` *(new)* · `apps/core/sitemaps.py` *(new)* · `templates/robots.txt` *(new)* · `templates/base.html` · `config/urls.py` · `config/settings/base.py` · `config/settings/production.py` · `apps/{hotels,cars,tours}/views.py` · `static/favicons/*` + `site.webmanifest`

**i18n**
`locale/fr/LC_MESSAGES/django.po` + `.mo` · `locale/ru/LC_MESSAGES/django.po` + `.mo`

**Accessibility + detail-JS i18n**
`static/js/hotels/hotel_list.js` · `static/js/cars/car_list.js` · `static/js/core/favourites.js` · `templates/{hotels,cars,tours}/*_list.html` · `templates/{hotels,cars,tours}/*_detail.html` · `static/js/{hotels,cars,tours}/*_detail.js` · `templates/contact/contact.html` · `static/js/contact/contact.js` · `templates/gallery/gallery.html` · `templates/core/home.html` · `static/js/core/home.js`

*(Unchanged & confirmed clean: `templates/static_pages/about.html`, `static/js/.../about.js`.)*
