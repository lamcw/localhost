# Dependencies
* Python>=3.7
* postgreSQL>=10.4
* psycopg2>=2.7.5


# Setup
Carefully follow these steps to set this project up:

**Note: the following steps assumes that you have PostgreSQL installed and
configured correctly.**

## 1. Installing dependencies
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Create database
[follow this guide](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04)
```sh
sudo su - postgres
createdb placeholder_db
```
In `psql` session:
```
placeholder_db=# CREATE USER {your_username} WITH PASSWORD '{your_password}';
placeholder_db=# GRANT ALL PRIVILEGES ON DATABASE placeholder_db TO {your_username};
placeholder_db=# ALTER ROLE {your_username} SET client_encoding TO 'utf8';
placeholder_db=# ALTER ROLE {your_username} SET default_transaction_isolation TO 'read committed';
placeholder_db=# \q
exit
```
Running the server
```sh
DB_USER={your_username} DB_PW={your_password} python manage.py migrate
DB_USER={your_username} DB_PW={your_password} python manage.py runserver --settings=placeholder.settings_dev
```

# Development
To use development settings
```sh
python manage.py runserver --settings=placeholder.settings_dev
```

# Tests

# Deploy
