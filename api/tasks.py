from koiki.client import Client

from sugarcrm.customer import Customer
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
        # update_user(email) method with celery task from a following api/tasks/woocommerce.py
        pass


def _check_customer_is_partner(email):
    customer = Customer().fetch(email)
    return customer.check_is_partner()
