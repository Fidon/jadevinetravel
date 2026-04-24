from django.db import models
from django.utils.translation import gettext_lazy as _


class GalleryCategory(models.Model):
    name_en = models.CharField(max_length=100, verbose_name=_('Name (English)'))
    name_fr = models.CharField(max_length=100, blank=True, null=True)
    name_ru = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Gallery Category')
        verbose_name_plural = _('Gallery Categories')
        ordering = ['order']

    def __str__(self):
        return self.name_en

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}', None) or self.name_en


class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', _('Photo')),
        ('video', _('Video')),
    ]

    category = models.ForeignKey(
        GalleryCategory, on_delete=models.SET_NULL, null=True, related_name='items'
    )
    media_type = models.CharField(
        max_length=10, choices=MEDIA_TYPE_CHOICES, default='photo'
    )
    image = models.ImageField(upload_to='gallery/photos/', blank=True, null=True)
    video_url = models.URLField(
        blank=True, null=True,
        help_text=_('YouTube or Vimeo embed URL')
    )
    video_file = models.FileField(
        upload_to='gallery/videos/', blank=True, null=True
    )
    caption_en = models.CharField(max_length=200, blank=True, null=True)
    caption_fr = models.CharField(max_length=200, blank=True, null=True)
    caption_ru = models.CharField(max_length=200, blank=True, null=True)
    is_featured = models.BooleanField(
        default=False,
        help_text=_('Show in Gallery Highlights section on homepage')
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Gallery Item')
        verbose_name_plural = _('Gallery Items')
        ordering = ['order']

    def __str__(self):
        return f"{self.get_media_type_display()} — {self.category}"

    def get_caption(self, lang='en'):
        return getattr(self, f'caption_{lang}', None) or self.caption_en