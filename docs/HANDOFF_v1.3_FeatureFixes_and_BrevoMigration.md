# Jadevine Travel & Tours — Combined Handoff v1.3
**Feature Fixes (Loader · Footer · Newsletter i18n · Leak Fix) + Gmail SMTP → Brevo Email Migration**

*June 2026 — Fidon / Jadevine Travel & Tours*
*Consolidates: Feature Fixes v1.2 + Brevo Email Migration session*

---

## Overview

This document covers two independent work streams completed this cycle.

| Part | Work stream | Files touched | Status |
|------|-------------|---------------|--------|
| **1** | Feature Fixes — page loader, footer redesign, newsletter i18n, global-class leak fix | `templates/base.html`, `static/css/main.css`, `static/js/main.js` | Code complete; `makemessages` + `collectstatic` + test pending |
| **2** | Email migration — Gmail SMTP → Brevo SMTP relay (all environments) | `config/settings/base.py`, `config/settings/development.py`, `config/settings/production.py`, `.env` (dev + prod) | Brevo + DNS authenticated; live test + key rotation pending |

The two parts are unrelated in surface area (public-site frontend globals vs. settings/infra) and can be deployed independently. A consolidated action list and combined learnings appear at the end (§Consolidated Next Actions, §Combined Key Learnings).

---
---

# PART 1 — FEATURE FIXES (v1.2)

**Page Loader · Footer Redesign · Newsletter i18n Fix · Global-class Leak Fix**

## Scope of this work

Four pieces of work, all on **public-site global files only**. No models, views, URLs, or portal files touched.

**Files modified:** `templates/base.html`, `static/css/main.css`, `static/js/main.js`.

---

## 1.1 · Page Loader (public site only)

A branded full-screen loader shown until the DOM is ready. Lives in `base.html`, so it is automatically public-only — the portal renders from `portal_base.html` and is unaffected.

### Design contract (non-negotiable behaviour)

- **Dismiss on `DOMContentLoaded`, not `window.load`.** Revealing on `load` would hide readable content behind the overlay until every image/font finishes — unacceptable on variable TZ connectivity.
- **`MIN_VISIBLE = 400ms`** floor (prevents flash on cache-hot loads).
- **`MAX_VISIBLE = 2500ms`** hard ceiling — force-dismiss so a stalled asset can never trap the user.
- **`pageshow` + `e.persisted`** — clears a frozen loader if the page is restored from bfcache after the user navigated away mid-load.
- **Fails open without JS** — `<noscript>` hides the overlay and restores scroll.
- **Single source of truth:** the `jd-loading` class on `<html>`. Removing it both fades the overlay and restores scroll.

### `base.html` changes

- `<html>` tag now carries `class="jd-loading"` (alongside `lang` / conditional `dir`).
- `<head>`: critical inline `<style>` (paints the dark overlay before `main.css` resolves) + `<noscript>` fail-open override, inserted after the `main.css` link.
- `<body>`: loader markup is the **first child**:

```html
<div id="jd-loader" role="status" aria-live="polite" aria-label="{% trans 'Loading' %}">
  <div class="jd-loader-inner">
    <div class="jd-loader-emblem">
      <span class="jd-loader-ring" aria-hidden="true"></span>
      <img src="{% static 'images/logo.png' %}" alt="" class="jd-loader-logo" />
    </div>
    <div class="jd-loader-wordmark">Jadevine</div>
    <div class="jd-loader-sub">{% trans "Travel & Tours" %}</div>
  </div>
</div>
```

### `main.js` changes

Vanilla IIFE added at the **very top of the file, above `$(function () {`** (teardown must not depend on jQuery loading):

