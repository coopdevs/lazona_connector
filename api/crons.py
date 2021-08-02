from django_cron import CronJobBase, Schedule
from django.db.models import Q
from api.tasks import update_delivery_status
from api.models import Shipment


class UpdateShipmentStatusCronJob(CronJobBase):
    RUN_EVERY_MINS = 480

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'api.update_shipment_status_cron_job'

    def do(self):
        shipments = Shipment.objects.all().exclude(Q(delivery_id='') | Q(status='DELIVERED'))
        if shipments:
            for shipment in shipments:
                # print("TESTING SHIPMENT", str(shipment.status))
                # update_delivery_status.delay(shipment.delivery_id, email_notify=True)
                update_delivery_status(shipment.delivery_id, email_notify=True)
