# ifbcat

ifbcat is the database hosting and serving the IFB Catalogue through a REST API.

# How to contribute

## How code is formatted

Code is formatted using https://github.com/psf/black. Please use pre-commit along with black to commit only well formatted code:
```
#install dependencies
pip install -r requirements-dev.txt
#enable black as a pre-commit hook which will prevent committing not formated source 
pre-commit install
#run black as it will be before each commit
pre-commit run black
```

## run the db locally
```
docker-compose run db
```
also do not forget to [create a superuser](#create-a-superuser)

# How to manage the server

*All of this consider that you already are on the server and you are sudoer* 

## Restart the service
```
sudo service ifbcat restart
```

## Pull the latest sources and restart
```
cd /var/ifbcat-src
sudo git pull
sudo service ifbcat restart
```

## Create a superuser
```
cd /var/ifbcat-src
sudo docker-compose exec web python manage.py createsuperuser
```

## Do some import
```
cd /var/ifbcat-src
sudo docker-compose run -v /var/ifbcat-importdata:/import_data web python manage.py load_persons /import_data/persons.csv /import_data/drupal_db_dump/users.txt
sudo docker-compose run -v /var/ifbcat-importdata:/import_data web python manage.py load_bioinformatics_teams /import_data/platforms.csv
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