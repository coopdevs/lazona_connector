web: gunicorn lazona_connector.wsgi
release: python manage.py migrate
worker: celery -A api.tasks worker --loglevel=INFO
