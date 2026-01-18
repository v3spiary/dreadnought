"""
Команда для инициализации трекера.
Создает типы метрик и нормативы по умолчанию.
"""


from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tracker.models import MetricTarget, MetricType

User = get_user_model()


class Command(BaseCommand):
    help = "Инициализация трекера: создание типов метрик и нормативов по умолчанию"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Имя пользователя для создания нормативов (по умолчанию для всех пользователей)",
        )
        parser.add_argument(
            "--skip-metrics",
            action="store_true",
            help="Пропустить создание типов метрик",
        )
        parser.add_argument(
            "--skip-targets",
            action="store_true",
            help="Пропустить создание нормативов",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Пересоздать существующие типы метрик",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🚀 Инициализация трекера..."))

        # Создание типов метрик
        if not options["skip_metrics"]:
            self.create_metric_types(force=options["force"])
        else:
            self.stdout.write("⏭️  Пропущено создание типов метрик")

        # Создание нормативов
        if not options["skip_targets"]:
            username = options.get("username")
            self.create_default_targets(username)
        else:
            self.stdout.write("⏭️  Пропущено создание нормативов")

        self.stdout.write(self.style.SUCCESS("✅ Инициализация завершена!"))

    def create_metric_types(self, force=False):
        """Создание типов метрик"""

        # Определяем типы метрик по умолчанию
        DEFAULT_METRICS = [
            # Питание
            {
                "code": "calories",
                "name": "Калории",
                "category": "nutrition",
                "unit": "kcal",
                "description": "Общая калорийность рациона",
                "order": 10,
            },
            {
                "code": "protein",
                "name": "Белок",
                "category": "nutrition",
                "unit": "g",
                "description": "Белок в граммах",
                "order": 11,
            },
            {
                "code": "fat",
                "name": "Жиры",
                "category": "nutrition",
                "unit": "g",
                "description": "Жиры в граммах",
                "order": 12,
            },
            {
                "code": "carbs",
                "name": "Углеводы",
                "category": "nutrition",
                "unit": "g",
                "description": "Углеводы в граммах",
                "order": 13,
            },
            {
                "code": "water",
                "name": "Вода",
                "category": "nutrition",
                "unit": "l",
                "description": "Потребление воды в литрах",
                "order": 14,
            },
            {
                "code": "fiber",
                "name": "Клетчатка",
                "category": "nutrition",
                "unit": "g",
                "description": "Пищевые волокна",
                "order": 15,
            },
            # Активность
            {
                "code": "sleep",
                "name": "Сон",
                "category": "activity",
                "unit": "hours",
                "description": "Продолжительность сна",
                "order": 20,
            },
            {
                "code": "steps",
                "name": "Шаги",
                "category": "activity",
                "unit": "steps",
                "description": "Количество шагов за день",
                "order": 21,
            },
            # Интеллект
            {
                "code": "math_tasks",
                "name": "Математические задачи",
                "category": "intellect",
                "unit": "count",
                "description": "Количество решенных задач",
                "order": 30,
            },
            {
                "code": "diary_entry",
                "name": "Дневник",
                "category": "intellect",
                "unit": "count",
                "description": "Ведение дневника (0/1)",
                "order": 31,
            },
            {
                "code": "leetcode_tasks",
                "name": "LeetCode задачи",
                "category": "intellect",
                "unit": "count",
                "description": "Количество задач LeetCode",
                "order": 32,
            },
            {
                "code": "ctf_tasks",
                "name": "CTF задачи",
                "category": "intellect",
                "unit": "count",
                "description": "Количество CTF задач",
                "order": 33,
            },
            {
                "code": "pages_read",
                "name": "Прочитанные страницы",
                "category": "intellect",
                "unit": "pages",
                "description": "Количество прочитанных страниц",
                "order": 34,
            },
            # Силовые
            {
                "code": "pushups",
                "name": "Отжимания",
                "category": "strength",
                "unit": "count",
                "description": "Количество отжиманий",
                "order": 40,
            },
            {
                "code": "crunches",
                "name": "Скручивания",
                "category": "strength",
                "unit": "count",
                "description": "Количество скручиваний",
                "order": 41,
            },
            {
                "code": "squats",
                "name": "Приседания",
                "category": "strength",
                "unit": "count",
                "description": "Количество приседаний",
                "order": 42,
            },
            {
                "code": "neck_training",
                "name": "Тренировка шеи",
                "category": "strength",
                "unit": "count",
                "description": "Упражнения для шеи",
                "order": 43,
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for metric_data in DEFAULT_METRICS:
                code = metric_data["code"]

                if force:
                    # Удаляем существующую метрику если force=True
                    MetricType.objects.filter(code=code).delete()

                obj, created = MetricType.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": metric_data["name"],
                        "category": metric_data["category"],
                        "unit": metric_data["unit"],
                        "description": metric_data.get("description", ""),
                        "order": metric_data.get("order", 0),
                        "is_active": True,
                    },
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        f"  ✅ Создана метрика: {metric_data['name']} ({code})"
                    )
                elif force:
                    updated_count += 1
                    self.stdout.write(
                        f"  🔄 Обновлена метрика: {metric_data['name']} ({code})"
                    )
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"📊 Типы метрик: создано {created_count}, обновлено {updated_count}, пропущено {skipped_count}"
            )
        )

    def create_default_targets(self, username=None):
        """Создание нормативов по умолчанию"""

        # Значения по умолчанию для нормативов
        DEFAULT_TARGETS = [
            # Питание
            {"code": "calories", "target_type": "max", "value": 2800},
            {"code": "protein", "target_type": "min", "value": 180},
            {"code": "fat", "target_type": "max", "value": 90},
            {"code": "carbs", "target_type": "max", "value": 300},
            {"code": "water", "target_type": "min", "value": 3.0},
            {"code": "fiber", "target_type": "min", "value": 30},
            # Активность
            {"code": "sleep", "target_type": "min", "value": 8.0},
            {"code": "steps", "target_type": "min", "value": 10000},
            # Интеллект
            {"code": "math_tasks", "target_type": "min", "value": 3},
            {"code": "diary_entry", "target_type": "min", "value": 1},
            {"code": "leetcode_tasks", "target_type": "min", "value": 1},
            {"code": "ctf_tasks", "target_type": "min", "value": 1},
            {"code": "pages_read", "target_type": "min", "value": 20},
            # Силовые (по желанию, можно комментировать)
            {"code": "pushups", "target_type": "min", "value": 50},
            {"code": "crunches", "target_type": "min", "value": 50},
            {"code": "squats", "target_type": "min", "value": 50},
            {"code": "neck_training", "target_type": "min", "value": 10},
        ]

        # Определяем пользователей
        if username:
            users = User.objects.filter(username=username)
            if not users.exists():
                self.stdout.write(
                    self.style.ERROR(f"❌ Пользователь '{username}' не найден")
                )
                return
        else:
            users = User.objects.all()
            self.stdout.write(
                f"👥 Создание нормативов для всех пользователей ({users.count()})"
            )

        created_count = 0
        skipped_count = 0
        today = timezone.now().date()
        next_year = today.replace(year=today.year + 1)

        for user in users:
            with transaction.atomic():
                for target_data in DEFAULT_TARGETS:
                    try:
                        metric_type = MetricType.objects.get(
                            code=target_data["code"], is_active=True
                        )
                    except MetricType.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠️  Метрика '{target_data['code']}' не найдена, пропуск"
                            )
                        )
                        continue

                    # Проверяем, существует ли уже норматив
                    existing = MetricTarget.objects.filter(
                        user=user,
                        metric_type=metric_type,
                        is_active=True,
                        valid_from__lte=today,
                        valid_to__gte=today,
                    ).exists()

                    if existing:
                        skipped_count += 1
                        continue

                    # Создаем норматив
                    MetricTarget.objects.create(
                        user=user,
                        metric_type=metric_type,
                        target_type=target_data["target_type"],
                        value=target_data["value"],
                        valid_from=today,
                        valid_to=next_year,
                        is_active=True,
                    )
                    created_count += 1

            self.stdout.write(
                f"  ✅ Созданы нормативы для пользователя: {user.username}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"🎯 Нормативы: создано {created_count}, пропущено (уже существуют) {skipped_count}"
            )
        )
