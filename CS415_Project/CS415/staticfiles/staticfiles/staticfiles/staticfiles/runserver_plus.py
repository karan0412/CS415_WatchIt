from django.core.management.commands.runserver import Command as RunserverCommand
import os
from django.conf import settings

class Command(RunserverCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--cert', dest='cert', type=str, default='certs/localhost.crt')
        parser.add_argument('--key', dest='key', type=str, default='certs/localhost.key')

    def handle(self, *args, **options):
        cert = options.get('cert')
        key = options.get('key')
        if cert and key:
            self.stdout.write(f"Starting development server at https://{self.addr}:{self.port}/\n")
            self.run(*args, **options, use_reloader=True, use_ipv6=False, keyfile=key, certfile=cert)
        else:
            super().handle(*args, **options)