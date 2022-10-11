import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BargainBinWorldpress.settings')

app = Celery('BargainBinWorldpress')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fill_console_with_riveting_stuff': {
        'task': 'bbw.tasks.hello',
        'schedule': 20,
    },
    'send_weekly_digest': {  # todo change to more reasonable schedule =)
        'task': 'bbw.tasks.weekly_digest',
        'schedule': crontab(minute='*/2')  # crontab(hour=12, minute=0, day_of_week='sunday')
    }
}
