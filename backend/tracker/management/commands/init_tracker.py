from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tracker.models import FlexibleGoal, UserProfile


class Command(BaseCommand):
    help = "Инициализация начальных данных для трекера"

    def handle(self, *args, **options):
        self.stdout.write("Начинаем инициализацию начальных данных...")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(
                self.style.SUCCESS("Создан суперпользователь admin/admin")
            )

        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f"Создан профиль для пользователя {user.username}")

            standard_goals = [
                {
                    "name": "Тренировки в неделю",
                    "description": "Посещать тренажерный зал минимум 3 раза в неделю",
                    "target_value": 3,
                    "period": "WEEK",
                },
                {
                    "name": "Книги в месяц",
                    "description": "Прочитать 1 книгу в месяц (условно 300 страниц)",
                    "target_value": 300,
                    "period": "MONTH",
                },
                {
                    "name": "LeetCode в неделю",
                    "description": "Решить 7 задач LeetCode в неделю",
                    "target_value": 7,
                    "period": "WEEK",
                },
                {
                    "name": "Математические задачи в месяц",
                    "description": "Решить 50 математических задач в месяц",
                    "target_value": 50,
                    "period": "MONTH",
                },
                {
                    "name": "CTF задачи в квартал",
                    "description": "Решить 20 CTF задач за квартал",
                    "target_value": 20,
                    "period": "QUARTER",
                },
            ]

            for goal_data in standard_goals:
                goal, created = FlexibleGoal.objects.get_or_create(
                    user=user,
                    name=goal_data["name"],
                    defaults={
                        "description": goal_data["description"],
                        "target_value": goal_data["target_value"],
                        "period": goal_data["period"],
                        "start_date": date.today(),
                        "current_value": 0,
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(f'  Создана цель: {goal_data["name"]}')

        if not User.objects.filter(username="demo").exists():
            demo_user = User.objects.create_user("demo", "demo@example.com", "demo")
            demo_user.first_name = "Демо"
            demo_user.last_name = "Пользователь"
            demo_user.save()

            demo_profile = UserProfile.objects.create(
                user=demo_user,
                calories_target=2300,
                protein_target=140,
                sleep_target=7.0,
            )

            self.stdout.write(self.style.SUCCESS("Создан демо-пользователь demo/demo"))

        self.stdout.write(self.style.SUCCESS("Инициализация завершена успешно!"))
        self.stdout.write("\nДоступные пользователи:")
        self.stdout.write("  admin / admin (суперпользователь)")
        self.stdout.write("  demo / demo (демо-пользователь)")
        self.stdout.write("\nДля запуска выполните:")
        self.stdout.write("  python manage.py runserver")