```js
(function () {
  var docEl = document.documentElement;
  if (!docEl.classList.contains("jd-loading")) return;
  var MIN_VISIBLE = 400, MAX_VISIBLE = 2500, navStart = Date.now();
  function elapsed() {
    return window.performance && performance.now ? performance.now() : Date.now() - navStart;
  }
  function dismiss() {
    if (!docEl.classList.contains("jd-loading")) return;
    setTimeout(function () { docEl.classList.remove("jd-loading"); }, Math.max(0, MIN_VISIBLE - elapsed()));
  }
  if (document.readyState === "interactive" || document.readyState === "complete") dismiss();
  else document.addEventListener("DOMContentLoaded", dismiss);
  window.addEventListener("load", dismiss);
  setTimeout(function () { docEl.classList.remove("jd-loading"); }, MAX_VISIBLE);
  window.addEventListener("pageshow", function (e) { if (e.persisted) docEl.classList.remove("jd-loading"); });
})();
```

### `main.css` changes

Loader block **appended at end of file**. New selectors: `#jd-loader`, `html:not(.jd-loading) #jd-loader`, `html.jd-loading`, `.jd-loader-inner`, `.jd-loader-emblem`, `.jd-loader-logo`, `.jd-loader-ring`, `.jd-loader-wordmark`, `.jd-loader-sub`.

Key decisions:

- **Logo PNG has a solid black background (RGB, no alpha).** `.jd-loader-logo` is clipped with `border-radius: 50%` so only the circular emblem shows on the dark field.
- Field: `radial-gradient(circle at 50% 38%, #163021 -> #0b1810 -> #050a07)`.
- Gold halo (`.jd-loader-ring`) = conic-gradient + radial `mask` producing a thin 2-3px rotating arc.
- Wordmark uses `background-clip: text` gradient shimmer with `color: var(--color-accent-light)` fallback.
- **New keyframes:** `jd-loader-spin`, `jd-loader-breathe`, `jd-loader-shimmer` (no collision with existing `jd-spin`).
- **New `@media (prefers-reduced-motion: reduce)`** block, scoped to loader elements only (none existed in the file before).
- `z-index: 9999` (above the `--z-toast: 600` scale top).

---

## 1.2 · Footer Redesign (visual only — behaviour preserved)

Restructured layout and visuals; **no functional change**. Newsletter form, all `{% url %}` targets, contact values, social links, and the developer credit are unchanged.

### `base.html` — entire `<footer>` replaced

New structure:

- **`.jd-footer-top`** — newsletter promoted into a dedicated band (heading + subtext on the left, form on the right).
- **`.jd-footer-main`** — 4-col CSS grid: brand block (circular `logo.png` emblem + wordmark + desc + socials), Services, Company, Contact.
- **`.jd-footer-bottom`** — refined copy / credit / license bar.

Newsletter form retains `class="jd-newsletter-form"`, `{% csrf_token %}`, `input[type=email]`, and `[type=submit]` — so the global handler in `main.js` is untouched. The submit button is now a text label (`Subscribe`) instead of an icon, which makes the JS disabled/reset cycle coherent.

### `main.css` — entire FOOTER section replaced

New/changed selectors: `.jd-footer` (now `position: relative`, radial-glow background, gold `::before` top hairline), `.jd-footer-top*`, `.jd-newsletter-input`, `.jd-newsletter-btn`, `.jd-footer-main`, `.jd-footer-brand-row`, `.jd-footer-emblem`, `.jd-footer-brand-block`, `.jd-footer-heading::after` (gold underline accent), plus responsive grid at 991px / 575px.

**Note:** `.jd-footer-brand` is now a `<p>` (was a `<div>`) — CSS targets the class, and `margin: 0` is set to kill the default paragraph margin.

**Redundant rule:** the old `@media (min-width: 992px) { .jd-footer-bottom { ... } }` near the bottom of `main.css` is now duplicated inside the new block. Harmless; delete the old one if tidying.

### i18n decision

The band title is a **single `{% trans %}` string**, not a sentence split around a styled `<span>`. Splitting a sentence across two trans tags to colour one word breaks FR/RU word order. Correctness over flourish.

