from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'jadevine_db.sqlite3',
    }
}

# Use local file storage in development
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Email settings 
# Email — inherited from base.py (Brevo SMTP relay).
# To work offline or avoid spending the 300/day quota while testing,
# set EMAIL_BACKEND in your .env to print emails to the terminal instead:
#   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
