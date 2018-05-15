from django_cron import CronJobBase, Schedule
from Workflow.utils import trelloToSQL, publish
from Bibliothek.utils import zotero_import

'''
Crontab Configuration:
*/5 * * * * "$(command -v bash)" -c 'cd /home/scholarium/scholarium_production && source venv/bin/activate && python manage.py runcrons'
'''


class cron_t2sql(CronJobBase):  # Not in use
    RUN_EVERY_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Trello to SQL Cronjob'

    def do(self):
        trelloToSQL()


class cron_publish(CronJobBase):
    RUN_EVERY_MINS = 10

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Publish article Cronjob'

    def do(self):
        return publish()


class cron_zotero(CronJobBase):
    RUN_AT_TIMES = ['04:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'Zotero Import Cronjob'

    def do(self):
        return zotero_import()
