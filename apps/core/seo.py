"""
apps/core/seo.py

Centralised SEO helpers. One source of truth for:
  - the canonical scheme + host (settings.SITE_URL)
  - absolute-URL construction (used by context processor, views, sitemaps)
  - which paths are public/i18n (eligible for indexing + hreflang)
  - XSS-safe JSON-LD serialisation for <script type="application/ld+json">
  - clean plain-text extraction for meta descriptions
  - BreadcrumbList schema construction

Never build canonical/hreflang/OG URLs from request.get_host(): behind Nginx the
request host/scheme is unreliable (www vs non-www, http vs https) and that is the
single most common cause of duplicate-content + wrong-canonical penalties on a
multilingual site. SITE_URL is the only host we ever emit.
"""
import json
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

# Path prefixes that live OUTSIDE i18n_patterns. They have no language variants,
# must never be indexed, and must never receive hreflang tags.
NON_PUBLIC_PREFIXES = ('/portal/', '/admin/', '/book/', '/reviews/', '/i18n/', '/accounts/')


def get_site_url():
    """Canonical scheme + host, no trailing slash. e.g. 'https://jadevinetravel.com'."""
    return settings.SITE_URL.rstrip('/')


def absolute_url(path):
    """
    Build an absolute URL on the canonical host from a root-relative path.
    Passes through values that are already absolute (e.g. S3 media URLs in prod).
    """
    if not path:
        return get_site_url() + '/'
    if path.startswith(('http://', 'https://')):
        return path
    if not path.startswith('/'):
        path = '/' + path
    return get_site_url() + path


def is_public_i18n_path(path):
    """True for public, language-prefixed pages (the only pages we index + hreflang)."""
    return not any(path.startswith(p) for p in NON_PUBLIC_PREFIXES)


def strip_query(url_or_path):
    """Return the URL/path with any query string and fragment removed (for canonical)."""
    parts = urlsplit(url_or_path)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))


def clean_text(value, length=None):
    """
    Plain-text suitable for a meta description or schema description: strip any HTML,
    collapse whitespace/newlines to single spaces, optionally truncate to `length`
    characters on a word boundary with an ellipsis. Returns '' for empty input.
    """
    if not value:
        return ''
    text = ' '.join(strip_tags(str(value)).split())
    if length:
        text = Truncator(text).chars(length)
    return text


def breadcrumb_schema(crumbs):
    """
    Build a BreadcrumbList dict from an ordered list of (name, absolute_url) tuples.
    Names MUST be real str (call gettext, not gettext_lazy) — lazy proxies are not
    JSON-serialisable and will raise inside jsonld_safe().
    """
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(crumbs)
        ],
    }


def jsonld_safe(data):
    """
    Serialise a dict to a JSON-LD string that is safe to embed directly inside a
    <script type="application/ld+json"> block.

    json.dumps does NOT escape '<', '>' or '&', so a listing description containing
    '</script>' would break out of the tag. We escape those three characters to
    their \\uXXXX forms — the canonical, spec-compliant way to inline JSON-LD.
    ensure_ascii=False keeps Cyrillic/accented content human-readable in UTF-8.
    """
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    raw = raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return mark_safe(raw)