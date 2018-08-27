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

## 2. Create database for development
`username` = your Linux username
```sh
createdb placeholder_db
sudo su - postgres
psql
placeholder_db=# GRANT ALL PRIVILEGES ON DATABASE placeholder_db TO {username};
placeholder_db=# ALTER ROLE {username} SET client_encoding TO 'utf8';
placeholder_db=# ALTER ROLE {username} SET default_transaction_isolation TO 'read committed';
placeholder_db=# \q
exit
```
Running the server
```sh
./manage.py makemigrations # you may have to specify app label in order to generate all migration files
./manage.py migrate
./manage.py runserver
```

# Tests
```sh
./manage.py test [test_label]
```

# Deploy
Use production settings
```sh
DB_USER={username} DB_PW={password} ./manage.py runserver --settings=placeholder.settings_production
```
