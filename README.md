# La Zona connector

This Django app aims to integrate Lazona's Woocommerce site to other services.
So far, Koiki's API, its delivery and distribution provider and the CRM, Sugar
CRM.

This is implemented using Django and Celery with Webhooks and API calls.

## Requirements

* Python 3.8.3
* PostgreSQL
* Redis
* [direnv](https://direnv.net/)

## Setup

You have two options to work on the project: to run the docker containers or to run the project manually.

### Run Docker

You can have the project up & running locally just with a command:
`docker-compose up`. 

You need to have an .env file created. Check the .env.example to see the required variables and their purpose. Run:

```
cp .env.example .env
```
Edit the variables on .env adding the actual data.

### Run manually

#### Python

First, install the Python versions listed above. We strongly recommend [pyenv]
with its [pyenv-virtualenv] plugin.

[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: pyenv-virtualenv

#### Database

We need to create lazona_connector database on PostgreSQL. Login to PostgreSQL using psql and create it.

```
CREATE DATABASE lazona_connector;
```

The app relies on PostgreSQL peer authentication to work with a simple database
configuration. To enable that add a new entry to the bottom of your pg_hba.conf,
which you'll find at `/etc/postgresql/<postgresql_version>/main/pg_hba.conf`, as
follows.

```
# TYPE  DATABASE          USER            ADDRESS                 METHOD
local   lazona_connector  <your_user>                             peer
```

Where `<your_user>` is your current user's name.

#### Redis

We use Celery with Redis as broker. The quickest way to set it up locally is:

```sh
$ docker run -p 6379:6379 redis
```

Alternatively, you can install the appropriate Redis package for your OS.

#### Direnv

We keep required config environment variables in `.envrc` which is managed by
[direnv](https://direnv.net/). Any time you modify that file, you'll need to run
`direnv allow`. You'll see an error message telling you so when cd-ing into the
project's directory.

You need to have an .envrc file created. Check the .envrc.example to see the required variables and their purpose. Run:

```
cp .envrc.example .envrc
```
Edit the variables on .envrc adding the actual data.

#### Django

Create a superuser to authenticate Woocommerce's webhook requests:

```
python manage.py createsuperuser --username woocommerce --email woocommerce@example.com
```


Once all previous points are setup run migrations to create the necessary tables on django

```
python manage.py migrate

```

## Usage

### Authentication

The API we expose for Woocommerce to send its webhook uses a signature mechanism. The signature is verified using our custom [SignatureValidaton](https://github.com/coopdevs/lazona_connector/blob/main/api/authentication.py).

### Sending a request to the connector

We'll need to configure our woocommerce instance to send requests to the connector.

First of all, define the webhook on WooCommerce / Ajustes / Avanzado / Webhooks

Afterwards, depending on the webhook defined, actions applied to Woocommerce orders will turn into API requests to the connector.


### Expose my local instance of the connector for testing

For developing purposes we'll use a staging Woocomerce version to create the request and we'll send them to our local instance. To do this we expose our localhost:8000 using ngrok.

You can read ngrok documentation [here](https://ngrok.com/product)
