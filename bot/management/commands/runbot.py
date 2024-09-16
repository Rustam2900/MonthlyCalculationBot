import logging
import sys
import asyncio

from django.core.management import BaseCommand

from bot.main import main


class Command(BaseCommand):
    help = "RUN COMMAND: python manage.py runbot"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
