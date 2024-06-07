# myapp/management/commands/backup_db.py

from django.core.management.base import BaseCommand
from WatchIt.utils import backup_database

class Command(BaseCommand):
    help = 'Backup the database'

    def handle(self, *args, **kwargs):
        backup_file = backup_database()
        if backup_file:
            self.stdout.write(self.style.SUCCESS(f'Backup successful: {backup_file}'))
        else:
            self.stdout.write(self.style.ERROR('Backup failed'))
