#!/bin/bash

SECRET_KEY=$1
DB_USER=$2
DB_PW=$3

for j in {1..4}; do
    for i in 10 100 1000 10000 100000 1000000; do
        echo Trial $j / Size $i >> test_output.txt 2>&1
	echo '##################\n' >> test_output.txt 2>&1
	BATCH_SIZE=$i SECRET_KEY=$SECRET_KEY DB_USER=$DB_USER DB_PW=$DB_PW ../manage.py test localhost --noinput >> test_output.txt 2>&1
    done
done
