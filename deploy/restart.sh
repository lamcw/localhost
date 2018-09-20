#!/bin/bash

tput setaf 1; echo "Requires system privileges"
tput setaf 6; echo "Installing nginx config..."
sudo ln -fs $PWD/nginx.conf /etc/nginx/sites-enabled/localhost.conf

tput setaf 6; echo "Restarting nginx..."
sudo /etc/init.d/nginx stop
sudo /etc/init.d/nginx start

tput setaf 6; echo "Starting uwsgi..."
sudo su ubuntu
source ../venv/bin/activate
SECRET_KEY="$1" DB_USER="$2" DB_PW="$3" uwsgi --socket :8001 --wsgi-file ../localhost/wsgi.py
exit

tput setaf 6; echo "Finished...exiting."
