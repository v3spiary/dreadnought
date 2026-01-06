from decimal import Decimal

from .models import DailyMetric, ForceMajeureEvent, UserProfile


class GradeCalculator:
    """Калькулятор оценок по системе S-F с +/-"""

    GRADE_RANGES = {
        "S": (95, 100),
        "A+": (90, 94),
        "A": (85, 89),
        "A-": (80, 84),
        "B+": (77, 79),
        "B": (73, 76),
        "B-": (70, 72),
        "C+": (65, 69),
        "C": (60, 64),
        "C-": (55, 59),
        "D+": (50, 54),
        "D": (45, 49),
        "D-": (40, 44),
        "F": (0, 39),
    }

    @staticmethod
    def calculate_daily_grade(user, target_date):
        """Рассчитать оценку за конкретный день"""
        try:
            metric = DailyMetric.objects.get(user=user, date=target_date)
            profile = UserProfile.objects.get(user=user)

            # Проверяем форс-мажор
            is_force_majeure = (
                ForceMajeureEvent.objects.filter(
                    user=user,
                    start_date__lte=target_date,
                    end_date__gte=target_date,
                    is_active=True,
                ).exists()
                or metric.is_force_majeure
            )

            # Расчет по категориям
            vital_percentage = GradeCalculator._calculate_vital(
                metric, profile, is_force_majeure
            )
            mind_percentage = GradeCalculator._calculate_mind(metric, is_force_majeure)
            discipline_percentage = GradeCalculator._calculate_discipline(
                metric, is_force_majeure
            )

            # Итоговый процент с весами
            total_percentage = (
                vital_percentage * Decimal("0.4")  # 40%
                + mind_percentage * Decimal("0.4")  # 40%
                + discipline_percentage * Decimal("0.2")  # 20%
            )

            # Определение буквенной оценки
            grade = GradeCalculator._percentage_to_grade(total_percentage)

            return {
                "total_percentage": total_percentage,
                "grade": grade,
                "vital_percentage": vital_percentage,
                "mind_percentage": mind_percentage,
                "discipline_percentage": discipline_percentage,
                "is_force_majeure": is_force_majeure,
                "details": {
                    "vital_breakdown": GradeCalculator._get_vital_breakdown(
                        metric, profile
                    ),
                    "mind_breakdown": GradeCalculator._get_mind_breakdown(metric),
                    "discipline_breakdown": GradeCalculator._get_discipline_breakdown(
                        metric
                    ),
                },
            }

        except DailyMetric.DoesNotExist:
            return None

    @staticmethod
    def _calculate_vital(metric, profile, is_force_majeure):
        """Расчет категории Vital (40%)"""
        adjustments = Decimal("0.8") if is_force_majeure else Decimal("1.0")

        # Калории (25% от категории)
        if profile.calories_target > 0:
            calories_diff = abs(metric.calories - profile.calories_target)
            calories_pct = max(0, 100 - (calories_diff / profile.calories_target * 100))
            calories_score = min(calories_pct, 100) * Decimal("0.25")
        else:
            calories_score = Decimal("0")

        # Белок (25% от категории)
        if profile.protein_target > 0:
            protein_pct = min((metric.protein / profile.protein_target * 100), 100)
            protein_score = protein_pct * Decimal("0.25")
        else:
            protein_score = Decimal("0")

        # Сон (30% от категории)
        if metric.sleep_hours >= Decimal("7.5"):
            sleep_pct = 100
        elif metric.sleep_hours >= Decimal("6"):
            sleep_pct = (metric.sleep_hours / Decimal("7.5")) * 100
        else:
            sleep_pct = (metric.sleep_hours / Decimal("7.5")) * 80  # Штраф за недосып

        sleep_score = sleep_pct * Decimal("0.3")

        # Тренировки (20% от категории)
        training_pct = (
            100 if (metric.was_training or metric.was_training_yesterday) else 0
        )
        training_score = training_pct * Decimal("0.2")

        total = (
            calories_score + protein_score + sleep_score + training_score
        ) * adjustments
        return min(total, 100)

    @staticmethod
    def _calculate_mind(metric, is_force_majeure):
        """Расчет категории Mind (40%)"""
        adjustments = Decimal("0.8") if is_force_majeure else Decimal("1.0")

        # Математика (30%)
        math_pct = min((metric.math_tasks_solved / 3 * 100), 100)
        math_score = math_pct * Decimal("0.3")

        # LeetCode (30%)
        leetcode_pct = min(metric.leetcode_tasks_solved * 100, 100)
        leetcode_score = leetcode_pct * Decimal("0.3")

        # CTF (20%)
        ctf_pct = min(metric.ctf_tasks_solved * 100, 100)
        ctf_score = ctf_pct * Decimal("0.2")

        # Книги (20%)
        pages_pct = min((metric.pages_read / 20 * 100), 100)
        pages_score = pages_pct * Decimal("0.2")

        total = (math_score + leetcode_score + ctf_score + pages_score) * adjustments
        return min(total, 100)

    @staticmethod
    def _calculate_discipline(metric, is_force_majeure):
        """Расчет категории Discipline (20%) с штрафами за срывы"""
        base_score = 100 if metric.diary_entry_done else 0

        # Штрафы за срывы (вычитаются из базового)
        penalties = (
            metric.dopamine_critical * 15  # -15% за каждый критический
            + max(0, metric.dopamine_moderate - 1)
            * 10  # -10% за умеренный сверх лимита
            + max(0, metric.dopamine_light - 2) * 5  # -5% за легкий сверх лимита
        )

        total = max(0, base_score - penalties)

        if is_force_majeure:
            total = total * Decimal("0.7")  # Меньше требований в форс-мажоре

        return min(total, 100)

    @staticmethod
    def _percentage_to_grade(percentage):
        """Конвертация процента в буквенную оценку"""
        percentage_float = float(percentage)
        for grade, (min_range, max_range) in GradeCalculator.GRADE_RANGES.items():
            if min_range <= percentage_float <= max_range:
                return grade
        return "F"

    @staticmethod
    def _get_vital_breakdown(metric, profile):
        return {
            "calories": {"value": metric.calories, "target": profile.calories_target},
            "protein": {"value": metric.protein, "target": profile.protein_target},
            "sleep": {
                "value": float(metric.sleep_hours),
                "target": float(profile.sleep_target),
            },
            "training": {
                "today": metric.was_training,
                "yesterday": metric.was_training_yesterday,
            },
        }

    @staticmethod
    def _get_mind_breakdown(metric):
        return {
            "math_tasks": metric.math_tasks_solved,
            "leetcode": metric.leetcode_tasks_solved,
            "ctf": metric.ctf_tasks_solved,
            "pages": metric.pages_read,
        }

    @staticmethod
    def _get_discipline_breakdown(metric):
        return {
            "diary": metric.diary_entry_done,
            "dopamine_critical": metric.dopamine_critical,
            "dopamine_moderate": metric.dopamine_moderate,
            "dopamine_light": metric.dopamine_light,
        }
