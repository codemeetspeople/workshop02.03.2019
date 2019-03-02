"""Database tasks."""

from invoke import Collection
from db.migrations.tasks.create import create
from db.migrations.tasks.shell import shell
from db.migrations.tasks.upgrade import upgrade, downgrade

ns = Collection('db', create)
ns.add_task(upgrade)
ns.add_task(downgrade)
ns.add_task(shell)

