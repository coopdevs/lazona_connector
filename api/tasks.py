from koiki.client import Client
from lazona_connector.celery import app


@app.task
def create_delivery(order):
    Client(order).create_delivery()
