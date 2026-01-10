"""
Команда для сброса данных трекера.
Осторожно: удаляет все данные!
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from tracker.models import MetricType, MetricTarget, DailyMetric, BodyMeasurement, TrainingSession
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Сброс данных трекера (удаляет все данные, кроме пользователей)"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Автоматически подтвердить удаление"
        )
        parser.add_argument(
            "--keep-metrics",
            action="store_true",
            help="Не удалять типы метрик"
        )
        parser.add_argument(
            "--keep-targets",
            action="store_true",
            help="Не удалять нормативы"
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            confirm = input(
                "⚠️  ВНИМАНИЕ: Эта команда удалит все данные трекера!\n"
                "Удаляемые данные:\n"
                "- Ежедневные метрики\n"
                "- Замеры тела\n"
                "- Тренировки\n"
                f"- Типы метрик и нормативы\n\n"
                "Вы уверены? [y/N]: "
            )
            if confirm.lower() != "y":
                self.stdout.write("❌ Отменено")
                return

        with transaction.atomic():
            # Удаляем данные в правильном порядке (из-за внешних ключей)
            deleted_data = {}
            
            if not options["keep_targets"]:
                deleted_data["Нормативы"] = MetricTarget.objects.all().delete()[0]
            
            deleted_data["Ежедневные метрики"] = DailyMetric.objects.all().delete()[0]
            deleted_data["Замеры тела"] = BodyMeasurement.objects.all().delete()[0]
            deleted_data["Тренировки"] = TrainingSession.objects.all().delete()[0]
            
            if not options["keep_metrics"]:
                deleted_data["Типы метрик"] = MetricType.objects.all().delete()[0]

        # Выводим статистику
        self.stdout.write(self.style.SUCCESS("✅ Данные трекера сброшены!"))
        for model_name, count in deleted_data.items():
            if count > 0:
                self.stdout.write(f"  🗑️  Удалено {count} записей: {model_name}")
                