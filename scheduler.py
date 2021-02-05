from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

def fn():
    print('Hello, world!')

sched = BlockingScheduler()

# Execute fn() at the start of each minute.
sched.add_job(fn, trigger=CronTrigger(second=00))
sched.start()