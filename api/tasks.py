import pprint
from datetime import datetime
from koiki.client import Client
from koiki.email import FailedDeliveryMail, SuccessDeliveryMail, UpdateDeliveryStatusChangedMail
from sugarcrm.customer import Customer
from lazona_connector.vars import logger, wp_partner_role, TESTING
from wordpress.user import WPUser
from lazona_connector.celery import app
from django.db.models import Q

if __name__ == '__main__' or TESTING:
    from api.models import Shipment, ShipmentStatus


@app.task
def create_or_update_delivery(order_data, vendor_id=None):
    deliveries_by_vendor = Client().create_delivery(order_data, vendor_id)
    for delivery in deliveries_by_vendor:
        label_url = ""
        if delivery._is_errored():
            delivery_status = ShipmentStatus.ERROR_FROM_BODY
            FailedDeliveryMail(
                order_id=delivery.get_data_val("order_id"),
                error_returned=delivery.get_data_val("message"),
                req_body=delivery.req_body,
            ).send()
        else:
            delivery_status = ShipmentStatus.LABEL_SENT
            label_url = delivery.print_pdf()

            logger.info("Sending Koiki pdf to vendor with id {}".format(delivery.vendor.id))
            SuccessDeliveryMail(
                pdf_path=label_url,
                recipient=delivery.vendor.email,
                order_id=delivery.get_data_val("order_id"),
            ).send()
        shipment, created = Shipment.objects.get_or_create(
            order_id=int(delivery.get_data_val("order_id")), vendor_id=int(delivery.vendor.id)
        )
        shipment.req_body = pprint.pformat(delivery.req_body)
        shipment.delivery_message = delivery.get_data_val("message")
        shipment.delivery_id = delivery.get_data_val("barcode")
        shipment.label_url = label_url
        shipment.status = delivery_status
        shipment.update_at = datetime.now()
        shipment.save()


@app.task
def update_delivery_status(delivery_id, email_notify=False):
    from api.models import Shipment, ShipmentStatus
    delivery_status = Client().update_delivery_status(delivery_id)
    if delivery_status and delivery_id:
        shipment = Shipment.objects.get(delivery_id=delivery_id)
        shipment.tracking_updated_at = datetime.now()
        shipment_status = delivery_status.get_data_val('shipment_status')
        old_shipment_status = shipment.status
        old_shipment_delivery_message = shipment.delivery_message
        if delivery_status.is_errored():
            shipment.status = shipment_status
            shipment.delivery_message = delivery_status.get_data_val('response_error_message')
            shipment.tracking_status_created_at = None
        else:
            shipment.tracking_status_created_at = delivery_status.get_data_val('response_date')
            shipment.delivery_notes = delivery_status.get_data_val('response_notes')
            if shipment_status:
                shipment.status = shipment_status
                shipment.delivery_message = delivery_status.get_data_val('response_message')
            else:
                shipment.status = ShipmentStatus.ERROR_FROM_TRACKING
                shipment.delivery_message = "{}. Doesn't match any shipment status".format(
                    delivery_status.get_data_val('response_message')
                )
        shipment.save()
        if email_notify:
            if (shipment.status != old_shipment_status or
                    shipment.delivery_message != old_shipment_delivery_message):
                UpdateDeliveryStatusChangedMail(shipment).send()
        return True
    return False


@app.task(name='update_delivery_status_periodic')
def update_delivery_status_periodic():
    from api.models import Shipment
    shipments = Shipment.objects.all().exclude(Q(delivery_id='') | Q(status='DELIVERED'))
    if shipments:
        for shipment in shipments:
            logger.info(
                "Updating shipment stratus for delivery id {}".format(
                    shipment.delivery_id
                )
            )
            update_delivery_status(shipment.delivery_id, email_notify=True)


@app.task
def update_customer_if_is_partner(email):
    if _check_customer_is_partner(email):
        update_user_as_partner.delay(email)


def _check_customer_is_partner(email):
    customer = Customer().fetch(email)
    return customer.check_is_partner()


@app.task
def update_user_as_partner(email):
    wp_user = WPUser().fetch_by_email(email)
    if wp_user.roles and "customer" in wp_user.roles:
        wp_user.update(roles=wp_partner_role)
