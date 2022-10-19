from django.core.management.base import BaseCommand, CommandError
from django.core import management


class Command(BaseCommand):
    help = 'Печатает hello.'  # показывает подсказку при вводе "python manage.py <ваша команда> --help"

    def handle(self, *args, **options):
        self.stdout.readable()
        self.stdout.write(self.style.NOTICE('Хочешь красненьким напечатаем? yes/no'))
        answer = input()  # считываем подтверждение

        if answer.lower() == 'yes':
            management.call_command('printred', 'hello', red=True)
        else:
            management.call_command('printred', 'hello')
