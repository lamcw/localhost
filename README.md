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
```sh
sudo su - postgres
createdb placeholder_db
exit
psql palceholder_db
```
In `psql` session:
```
placeholder_db=# CREATE USER admin WITH PASSWORD 'admin_password';
placeholder_db=# GRANT ALL PRIVILEGES ON DATABASE placeholder_db TO admin;
placeholder_db=# ALTER ROLE admin SET client_encoding TO 'utf8';
placeholder_db=# ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
```
Enter `\q` to exit the session.
```sh
python manage.py migrate
python manage.py runserver --settings=placeholder.settings_dev
```

# Development
To use development settings
```sh
python manage.py runserver --settings=placeholder.settings_dev
```

# Tests

# Deploy
