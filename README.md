# La Zona connector

This Django app aims to integrate Lazona's Woocommerce site to Koiki's API, its
delivery and distribution provider.

## Requirements

* Python 3.8.3
* PostgreSQL
* [direnv](https://direnv.net/)

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

### Direnv

We keep required config environment variables in `.envrc` which is managed by
[direnv](https://direnv.net/). Any time you modify that file, you'll need to run
`direnv allow`. You'll see an error message telling you so when cd-ing into the
project's directory.

## Usage

### Authentication

The API we expose for Woocommerce to send its webhook requests requires token
authentication.

To generate one you need to create a Django superuser and then to create a token
for it. You can do so running the commands:

```
python manage.py createsuperuser --username pau --email pau@example.com
python manage.py drf_create_token pau
```

This will give you the token to use with the `Authorization` HTTP header in your
requests like `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`.
See:
https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication.

### Running in development

We recommend [HTTPie](https://httpie.io/) to send requests to the API. It helps
a great deal in managing the request bodies and authentication against the API.

Once installed, make sure you have a user and a token for it in the DB.
You can build an anonymous session like the one below.

```json
# session.json
{
    "__meta__": {
        "about": "HTTPie session file",
        "help": "https://httpie.org/doc#sessions",
        "httpie": "1.0.3"
    },
    "auth": {
        "password": null,
        "type": null,
        "username": null
    },
    "cookies": {},
    "headers": {
        "Accept": "application/json, */*",
        "Authorization": "Token <put_your_token_here>"
    }
}
```

then you need a dummy JSON body to send:

```json
# data.json
{
  "order_key": "abc",
  "shipping": {
    "first_name": "John",
    "last_name": "Lennon",
    "address_1": "Beatles Street 66",
    "address_2": "",
    "postcode": "08032",
    "city": "Barcelona",
    "state": "Barcelona",
    "country": "ES"
  },
  "billing": {
    "phone": "666666666",
    "email": "lennon@example.com"
  },
  "customer_note": "prueba"
}
```

Now, provided that we point to the Koiki's staging environment by default (see
`.envrc`), you can run the dev server as `python manage.py runserver` and send
requests as follows.

```sh
$ http --json post http://127.0.0.1:8000/api/deliveries/ \
   --session=./session.json \
   < data.json

HTTP/1.1 201 Created
Allow: POST, OPTIONS
Content-Length: 279
Content-Type: application/json
(...)
```
