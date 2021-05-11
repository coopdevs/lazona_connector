from koiki.client import Client
from lazona_connector.celery import app


@app.task
def create_delivery(order):
    delivery = Client(order).create_delivery()

    if type(delivery).__name__ == 'Error':
        return delivery.to_dict()
    else:
        delivery.print_pdf()
        return {'success': 'all good'}
