import logging
import re

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from datetime import datetime, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from d5 import get_random_sentences

from bbw.models import Post, SiteUser, Tags, Category, STRIP_HTML_TAGS

import pytz

utc = pytz.UTC





logger = logging.getLogger(__name__)

POSTS_INTERVAL = 60*60*24*7  # seconds

# наша задача по выводу текста на экран
def my_job():
    "Slowly fills the console with riveting reading material"
    print(get_random_sentences())


def send_weekly_mails():
    """Make personalized emails for every User that subscribed to something"""
    one_week_ago = datetime.now() - timedelta(seconds=POSTS_INTERVAL)
    all_site_users=SiteUser.objects.all()
    for user in all_site_users:
        if not (user.category_set.all() or user.tags_set.all()):
            print(f'{user} has no active subscriptions')
            continue
        else:
            posts_for_user = []
            print(f'{user} HAS active subscriptions')
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
                print(f'Nothing to send to{user} this week, sadly!')
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
                                                       })+ '\n\n\n'
            html += render_to_string('email_footer.html')

            subject = f'Твой еже-{POSTS_INTERVAL}-секундный дайджест новостей от Newsandstuff, {user}'
            body = re.sub(STRIP_HTML_TAGS, '', html).replace('\n\n', '\n')  # Whatever! Good enough
            weekly_email = EmailMultiAlternatives(subject=subject,
                                                  body=body,
                                                  from_email='test@testing.time',
                                                  to=[user.user.email])
            weekly_email.attach_alternative(html, "text/html")
            weekly_email.send()  # sending e-mail
            print(f'SENT EMAIL FOR {user}!')

    pass


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/5"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        scheduler.add_job(
            send_weekly_mails,
            trigger=CronTrigger(second="*/10"),  # todo paste POSTS_INTERVAL here
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="send_weekly_mails",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")