"""Admin server task module."""

from invoke import task
from gunicorn.app.wsgiapp import WSGIApplication

from config import settings
from admin.app import app


@task(
    help={
        'bind': f'Bind to custom address or/and port. Default: {settings.api.host}:{settings.api.port}',
        'develop': 'Running server in dev mode. Default: False'
    }
)
def runserver(ctx, bind=None, develop=False):
    """Start Admin server."""
    if bind:
        host, port = bind.split(':')
    else:
        host, port = settings.admin.host, settings.admin.port

    if develop:
        executable = 'gunicorn'

        args = [executable, 'admin.app:app']
        args += ['-b', '{}:{}'.format(host, port)]
        args += ['--timeout', '600']
        args += ['--reload']

        g_app = WSGIApplication()
        g_app.run()
    else:
        app.run(debug=settings.debug, host=host, port=int(port))
        return
