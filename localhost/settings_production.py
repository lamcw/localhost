import os

from localhost.settings import *

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '54.206.61.115', 'h11a.xyz', 'websocket'
]

# Security
# >= 50 characters & > 5 unique characters
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

# prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# Setup HTTPS before using the below options
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

FILE_UPLOAD_PERMISSIONS = 0o644

# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'localhost_db'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PW'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
# END DATABASE CONFIGURATION
