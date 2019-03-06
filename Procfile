web: PYTHONPATH=$(pwd)'/blogapi' gunicorn blogapi.wsgi:application --log-file -
worker: PYTHONPATH=$(pwd)'/blogapi' celery -A blogapi.celery_tasks worker --beat