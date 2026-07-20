import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import InterfaceError, OperationalError


class Command(BaseCommand):
    help = "Wait for the database to become available."

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")

        database_available = False

        while not database_available:
            try:
                connections["default"].ensure_connection()
                database_available = True
            except (InterfaceError, OperationalError):
                self.stdout.write(
                    "Database unavailable, waiting 1 second..."
                )
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS("Database available!")
        )
