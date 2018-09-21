#!/bin/bash

tput setaf 6; echo "Installing nginx config..."
sudo ln -fs $PWD/nginx.conf /etc/nginx/sites-available/localhost.conf
sudo ln -fs /etc/nginx/sites-enabled/localhost.conf /etc/nginx/sites-available/localhost.conf

tput setaf 6; echo "Restarting nginx..."
sudo /etc/init.d/nginx stop
sudo /etc/init.d/nginx start

cd ..
source venv/bin/activate
tput setaf 6; echo "Restarting uwsgi..."
while $(killall uwsgi &> /dev/null); do
    sleep 1
done
SECRET_KEY="$1" DB_USER="$2" DB_PW="$3" uwsgi --socket :8001 --wsgi-file localhost/wsgi.py &> /tmp/uwsgi.log &
exit
tput setaf 6; echo "Finished...exiting."
