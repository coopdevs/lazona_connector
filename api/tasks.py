from koiki.client import Client
from sugarcrm.customer import Customer
import wordpress
from wordpress.user import WPUser
from lazona_connector.celery import app

@app.task
def create_delivery(order):
    deliveries_by_vendor = Client(order).create_delivery()
    deliveries_success = []
    deliveries_error = []
    for delivery in deliveries_by_vendor:
        if type(delivery).__name__ == 'Error':
            # TODO: logger info about the error
            deliveries_error.append(delivery)
        else:
            deliveries_success.append(delivery)
            delivery.send_mail_to_vendor()
    return {'success': [deliveries_success], 'error': [deliveries_error]}

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
