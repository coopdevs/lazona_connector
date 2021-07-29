from celery import Celery
from django.conf import settings
import scout_apm.celery
import os
from lazona_connector.vars import redis_url

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lazona_connector.settings')

if redis_url.lower().startswith('rediss://'):
    backend_url = f'{redis_url}?ssl_cert_reqs=none'
else:
    backend_url = redis_url

app = Celery(
    'lazona_connector',
    broker=redis_url,
    backend=backend_url
)
app.config_from_object(settings)
app.autodiscover_tasks()

scout_apm.celery.install(app)
