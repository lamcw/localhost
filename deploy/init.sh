#!/bin/bash
tput setaf 6; echo "Installing nginx config..."
ln -fs $PWD/nginx/localhost.conf /etc/nginx/sites-available/
ln -fs /etc/nginx/sites-available/localhost.conf /etc/nginx/sites-enabled/

tput setaf 6; echo "Restarting services..."
systemctl restart nginx.service gunicorn.service daphne.service

tput setaf 6; echo "Finished...exiting."
