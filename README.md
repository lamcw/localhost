# localhost

## Dependencies
* Python>=3.6.5
* pip>=18.1
* PostgreSQL>=9.6.10
* Redis>=4.0.9

localhost is a real-time property auction platform tailored for short stays.
It was developed by team *Undergrads* for the capstone course [COMP3900: Computer Science Project](http://legacy.handbook.unsw.edu.au/undergraduate/courses/2018/COMP3900.html) in Semester 2 2018 at [UNSW](https://www.unsw.edu.au/).

![localhost splash page](screenshot.jpg)

## Contributing
### Setup

#### Install PostgreSQL
```sh
# pacman -S postgresql                          # for arch-based distros
# apt-get install postgresql postgresql-contrib # for debian-based distros
# xbps-install -S postgresql postgresql-client  # for void linux
```

#### Create database cluster
```sh
$ sudo -u postgres -i
[postgres]$ initdb -D '/var/lib/postgres/data'
[postgres]$ createuser --interactive  # use your own linux user name
[postgres]$ ^D
```

Note that the path `/var/lib/postgres` differs between distributions. The directory should be created when *postgresql* is installed so verify its location before running `initdb`.

In the `data` folder for the *postgres* installation, there is a file called `pg_hba.conf`. This file is responsible for how authentication is managed on the service. On general desktop distributions such as *Arch* and *Debian*, entries are configured with the value `trust`. This allows for use by accounts without passwords. On server tailored distributions such as *Gentoo* and *Ubuntu Server*, *postgres* is more likely to be configured to require password authentication - so an account with credentials must be made instead. If there's any doubt, review the bottom of `pg_hba.conf` to check whether or not `trust` is used and configure accordingly.

#### Enable postgresql service
For `systemd`:
```sh
# systemctl enable postgresql.service
# systemctl start postgresql.service
```

For `runit`:
```sh
# ln -s /etc/sv/postgresql /var/service/
```

#### Create database for development
```sh
$ createdb localhost_db
$ sudo -u postgres -i
[postgres]$ psql
localhost_db=# GRANT ALL PRIVILEGES ON DATABASE localhost_db TO {username};
localhost_db=# ALTER ROLE {username} SET client_encoding TO 'utf8';
localhost_db=# ALTER ROLE {username} SET default_transaction_isolation TO 'read committed';
localhost_db=# \q
[postgres]$ exit
```

#### Clone repository and set up a Python virtual environment
```sh
$ git clone git@github.com:lamcw/localhost.git && cd localhost
$ python -m venv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
```

#### Celery
To start the celery service, run:
```sh
celery -A localhost worker -l info -E -B
```
This is only used in development. To use Celery in production, see [here](http://docs.celeryproject.org/en/latest/userguide/daemonizing.html#daemonizing)

#### Install Redis
```sh
# apt-get install redis-server # for debian based distros
# xbps-install -S redis        # for void linux
```

A server instance can now be started with:
```sh
$ redis-server
```

As the project uses the default port, no further configuration should be required.

### Development

#### Rebuild tool

To automate the process dropping, creation and repopulation of the development
database, a bash script was written and is available in the project root.
```sh
$ ./rebuild.sh [database name] -Mmsl [data name]
```

* `-M` is short for `--Makemigrations`
* `-m` is short for `--migrate`
* `-s` is short for `--server` and should only be used on the server deployment
* `-l` is short for `--loaddata` and loads both `testdata` and `propertyimages`

This can be used immediately after *Setup* with `./rebuild.sh localhost_db -Mml`.
If only one of the test sets is required, simply omit `-l` and load the set manually.

To export data in database,
```sh
./manage.py dumpdata --indent=2 --natural-foreign core django_celery_beat authentication [other apps] -o [file]
```

To export data in database,
```sh
./manage.py dumpdata --indent=2 --natural-foreign core django_celery_beat authentication [other apps] -o [file]
```

#### Testing

To run the tests you must specify the batch size used for the testing database:
```sh
$ BATCH_SIZE=100 python manage.py test localhost.core.tests
```

#### Logging
To set logging level, use `DJANGO_LOG_LEVEL` environment variable. See the list
of logging levels [here](https://docs.python.org/3/library/logging.html#logging-levels).

#### Linters

Strongly recommended is the [ALE](https://github.com/w0rp/ale) plugin for *vim* and *neovim*.

In the Python section of the *ALE* documentation, all the support linters are listed. They can be installed using `pip` as follows; only are subset are installed in the following example.

```
$ pip3 install flake8 pylint python-language-server --user
```

*vim* and *neovim* must then be configured to allow autocompletion and to select the installed linters.

```
$ cat ~/.config/nvim/init.vim

...

let g:ale_completion_enabled = 1
let g:ale_linters = {
\   'python': ['flake8', 'pylint', 'pyls']
\}
```

Not all the linters provided in the *ALE* documentation are good quality and some may not run well alongside others. Add each linter one at a time and watch for unacceptable performance drops before continuing.

#### Style Guide
Python code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/?) and docstring should follow [Google style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings).

#### Branches and pull requests

* `master` contains the latest stable release.
* `dev` contains a *moderately* stable release that is being prepared for merge into `master`.

All development work should be done on custom branches off `dev`. When a feature is complete,  a pull request should be made to be reviewed by other members of the development team.

##### Reviews

* If there are code corrections to be made, request them to be made before the pull request is merged. 
* Ensure that the changes do not break any functionality.

## Deployment

Please note that while this README is updated in the `dev` branch of the repository, the server ***must*** be deployed under the `master` branch. Server specific fixes are directly committed to the `master` branch.

`localhost` is deployed on an EC2 AWS instance running Ubuntu 18.04.1 LTS. The distribution can be installed through the community marketplace. The path of the repository, for consistency, is `/home/ubuntu/localhost/`.

### Port Forwarding Configuration

On the EC2 Dashboard, navigate to the running instance with `localhost`, scroll to the far right and select 'launch-wizard'. This will open a tab for configuring ports at the bottom on the page. Ports `80` and `443` must be enabled.

### Services

#### Django

[Django](https://www.djangoproject.com/) follows the same instructions as in Development with only minor differences:
* The environment variable `SECRET_KEY` must be set when running commands requiring it.
* Django must be run using `settings_production.py`.

#### PostgreSQL

[PostgresSQL](https://www.postgresql.org/) follows the same instructions as in Development with only minor differences:
* `initdb` may not be in the path and require you to use the full path to the script.
* `pg_hba.conf` will require password authentication for the database. After creating an account, the `\password` command must be used in the `psql` shell to set a password.
* Environment variables `DB_USER` and `DB_PW` must be manually set when running commands requiring them.

#### NGINX

[NGINX](https://www.nginx.com/) is used as the web server. `deploy/nginx.conf` contains the required configuration for the server.
* Requests to port 80 are automatically redirected to port 443.
* SSL certificates are installed using [certbot](https://certbot.eff.org/) with [Let's Encrypt](https://letsencrypt.org/). On a fresh install *certbot* should automatically use the certificates that have already been registered. Certificates must be renewed every three months.
* Serves media and static files.
* Websocket requests are redirected to a local network port that *Daphne* listens to.
* Remaining requests are redirected to a file socket at `/home/ubuntu/localhost.sock` that *Gunicorn* listens to.

#### Gunicorn

*NGINX* cannot interface with *Django* directly. [Gunicorn](https://gunicorn.org/) is used to handle requests from *NGINX* that require *Django*.

The service script required can be found in `deploy/systemd/gunicorn.service`. The environment variables for `SECRET_KEY`, `DB_USER`, and `DB_PW` must be set prior to enabling. Below `Environment="DJANGO_SETTINGS_MODULE=localhost.settings_production"` add:

```
Environment="SECRET_KEY=YOUR KEY HERE"
Environment="DB_USER=ubuntu"
Environment="DB_PW=YOUR DB PASSWORD HERE"
```

#### Daphne

[Daphne](https://github.com/django/daphne) is used as a WebSocket protocol server for Django Channels. *NGINX* redirects all WebSocket requests to a local network socket for *Daphne* to operate on.

The service script required can be found in `deploy/systemd/daphne.service`. The environment variables for `SECRET_KEY`, `DB_USER`, and `DB_PW` must be set prior to enabling. Below `Environment="DJANGO_SETTINGS_MODULE=localhost.settings_production"` add:

```
Environment="SECRET_KEY=YOUR KEY HERE"
Environment="DB_USER=ubuntu"
Environment="DB_PW=YOUR DB PASSWORD HERE"
```

### init.sh

To automate the installation / update of the `NGINX` configuration script and to restart the services a script is provided at `deploy/init.sh`. It requires sudo privileges.

```
# ./init.sh
Installing nginx config...
Restarting services...
Finished...exiting.
```

This should be run whenever a rebuild takes place.
