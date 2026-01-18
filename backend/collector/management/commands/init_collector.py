"""
Команда для инициализации коллектора.
TODO.
"""


from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = "Инициализация коллектора. В разработке."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🚀 Инициализация коллектора..."))
