from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lazona_connector.settings')

app = Celery('lazona_connector')
app.config_from_object(settings)
app.autodiscover_tasks()
