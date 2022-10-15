from django.core.management.base import BaseCommand, CommandError
from django.core import management
from bbw.models import *


class Command(BaseCommand):
    help = 'Тестируем-с!'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"
    requires_migrations_checks = True

    def handle(self, *args, **options):
        self.stdout.readable()
        self.stdout.write(self.style.NOTICE('Хочеш котлетку? yes/no'))
        answer = input()  # считываем подтверждение

        if answer.lower() == 'yes':
            for author in SiteUser.objects.all():
                if author.total_posts:
                    self.stdout.write(self.style.SUCCESS(f'{author.display_username} запилил {author.total_posts} постов'))
                    management.call_command('othercommand', str(author.total_posts), red=False)
                else:
                    management.call_command('othercommand', author.display_username, red=True)
        else:
            self.stdout.write(self.style.ERROR('Ну и ладно!'))  # в случае неправильного подтверждения, говорим, что в доступе отказано