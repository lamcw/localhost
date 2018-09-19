#!/bin/bash
# saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset

OPTIONS=Mml:
LONGOPTS=makemigrations,migrate,loaddata:

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

M=n m=n data=-
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
            data="$2"
            shift 2
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
    ./manage.py makemigrations core report messaging dashboard authentication
fi

if [ $m = y ]; then
    tput setaf 5; echo "Migrating..."
    ./manage.py migrate
fi

if [ $data != - ]; then
    tput setaf 5; echo "Loading data..."
    ./manage.py loaddata $data
fi

tput setaf 5; echo "Finished...exiting."
exit 0
