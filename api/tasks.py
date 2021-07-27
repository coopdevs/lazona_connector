from koiki.vars import logger
from koiki.client import Client
from koiki.email import FailedDeliveryMail, SuccessDeliveryMail
from sugarcrm.customer import Customer
import wordpress
from wordpress.user import WPUser
from lazona_connector.celery import app


@app.task
def create_delivery(order_data):
    from api.models import Shipment, ShipmentStatus
    deliveries_by_vendor = Client().create_delivery(order_data)
    for delivery in deliveries_by_vendor:
        label_url = ""
        if delivery._is_errored():
            delivery_status = ShipmentStatus.ERROR_FROM_BODY
            FailedDeliveryMail(
                order_id=delivery.get_data_val("order_id"),
                error_returned=delivery.get_data_val("message"),
                req_body=delivery.req_body
            ).send()
        else:
            delivery_status = ShipmentStatus.LABEL_SENT
            label_url = delivery.print_pdf()

            logger.info("Sending Koiki pdf to vendor with id {}".format(delivery.vendor.id))
            SuccessDeliveryMail(
                pdf_path=label_url,
                recipient=delivery.vendor.email,
                order_id=delivery.get_data_val("order_id")
            ).send()

        Shipment(
            delivery_id=delivery.get_data_val("barcode"),
            order_id=int(delivery.get_data_val("order_id")),
            vendor_id=int(delivery.vendor.id),
            label_url=label_url,
            status=delivery_status,
        ).save()


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
        wp_user.update(roles=wordpress.wp_partner_role)
