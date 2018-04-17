#!/bin/bash

python manage.py migrate
python manage.py createcachetable

echo Starting uWSGI.
exec uwsgi --ini /config/uwsgi.ini
