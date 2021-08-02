import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import scout_apm.celery
from lazona_connector.vars import redis_url
from django_celery_beat.models import PeriodicTask, IntervalSchedule

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

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#         crontab(hour=8),
#         api.tasks.update_delivery_status_periodic(),
#         name='Update shipment status'
#     )

schedule, created = IntervalSchedule.objects.get_or_create(
    every=8,
    period=IntervalSchedule.HOURS,
)
schedule_sec, created_sec = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.SECONDS,
)
pt = PeriodicTask.objects.get(name='Updating shipment status')
if not pt:
    PeriodicTask.objects.create(
        interval=schedule_sec,
        name='Updating shipment status',
        task='api.update_delivery_status_periodic'
    )