#!/bin/bash
python manage.py makemigrations api
python manage.py makemigrations django_celery_results
python manage.py makemigrations
python manage.py migrate 
python manage.py collectstatic
python manage.py runserver 0.0.0.0:2006
# gunicorn --bind "0.0.0.0:2006" persona_backend.wsgi 
