#!/bin/bash
# saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset

OPTIONS=Mmsl
LONGOPTS=makemigrations,migrate,server,loaddata

# -use ! and PIPESTATUS to get exit code with errexit set
# -temporarily store output to be able to check for errors
# -activate quoting/enhanced mode (e.g. by writing out “--options”)
# -pass arguments only via   -- "$@"   to separate them correctly
! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    # e.g. return value is 1
    #  then getopt has complained about wrong arguments to stdout
    exit 2
fi
eval set -- "$PARSED"

M=n m=n s=n l=n
while true; do
    case "$1" in
        -M|--makemigrations)
            M=y
            shift
            ;;
        -m|--migrate)
            m=y
            shift
            ;;
        -l|--loaddata)
            l=y
            shift
            ;;
        -s|--server)
            s=y
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unsupported argument."
            exit 3
            ;;
    esac
done

if [[ $# -ne 1 ]]; then
    echo "$0: The database name is required."
    exit 4
fi

if psql -l | grep "$1 | $USER" &> /dev/null; then
    tput setaf 6; echo "Database found."
else
    tput setaf 1; echo "The specified database cannot be found."
    echo "Exiting."
    exit 5
fi

tput setaf 5; echo "Dropping database..."
dropdb $1

find . -name "migrations" | grep localhost | xargs rm -rf || true

tput setaf 5; echo "Creating database..."
createdb $1

if [ $M = y ]; then
    tput setaf 5; echo "Making migrations..."
    if [ $s = y ]; then
        ./manage.py makemigrations core report messaging dashboard authentication --settings localhost.settings_production
    else
        ./manage.py makemigrations core report messaging dashboard authentication
    fi
fi

if [ $m = y ]; then
    tput setaf 5; echo "Migrating..."
    if [ $s = y ]; then
        ./manage.py migrate --settings localhost.settings_production
    else
        ./manage.py migrate
    fi
fi

data1='testdata'
data2='propertyimages'
if [ $l = y ]; then
    tput setaf 5; echo "Loading data..."
    if [ $s = y ]; then
        ./manage.py loaddata $data1 $data2 --settings localhost.settings_production
    else
        ./manage.py loaddata $data1 $data2
    fi
fi

tput setaf 5; echo "Finished...exiting."
exit 0
