from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, post_delete, pre_delete, m2m_changed
from .views import Post as PostDetails
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import re
from bbw.tasks import send_single_email
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
        # Generating tasks to send e-mails!
        for user in mail_new_posts_to_users.to_list:
            send_single_email.delay(subject=mail_new_posts_to_users.subject,
                                    html_body=mail_new_posts_to_users.html,
                                    body=mail_new_posts_to_users.body,
                                    from_email='test@testing.time',
                                    to_emails=[user])

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
    if not created:
        return

    subject = f'Добро пожаловать на Newsandstuff, {instance.display_username}'
    html = render_to_string('welcome_email.html', {})
    send_single_email.delay(subject=subject,
                            html_body=html,
                            from_email='test@testing.time',
                            to_emails=[instance.user.email])

@receiver(m2m_changed, sender=User.groups.through)
def update_author_editor_admin(sender, instance, **kwargs):
    """Changes status of SiteUser, when SiteUser is made author/editor/admin/ todo: is banned, is muted"""
    print(kwargs['action'])
    print(instance.__dict__)
    if kwargs['action'] in ('post_add', 'post_remove'):
        if kwargs['reverse']:
            return
        else:
            site_user = instance.siteuser
        # except Exception:
        #     site_user = siteuser = SiteUser.objects.create(user=instance, display_username=instance.username)

        site_user.is_author = bool(instance.groups.filter(pk=2))
        site_user.is_editor = bool(instance.groups.filter(pk=3))
        site_user.can_publish = bool(instance.groups.filter(pk=4))
        site_user.is_admin = bool(instance.groups.filter(pk=5))
        site_user.is_moderator = bool(instance.groups.filter(pk=6))
        site_user.save()
        print(site_user.__dict__)