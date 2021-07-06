from koiki.client import Client
from koiki.email import FailedDeliveryMail, SuccessDeliveryMail
from sugarcrm.customer import Customer
import wordpress
from wordpress.user import WPUser
from lazona_connector.celery import app
from api.models import Shipment, DeliveryStatus


@app.task
def create_delivery(order):
    deliveries_by_vendor = Client(order).create_delivery()
    for delivery in deliveries_by_vendor:
        label_url = ""
        if delivery._is_errored():
            status_delivery = DeliveryStatus.ERROR_FROM_BODY
            FailedDeliveryMail(
                order_id=delivery.order_id,
                error_returned=delivery.data.get("mensaje"),
                req_body=delivery.req_body
            ).send()
        else:
            status_delivery = DeliveryStatus.LABEL_SENT
            label_url = delivery.print_pdf()
            SuccessDeliveryMail(
                pdf_path=label_url,
                recipient=delivery.vendor.email,
                order_id=delivery.order_id
            ).send()

        Shipment(
            shipment=delivery.data.get("codBarras"),
            order=int(delivery.order_id),
            vendor=int(delivery.vendor.id),
            label_url=label_url,
            status=status_delivery,
        )


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
