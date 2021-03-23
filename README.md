# La Zona connector

This Django app aims to integrate Lazona's Woocommerce site to Koiki's API, its
delivery and distribution provider.

## Requirements

* Python 3.8.3
* PostgreSQL

## Setup

### Python

First, install the Python versions listed above. We strongly recommend [pyenv]
with its [pyenv-virtualenv] plugin.

### Database

The app relies on PostgreSQL peer authentication to work with a simple database
configuration. To enable that add a new entry to the bottom of your pg_hba.conf,
which you'll find at `/etc/postgresql/<postgresql_version>/main/pg_hba.conf`, as
follows.

```
# TYPE  DATABASE          USER            ADDRESS                 METHOD
local   lazona_connector  <your_user>                             peer
```

Where `<your_user>` is your current user's name.

[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: pyenv-virtualenv

## Usage

### Authentication

The API we expose for Woocommerce to send its webhook requests requires token
authentication.

To generate one you need to create a Django superuser and then to create a token
for it. You can do so running the commands:

```
python manage.py createsuperuser --username pau --email
pau@example.com
python manage.py drf_create_token pau
```

This will give you the token to use with the `Authorization` HTTP header in your
requests like `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`.
See:
https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication.
