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
