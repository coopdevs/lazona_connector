web: gunicorn lazona_connector.wsgi
release: python manage.py migrate
worker: celery -A api.tasks worker --beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
