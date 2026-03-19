"""
WSGI config for cears_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import django.db.backends.mysql.base
from django.db.backends.mysql.features import DatabaseFeatures

# Force the fix here
django.db.backends.mysql.base.DatabaseWrapper.check_database_version_supported = lambda self: None
DatabaseFeatures.has_returning_fields = False

import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cears_backend.settings')
application = get_wsgi_application()