---

## 1.3 · Newsletter JS i18n Fix

The section-8 newsletter handler in `main.js` had hardcoded English (`"…"`, `"Subscribed! Thank you."`, `"Something went wrong."`, `"Network error…"`, `"Subscribe"`). Routed through the project's `window.JD_STRINGS` convention.

### `base.html` — `JD_STRINGS` block added **before** the `main.js` `<script>`

```html
{% trans "Subscribe" as jd_s_subscribe %}
{% trans "Subscribing…" as jd_s_subscribing %}
{% trans "Subscribed! Thank you." as jd_s_subscribed %}
{% trans "Something went wrong." as jd_s_newsletter_error %}
{% trans "Network error. Please try again." as jd_s_network_error %}
<script>
  window.JD_STRINGS = {
    subscribe: "{{ jd_s_subscribe|escapejs }}",
    subscribing: "{{ jd_s_subscribing|escapejs }}",
    subscribed: "{{ jd_s_subscribed|escapejs }}",
    newsletterError: "{{ jd_s_newsletter_error|escapejs }}",
    networkError: "{{ jd_s_network_error|escapejs }}"
  };
</script>
```

`|escapejs` is mandatory — translations may contain apostrophes (`S'abonner`), quotes, or `</script>`; it escapes them to `\uXXXX` so they can't break the literal or close the tag. `{% trans … as var %}` is required because a filter can't pipe directly onto `{% trans %}`.

### `main.js` — section 8 rewritten

