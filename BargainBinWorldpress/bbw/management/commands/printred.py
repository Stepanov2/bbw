from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Печатает красным, если --red'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('what', nargs=1, type=str)
        parser.add_argument('--red', action='store_true', help='Красненького?')

    def handle(self, *args, **options):
        # здесь можете писать любой код, который выполнится при вызове вашей команды
        self.stdout.readable()
        if options['red']:
            self.stdout.write(self.style.NOTICE(f'{args}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'{args}'))
