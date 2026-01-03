from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from tracker.models import DailyGrade, DailyMetric
from tracker.utils.grade_calculator import GradeCalculator


class Command(BaseCommand):
    help = "Рассчитать оценки за вчерашний день для всех пользователей"

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)

        for user in User.objects.all():
            result = GradeCalculator.calculate_daily_grade(user, yesterday)
            if result:
                DailyGrade.objects.update_or_create(
                    user=user,
                    date=yesterday,
                    defaults={
                        "total_percentage": result["total_percentage"],
                        "grade": result["grade"],
                        "vital_percentage": result["vital_percentage"],
                        "mind_percentage": result["mind_percentage"],
                        "discipline_percentage": result["discipline_percentage"],
                        "details_json": result["details"],
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"Рассчитаны оценки за {yesterday}"))
