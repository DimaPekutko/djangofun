#!/bin/bash

sleep 15
python manage.py makemigrations --no-input
python manage.py migrate --no-input

python manage.py runserver 0.0.0.0:$PORT