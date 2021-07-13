# Operations

The infrastructure is all managed by Heroku as apps named
`lazona-connector-staging` and `lazona-connector-production`. This includes the
entire infrastructure: app servers, background workers, databases and
third-party services. You can see these by logging into
https://dashboard.heroku.com/ with the `Heroku Coopdevs` credentials in
Bitwarden. If you have access with your account, however, it's advisable you use
that one instead.



## Deployment

`lazona-connector-staging` is configured to automatically deploy on every commit
to `main`, so every merged pull request will be immediately available there,
which ensures that server contains the latest changes while ensuring `main` is
in a deployable state.

In any case, to deploy either to staging or production head over to the app's
[deploy] tab, scroll down to "Manual deploy" and choose the branch you want to
deploy, likely `main` and push the button.

Alternatively, if you have the Git remote configured as described in [Creating
a Heroku remote], you can do so from your terminal running `git push heroku
main`. More details: https://devcenter.heroku.com/articles/git.

## Restarting

If the app crashes for some reason and you want to restart it, after [logging in] from the CLI, Run:

```
$ heroku restart -a lazona-connector-production
```

Note you can replace `lazona-connector-production` with
`lazona-connector-staging` to restart staging instead.

## How to connect to the app

You can log into the app container as you would do with Docker. You can execute
commands on a new app container like:

```
$ heroku run python manage.py shell -a lazona-connector-production
```

which enables you to have shell access to the container like:

```
$ heroku run bash -a lazona-connector-production
```

## Troubleshooting

In case of an incident, you should look at the logs and the error tracker. 

### Logs

Go to the app's [Resources] tab and click on Papertrail, the third-party log
manager. From there you can watch the logs in real-time or use any of the saved
searches listed in its Dashboard.

You can also watch the logs as a stream from your terminal by running the
following command. However, that won't be very useful with high traffic.

```
$ heroku logs --tail -a lazona-connector-production
```

Note you can replace `lazona-connector-production` with
`lazona-connector-staging` to watch the staging's logs instead.

### Error tracking

Like the logs, the error tracking is managed as a Heroku add-on, Sentry, that
can reach from the [Resources] tab.

### Application Performance Monitoring

To have a view over the system performance and requests traces, click on Scout
APM from the [Resources] tab. That can give you an idea of where slow-downs are
coming from or if requets are piling up and thus, having a large request
queue time.


[deploy]: https://dashboard.heroku.com/apps/lazona-connector-staging/deploy/github
[Creating a Heroku remote]: https://devcenter.heroku.com/articles/git#creating-a-heroku-remote
[Resources]: https://dashboard.heroku.com/apps/lazona-connector-staging/resources
[logging in]: https://devcenter.heroku.com/articles/heroku-cli#getting-started
