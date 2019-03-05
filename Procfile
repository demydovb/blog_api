web: PYTHONPATH=$(pwd)'/blogapi' gunicorn blogapi.wsgi:application --log-file -
worker: celery -A celery_tasks worker --beat