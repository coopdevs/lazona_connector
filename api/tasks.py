from koiki.client import Client
from sugarcrm.client import Client as CrmClient
from sugarcrm import CrmError
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
def check_customer_is_partner(customer, created=True):
    crm_client = CrmClient()
    try:
        is_partner = crm_client.check_customer_is_partner(customer)
    except CrmError:
        return {"error": "Error connecting to CRM", "customer": customer}

    if is_partner:
        # here will come the code to update the Wordpress user role.
        pass

    # in case we will do daily cronjobs from the wordpress users to update to false their role
    # if their partner status has been removed from the CRM
    if not created:
        pass
    return {"is_partner": is_partner}
