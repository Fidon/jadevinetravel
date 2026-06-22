"""
apps/core/context_processors.py

Site-wide SEO context, computed for every request. Handles everything that is
derivable from the URL alone — canonical, hreflang alternates (+ x-default),
robots index/noindex — so listing pages and static pages need ZERO per-view work
for those. Per-object data (a specific hotel's title/description/image/schema) is
injected by the detail views instead; see each app's views.py.

NOTE: if apps/core already has a context_processors.py (it does not in the current
tree, but to be safe), merge the `seo` function into it rather than overwriting.
"""
from django.conf import settings
from django.urls import translate_url

from .seo import absolute_url, get_site_url, is_public_i18n_path

# og:locale needs a full locale, not just the language subtag.
OG_LOCALE_MAP = {'en': 'en_US', 'fr': 'fr_FR', 'ru': 'ru_RU'}


def seo(request):
    path = request.path
    public = is_public_i18n_path(path)
    has_query = bool(request.META.get('QUERY_STRING'))

    # Canonical always points at the clean (query-less) URL on the canonical host.
    # request.path already excludes the query string.
    canonical = absolute_url(path)

    alternates = []
    x_default = None
    if public:
        for code, _name in settings.LANGUAGES:
            try:
                alt_path = translate_url(path, code)
            except Exception:
                alt_path = path
            url = absolute_url(alt_path)
            alternates.append({
                'lang': code,
                'url': url,
                'og_locale': OG_LOCALE_MAP.get(code, code),
            })
            if code == settings.LANGUAGE_CODE:
                x_default = url

    # Index only public pages with no filter/sort/pagination query string.
    # Every filtered listing permutation (?location=…&stars=…) is noindex,follow
    # with its canonical pointing back at the clean listing URL — this is what
    # keeps Google's index free of thin, near-duplicate filter pages.
    robots_index = public and not has_query

    return {
        'SEO': {
            'site_url': get_site_url(),
            'canonical_url': canonical,
            'hreflang_alternates': alternates,
            'hreflang_x_default': x_default,
            'robots_index': robots_index,
            'is_public': public,
            'og_locale': OG_LOCALE_MAP.get(getattr(request, 'LANGUAGE_CODE', 'en'), 'en_US'),
        },
        'GA4_MEASUREMENT_ID': getattr(settings, 'GA4_MEASUREMENT_ID', ''),
        'GSC_VERIFICATION': getattr(settings, 'GSC_VERIFICATION', ''),
    }