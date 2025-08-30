"""
WSGI config for Proyecto_cita_medica project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'Proyecto_cita_medica.settings')

application = get_wsgi_application()
