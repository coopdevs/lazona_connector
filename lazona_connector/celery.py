from celery import Celery
from django.conf import settings
import scout_apm.celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lazona_connector.settings')

app = Celery(
    'lazona_connector',
    broker=os.environ['REDIS_URL'],
    backend=f'{os.environ["REDIS_URL"]}?ssl_cert_reqs=none'
)
app.config_from_object(settings)
app.autodiscover_tasks()

scout_apm.celery.install(app)
