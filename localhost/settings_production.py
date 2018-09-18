import os

from localhost.settings import *


ALLOWED_HOSTS = ['localhost', '127.0.0.1', '54.206.61.115']

# Security
# >= 50 characters & > 5 unique characters
SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = False

# prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# Setup HTTPS before using the below options
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 3600
# SECURE_SSL_REDIRECT = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

FILE_UPLOAD_PERMISSIONS = 0o644
