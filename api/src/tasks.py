from invoke import Collection

from commons.tasks import shell
from db.migrations.tasks import ns as database_tasks
from admin.tasks import ns as admin_tasks

ns = Collection()
ns.add_task(shell)

ns.add_collection(database_tasks)
ns.add_collection(admin_tasks)
