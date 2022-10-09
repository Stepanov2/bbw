from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_delete, m2m_changed
from .views import Post as PostDetails
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import re

from .models import Post, SiteUser, Category, Tags, STRIP_HTML_TAGS


@receiver(post_save, sender=Post)
@receiver(m2m_changed, sender=Post.tags.through)
def mail_new_posts_to_users(sender, instance, created=False, **kwargs):
    """Mails posts to subscribed users on post creation.
    This function gets called 3 times.
    1. On Post.post_save signal.
    2. On m2m_changed.pre_add.
    3. On m2m_changed.post_add.
    We are interested in 1st and 3rd call.
    During first call we fetch category.subscribers and create e_mail headers.
    During third call we fetch tags.subscribers and send email.
    State is preserved between calls through func_name.var "static" variables.
    """

    if sender == Post and created:  # first call of the function (post_save)
        mail_new_posts_to_users.email_initiated = True  # this remembers that we started the e-mail generation process

        # preparing email
        mail_new_posts_to_users.subject = f'Newsandstuff - Новый пост "{instance.title}" от автора {instance.author}'
        mail_new_posts_to_users.body = re.sub(STRIP_HTML_TAGS, '', instance.content)
        mail_new_posts_to_users.html = render_to_string('post.html', {'post': instance,
                                                                      'render_comments': False,
                                                                      'short_preview': True,
                                                                      'is_for_email': True})

        # Adding people, who subscribed to category to the list of recipients.
        mail_new_posts_to_users.to_list = []
        mail_new_posts_to_users.to_list.extend([site_user.user.email for site_user in instance.category.subscribers.all()])
        print('Раз!')
        return

    elif sender == Post:  # Someone has modified the post, not created it. Abort!
        mail_new_posts_to_users.email_initiated = False
        print('Нэт!')

    # ******

    # If first part of email generation was successful, add people, who are subscribed to tags to list and send e-mail
    if sender == Post.tags.through and mail_new_posts_to_users.email_initiated and kwargs['action'] == 'post_add':
        print('Два!')

        for tag in instance.tags.all():
            mail_new_posts_to_users.to_list.extend([site_user.user.email for site_user in tag.subscribers.all()])

        mail_new_posts_to_users.to_list = list(set(mail_new_posts_to_users.to_list))

        # mail_new_posts_to_users.to_list now contains all the potential recepients of e-mail exactly once.
        # Ready to send!
        # Note: it is implied that splitting this e-mail into len(to_list) separate e-mails is done by mailing service

        mass_email = EmailMultiAlternatives(subject=mail_new_posts_to_users.subject,
                                            body=mail_new_posts_to_users.body,
                                            from_email='test@testing.time',
                                            to=mail_new_posts_to_users.to_list)
        mass_email.attach_alternative(mail_new_posts_to_users.html, "text/html")
        mass_email.send() # sending e-mail

        # and, finally, setting .email_initiated back to False, so the code can run again for another post
        mail_new_posts_to_users.email_initiated = False


@receiver(post_save, sender=User)  # todo
def add_new_user_to_site_users(sender, instance, created, **kwargs):
    pass


@receiver(post_save, sender=Post)
def add_one_to_post_count(sender, instance, created, **kwargs):
    user = instance.author
    if created:
        user.total_posts += 1
        user.save()


@receiver(pre_delete, sender=Post)
def subtract_one_from_post_count(sender, instance, **kwargs):
    user = instance.author
    user.total_posts -= 1
    user.save()
    print(f"Someone've killed post#{instance.pk}. How could (s)he?")


@receiver(post_save, sender=SiteUser)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        return
    subject = f'Добро пожаловать на Newsandstuff, {instance.display_username}'
    body = 'Ну кто читает plain text в 2022, а?..'
    html = render_to_string('welcome_email.html', {})
    mass_email = EmailMultiAlternatives(subject=subject,
                                        body=body,
                                        from_email='test@testing.time',
                                        to=[instance.user.email])
    mass_email.attach_alternative(html, "text/html")
    mass_email.send()  # sending e-mail