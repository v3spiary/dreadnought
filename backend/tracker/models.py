from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TrackerUserProfile(models.Model):
    """Расширенный профиль пользователя с настройками целей"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    force_majeure_mode = models.BooleanField(
        default=False,
        verbose_name="Режим форс-мажора",
        help_text="Активен при болезни/отпуске, меняет правила оценки",
    )
    calories_target = models.PositiveIntegerField(
        default=2500, verbose_name="Целевые калории"
    )
    protein_target = models.PositiveIntegerField(
        default=220, verbose_name="Целевой белок (г)"
    )
    sleep_target = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=7.5,
        validators=[MinValueValidator(6), MaxValueValidator(10)],
        verbose_name="Целевой сон (часы)",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


class DailyMetric(models.Model):
    """Ежедневные показатели пользователя"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_metrics"
    )
    date = models.DateField(auto_now_add=True, verbose_name="Дата записи")

    # Базовые метрики
    calories = models.PositiveIntegerField(default=0, verbose_name="Калории (ккал)")
    protein = models.PositiveIntegerField(default=0, verbose_name="Белок (грамм)")
    sleep_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
        verbose_name="Сон (часы)",
    )
    was_training = models.BooleanField(default=False, verbose_name="Тренировка сегодня")
    was_training_yesterday = models.BooleanField(
        default=False, verbose_name="Тренировка вчера"
    )

    # Интеллектуальные метрики
    math_tasks_solved = models.PositiveIntegerField(
        default=0, verbose_name="Решено мат. задач"
    )
    diary_entry_done = models.BooleanField(
        default=False, verbose_name="Запись в дневнике"
    )
    leetcode_tasks_solved = models.PositiveIntegerField(
        default=0, verbose_name="Решено LeetCode"
    )
    ctf_tasks_solved = models.PositiveIntegerField(default=0, verbose_name="Решено CTF")
    pages_read = models.PositiveIntegerField(
        default=0, verbose_name="Прочитано страниц"
    )

    # Дофаминовые срывы (сегрегированные)
    dopamine_critical = models.PositiveIntegerField(
        default=0,
        verbose_name="Критические срывы",
        help_text="Порн, серьезные нарушения",
    )
    dopamine_moderate = models.PositiveIntegerField(
        default=0,
        verbose_name="Умеренные срывы",
        help_text="Рилсы (TikTok, YT Shorts >15 мин)",
    )
    dopamine_light = models.PositiveIntegerField(
        default=0, verbose_name="Легкие срывы", help_text="Сладкое (печенье, шоколад)"
    )

    # Служебные поля
    is_force_majeure = models.BooleanField(
        default=False, verbose_name="День в режиме форс-мажора"
    )
    notes = models.TextField(blank=True, verbose_name="Заметки за день")

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]
        verbose_name = "Ежедневная метрика"
        verbose_name_plural = "Ежедневные метрики"


class DailyGrade(models.Model):
    """Рассчитанная оценка за день"""

    GRADE_CHOICES = [
        ("S", "S"),
        ("A+", "A+"),
        ("A", "A"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B", "B"),
        ("B-", "B-"),
        ("C+", "C+"),
        ("C", "C"),
        ("C-", "C-"),
        ("D+", "D+"),
        ("D", "D"),
        ("D-", "D-"),
        ("F", "F"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_grades"
    )
    date = models.DateField(verbose_name="Дата оценки")
    total_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Итоговый процент",
    )
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, verbose_name="Оценка")

    # Проценты по категориям (для графиков)
    vital_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Vital %"
    )
    mind_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Mind %"
    )
    discipline_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Discipline %"
    )

    # Детализация для анализа
    details_json = models.JSONField(default=dict, verbose_name="Детали расчета")

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]
        verbose_name = "Оценка дня"
        verbose_name_plural = "Оценки дней"


class BodyMeasurement(models.Model):
    """Периодические замеры физических показателей"""

    MEASUREMENT_TYPE_CHOICES = [
        ("GYM", "Зал (силовые)"),
        ("BODY", "Композиция тела"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="body_measurements"
    )
    date = models.DateField(auto_now_add=True, verbose_name="Дата замера")
    measurement_type = models.CharField(
        max_length=10, choices=MEASUREMENT_TYPE_CHOICES, verbose_name="Тип замера"
    )

    # Показатели состава тела
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Вес (кг)"
    )
    muscle_mass = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Мышечная масса (кг)",
    )
    fat_percent = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Процент жира (%)",
    )
    visceral_fat = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Висцеральный жир (уровень)",
    )

    # Силовые показатели (структурированные)
    exercise_data = models.JSONField(
        default=dict,
        verbose_name="Данные по упражнениям",
        help_text="{'жим_лежа': {'вес': 80, 'повторы': 8, 'подходы': 3}, ...}",
    )

    notes = models.TextField(blank=True, verbose_name="Заметки к замеру")

    class Meta:
        ordering = ["-date"]
        verbose_name = "Физический замер"
        verbose_name_plural = "Физические замеры"


class FlexibleGoal(models.Model):
    """Гибкая цель для показателей, которые фиксируются не каждый день"""

    GOAL_PERIOD_CHOICES = [
        ("WEEK", "Раз в неделю"),
        ("TWO_WEEKS", "Раз в две недели"),
        ("MONTH", "Раз в месяц"),
        ("QUARTER", "Раз в квартал"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="flexible_goals"
    )
    name = models.CharField(max_length=255, verbose_name="Название цели")
    description = models.TextField(blank=True, verbose_name="Описание цели")
    target_value = models.PositiveIntegerField(verbose_name="Целевое значение")
    current_value = models.PositiveIntegerField(
        default=0, verbose_name="Текущее значение"
    )
    period = models.CharField(
        max_length=20, choices=GOAL_PERIOD_CHOICES, verbose_name="Период"
    )
    start_date = models.DateField(verbose_name="Дата начала отсчета")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    # Для автоматического сброса
    last_reset_date = models.DateField(
        null=True, blank=True, verbose_name="Дата последнего сброса"
    )

    class Meta:
        ordering = ["period", "start_date"]
        verbose_name = "Гибкая цель"
        verbose_name_plural = "Гибкие цели"


class ForceMajeureEvent(models.Model):
    """События форс-мажора для корректировки оценок"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="force_majeure_events"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    reason = models.CharField(max_length=255, verbose_name="Причина")
    description = models.TextField(blank=True, verbose_name="Подробное описание")
    adjustment_multiplier = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name="Коэффициент корректировки",
        help_text="На сколько снижать планку (0.5 = на 50%)",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Событие форс-мажора"
        verbose_name_plural = "События форс-мажора"
