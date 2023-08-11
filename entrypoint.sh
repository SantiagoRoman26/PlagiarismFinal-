#!/bin/sh

echo 'Running collecstatic...'
python manage.py collectstatic --no-input --settings=PlagiarismDetector.settings.production

echo 'Applying migrations...'
python manage.py wait_for_db --settings=PlagiarismDetector.settings.production
python manage.py migrate --settings=PlagiarismDetector.settings.production

echo 'Running server...'
gunicorn --env DJANGO_SETTINGS_MODULE=PlagiarismDetector.settings.production PlagiarismDetector.wsgi:application --bind 0.0.0.0:$PORT