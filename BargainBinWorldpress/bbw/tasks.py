from celery import shared_task
from typing import Union
import time
# import logging
import re

# from django.conf import settings

# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
# from django.core.management.base import BaseCommand
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution
from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
#
from d5 import get_random_sentences
#
from bbw.models import Post, SiteUser, Tags, Category, STRIP_HTML_TAGS
#
import pytz

# =====

utc = pytz.UTC
POSTS_INTERVAL = 60*60*24*7  # seconds


@shared_task
def hello():
    print(get_random_sentences())


@shared_task
def send_single_email(subject: str,
                      to_emails: Union[str, list],
                      from_email: Union[str, None] = 'test@testing.time',
                      body: Union[str, None] = None,
                      html_body: Union[str, None] = None) -> str:
    """Send an email. Will generate body from html_body if needed.
    Despite the name this function will accept a list of recipients.
    But you shouldn't use it this way, (unless you are emailing stuff)
    as it will leak the list of emails to everyone on that list.
    """

    # prep work
    if body is None and html_body is None:
        raise ValueError('This function needs either body or html_body parameter to work!')
    if body is None:  # generate plain-text body from html
        body = re.sub(STRIP_HTML_TAGS, '', html_body).replace('\n\n', '')
    if from_email is None:
        from_email = 'test@testing.time'
    if not isinstance(to_emails, list):  # convert str to list
        to_emails = [to_emails]

    # generating e-mail.
    my_email = EmailMultiAlternatives(subject=subject,
                                          body=body,
                                          from_email=from_email,
                                          to=to_emails)
    if html_body is not None:
        my_email.attach_alternative(html_body, "text/html")
    my_email.send()  # sending e-mail

    return f'Sent a letter "{subject}" to {str(to_emails)}'


@shared_task
def weekly_digest() -> str:
    """Make personalized emails for every User that subscribed to something"""
    one_week_ago = datetime.now() - timedelta(seconds=POSTS_INTERVAL)
    all_site_users = SiteUser.objects.all()
    for user in all_site_users:
        if not (user.category_set.all() or user.tags_set.all()):
            print(f'{user} has no active subscriptions')
            continue
        else:
            posts_for_user = []
            print(f'{user} HAS active subscriptions!', end=' ')
            # getting posts for users

            # COMMENT THESE LINES FOR PRODUCTION
            # these are for debug (no date filtering = lots of posts to include in e-mail)
            posts_for_user.extend(Post.objects.filter(category__in=user.category_set.all()))
            posts_for_user.extend(Post.objects.filter(tags__in=user.tags_set.all()))

            # UNCOMMENT THESE LINES FOR PRODUCTION
            # posts_for_user.extend(Post.objects.filter(category__in=user.category_set.all(),
            #                                           publication_date__gt=one_week_ago,
            #                                           publication_date__lt=datetime.now(tz=utc)))
            # posts_for_user.extend(Post.objects.filter(tags__in=user.tags_set.all(),
            #                                           publication_date__gt=one_week_ago,
            #                                           publication_date__lt=datetime.now(tz=utc)))

            if not len(posts_for_user):
                print(f'Nothing to send to {user} this week, sadly!')
                continue

            posts_for_user = list(set(posts_for_user))
            posts_for_user = sorted(posts_for_user,
                                    key=lambda x: x.publication_date if x.publication_date is not None
                                    else utc.localize(datetime(year=2050, month=1, day=1, hour=0, minute=0, second=0)),
                                    reverse=True)
            # Todo: above voodoo should not be necessary once I finally implement Post.is_published signal
            # print(posts_for_user)

            # rendering html body
            html = render_to_string('email_header.html')
            for post in posts_for_user:
                html += render_to_string('post.html', {'post': post,
                                                       'render_comments': False,
                                                       'short_preview': True,
                                                       }) + '\n\n\n'
            html += render_to_string('email_footer.html')

            subject = f'Твой еже-{POSTS_INTERVAL}-секундный дайджест новостей от Newsandstuff, {user}'
            send_single_email.delay(subject=subject,
                                    html_body=html,
                                    from_email='test@testing.time',
                                    to_emails=[user.user.email])
            print(f'PLANNED an email for {user}!')

    return f'Successfully created tasks for weekly digest!'



