from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from apps.accounts.views import JadevineLoginView
from apps.core.sitemaps import sitemaps as all_sitemaps

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': all_sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'), name='robots'),

    path('book/', include('apps.bookings.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('portal/', include('apps.portal.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Language-prefixed public URLs
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/login/', JadevineLoginView.as_view(), name='account_login'),
    path('accounts/', include('allauth.urls')),
    path('hotels/', include('apps.hotels.urls')),
    path('tours/', include('apps.tours.urls')),
    path('cars/', include('apps.cars.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('contact/', include('apps.contact.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)