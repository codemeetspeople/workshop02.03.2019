"""Synctool public API tasks."""

from invoke import Collection

from api.tasks.runserver import runserver

ns = Collection('api', runserver)
