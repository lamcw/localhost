#!/bin/bash
tput setaf 6; echo "Installing nginx config..."
ln -fs /home/ubuntu/localhost/deploy/nginx/localhost.conf /etc/nginx/sites-available/
ln -fs /etc/nginx/sites-available/localhost.conf /etc/nginx/sites-enabled/

tput setaf 6; echo "Updating static..."
source /home/ubuntu/localhost/venv/bin/activate
python /home/ubuntu/localhost/manage.py collectstatic --no-input
deactivate

tput setaf 6; echo "Restarting services..."
systemctl restart nginx.service gunicorn.service daphne.service celery.service celery-beat.service

tput setaf 6; echo "Finished...exiting."
