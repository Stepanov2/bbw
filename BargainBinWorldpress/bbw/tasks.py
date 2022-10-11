from celery import shared_task
import time
# import logging
# import re

# from django.conf import settings

# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.contrib.auth.models import User
# from django.core.management.base import BaseCommand
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution
# from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
#
# from d5 import get_random_sentences
#
# from bbw.models import Post, SiteUser, Tags, Category, STRIP_HTML_TAGS
#
# import pytz


@shared_task
def hello():
    print('#' * 80)
    time.sleep(5)
    print('#' * 80)


@shared_task
def mail_test():
    weekly_email = EmailMultiAlternatives(subject='Sent via Celery',
                                          body='get_random_sentences(10)',
                                          from_email='test@testing.time',
                                          to=['test2@testing.time'])
    weekly_email.send()  # sending e-mail



