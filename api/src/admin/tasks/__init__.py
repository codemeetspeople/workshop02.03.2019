"""Admin tasks module."""

from invoke import Collection

from admin.tasks.runserver import runserver

ns = Collection('admin', runserver)
