from koiki.client import Client
from koiki.email import FailedDeliveryMail, SuccessDeliveryMail
from sugarcrm.customer import Customer
import wordpress
from wordpress.user import WPUser
from lazona_connector.celery import app


@app.task
def create_delivery(order):
    deliveries_by_vendor = Client(order).create_delivery()
    for delivery in deliveries_by_vendor:
        if not delivery._is_errored():
            SuccessDeliveryMail(
                pdf_path=delivery.print_pdf(),
                recipient=delivery.vendor.email,
                order_id=delivery.order_id
            ).send()
        else:
            FailedDeliveryMail(
                order_id=delivery.order_id,
                error_returned=delivery.data.get("mensaje"),
                req_body=delivery.req_body
            ).send()


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