Reads from `var STR = window.JD_STRINGS || {};` with fallback precedence: **server message** (`res.message`/`res.error`, already localised by the view's `gettext`) -> **`JD_STRINGS`** -> **English literal**. The `.js` file now contains zero translatable literals — the correct end state.

---

## 1.4 · Bug Fix — Footer styling leaked onto the home newsletter form

**Symptom:** the home page **"Get Exclusive Travel Offers"** form was capped at exactly 460px.

**Root cause (self-inflicted in §1.2):** footer-specific layout (`max-width: 460px; flex: 1 1 320px; min-width: 320px`) was placed on the **shared global `.jd-newsletter-form` class** — the same class the global AJAX handler binds to, used by both the footer and `templates/core/home.html`. A behavioural class must not carry one context's layout.

**Fix:** all newsletter selectors introduced in §1.2 were scoped under **`.jd-footer-top`** (6 edits in `main.css`): `.jd-footer-top .jd-newsletter-form`, `…-input`, `…-input::placeholder`, `…-input:focus`, `…-btn`, and the 575px responsive rule. The home form now reverts to `home.css` control (the leak had been *narrowing* it).

---

## 1.5 · Footer band title font

`.jd-footer-top-title` switched from `var(--font-heading)` (Cormorant Garamond) to `var(--font-body)` (Jost), with `font-size: 1.6rem`, `font-weight: 500`, `letter-spacing: 0.01em` — Jost renders heavier per point than the serif, so size/weight were reduced to compensate.

---

## 1.6 · New translatable strings (Part 1)

Run `makemessages -l fr -l ru`:

`Loading` · `Travel inspiration, straight to your inbox` · `Curated escapes, seasonal offers and Zanzibar travel tips. No spam.` · `Your email address` · `Subscribe` · `Subscribing…` · `Subscribed! Thank you.` · `Something went wrong.` · `Network error. Please try again.`

All are in `base.html` template `{% trans %}` tags — standard `makemessages` picks them up; no `djangojs` domain needed.

---
---

# PART 2 — EMAIL MIGRATION (Gmail SMTP → Brevo)

**Scope:** Migrate transactional email from Gmail SMTP to Brevo SMTP relay across all environments (dev + prod).
**Status:** Brevo account + DNS fully configured and authenticated. Code changes delivered. Final live test + key rotation pending.

## 2.1 · Decision & Rationale

**Use Brevo SMTP relay, not the Brevo HTTP API.**
The entire send path is `EmailMultiAlternatives` over `django.core.mail`, dispatched through Django-Q2. An SMTP relay is a drop-in: only `EMAIL_HOST`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` change. Zero changes to email tasks, table-based HTML templates, or the task queue. The HTTP API would force a rewrite of every send path plus an SDK dependency for no functional gain at this volume.

**Use Brevo everywhere, drop SendGrid.**
Setup difficulty is identical (both are SMTP relays with the same eight Django settings). Brevo's free tier is 300 emails/day with no expiration, the account already exists, and one provider across dev + prod gives configuration parity (same DKIM, same From, same behaviour). Running two providers was maintenance overhead for nothing.

**Why Gmail SMTP was the wrong fit:** Gmail SMTP forces the authenticated Gmail account as the sender; you cannot cleanly send as `info@jadevinetravel.com` without it being a verified "send as" alias. Brevo lets us send from the authenticated domain properly. Deliverability — not the 300/day cap — was the real reason to move.

---

## 2.2 · Brevo Account State (completed)

| Item | Value / Status |
|------|----------------|
| Brevo account email | `fidontakakwa@gmail.com` |
| Plan | Free (300 emails/day, resets midnight UTC, no expiration) |
| Domain `jadevinetravel.com` | **Authenticated** ✓ |
| DKIM signature | `jadevinetravel.com` ✓ |
| DMARC | Configured ✓ |
| Sender `Jadevine Travel & Tours <info@jadevinetravel.com>` | **Verified** ✓ |
| Sender-domain compliance | Compliant with Google / Yahoo / Microsoft sender requirements ✓ |
| SMTP login (`EMAIL_HOST_USER`) | `a88118001@smtp-brevo.com` |
| SMTP key (`EMAIL_HOST_PASSWORD`) | Generated, stored in `.env` only. **Pending rotation** — see §2.7. |

**Navigation reference (Brevo UI):**
- Domain auth & senders: **Settings → Senders, domains, IPs →** `Domains` / `Senders` tabs.
- SMTP key: **Settings → SMTP & API → SMTP tab → Generate a new SMTP key** (key shown once at creation).

---

## 2.3 · DNS State

- Registrar: **Namecheap**. Nameservers point to **DigitalOcean** (`ns1/ns2/ns3.digitalocean.com`).
- **All DNS records (brevo-code, DKIM, SPF, DMARC) are managed in DigitalOcean → Networking → Domains → jadevinetravel.com.** Namecheap's Advanced DNS tab is **not** used.
- Brevo SPF include value: `v=spf1 include:spf.brevo.com ~all` (merge into any existing SPF record — never create a second SPF TXT).
- DMARC starts at `p=none` (monitor-only); tighten to `quarantine`/`reject` later once mail is confirmed passing.

---

## 2.4 · Brevo SMTP Reference Values

| Setting | Value |
|---------|-------|
| Host | `smtp-relay.brevo.com` |
| Port | `587` (STARTTLS) — `465` available for SSL, `2525` fallback if 587 blocked |
| Encryption | STARTTLS (`EMAIL_USE_TLS=True`) |
| Username | Brevo **SMTP login** (`a88118001@smtp-brevo.com`) — NOT the From address |
| Password | Brevo **SMTP key** (`xsmtpsib-…`) — NOT an API key |

**Critical distinction:** `EMAIL_HOST_USER` (the SMTP login) and `DEFAULT_FROM_EMAIL` (`info@jadevinetravel.com`) are intentionally different. The login authenticates the relay; the From identifies the brand.

---

## 2.5 · Code Changes

Email config was **consolidated into `base.py`** as a single source of truth, since both environments now use the same provider. Previously it was duplicated across `base.py`, `development.py`, and `production.py` with three different default From addresses — a drift risk. `development.py` and `production.py` now inherit the email config and only override what differs.

### 2.5.1 `config/settings/base.py`

Replaced the old 4-line email block with the full Brevo config:

```python
# Email — Brevo SMTP relay (smtp-relay.brevo.com), shared across all environments.
# EMAIL_HOST_USER is your Brevo SMTP login (NOT info@jadevinetravel.com).
# EMAIL_HOST_PASSWORD is a Brevo SMTP key (NOT an API key).
# DEFAULT_FROM_EMAIL must be a sender on a domain authenticated in Brevo.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp-relay.brevo.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Jadevine Travel & Tours <info@jadevinetravel.com>')
ADMIN_NOTIFICATION_EMAIL = os.environ.get('ADMIN_NOTIFICATION_EMAIL', 'fidontakakwa@gmail.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

### 2.5.2 `config/settings/development.py`

Removed the entire duplicated email block. Now inherits from `base.py`; only a console-backend escape hatch documented:

```python
# Email — inherited from base.py (Brevo SMTP relay).
# To work offline or avoid spending the 300/day quota while testing,
# set EMAIL_BACKEND in your .env to print emails to the terminal instead:
#   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 2.5.3 `config/settings/production.py`

**Deleted** the SendGrid block entirely (now inherited from `base.py`):

```python
# REMOVED:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
```

`SENDGRID_API_KEY` is also removed from the production `.env`.

### 2.5.4 `.env` — email block

**Production `.env`:**

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=a88118001@smtp-brevo.com
EMAIL_HOST_PASSWORD=<full-xsmtpsib-key>
DEFAULT_FROM_EMAIL=Jadevine Travel & Tours <info@jadevinetravel.com>
ADMIN_NOTIFICATION_EMAIL=jadevinetravel@gmail.com
```

**Development `.env`:** identical SMTP values, but the admin recipient stays the developer's inbox (or use the console backend) to avoid sending test bookings to the client:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=a88118001@smtp-brevo.com
EMAIL_HOST_PASSWORD=<full-xsmtpsib-key>
DEFAULT_FROM_EMAIL=Jadevine Travel & Tours <info@jadevinetravel.com>
ADMIN_NOTIFICATION_EMAIL=fidontakakwa@gmail.com
# Optional, to avoid burning quota / sending real mail while testing:
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 2.6 · Environment Split (important)

`ADMIN_NOTIFICATION_EMAIL` is only ever a **recipient** (admin notifications are sent *from* `info@jadevinetravel.com` *to* this address), so a `@gmail.com` value has no deliverability impact.

- **Production** → `ADMIN_NOTIFICATION_EMAIL=jadevinetravel@gmail.com` (the client). This is the only place the client's address belongs.
- **Development** → `ADMIN_NOTIFICATION_EMAIL=fidontakakwa@gmail.com` (developer) or console backend. Prevents test bookings from spamming the client's real inbox.
- `base.py` fallback default stays `fidontakakwa@gmail.com` — a developer fallback is the correct thing to land on if an env var is ever missing, so a misconfigured environment never silently emails the client.

---

## 2.7 · Security Notes

- **Rotate the current SMTP key before go-live.** It was partially visible in screenshots shared during setup. Regenerate it in **SMTP & API → SMTP**, update `EMAIL_HOST_PASSWORD` in both `.env` files, and restart processes.
- `.env` is never committed to version control. Confirm it remains in `.gitignore`.
- The SMTP key is shown only once at creation; store it immediately. A lost key requires regeneration.

---

## 2.8 · Branding & Quota Caveats

- **Free-plan "Sent with Brevo" footer** applies to **marketing campaigns** built in Brevo's editor, not transactional SMTP relay sends (which render the raw HTML handed to them). **Verify** by sending a real booking confirmation to Gmail + Outlook and inspecting the footer before launch. If anything is injected, plan around it.
- **300 emails/day** covers transactional volume comfortably (≈2 emails/booking + occasional auth mail). Monitor under **Transactional → Statistics**.
- **Newsletter:** currently collects subscribers only (no programmatic sending). When newsletter sending is built, it goes through **Brevo Campaigns** — never the transactional relay (300/day cap + wrong channel).

---
---

# CONSOLIDATED NEXT ACTIONS

### Part 1 — Feature Fixes
1. **`makemessages -l fr -l ru`** for the 9 new strings (§1.6); translate (client-approved MT or manual).
2. **`collectstatic --no-input`** before deploy (`main.css` and `main.js` both changed).
3. **Home form width (OPEN):** to widen the home newsletter form precisely, provide `static_pages/css/home.css` (newsletter rules) + the newsletter `<section>` markup from `templates/core/home.html`. Will be set at the correct selector — no guessing, no new leak.
4. **Test checklist:**
   - Loader: throttle to Slow 3G → page reveals on DOM-ready, not full image load; disable JS → no overlay, page scrolls; block an asset → 2.5s hard-cap fires; back/forward (bfcache) → no frozen loader.
   - Footer: responsive at 991px / 575px; newsletter submit succeeds and toasts in FR/RU.

### Part 2 — Email Migration
5. **Live test send** and confirm SPF/DKIM/DMARC pass:
   ```python
   from django.core.mail import send_mail
   send_mail('Brevo test', 'Plain body.', None, ['fidontakakwa@gmail.com'])
   ```
   `None` forces use of `DEFAULT_FROM_EMAIL`. Expect return value `1`. In Gmail → **Show original** → confirm **SPF: PASS, DKIM: PASS, DMARC: PASS**, inbox not spam.
6. After the shell test passes, fire one **real booking confirmation through `qcluster`** to confirm the async path end-to-end. (Restart **`qcluster` AND `runserver`** after any `.env` change — env is read only at process start.)
7. **Rotate** the screenshotted SMTP key; update both `.env` files; restart.
8. **Inspect** a delivered transactional email for any Brevo footer.
9. Set `ADMIN_NOTIFICATION_EMAIL` correctly **per environment** on the droplet's prod `.env`.

### Unrelated production bugs noticed (flagged, not yet fixed)
- `production.py`: `ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', '')]` wraps the whole comma-separated string as one list element — multi-host values won't match. Needs to split on commas.
- `production.py`: `AWS_DEFAULT_ACL = 'public-read'` throws on buckets with ACLs disabled (AWS default since 2023). Should be `None` with `AWS_QUERYSTRING_AUTH = False` (per Phase 6 notes — confirm the live file matches).

---

# COMBINED KEY LEARNINGS

**Frontend / public site:**
- **Behavioural classes ≠ layout classes.** Anything the JS binds to (`.jd-newsletter-form`) must stay layout-neutral globally; scope visual styling to a context (`.jd-footer-top …`).
- **Loader teardown is vanilla JS**, runs before jQuery, single source of truth = `html.jd-loading`.
- **JS strings always via `window.JD_STRINGS`** with `{% trans … as var %}` + `|escapejs`; server-supplied messages take precedence over client fallbacks.
- Don't split a sentence across two `{% trans %}` tags to style one word — it breaks FR/RU word order.

**Email / infrastructure:**
- The hard part of an email-provider switch is **DNS/deliverability authentication**, not the Django settings. Swapping credentials is 10 minutes; DKIM/SPF/DMARC alignment is what makes mail actually deliver under the Feb-2024 Gmail/Yahoo sender rules.
- With one provider across environments, email config belongs in `base.py`; environment files override only what differs.
- SMTP **login** ≠ From address. Confusing the two is the most common Brevo setup failure.
- Use an **SMTP key**, not an API key, for the relay.
- `ADMIN_NOTIFICATION_EMAIL` is a recipient — keep the client's address out of dev to avoid test-booking spam.

---

*End of Combined Handoff v1.3 | June 2026*
*Prepared by Fidon for Jadevine Travel & Tours*
