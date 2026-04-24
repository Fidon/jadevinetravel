from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    INQUIRY_TYPE_CHOICES = [
        ('general', _('General Inquiry')),
        ('custom_tour', _('Custom Tour Request')),
        ('partnership', _('Partnership')),
        ('press', _('Press / Media')),
    ]

    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('ru', 'Русский'),
    ]

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))
    inquiry_type = models.CharField(
        max_length=20, choices=INQUIRY_TYPE_CHOICES, default='general'
    )
    preferred_lang = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default='en'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(
        blank=True, null=True,
        help_text=_('Internal notes — never shown to customer')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Newsletter Subscriber')
        verbose_name_plural = _('Newsletter Subscribers')

    def __str__(self):
        return self.email