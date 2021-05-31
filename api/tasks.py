from koiki.client import Client
from sugarcrm.customer import Customer
import wordpress
from wordpress.user import WPUser
from lazona_connector.celery import app


@app.task
def create_delivery(order):
    delivery = Client(order).create_delivery()

    if type(delivery).__name__ == 'Error':
        return delivery.to_dict()
    else:
        delivery.print_pdf()
        return {'success': 'all good'}


@app.task
def update_customer_if_is_partner(email):
    if _check_customer_is_partner(email):
        update_user_as_partner.delay(email)


def _check_customer_is_partner(email):
    customer = Customer().fetch(email)
    return customer.check_is_partner()


@app.task
def update_user_as_partner(email):
    wp_user = WPUser().fetch(email)
    if wp_user.roles and "customer" in wp_user.roles:
        wp_user.update(roles=wordpress.wp_partner_role)
