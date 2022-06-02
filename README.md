# ifbcat

ifbcat is the database hosting and serving the [IFB Catalogue](https://catalogue.france-bioinformatique.fr/) through a REST API.

# How to contribute

## How code is formatted

Code is formatted using https://github.com/psf/black (version 20.8b1). Please use pre-commit along with black to commit only well formatted code:
```
#install dependencies
pip install -r requirements-dev.txt
#enable black as a pre-commit hook which will prevent committing not formated source
pre-commit install
#run black as it will be before each commit
pre-commit run black
```

## Run the API locally

1. Install requirements:

  * [docker](https://docs.docker.com/get-docker/),
  * [docker-compose](https://docs.docker.com/compose/install/),
  * postgresql-devel (libpq-dev in Debian/Ubuntu, libpq-devel on Centos/Cygwin/Babun.),
  * Virtual env,
  * requirements.txt

```
virtualenv .venv -p python3
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run the DB locally:
```
# Copy (and optionally tweak) ini 
cp resources/default.ini local.ini
cp ifbcat/settings.example.ini ifbcat/settings.ini
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml run db
```
Note that a volume is created. To remove it run:
```sh
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down --volumes
```

3. Retrieve import data (ask access to private repository if needed):
```
git clone git@github.com:IFB-ElixirFr/ifbcat-importdata.git import_data
```

4. Run tests:
```
python manage.py test
```
Currently, you should expect to see some "ERROR" but tests should be "OK" in the end of the log. 

5. Do migrations, superuser creation, some imports and start the test server:
```
python manage.py migrate
python manage.py createsuperuser
python manage.py load_catalog
python manage.py runserver
```

6. You can do more imports using commands available in `ifbcat_api/management/commands`. Some are not currently working
   properly but at least these ones below should.

```
python manage.py load_catalog
python manage.py load_biotools
```

## Run the API locally with only docker-compose

You can run the webserver within the docker-compose, it allows you to not have a fully functional virtualenv (without
psycopg2-binary system library for example). The drawback is that you will not be able to use the debugger of your IDE.

1. Retrieve data

```
git clone git@github.com:IFB-ElixirFr/ifbcat-importdata.git ./import_data
```

2. Build and start the whole compose with dev settings

```
# Copy (and optionally tweak) ini 
cp resources/default.ini local.ini
docker-compose build
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d
```

The webserver is running at http://0.0.0.0:8080 (the instance on 8000 does not have css served)

3. Create a superuser, do some imports

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py load_catalog
```

4. Do some cleanup
To remove db volumes run:
```sh
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down --volumes
```
To remove build and pulled images:
```sh
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml down --rmi all
```

# How to manage the server

*All of this consider that you already are on the server and you are sudoer*

## Restart the service

```
sudo service ifbcat restart
```

## Pull the latest sources and restart
 * Restart stop the service, flush old images from disk, rebuild images and start the service. It clean up the server and helps in case of server full error 
```
cd /var/ifbcat-src
sudo git pull
sudo service ifbcat restart
```
 * Reload will rebuild the service before restarting it, it does not remove old image. It is faster
```
cd /var/ifbcat-src/ && sudo git pull && sudo service ifbcat reload
```
## Create a superuser
```
cd /var/ifbcat-src
sudo docker-compose exec web python manage.py createsuperuser
```

## Do some import
```
cd /var/ifbcat-src
sudo docker-compose -f docker-compose.yaml -f docker-compose.import.yaml run web python manage.py load_users
sudo docker-compose -f docker-compose.yaml -f docker-compose.import.yaml run web python manage.py load_biotools
```

Or all imports :
```
sudo docker-compose -f docker-compose.yaml -f docker-compose.import.yaml run web python manage.py load_catalog
```

# How to generate graph models

To export the models to an image, you hav to:
 * uncomment django_extensions in settings.py
 * and then run this:
```bash
pip install pygraphviz django-extensions
python manage.py graph_models -a -g -o ifb_cat.png
python manage.py graph_models -a -g -o ifb_cat.svg
```
