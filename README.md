# Dependencies
* Python>=3.7
* postgreSQL>=10.4
* psycopg2>=2.7.5

# Development
## Setup
Carefully follow these steps to set this project up:

### 1. Installing PostgreSQL
Choose package to install based on your distro.
```sh
sudo apt-get install postgresql postgresql-contrib # for ubuntu-based distro
sudo xbps-install -S postgresql postgresql-client # for void linux
sudo pacman -S postgresql # for arch-based distro
```
### 2. Database cluster initialization
```sh
sudo -u postgres -i
[postgres]$ initdb -D '/var/lib/postgres/data'
[postgres]$ systemctl enable postgresql.service
[postgres]$ systemctl start postgresql.service
[postgres]$ createuser --interactive  # use your own linux user name
[postgres]$ ^D
exit
```

### 3. Installing dependencies
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create database for development
```sh
createdb localhost_db
sudo -u postgres -i
psql
localhost_db=# GRANT ALL PRIVILEGES ON DATABASE localhost_db TO {username};
localhost_db=# ALTER ROLE {username} SET client_encoding TO 'utf8';
localhost_db=# ALTER ROLE {username} SET default_transaction_isolation TO 'read committed';
localhost_db=# \q
exit
```
Running the server
```sh
./manage.py makemigrations [app_label [app_label [...]]]
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
DB_USER={username} DB_PW={password} ./manage.py runserver --settings=localhost.settings_production
```

# Docker for bidding and messaging 
docker run -p 6379:6379 -d redis:2.8
