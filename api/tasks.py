from datetime import datetime
from koiki.client import Client
from koiki.email import FailedDeliveryMail, SuccessDeliveryMail
from sugarcrm.customer import Customer
import lazona_connector.vars
from lazona_connector.vars import logger
from wordpress.user import WPUser
from lazona_connector.celery import app


@app.task
def create_or_update_delivery(order_data, vendor_id=None):
    from api.models import Shipment, ShipmentStatus
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
        shipment.delivery_id = delivery.get_data_val("barcode")
        shipment.label_url = label_url
        shipment.status = delivery_status
        shipment.update_at = datetime.now()
        shipment.save()


@app.task
def update_delivery_status(delivery_id):
    from api.models import Shipment, ShipmentStatus
    delivery_status = Client().update_delivery_status(delivery_id)
    if delivery_status and delivery_id:
        shipment = Shipment.objects.get(delivery_id=delivery_id)
        shipment.tracking_updated_at = datetime.now()
        shipment_status = delivery_status.get_data_val('shipment_status')
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
        return True
    return False


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
        wp_user.update(roles=lazona_connector.vars.wp_partner_role)
