from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser.
    
    Customers log in with EMAIL + password (via django-allauth).
    Admin and Mini-Admin log in with USERNAME + password (Django built-in auth).
    
    We extend AbstractUser (not AbstractBaseUser) to keep all of Django's
    built-in auth machinery. We only need to add our extra fields.
    
    CRITICAL: This model must be defined and migrated before any other model
    in the project. Changing AUTH_USER_MODEL after migrations exist requires
    deleting all migrations and starting over.
    """

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('ru', 'Русский'),
    ]

    # Extra fields beyond AbstractUser defaults
    # AbstractUser already provides: id, username, first_name, last_name,
    # email, is_staff, is_active, is_superuser, date_joined, last_login,
    # password, groups, user_permissions

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Phone Number'),
    )
    nationality = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Nationality'),
    )
    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Preferred Language'),
    )
    profile_photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('Profile Photo'),
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email or self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class MiniAdminProfile(models.Model):
    """
    Marker model for mini-admin users.
    A user is a mini-admin if they have a MiniAdminProfile linked to them.
    is_staff=True is also set on the CustomUser so they can access /portal/.
    
    We check `hasattr(user, 'miniadminprofile')` in views to distinguish
    mini-admins from super admins (both have is_staff=True).
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='miniadminprofile',
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_miniadmins',
        verbose_name=_('Created By'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Mini-Admin Profile')
        verbose_name_plural = _('Mini-Admin Profiles')

    def __str__(self):
        return f"Mini-Admin: {self.user}"