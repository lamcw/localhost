"""
WSGI config for localhost project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

SETTINGS = 'localhost.settings_production' if os.environ.get(
    'SECRET_KEY') else 'localhost.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS)

application = get_wsgi_application()
