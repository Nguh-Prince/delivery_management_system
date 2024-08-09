# delivery_management/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_management.settings')

application = get_wsgi_application()
