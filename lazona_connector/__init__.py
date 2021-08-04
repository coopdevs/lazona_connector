# from django_celery_beat.models import PeriodicTask, IntervalSchedule
# schedule, created = IntervalSchedule.objects.get_or_create(
#     every=8,
#     period=IntervalSchedule.HOURS,
# )
# schedule_sec, created_sec = IntervalSchedule.objects.get_or_create(
#     every=1,
#     period=IntervalSchedule.SECONDS,
# )
# pt = PeriodicTask.objects.get(name='Updating shipment status')
# if not pt:
#     PeriodicTask.objects.create(
#         interval=schedule_sec,
#         name='Updating shipment status',
#         task='api.update_delivery_status_periodic'
#     )
