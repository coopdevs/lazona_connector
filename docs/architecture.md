# Architecture

La Zona Connector follows a pretty standard web API architecture on a classic Django stack. It behaves as a glue between diverse services and as such, implements an API to listen to webhook events and sends requests to other APIs.

## API

The API is implemented as a Django app named [api] in a Django project called [lazona_connector].

This API responds to incoming webhook requests, so far only from Woocommerce, and because of that it expects request body's to stick to Woocommerce's REST API [docs].

Each integration is meant to have its own endpoint, mapping to a REST resource, such as `/api/deliveries` or `/api/customers` and implementing POST actions. These incoming requests are just event notifications although we try to stick to REST as much as we can. However, while events that trigger create actions fit well into the REST paradigm, events trigering updates don't because they don't come with a PUT method.

### 3rd party APIs

All the code related to communicating with 3rd parties is implemented as a separate Python module and used from a Django app.

These modules contain an API client plus domain objects, as if they were an SDK; with no La Zona-related logic. Check [koiki] for an example. This aims to set very clear boundaries between business-logic and 3rd parties. As a rule of thumb, it should be possible to publish them as Python packages in PyPi without having to refactor the code first.

So, any integration we implement will use one or many of these modules to communicate with 3rd party systems, such as the CRM, the shipping company, etc.

## Background jobs

All incoming webhook requests are handled asyncronously to avoid blocking the request for too long. Most of the triggered actions are heavy-weight, involving mutliple other HTTP requests, which would result in time-outs otherwise. Furthermore, webhooks are not concerned about the response as long as there's one. So, we send a response as quickly as possible and handle the action asyncronously.

### Celery tasks

Background jobs are implemented with [Celery] and Redis as backend.

All tasks should be short and do just one thing, possibly calling other tasks. Only this way we can provide a resilient system, gracefully handling errors. Although existing ones are still simple, Celery supports more complex workflows that we'll surely need in the future. This and other best practices are covered in Heroku's [Celery best practices], which is a recommended reading.


[api]: https://github.com/coopdevs/lazona_connector/tree/main/api
[lazona_connector]: https://github.com/coopdevs/lazona_connector/tree/main/lazona_connector
[docs]: https://woocommerce.github.io/woocommerce-rest-api-docs/#introduction
[Celery]: https://docs.celeryproject.org/en/stable/
[Celery best practices]: https://devcenter.heroku.com/articles/celery-heroku#celery-best-practices
[koiki]: https://github.com/coopdevs/lazona_connector/tree/main/koiki
