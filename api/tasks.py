from koiki.client import Client

import sugarcrm
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
        # here will come the code to update the Wordpress user role.
        pass


def _check_customer_is_partner(email):
    customer = Customer().fetch(email)
    # if the user in the crm has a role that it is considered as a LaZona partner/membership
    for role in customer.roles:
        if role in sugarcrm.membership_roles:
            customer.logger.info("{} has the membership role in the CRM".format(email))
            return True
    customer.logger.info("{} does not have the membership role in the CRM".format(email))

    return False
