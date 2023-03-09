# Install

```bash
brew install libgeoip gdal
```
## Settings.py

Add the following

```python
import os
GDAL_LIBRARY_PATH = '/opt/homebrew/opt/gdal/lib/libgdal.dylib'
GEOS_LIBRARY_PATH = '/opt/homebrew/opt/geos/lib/libgeos_c.dylib'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    ## Added by Dave
    'django.contrib.gis',
    'steps'
]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get('db_name'),
        "USER": os.environ.get('db_user'),
        "PORT": os.environ.get('db_port'),
        "HOST": os.environ.get('db_host'),
        "PASSWORD": os.environ.get('db_password'),
        "OPTIONS" :{
            'options': '-c search_path=locaria_geodjango,public'
        }
    }
}
```

## Within venv (pycharm)

```bash
python -m pip install Django
pip install pyscopg2, Pillow

django-admin startproject stepsproto
cd stepsproto
python manage.py startapp steps

python manage.py makemigrations
python mange.py migrate

python manage.py createsuperuser
python manage.py runserver
```
## Clearing after altering model

- remove everything from migrations dir
- makemigrations
- migrate

## siteartifacts app

Idea here is to have a single app with editable site artifacts, specifically

- about
- contact us
- help
- privacy policy

```bash

python manage.py startapp siteartifacts
pip install django-ckeditor #for rich text editing
```

Add siteartifacts, ckeditor to INSTALLED_APPS

## Ordered model

```bash
pip install django-ordered-model
```

Add ordered_model.models to SETTINGS.INSTALLED_APPS






