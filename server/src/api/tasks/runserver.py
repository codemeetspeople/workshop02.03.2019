"""Run API server task."""

import asyncio
import uvloop
from aiohttp import web
from invoke import task

from api.app import init_server
from config import settings


@task(
    help={
        'bind': f'Bind to custom address or/and port. Default: {settings.api.host}:{settings.api.port}',
        'develop': 'Running server in dev mode. Default: False'
    }
)
def runserver(ctx, bind=None, develop=False):
    """Start Service API server."""
    if bind:
        host, port = bind.split(':')
    else:
        host, port = settings.api.host, settings.api.port

    if develop:
        executable = 'gunicorn'

        args = [executable, 'api.app:app']
        args += ['-b', '{}:{}'.format(host, port)]
        args += ['--timeout', '600']
        args += ['--reload']
        args += ['--worker-class aiohttp.worker.GunicornUVLoopWebWorker']

        ctx.run(' '.join(args))
    else:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        app = init_server()
        web.run_app(app, host=host, port=int(port))
